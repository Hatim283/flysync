import os
import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger("FlySync.PlannerAgent")

class ItineraryDay(BaseModel):
    day_number: int
    morning: str
    afternoon: str
    evening: str

class ItineraryPlan(BaseModel):
    destination: str
    days: List[ItineraryDay]
    local_tips: str

def generate_itinerary(destination: str, duration_days: int, user_interests: str) -> Dict[str, Any]:
    """
    Agent Tool: Generates a day-by-day itinerary based on the destination and user interests.
    Uses Gemini Structured Outputs.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "destination": destination,
            "days": [{"day_number": 1, "morning": "City Tour", "afternoon": "Museum Visit", "evening": "Local Dinner"}],
            "local_tips": "Mocked itinerary due to missing API key."
        }
        
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"You are a local expert travel guide for {destination}. "
            f"Create a highly detailed {duration_days}-day itinerary tailored to these interests: {user_interests}. "
            "Include morning, afternoon, and evening activities. Also provide some local tips."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ItineraryPlan,
            ),
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Itinerary Planner Agent failed: {e}")
        return {"error": "Failed to generate itinerary"}
