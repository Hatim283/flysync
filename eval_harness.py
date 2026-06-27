import os
import sys
import logging
import datetime
import json

from schema import AgentState, UserPreferences
from agent_graph import FlySyncGraphOrchestrator
import mcp_tools

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("FlySync.Eval")

def run_llm_judge(state: AgentState, test_name: str) -> dict:
    """
    Acts as the LLM-as-a-Judge rule.
    Submits the state output and execution trace to Gemini to verify that 
    the agents correctly solved currency translations, loyalty programs, and schedule constraints.
    """
    logger.info(f"[{test_name}] Starting LLM-as-a-Judge validation...")
    
    # Render detailed data for the judge
    state_json = json.dumps({
        "user_preferences": state.user_preferences.model_dump(),
        "selected_flight": state.selected_flight.model_dump() if state.selected_flight else None,
        "selected_hotel": state.selected_hotel.model_dump() if state.selected_hotel else None,
        "calendar_conflicts": state.calendar_conflicts,
        "total_cost_home": state.total_cost_home,
        "loyalty_details": state.loyalty_details.model_dump() if state.loyalty_details else None,
        "price_analysis": state.price_analysis.model_dump() if state.price_analysis else None,
    }, indent=2)
    
    trace_text = "\n".join(state.execution_trace)
    
    # Pre-calculated rule-based check as the local fallback judge
    local_pass = True
    reasons = []
    
    # 1. Budget shield check
    if state.selected_flight and state.selected_hotel:
        total_calculated = state.selected_flight.price_home + (state.selected_hotel.price_home * 3)
        if total_calculated > state.user_preferences.max_budget:
            if "breach" not in state.status_message.lower() and "breach" not in "".join(state.execution_trace).lower():
                local_pass = False
                reasons.append("Budget shield failed to flag a budget breach.")
        else:
            if "breach" in state.status_message.lower():
                local_pass = False
                reasons.append("Budget shield incorrectly flagged a breach when cost is within limits.")
                
    # 2. Calendar check
    has_overlap_dates = False
    if state.selected_flight:
        # simple check if departure is 2026-07-10
        if "2026-07-10" in state.selected_flight.departure_time:
            has_overlap_dates = True
            
    if has_overlap_dates and not state.calendar_conflicts:
        local_pass = False
        reasons.append("Calendar overlap was not identified by the Sync Coordinator.")
        
    # 3. Loyalty check
    if state.loyalty_details:
        expected_multiplier = {
            "flyBronze": 1.0,
            "flySilver": 1.2,
            "flyGold": 1.5,
            "flyDiamond": 2.0
        }.get(state.user_preferences.membership_tier, 1.0)
        
        # calculate base points: total_usd * 10
        total_usd = mcp_tools.convert_currency(state.total_cost_home, state.user_preferences.home_currency, "USD")
        expected_points = round(total_usd * 10.0 * expected_multiplier, 2)
        diff = abs(state.loyalty_details.points_accrued - expected_points)
        if diff > 10.0: # allow minor rounding margin
            local_pass = False
            reasons.append(f"Loyalty points calculation error. Expected: {expected_points}, Got: {state.loyalty_details.points_accrued}")

    judge_result = {
        "verdict": "PASS" if local_pass else "FAIL",
        "explanation": "Local rules-based verification completed successfully. " + ("; ".join(reasons) if reasons else "All systems operating within specifications.")
    }
    
    # Try using actual LLM-as-a-Judge if GEMINI_API_KEY is active
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        import time
        time.sleep(15) # Throttle LLM judge
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            prompt = (
                f"You are the LLM-as-a-Judge for the FlySync Multi-Agent Concierge system.\n"
                f"Review the following agent output state and execution trace to verify that the agents executed instructions correctly.\n\n"
                f"=== AGENT OUTPUT STATE ===\n{state_json}\n\n"
                f"=== AGENT EXECUTION TRACE ===\n{trace_text}\n\n"
                f"Verify the following rules:\n"
                f"1. Currency conversions are accurate and display the home currency code: {state.user_preferences.home_currency}.\n"
                f"2. The 'Smart Budget Shield' successfully blocked options exceeding the max budget of {state.user_preferences.max_budget}.\n"
                f"3. Calendar overlaps (if any) are flagged as conflicts and timezones are formatted.\n"
                f"4. The loyalty tier reward point multipliers (flyBronze=1x, flySilver=1.2x, flyGold=1.5x, flyDiamond=2x) and hotel discounts (Silver=10%, Gold=15%, Diamond=20%) are correctly applied.\n\n"
                f"Output a JSON dict with exactly two keys:\n"
                f"- 'verdict': 'PASS' or 'FAIL'\n"
                f"- 'explanation': 'A detailed explanation of why it passed or failed'\n"
                f"Only output the JSON block."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            text = response.text.strip()
            # Clean markdown codeblocks
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                text = match.group(0)
            data = json.loads(text)
            
            if "verdict" in data and "explanation" in data:
                logger.info(f"[{test_name}] Gemini Judge Verdict: {data['verdict']}")
                logger.info(f"[{test_name}] Gemini Judge Explanation: {data['explanation']}")
                return data
        except Exception as e:
            logger.warning(f"[{test_name}] Gemini Judge call failed: {e}. Defaulting to rule-based verification.")
            
    logger.info(f"[{test_name}] Local Judge Verdict: {judge_result['verdict']}")
    logger.info(f"[{test_name}] Local Judge Explanation: {judge_result['explanation']}")
    return judge_result

def test_scenario_1():
    """
    Test Case 1: Standard Search with Silver Tier
    - User home currency: USD
    - Preferred seat: window
    - Tier: flySilver (1.2x points, 10% hotel discount)
    - Budget: $2500 USD (Should easily fit)
    - Travel: DXB to LON on 2026-07-05 (Should be no calendar conflicts)
    """
    logger.info("\n==========================================")
    logger.info("Executing Test Scenario 1: Silver Tier Concierge Sync")
    logger.info("==========================================")
    
    prefs = UserPreferences(
        home_currency="USD",
        preferred_seating="window",
        membership_tier="flySilver",
        max_budget=2500.0,
        preferred_airline="FlySync Airways"
    )
    
    state = AgentState(user_preferences=prefs)
    orchestrator = FlySyncGraphOrchestrator()
    
    # Run the multi-agent graph
    final_state = orchestrator.execute_workflow(
        state=state,
        origin="DXB",
        destination="LON",
        travel_date="2026-07-05"
    )
    
    # Core assertions
    assert final_state.selected_flight is not None, "Flight should have been selected"
    assert final_state.selected_hotel is not None, "Hotel should have been selected"
    assert len(final_state.calendar_conflicts) == 0, "There should be no calendar conflicts on July 5"
    assert final_state.total_cost_home <= prefs.max_budget, "Total cost should be within budget"
    assert final_state.loyalty_details is not None, "Loyalty details must be calculated"
    assert final_state.loyalty_details.tier == "flySilver", "Loyalty tier must be flySilver"
    
    # Run LLM judge
    judge = run_llm_judge(final_state, "Test Scenario 1")
    return final_state, judge

def test_scenario_2():
    """
    Test Case 2: Over budget, calendar conflict, Diamond Tier
    - User home currency: GBP
    - Tier: flyDiamond (2.0x points, 20% hotel discount + priority perks)
    - Budget: £200 GBP (Low budget, triggers Smart Budget Shield warning)
    - Travel: LHR to SIN on 2026-07-10 (overlaps corporate summit conflict)
    """
    logger.info("\n==========================================")
    logger.info("Executing Test Scenario 2: Over Budget, Calendar Overlap & Diamond Perks")
    logger.info("==========================================")
    
    prefs = UserPreferences(
        home_currency="GBP",
        preferred_seating="aisle",
        membership_tier="flyDiamond",
        max_budget=200.0
    )
    
    state = AgentState(user_preferences=prefs)
    orchestrator = FlySyncGraphOrchestrator()
    
    # Run the multi-agent graph
    final_state = orchestrator.execute_workflow(
        state=state,
        origin="LHR",
        destination="SIN",
        travel_date="2026-07-10"
    )
    
    # Core assertions
    assert final_state.selected_flight is not None, "Should still return cheapest selection even on breach"
    assert len(final_state.calendar_conflicts) > 0, "Calendar conflict must be flagged for July 10"
    assert final_state.status_message == "Budget Shield Breached", "Budget shield should flag a breach"
    assert final_state.loyalty_details.tier == "flyDiamond", "Loyalty tier must be flyDiamond"
    assert any("Priority Support Routing" in perk for perk in final_state.loyalty_details.perks_unlocked), "Diamond priority support perk must unlock"
    
    # Run LLM judge
    judge = run_llm_judge(final_state, "Test Scenario 2")
    return final_state, judge

if __name__ == "__main__":
    logger.info("Starting FlySync Capstone Agent Evaluation Harness")
    
    results = {"passed": 0, "failed": 0, "scenarios": []}
    
    try:
        # Scenario 1
        s1_state, s1_judge = test_scenario_1()
        results["passed"] += 1 if s1_judge["verdict"] == "PASS" else 0
        results["failed"] += 1 if s1_judge["verdict"] == "FAIL" else 0
        results["scenarios"].append({"name": "Scenario 1", "judge": s1_judge})
        
        # Scenario 2
        s2_state, s2_judge = test_scenario_2()
        results["passed"] += 1 if s2_judge["verdict"] == "PASS" else 0
        results["failed"] += 1 if s2_judge["verdict"] == "FAIL" else 0
        results["scenarios"].append({"name": "Scenario 2", "judge": s2_judge})
        
        logger.info("\n==========================================")
        logger.info("Evaluation Harness Results Summary")
        logger.info(f"Total Scenarios Evaluated: {results['passed'] + results['failed']}")
        logger.info(f"Passed Scenarios: {results['passed']}")
        logger.info(f"Failed Scenarios: {results['failed']}")
        logger.info("==========================================")
        
        if results["failed"] > 0:
            logger.error("Harness failed. Please check state traces.")
            sys.exit(1)
        else:
            logger.info("All tests passed. System logic verified.")
            sys.exit(0)
            
    except Exception as e:
        logger.exception(f"Harness run crashed: {e}")
        sys.exit(1)
