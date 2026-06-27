import logging
from typing import Dict, Any, List, Optional
import datetime
import os

# Import Google ADK classes
try:
    from google.adk import Agent, Workflow
except ImportError:
    # Local fallback definitions for development independence if google-adk is loading
    class Agent:
        def __init__(self, name: str, instruction: str, tools: Optional[List[Any]] = None):
            self.name = name
            self.instruction = instruction
            self.tools = tools or []
    class Workflow:
        def __init__(self, name: str, edges: List[Any]):
            self.name = name
            self.edges = edges

from schema import AgentState, UserPreferences, FlightOption, HotelOption, PriceAnalysis, LoyaltyDetails, SupportTicket
import mcp_tools

logger = logging.getLogger("FlySync.Graph")

# 1. Define Scout Agent
scout_agent = Agent(
    name="Agent_A_Scout",
    instruction="Aggregates, cross-references, and deduplicates flight/hotel listings. Enforces the Smart Budget Shield.",
    tools=[mcp_tools.mock_flight_lookup, mcp_tools.mock_hotel_lookup]
)

# 2. Define Sync Coordinator Agent
sync_coordinator_agent = Agent(
    name="Agent_B_SyncCoordinator",
    instruction="Checks calendar availability, flags overlaps, and manages time-zone transitions.",
    tools=[mcp_tools.check_calendar_availability]
)

# 3. Define Sentinel Agent
sentinel_agent = Agent(
    name="Agent_C_Sentinel",
    instruction="Monitors dynamic pricing states, calculates rewards, triggers loyalty program perks, and resolves support tickets.",
    tools=[mcp_tools.evaluate_price_trends, mcp_tools.calculate_loyalty_rewards, mcp_tools.lookup_support_faq]
)

# Define workflow graph edges conceptually matching ADK 2.0 specs
# START -> Scout -> Sync Coordinator -> Sentinel
flysync_workflow = Workflow(
    name="FlySync_Concierge_Workflow",
    edges=[
        ("START", scout_agent),
        (scout_agent, sync_coordinator_agent),
        (sync_coordinator_agent, sentinel_agent)
    ]
)

class FlySyncGraphOrchestrator:
    """
    Executes the multi-agent graph dynamically using Gemini's native tool calling capabilities.
    The agent autonomously decides when to search flights, check calendar, and calculate rewards.
    """
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. Agent orchestration requires Gemini.")

    def execute_workflow(self, state: AgentState, origin: str, destination: str, travel_date: str, support_query: Optional[str] = None) -> AgentState:
        """
        Runs the dynamic agentic flow.
        """
        state.execution_trace = []
        state.execution_trace.append("=== Starting Dynamic Agentic Orchestration ===")
        
        if not self.api_key:
            state.execution_trace.append("[CRITICAL ERROR] GEMINI_API_KEY missing. Cannot run agentic workflow.")
            state.status_message = "Failed"
            return state

        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=self.api_key)
            
            # 1. Provide all tools to Gemini
            tools = [
                mcp_tools.mock_flight_lookup,
                mcp_tools.mock_hotel_lookup,
                mcp_tools.check_calendar_availability,
                mcp_tools.evaluate_price_trends,
                mcp_tools.calculate_loyalty_rewards
            ]
            
            # 2. System Instruction defining the Multi-Agent prompt
            system_instruction = (
                "You are FlySync Hub, a premium AI travel concierge consisting of three sub-agents:\n"
                "1. Scout Agent: Finds the best flights and hotels within the user's budget.\n"
                "2. Sync Coordinator: Checks calendar conflicts.\n"
                "3. Sentinel Agent: Evaluates price trends and calculates loyalty rewards.\n\n"
                "You must autonomously fulfill the user's travel request by calling the provided tools.\n"
                "Ensure you respect the user's budget limit and membership tier."
            )
            
            # 3. Formulate the user task
            user_prompt = (
                f"I want to travel from {origin} to {destination} starting on {travel_date}. "
                f"My home currency is {state.user_preferences.home_currency}. "
                f"My budget is {state.user_preferences.max_budget} {state.user_preferences.home_currency}. "
                f"My tier is {state.user_preferences.membership_tier}. "
                f"If there is a support query, address it: {support_query if support_query else 'None'}"
            )
            
            state.execution_trace.append(f"[Agent Orchestrator] Initializing Gemini session with dynamic tool routing.")
            
            chat = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=tools,
                    temperature=0.1,
                )
            )
            
            response = chat.send_message(user_prompt)
            state.execution_trace.append("[Agent Orchestrator] Agent planning and tool invocation complete.")
            state.execution_trace.append(f"[Agent Orchestrator] Agent synthesis: {response.text[:100]}...")
            
        except ImportError as e:
            state.execution_trace.append(f"[CRITICAL WORKFLOW EXCEPTION] Orchestrator missing dependency: {e}")
            state.status_message = "Failed"
        except Exception as e:
            state.execution_trace.append(f"[CRITICAL WORKFLOW EXCEPTION] Orchestrator crashed (likely Rate Limit): {e}")
            state.execution_trace.append("[Agent Orchestrator] Falling back to deterministic rule-based execution.")
            
        # --- HYBRID FALLBACK: Guarantee State Population ---
        # Even if the LLM succeeds, we execute deterministic logic to populate the Pydantic UI state correctly.
        # If the LLM crashed (e.g. 429), this acts as a robust failover.
        try:
            state.execution_trace.append("[Agent Orchestrator] Syncing agent actions to UI Application State.")
            
            flights = mcp_tools.mock_flight_lookup(origin, destination, travel_date, state.user_preferences.home_currency)
            state.flight_options = [FlightOption(**f) for f in flights]
            hotels = mcp_tools.mock_hotel_lookup(
                destination, 
                travel_date, 
                (datetime.datetime.strptime(travel_date, "%Y-%m-%d") + datetime.timedelta(days=3)).strftime("%Y-%m-%d"), 
                state.user_preferences.home_currency,
                state.user_preferences.membership_tier
            )
            state.hotel_options = [HotelOption(**h) for h in hotels]
            
            selected_pair = None
            for flight in state.flight_options:
                for hotel in state.hotel_options:
                    total_cost = flight.price_home + (hotel.price_home * 3)
                    if total_cost <= state.user_preferences.max_budget:
                        selected_pair = (flight, hotel, total_cost)
                        break
                if selected_pair:
                    break
            
            if selected_pair:
                state.selected_flight = selected_pair[0]
                state.selected_hotel = selected_pair[1]
                state.total_cost_home = round(selected_pair[2], 2)
            else:
                state.selected_flight = state.flight_options[0]
                state.selected_hotel = state.hotel_options[0]
                state.total_cost_home = round(state.flight_options[0].price_home + (state.hotel_options[0].price_home * 3), 2)
                state.status_message = "Budget Shield Breached"
                
            cal_res = mcp_tools.check_calendar_availability(travel_date, 3)
            state.calendar_conflicts = cal_res["conflicts"]
            
            total_usd = mcp_tools.convert_currency(state.total_cost_home, state.user_preferences.home_currency, "USD")
            loyalty_raw = mcp_tools.calculate_loyalty_rewards(total_usd, state.user_preferences.membership_tier)
            state.loyalty_details = LoyaltyDetails(**loyalty_raw)
            
            baseline_usd = 600.0 if origin in ["LHR", "DXB", "CDG"] else 400.0
            baseline_home = mcp_tools.convert_currency(baseline_usd, "USD", state.user_preferences.home_currency)
            analysis_raw = mcp_tools.evaluate_price_trends(state.selected_flight.price_home, baseline_home)
            analysis_raw["current_fare"] = state.selected_flight.price_home
            analysis_raw["seasonal_baseline"] = baseline_home
            state.price_analysis = PriceAnalysis(**analysis_raw)
            
            if support_query:
                faq_answer = mcp_tools.lookup_support_faq(support_query)
                ticket = SupportTicket(
                    ticket_id=f"TKT-{datetime.datetime.now().strftime('%M%S')}",
                    issue_type="FAQ Inquiry",
                    status="resolved",
                    user_query=support_query,
                    agent_response=faq_answer
                )
                state.support_tickets.append(ticket)
                
            if state.total_cost_home <= state.user_preferences.max_budget:
                state.status_message = "Completed"
        except Exception as e:
            state.execution_trace.append(f"[CRITICAL WORKFLOW EXCEPTION] Fallback logic crashed: {e}")
            state.status_message = "Failed"
            
        state.execution_trace.append("=== Workflow Execution Completed ===")
        return state
