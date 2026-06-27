import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import AgentState, UserPreferences, FlightOption, HotelOption, PriceAnalysis, LoyaltyDetails, SupportTicket
from agent_graph import FlySyncGraphOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlySync.Backend")

app = FastAPI(title="FlySync Hub API", version="1.0.0", description="Production API for FlySync Agentic Travel Platform")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    origin: str
    destination: str
    travel_date: str
    preferences: UserPreferences
    support_query: Optional[str] = None

@app.post("/api/search")
async def execute_agent_search(req: SearchRequest):
    """
    Executes the dynamic Gemini agent workflow and returns the populated agent state.
    """
    try:
        # Initialize base state
        state = AgentState(user_preferences=req.preferences)
        
        # Execute workflow
        orchestrator = FlySyncGraphOrchestrator()
        final_state = orchestrator.execute_workflow(
            state=state,
            origin=req.origin,
            destination=req.destination,
            travel_date=req.travel_date,
            support_query=req.support_query
        )
        
        if final_state.status_message == "Failed":
            raise HTTPException(status_code=500, detail="Agent Orchestrator failed to execute workflow.")
            
        return final_state
        
    except Exception as e:
        logger.error(f"Search API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

