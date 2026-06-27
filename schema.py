from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserPreferences(BaseModel):
    home_currency: str = Field(default="USD", description="The currency the user prefers to see overall prices in (AED, USD, INR, GBP, EUR, SGD).")
    preferred_seating: str = Field(default="window", description="Seat preference, e.g., window, aisle.")
    membership_tier: str = Field(default="flyBronze", description="Membership tier: flyBronze, flySilver, flyGold, flyDiamond.")
    max_budget: float = Field(default=2000.0, description="The maximum travel budget in the home currency.")
    preferred_airline: Optional[str] = Field(default=None, description="Preferred airline name if any.")
    seating_class: str = Field(default="economy", description="Economy, Premium Economy, Business, First.")
    points_balance: float = Field(default=0.0, description="The user's current loyalty points balance.")

class FlightOption(BaseModel):
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    price_native: float
    currency_native: str
    price_home: float
    stops: int = 0
    cabin_class: str = "economy"
    confirmation_number: Optional[str] = None

class HotelOption(BaseModel):
    hotel_name: str
    location: str
    price_native: float
    currency_native: str
    price_home: float
    rating: float
    amenities: List[str] = []
    check_in: str
    check_out: str
    room_type: str = "standard"
    confirmation_number: Optional[str] = None

class PriceAnalysis(BaseModel):
    current_fare: float
    seasonal_baseline: float
    price_status: str  # "Low", "Average", "High"
    buying_verdict: str  # "BUY NOW", "WAIT - LIKELY TO DROP"
    justification: str

class LoyaltyDetails(BaseModel):
    tier: str
    points_accrued: float
    discount_applied: float
    perks_unlocked: List[str] = []

class SupportTicket(BaseModel):
    ticket_id: str
    issue_type: str
    status: str  # "open", "resolved"
    user_query: str
    agent_response: str

class AgentState(BaseModel):
    user_preferences: UserPreferences
    flight_options: List[FlightOption] = []
    selected_flight: Optional[FlightOption] = None
    hotel_options: List[HotelOption] = []
    selected_hotel: Optional[HotelOption] = None
    calendar_conflicts: List[str] = []
    price_analysis: Optional[PriceAnalysis] = None
    loyalty_details: Optional[LoyaltyDetails] = None
    support_tickets: List[SupportTicket] = []
    execution_trace: List[str] = []
    total_cost_home: float = 0.0
    status_message: str = "Initialized"
