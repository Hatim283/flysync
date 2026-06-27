import os
import logging
from typing import Dict, Any
from pydantic import BaseModel

logger = logging.getLogger("FlySync.RiskAgent")

class RiskAssessment(BaseModel):
    destination: str
    weather_forecast: str
    travel_advisory_level: str
    safety_tips: str

def assess_travel_risk(destination: str, travel_date: str) -> Dict[str, Any]:
    """
    Agent Tool: Analyzes weather patterns and travel advisories for a destination.
    Uses Gemini Structured Outputs.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "destination": destination,
            "weather_forecast": "Sunny, 25°C",
            "travel_advisory_level": "Level 1: Exercise Normal Precautions",
            "safety_tips": "Mocked risk assessment due to missing API key."
        }
        
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            f"You are a global security and weather intelligence analyst. "
            f"Analyze the destination {destination} for the travel date {travel_date}. "
            "Provide a likely weather forecast, current general travel advisory level, and key safety tips."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RiskAssessment,
            ),
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Risk Agent failed: {e}")
        return {"error": "Failed to assess risk"}
