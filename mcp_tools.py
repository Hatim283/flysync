import os
import logging
import datetime
import time
from typing import List, Dict, Any, Optional

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlySync.Tools")

# Core exchange rates relative to USD (matrix: AED, USD, INR, GBP, EUR, SGD)
CURRENCY_RATES = {
    "USD": 1.0,
    "AED": 3.67,
    "INR": 83.5,
    "GBP": 0.79,
    "EUR": 0.93,
    "SGD": 1.35
}

def convert_currency(amount: float, from_curr: str, to_curr: str) -> float:
    """
    Normalizes a value to USD and converts it to the user's selected home currency.
    Supports AED, USD, INR, GBP, EUR, and SGD.
    """
    from_curr = from_curr.upper().strip()
    to_curr = to_curr.upper().strip()
    
    if from_curr not in CURRENCY_RATES or to_curr not in CURRENCY_RATES:
        # Fallback to USD or raise
        logger.warning(f"Unsupported currency conversion request: '{from_curr}' to '{to_curr}'. Defaulting to USD.")
        if from_curr not in CURRENCY_RATES:
            from_curr = "USD"
        if to_curr not in CURRENCY_RATES:
            to_curr = "USD"
            
    try:
        # Convert to USD first
        amount_usd = amount / CURRENCY_RATES[from_curr]
        # Convert from USD to target home currency
        amount_target = amount_usd * CURRENCY_RATES[to_curr]
        return round(amount_target, 2)
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        # Self-correction fallback loop
        return round(amount, 2)

def calculate_loyalty_rewards(amount_usd: float, tier: str) -> Dict[str, Any]:
    """
    Performs rewards point calculations ($1 USD = 10 base FlyPoints) 
    and returns tier-specific travel discounts and perks.
    Tiers: flyBronze, flySilver, flyGold, flyDiamond.
    """
    time.sleep(15) # Rate limit throttling for Gemini Free Tier
    valid_tiers = ["flyBronze", "flySilver", "flyGold", "flyDiamond"]
    if tier not in valid_tiers:
        tier = "flyBronze"
        
    multipliers = {
        "flyBronze": 1.0,
        "flySilver": 1.2,
        "flyGold": 1.5,
        "flyDiamond": 2.0
    }
    
    hotel_discounts = {
        "flyBronze": 0.0,
        "flySilver": 0.10,
        "flyGold": 0.15,
        "flyDiamond": 0.20
    }
    
    perks = {
        "flyBronze": ["Standard Mileage Accrual"],
        "flySilver": ["Standard Mileage Accrual", "10% Hotel Discount", "Priority Check-in"],
        "flyGold": ["Standard Mileage Accrual", "15% Hotel Discount", "Free Breakfast", "Lounge Access"],
        "flyDiamond": ["Standard Mileage Accrual", "20% Hotel Discount", "Free Breakfast", "Lounge Access", "Priority Support Routing"]
    }
    
    try:
        multiplier = multipliers[tier]
        base_points = amount_usd * 10.0
        points_earned = round(base_points * multiplier, 2)
        
        return {
            "tier": tier,
            "points_accrued": points_earned,
            "discount_applied": hotel_discounts[tier],
            "perks_unlocked": perks[tier]
        }
    except Exception as e:
        logger.error(f"Error calculating loyalty: {e}")
        return {
            "tier": "flyBronze",
            "points_accrued": amount_usd * 10.0,
            "discount_applied": 0.0,
            "perks_unlocked": ["Standard Mileage Accrual"]
        }

def mock_flight_lookup(origin: str, destination: str, date: str, preferred_home_currency: str) -> List[Dict[str, Any]]:
    """
    Scouts travel fares. Gathers simulated rates in native origin currencies
    and returns normalized prices in the home currency.
    Uses real-world airlines (Emirates, Gulf Air, British Airways, Singapore Airlines, Qatar Airways, etc.).
    """
    time.sleep(15) # Rate limit throttling for Gemini Free Tier
    origin = origin.upper().strip()
    destination = destination.upper().strip()
    
    # Set standard native origin currencies
    native_currency = "USD"
    if origin in ["LHR", "LON"]:
        native_currency = "GBP"
    elif origin in ["DXB", "DUB"]:
        native_currency = "AED"
    elif origin in ["CDG", "PAR", "AMS"]:
        native_currency = "EUR"
    elif origin in ["SIN"]:
        native_currency = "SGD"
    elif origin in ["BOM", "DEL"]:
        native_currency = "INR"

    # Base pricing constants (native currency)
    base_fares = {
        "LHR": 450.0,
        "DXB": 1800.0,
        "CDG": 500.0,
        "SIN": 750.0,
        "BOM": 38000.0,
        "NYC": 500.0,
        "SFO": 550.0
    }
    
    base_price = base_fares.get(origin, 600.0)
    
    # Map real-world airlines based on origin or destination
    if origin == "DXB":
        a1, a2, a3 = "Emirates", "Gulf Air", "flydubai"
    elif origin == "LHR":
        a1, a2, a3 = "British Airways", "Virgin Atlantic", "Gulf Air"
    elif origin == "SIN":
        a1, a2, a3 = "Singapore Airlines", "Scoot", "Qatar Airways"
    elif origin == "BOM" or origin == "DEL":
        a1, a2, a3 = "Air India", "Vistara", "IndiGo"
    else:
        a1, a2, a3 = "United Airlines", "Delta Air Lines", "British Airways"
        
    def get_logo(airline_name: str) -> str:
        logos = {
            "Emirates": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Emirates_logo.svg",
            "Gulf Air": "https://upload.wikimedia.org/wikipedia/en/b/ba/Gulf_Air_logo.svg",
            "flydubai": "https://upload.wikimedia.org/wikipedia/commons/5/52/Flydubai_Logo.svg",
            "British Airways": "https://upload.wikimedia.org/wikipedia/en/4/42/British_Airways_Logo.svg",
            "Virgin Atlantic": "https://upload.wikimedia.org/wikipedia/commons/2/25/Virgin_Atlantic_logo.svg",
            "Singapore Airlines": "https://upload.wikimedia.org/wikipedia/en/6/6b/Singapore_Airlines_Logo_2.svg",
            "Scoot": "https://upload.wikimedia.org/wikipedia/commons/3/30/Scoot_logo.svg",
            "Qatar Airways": "https://upload.wikimedia.org/wikipedia/en/9/9b/Qatar_Airways_Logo.svg",
            "Air India": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Air_India_Logo.svg",
            "Vistara": "https://upload.wikimedia.org/wikipedia/en/2/25/Vistara_Logo.svg",
            "IndiGo": "https://upload.wikimedia.org/wikipedia/commons/6/69/IndiGo_Airlines_logo.svg",
            "United Airlines": "https://upload.wikimedia.org/wikipedia/commons/e/e0/United_Airlines_Logo.svg",
            "Delta Air Lines": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Delta_logo.svg"
        }
        return logos.get(airline_name, "https://upload.wikimedia.org/wikipedia/commons/d/d1/Delta_logo.svg")

    # 3 mock flights matching different API sources
    flights = [
        {
            "flight_number": f"EK-{origin}-{destination}-101" if a1 == "Emirates" else f"BA-{origin}-{destination}-101" if a1 == "British Airways" else f"GF-{origin}-{destination}-101" if a1 == "Gulf Air" else f"SQ-{origin}-{destination}-101" if a1 == "Singapore Airlines" else f"AI-{origin}-{destination}-101",
            "airline": a1,
            "origin": origin,
            "destination": destination,
            "departure_time": f"{date}T08:00:00",
            "arrival_time": f"{date}T16:30:00",
            "duration": "8h 30m",
            "price_native": round(base_price, 2),
            "currency_native": native_currency,
            "stops": 0,
            "cabin_class": "economy",
            "baggage": "1x23kg, 1x7kg",
            "is_refundable": True,
            "carbon_emission_kg": 210,
            "logo_url": get_logo(a1)
        },
        {
            "flight_number": f"GF-{origin}-{destination}-202" if a2 == "Gulf Air" else f"VS-{origin}-{destination}-202" if a2 == "Virgin Atlantic" else f"SQ-{origin}-{destination}-202",
            "airline": a2,
            "origin": origin,
            "destination": destination,
            "departure_time": f"{date}T13:15:00",
            "arrival_time": f"{date}T22:45:00",
            "duration": "9h 30m",
            "price_native": round(base_price * 0.82, 2),
            "currency_native": native_currency,
            "stops": 1,
            "cabin_class": "economy",
            "baggage": "1x7kg",
            "is_refundable": False,
            "carbon_emission_kg": 340,
            "logo_url": get_logo(a2)
        },
        {
            "flight_number": f"QR-{origin}-{destination}-303" if a3 == "Qatar Airways" else f"GF-{origin}-{destination}-303" if a3 == "Gulf Air" else f"BA-{origin}-{destination}-303",
            "airline": a3,
            "origin": origin,
            "destination": destination,
            "departure_time": f"{date}T22:00:00",
            "arrival_time": f"{date}T06:15:00 (+1)",
            "duration": "8h 15m",
            "price_native": round(base_price * 1.28, 2),
            "currency_native": native_currency,
            "stops": 0,
            "cabin_class": "economy",
            "baggage": "2x23kg, 1x7kg",
            "is_refundable": True,
            "carbon_emission_kg": 255,
            "logo_url": get_logo(a3)
        }
    ]
    
    # Convert native prices to selected home currency
    for f in flights:
        f["price_home"] = convert_currency(f["price_native"], f["currency_native"], preferred_home_currency)
        
    return flights

def mock_hotel_lookup(location: str, check_in: str, check_out: str, preferred_home_currency: str, membership_tier: str) -> List[Dict[str, Any]]:
    """
    Looks up booking rates for hotels in native destination currency, 
    applies custom rewards discounts, and returns both currencies.
    Uses real-world luxury hotel chains (Burj Al Arab, Taj Mahal Palace, Savoy, Hilton, Ritz, Marina Bay Sands, etc.).
    """
    time.sleep(15) # Rate limit throttling for Gemini Free Tier
    location = location.upper().strip()
    
    native_currency = "USD"
    if location in ["LHR", "LON"]:
        native_currency = "GBP"
    elif location in ["DXB", "DUB"]:
        native_currency = "AED"
    elif location in ["CDG", "PAR", "AMS"]:
        native_currency = "EUR"
    elif location in ["SIN"]:
        native_currency = "SGD"
    elif location in ["BOM", "DEL"]:
        native_currency = "INR"

    base_rates = {
        "LON": 180.0,
        "DXB": 650.0,
        "PAR": 220.0,
        "SIN": 280.0,
        "BOM": 9500.0,
        "NYC": 240.0,
        "SFO": 260.0
    }
    
    base_price = base_rates.get(location, 190.0)
    
    # Retrieve discount rate from membership status
    loyalty = calculate_loyalty_rewards(100.0, membership_tier)
    discount_rate = loyalty["discount_applied"]
    
    # Real world hotel names mapping based on city
    if location in ["LON", "LHR"]:
        h1, h2, h3 = "The Savoy London", "Hilton London Metropole", "Premier Inn London City"
    elif location in ["DXB", "DUB"]:
        h1, h2, h3 = "Burj Al Arab Jumeirah Dubai", "Atlantis The Palm Dubai", "ibis Styles Dubai Jumeirah"
    elif location in ["SIN"]:
        h1, h2, h3 = "Marina Bay Sands Singapore", "Raffles Hotel Singapore", "Hotel Boss Singapore"
    elif location in ["BOM", "DEL"]:
        h1, h2, h3 = "The Taj Mahal Palace Mumbai", "Trident Nariman Point Mumbai", "Ginger Hotel Mumbai"
    elif location in ["PAR", "CDG"]:
        h1, h2, h3 = "The Ritz Paris", "Pullman Paris Tour Eiffel", "Hotel Campanile Paris"
    else:
        h1, h2, h3 = "The Ritz-Carlton", "Hilton Hotel", "Comfort Suites"
    
    hotels = [
        {
            "hotel_name": h1,
            "location": location,
            "price_native_base": round(base_price, 2),
            "currency_native": native_currency,
            "rating": 4.2,
            "amenities": ["Wi-Fi", "Fitness Center"],
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
            "is_refundable": False,
            "is_ai_recommended": False
        },
        {
            "hotel_name": h2,
            "location": location,
            "price_native_base": round(base_price * 1.45, 2),
            "currency_native": native_currency,
            "rating": 4.8,
            "amenities": ["Wi-Fi", "Pool", "Spa", "Lounge"],
            "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80",
            "is_refundable": True,
            "is_ai_recommended": True
        },
        {
            "hotel_name": h3,
            "location": location,
            "price_native_base": round(base_price * 0.72, 2),
            "currency_native": native_currency,
            "rating": 3.6,
            "amenities": ["Wi-Fi"],
            "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80",
            "is_refundable": True,
            "is_ai_recommended": False
        }
    ]
    
    res = []
    for h in hotels:
        # Apply rewards discount
        price_native = round(h["price_native_base"] * (1.0 - discount_rate), 2)
        price_home = convert_currency(price_native, h["currency_native"], preferred_home_currency)
        
        # Add free breakfast if Gold or Diamond tier
        amenities = list(h["amenities"])
        if membership_tier in ["flyGold", "flyDiamond"]:
            if "Free Breakfast" not in amenities:
                amenities.append("Free Breakfast")
                
        res.append({
            "hotel_name": h["hotel_name"],
            "location": h["location"],
            "price_native": price_native,
            "currency_native": h["currency_native"],
            "price_home": price_home,
            "rating": h["rating"],
            "amenities": amenities,
            "check_in": check_in,
            "check_out": check_out,
            "image_url": h["image_url"],
            "is_refundable": h["is_refundable"],
            "is_ai_recommended": h["is_ai_recommended"]
        })
        
    return res

def check_calendar_availability(date: str, duration_days: int) -> Dict[str, Any]:
    """
    Checks user calendar for overlaps.
    Flags overlaps and displays home timezone transitions.
    """
    time.sleep(15) # Rate limit throttling for Gemini Free Tier
    try:
        travel_start = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        try:
            travel_start = datetime.datetime.fromisoformat(date.split("T")[0]).date()
        except Exception:
            travel_start = datetime.date(2026, 7, 1)  # Fallback
            
    travel_end = travel_start + datetime.timedelta(days=duration_days)
    
    # Preset Corporate planning calendar overlap between 2026-07-10 and 2026-07-12
    conflict_start = datetime.date(2026, 7, 10)
    conflict_end = datetime.date(2026, 7, 12)
    
    overlaps = not (travel_end < conflict_start or travel_start > conflict_end)
    
    conflicts = []
    if overlaps:
        conflicts.append(f"Calendar Overlap: User has 'Q3 Corporate Strategy Summit' scheduled from {conflict_start} to {conflict_end}.")
        
    return {
        "status": "conflict" if conflicts else "available",
        "conflicts": conflicts,
        "timezone_info": "Origin Timezone: UTC+4. Destination Timezone: UTC+1. Conversion: -3 hours time difference shift."
    }

def evaluate_price_trends(current_fare: float, seasonal_baseline: float) -> Dict[str, Any]:
    """
    Evaluates price states relative to seasonal baseline.
    Uses Gemini Structured Outputs or falls back to rules if the API key is not configured.
    """
    # Deterministic rule-based evaluation (standard fallback)
    ratio = current_fare / seasonal_baseline
    if ratio < 0.88:
        price_status = "Low"
        buying_verdict = "BUY NOW"
        justification = f"Current fare is {round((1-ratio)*100, 1)}% below the seasonal baseline. Historically, fares are unlikely to drop further."
    elif ratio > 1.12:
        price_status = "High"
        buying_verdict = "WAIT - LIKELY TO DROP"
        justification = f"Current fare is {round((ratio-1)*100, 1)}% above the seasonal baseline. Pricing is inflated; recommend waiting for price correction."
    else:
        price_status = "Average"
        buying_verdict = "BUY NOW"
        justification = f"Fare is within seasonal baseline variance. Buying now secures the seat and schedule certainty."

    # Gemini integration using Structured Outputs
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from pydantic import BaseModel
            
            client = genai.Client(api_key=api_key)
            prompt = (
                f"You are a Kaggle Grandmaster flight price analysis engine. The current fare is {current_fare} "
                f"and the historical seasonal baseline is {seasonal_baseline}. "
                f"Evaluate if this price is Low, Average, or High. Decide whether the user should BUY NOW or "
                f"WAIT - LIKELY TO DROP. Provide a detailed professional justification."
            )
            
            class PriceTrendResponse(BaseModel):
                price_status: str
                buying_verdict: str
                justification: str
                
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PriceTrendResponse,
                ),
            )
            import json
            data = json.loads(response.text)
            
            # Verify schema matches
            if all(k in data for k in ["price_status", "buying_verdict", "justification"]):
                return data
        except Exception as e:
            logger.warning(f"Error calling Gemini in evaluate_price_trends: {e}. Utilizing rule-based fallback.")
            
    return {
        "price_status": price_status,
        "buying_verdict": buying_verdict,
        "justification": justification
    }

def lookup_support_faq(query: str) -> str:
    """
    Performs FAQ RAG lookup.
    """
    query_lower = query.lower().strip()
    faq_db = {
        "cancel": "FlySync bookings are fully refundable within 24 hours of purchase. Afterward, standard cancellation fees apply. flyDiamond members receive zero cancellation fees up to 2 hours before flight time.",
        "baggage": "Standard tickets include 1 carry-on bag (up to 7kg) and 1 checked suitcase (up to 23kg). flyGold and flyDiamond members get an extra 23kg bag allowance at no extra charge.",
        "upgrade": "Cabin upgrades to Business class are available via FlyPoints. flySilver/flyGold/flyDiamond members receive upgrade priority. Domestics require 15k points, internationals 50k points.",
        "change": "Flight changes can be processed through the app dashboard. Change fees are waived entirely for flyGold and flyDiamond members.",
        "refund": "Refund approvals are processed back to the original method of payment within 5 to 7 business days."
    }
    
    for key, response in faq_db.items():
        if key in query_lower:
            return response
            
    return "FlySync customer support FAQ: Standard booking rules apply. For dynamic cases, please open a support ticket. flyDiamond membership prioritizes customer support routing."
