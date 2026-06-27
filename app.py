import streamlit as st
import datetime
import os
import json
import random
from schema import AgentState, UserPreferences, FlightOption, HotelOption, PriceAnalysis, LoyaltyDetails, SupportTicket
from agent_graph import FlySyncGraphOrchestrator
import mcp_tools

# Configure Streamlit page settings
st.set_page_config(
    page_title="FlySync Hub - Flights, Hotels & Loyalty",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Initialize Authentication and State variables
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

if "membership_tier" not in st.session_state:
    st.session_state.membership_tier = "flyBronze"

if "points_balance" not in st.session_state:
    st.session_state.points_balance = 0.0

if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

if "selected_flight" not in st.session_state:
    st.session_state.selected_flight = None

if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = None

if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

if "booked_state" not in st.session_state:
    st.session_state.booked_state = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to FlySync Hub! Please sign in or register to search package deals, review deals, and check your loyalty tier points progress."}
    ]

# Dynamically calculate and check tier progression based on points balance
def check_tier_upgrade():
    pts = st.session_state.points_balance
    if pts >= 30000:
        st.session_state.membership_tier = "flyDiamond"
    elif pts >= 15000:
        st.session_state.membership_tier = "flyGold"
    elif pts >= 5000:
        st.session_state.membership_tier = "flySilver"
    else:
        st.session_state.membership_tier = "flyBronze"

check_tier_upgrade()

# 2. Inject Custom Premium CSS matching Skyscanner/Booking.com
def inject_ota_css():
    theme = st.session_state.theme
    
    if theme == "dark":
        bg = "#0E1117"
        surface = "#1F2937"
        border = "#374151"
        text = "#F3F4F6"
        subtext = "#9CA3AF"
        primary = "#3B82F6" # Royal Blue
        success = "#10B981" # Emerald Green
        warning = "#F59E0B" # Amber Alert
        badge_bg = "#111827"
        
        css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
        
        body, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {bg} !important;
            color: {text} !important;
            font-family: 'Outfit', sans-serif !important;
        }}
        
        .ota-header {{
            background-color: #111827;
            border-bottom: 1px solid {border};
            padding: 15px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .ota-brand {{
            font-size: 1.8rem;
            font-weight: 800;
            color: {primary};
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .ota-brand span {{
            color: {success};
        }}
        
        .search-widget {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .ota-card {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .ota-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.25);
            border-color: {primary};
        }}
        
        .original-price {{
            text-decoration: line-through;
            color: {subtext};
            font-size: 0.95rem;
            margin-right: 8px;
        }}
        .discount-price {{
            color: {success};
            font-weight: 700;
            font-size: 1.3rem;
        }}
        
        .rating-badge {{
            background-color: {primary};
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 0.85rem;
        }}
        
        .amenity-tag {{
            background-color: {badge_bg};
            border: 1px solid {border};
            color: {text};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-right: 5px;
            display: inline-block;
        }}
        
        .tier-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            display: inline-block;
        }}
        .tier-flySilver {{ background-color: #64748B; color: white; }}
        .tier-flyGold {{ background-color: #D97706; color: white; }}
        .tier-flyDiamond {{ background-color: #1D4ED8; color: white; box-shadow: 0 0 10px rgba(37,99,235,0.6); }}
        .tier-flyBronze {{ background-color: #B45309; color: white; }}
        
        .text-neon-green {{ color: {success} !important; font-weight: bold; }}
        .text-neon-amber {{ color: {warning} !important; font-weight: bold; }}
        .text-neon-blue {{ color: {primary} !important; font-weight: bold; }}
        
        .stButton>button {{
            background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 8px 24px !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
        }}
        .stButton>button:hover {{
            box-shadow: 0 0 15px rgba(88,166,255,0.6) !important;
            transform: translateY(-1px);
        }}
        
        .deal-voucher {{
            border: 2px dashed {primary};
            background-color: {surface};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            position: relative;
        }}
        .deal-badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: {success};
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }}
        
        .card-container {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        
        h1, h2, h3 {{
            color: #F0F6FC !important;
            font-weight: 800 !important;
        }}
        </style>
        """
    else:
        # Crisp Light Mode
        bg = "#F8FAFC"
        surface = "#FFFFFF"
        border = "#E2E8F0"
        text = "#0F172A"
        subtext = "#64748B"
        primary = "#1D4ED8" # Royal Blue
        success = "#10B981" # Emerald Green
        warning = "#D97706" # Amber
        badge_bg = "#F1F5F9"
        
        css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
        
        body, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {bg} !important;
            color: {text} !important;
            font-family: 'Outfit', sans-serif !important;
        }}
        
        .ota-header {{
            background-color: #FFFFFF;
            border-bottom: 1px solid {border};
            padding: 15px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }}
        .ota-brand {{
            font-size: 1.8rem;
            font-weight: 800;
            color: {primary};
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .ota-brand span {{
            color: {success};
        }}
        
        .search-widget {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.03);
        }}
        
        .ota-card {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }}
        .ota-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            border-color: {primary};
        }}
        
        .original-price {{
            text-decoration: line-through;
            color: {subtext};
            font-size: 0.95rem;
            margin-right: 8px;
        }}
        .discount-price {{
            color: {success};
            font-weight: 700;
            font-size: 1.3rem;
        }}
        
        .rating-badge {{
            background-color: {primary};
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 0.85rem;
        }}
        
        .amenity-tag {{
            background-color: {badge_bg};
            border: 1px solid {border};
            color: {text};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-right: 5px;
            display: inline-block;
        }}
        
        .tier-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            display: inline-block;
        }}
        .tier-flySilver {{ background-color: #64748B; color: white; }}
        .tier-flyGold {{ background-color: #D97706; color: white; }}
        .tier-flyDiamond {{ background-color: #1D4ED8; color: white; }}
        .tier-flyBronze {{ background-color: #B45309; color: white; }}
        
        .text-neon-green {{ color: {success} !important; font-weight: bold; }}
        .text-neon-amber {{ color: {warning} !important; font-weight: bold; }}
        .text-neon-blue {{ color: {primary} !important; font-weight: bold; }}
        
        .deal-voucher {{
            border: 2px dashed {primary};
            background-color: {surface};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            position: relative;
        }}
        .deal-badge {{
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: {success};
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }}
        
        .card-container {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }}
        
        h1, h2, h3 {{
            color: #0F172A !important;
            font-weight: 800 !important;
        }}
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# Render CSS styles
inject_ota_css()

# TOP LOGO HEADER
st.markdown(
    """
    <div style="background-color:#111827; padding: 15px 40px; border-bottom:1px solid #374151; display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size: 1.8rem; font-weight: 800; color:#3B82F6;">✈️ FlySync Hub</span>
        <span style="font-size: 0.95rem; color:#9CA3AF;">Elite Travel Assistant</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br/>", unsafe_allow_html=True)

# Create layout grid: Left for main interface, Right for Profile / Sign-in
main_col, profile_col = st.columns([3, 1])

# ==================== PROFILE & AUTHENTICATION COLUMN ====================
with profile_col:
    st.markdown("### 👤 Account Panel")
    
    if not st.session_state.authenticated:
        # Sign-in and Register Panel (Starts as unauthenticated guest)
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0;'>Sign In to FlySync</h4>", unsafe_allow_html=True)
            
            user_input = st.text_input("Username", value="munir_traveler")
            pwd_input = st.text_input("Password", type="password", value="password123")
            
            c_login, c_reg = st.columns(2)
            with c_login:
                if st.button("Sign In", use_container_width=True):
                    if user_input:
                        st.session_state.authenticated = True
                        st.session_state.username = user_input
                        st.session_state.membership_tier = "flyBronze"
                        st.session_state.points_balance = 0.0
                        st.success(f"Signed in as {user_input}")
                        st.rerun()
            with c_reg:
                if st.button("Register", use_container_width=True):
                    if user_input:
                        st.session_state.authenticated = True
                        st.session_state.username = user_input
                        st.session_state.membership_tier = "flyBronze"
                        st.session_state.points_balance = 0.0
                        st.success("Registered successfully!")
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Authenticated User Profile with read-only progress meters
        with st.container():
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown(f"<h4 style='margin-top:0;'>Welcome, {st.session_state.username}!</h4>", unsafe_allow_html=True)
            
            badge_map = {
                "flyBronze": "tier-flyBronze",
                "flySilver": "tier-flySilver",
                "flyGold": "tier-flyGold",
                "flyDiamond": "tier-flyDiamond"
            }
            tier_class = badge_map.get(st.session_state.membership_tier, "tier-flyBronze")
            
            st.markdown(f"Current Status: <span class='tier-badge {tier_class}'>{st.session_state.membership_tier}</span>", unsafe_allow_html=True)
            st.markdown(f"Balance: **{st.session_state.points_balance}** FlyPoints")
            
            # Progress Meters
            st.markdown("---")
            st.markdown("##### 📈 Tier Progression Progress")
            
            # flySilver Progress (5,000 pts)
            silver_progress = min(st.session_state.points_balance / 5000.0, 1.0)
            st.markdown(f"**flySilver Progress** ({int(silver_progress*100)}%)")
            st.progress(silver_progress)
            st.markdown(f"<span style='font-size:0.8rem; color:#888;'>{st.session_state.points_balance:.0f} / 5,000 points</span>", unsafe_allow_html=True)
            
            # flyGold Progress (15,000 pts)
            gold_progress = min(st.session_state.points_balance / 15000.0, 1.0)
            st.markdown(f"**flyGold Progress** ({int(gold_progress*100)}%)")
            st.progress(gold_progress)
            st.markdown(f"<span style='font-size:0.8rem; color:#888;'>{st.session_state.points_balance:.0f} / 15,000 points</span>", unsafe_allow_html=True)
            
            # flyDiamond Progress (30,000 pts)
            diamond_progress = min(st.session_state.points_balance / 30000.0, 1.0)
            st.markdown(f"**flyDiamond Progress** ({int(diamond_progress*100)}%)")
            st.progress(diamond_progress)
            st.markdown(f"<span style='font-size:0.8rem; color:#888;'>{st.session_state.points_balance:.0f} / 30,000 points</span>", unsafe_allow_html=True)
            
            if st.button("Sign Out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.search_performed = False
                st.session_state.agent_state = None
                st.session_state.selected_flight = None
                st.session_state.selected_hotel = None
                st.session_state.booked_state = None
                st.rerun()
                
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN WORKFLOW COLUMN ====================
with main_col:
    if not st.session_state.authenticated:
        # BLOCK OR LIMIT ACCESS IF UNAUTHENTICATED
        st.markdown(
            """
            <div class="card-container" style="text-align: center; padding: 50px;">
                <h3 style="margin: 0 0 10px 0; color:#3B82F6;">🔑 Access Restricted</h3>
                <p style="font-size:1.05rem; color:#9CA3AF; margin-bottom: 20px;">
                    Sign in or register an account using the Account Panel to unlock Skyscanner Flight searches, Booking.com hotel reservations, Deals, and loyalty point multipliers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Access granted! Show all tabs.
        tab_search, tab_deals_list, tab_rewards_chart = st.tabs([
            "✈️ Book Packages (Skyscanner Search)", 
            "🔥 Deals & Special Offers", 
            "👑 Loyalty Program Rewards"
        ])
        
        # TAB 1: SEARCH & BOOK
        with tab_search:
            # SEARCH WIDGET (Skyscanner Form style)
            with st.container():
                st.markdown('<div class="search-widget">', unsafe_allow_html=True)
                
                col_type, col_cabin, col_tier_info = st.columns([2, 2, 4])
                with col_type:
                    st.radio("Trip Type", ["Round-trip", "One-way"], horizontal=True, key="search_trip_type", label_visibility="collapsed")
                with col_cabin:
                    cabin_class = st.selectbox("Cabin Class", ["Economy", "Premium Economy", "Business", "First Class"], index=0, key="search_cabin_class", label_visibility="collapsed")
                with col_tier_info:
                    st.markdown(f"👑 **Active Loyalty Benefits**: {st.session_state.membership_tier} level active")

                st.markdown("<br/>", unsafe_allow_html=True)
                col_org, col_dest, col_date, col_dur, col_curr, col_budget = st.columns([2, 2, 2, 1.2, 1.8, 2.5])
                
                with col_org:
                    origin = st.text_input("From (Airport Code)", value="DXB", key="input_origin").upper().strip()
                with col_dest:
                    destination = st.text_input("To (Airport Code)", value="LHR", key="input_destination").upper().strip()
                with col_date:
                    travel_date = st.date_input("Departure Date", value=datetime.date(2026, 7, 5), key="input_date")
                with col_dur:
                    duration = st.number_input("Nights (Duration)", min_value=1, max_value=30, value=3, step=1, key="input_duration")
                with col_curr:
                    home_currency = st.selectbox("Show Prices in", ["USD", "AED", "INR", "GBP", "EUR", "SGD"], index=0, key="input_currency")
                with col_budget:
                    max_budget = st.number_input("Smart Budget Shield Limit", min_value=100.0, value=2500.0, step=100.0, key="input_budget")

                st.markdown("<br/>", unsafe_allow_html=True)
                col_air, col_search = st.columns([7, 3])
                with col_air:
                    preferred_airline = st.text_input("Preferred Airline (optional)", value="Emirates", placeholder="e.g. Gulf Air, British Airways", key="input_airline")
                with col_search:
                    search_clicked = st.button("🔍 Search Package Deals", use_container_width=True)
                    
                st.markdown('</div>', unsafe_allow_html=True)
                
            # SEARCH ACTION SUBMIT
            if search_clicked:
                prefs = UserPreferences(
                    home_currency=home_currency,
                    membership_tier=st.session_state.membership_tier,
                    max_budget=max_budget,
                    preferred_airline=preferred_airline if preferred_airline else None,
                    points_balance=st.session_state.points_balance
                )
                
                state = AgentState(user_preferences=prefs)
                orchestrator = FlySyncGraphOrchestrator()
                
                with st.spinner("Scouting real-world flight databases and hotel inventories..."):
                    final_state = orchestrator.execute_workflow(
                        state=state,
                        origin=origin,
                        destination=destination,
                        travel_date=travel_date.strftime("%Y-%m-%d")
                    )
                    st.session_state.agent_state = final_state
                    st.session_state.search_performed = True
                    st.session_state.selected_flight = None # Reset selections
                    st.session_state.selected_hotel = None
                    st.session_state.booked_state = None
            
            # CONDITIONAL EXECUTION GUARD: Check if search has been performed
            if not st.session_state.get("search_performed", False) or st.session_state.agent_state is None:
                st.markdown(
                    """
                    <div class="card-container" style="text-align: center; padding: 40px; margin-top:20px;">
                        <h4 style="margin:0 0 10px 0; color:#888;">Welcome to Skyscanner Package Scout</h4>
                        <p style="margin: 0; font-size:0.95rem; color:#666;">Enter your travel airports and budget limits above, and click the 'Search Package Deals' button to scout flights and hotels.</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                # Search has been performed, display grids
                state = st.session_state.agent_state
                
                grid_flights_col, grid_hotel_col = st.columns(2)
                
                # Render Flights Grid
                with grid_flights_col:
                    st.markdown("#### ✈️ Flight Scout Results")
                    if state.flight_options:
                        for idx, flight in enumerate(state.flight_options):
                            # Check selection state
                            is_selected = (st.session_state.selected_flight is not None and st.session_state.selected_flight.get("flight_number") == flight.flight_number)
                            border_color = "border: 2px solid #3B82F6;" if is_selected else ""
                            stops_label = "Direct" if flight.stops == 0 else f"{flight.stops} Stop"
                            
                            st.markdown(
                                f"""
                                <div class="ota-card" style="{border_color}">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <strong>{flight.airline}</strong>
                                        <span style="font-size:0.85rem; color:#888;">Flight: {flight.flight_number}</span>
                                    </div>
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin:10px 0;">
                                        <div>
                                            <span style="font-size:1.1rem; font-weight:bold;">{flight.departure_time.split('T')[-1]}</span>
                                        </div>
                                        <div style="text-align:center; flex-grow:1; border-bottom:1px dashed #666; margin:0 15px; padding-bottom:3px;">
                                            <span style="font-size:0.75rem; color:#888;">{flight.duration} ({stops_label})</span>
                                        </div>
                                        <div>
                                            <span style="font-size:1.1rem; font-weight:bold;">{flight.arrival_time.split('T')[-1]}</span>
                                        </div>
                                    </div>
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span style="font-size:0.85rem; color:#888;">GDS: {flight.price_native} {flight.currency_native}</span>
                                        <span class="discount-price">{flight.price_home} {state.user_preferences.home_currency}</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            if st.button(f"Select Flight {flight.flight_number}", key=f"sel_f_{idx}"):
                                # Save dictionary to session state
                                st.session_state.selected_flight = flight.model_dump()
                                st.rerun()
                    else:
                        st.write("No flights found.")
                
                # Render Hotels Grid
                with grid_hotel_col:
                    st.markdown("#### 🏨 Hotel Scout Results")
                    if state.hotel_options:
                        loyalty_info = mcp_tools.calculate_loyalty_rewards(100.0, st.session_state.membership_tier)
                        discount_rate = loyalty_info["discount_applied"]
                        
                        for idx, hotel in enumerate(state.hotel_options):
                            is_selected = (st.session_state.selected_hotel is not None and st.session_state.selected_hotel.get("hotel_name") == hotel.hotel_name)
                            border_color = "border: 2px solid #10B981;" if is_selected else ""
                            
                            original_native = round(hotel.price_native / (1.0 - discount_rate), 2) if discount_rate > 0 else hotel.price_native
                            original_home = mcp_tools.convert_currency(original_native, hotel.currency_native, state.user_preferences.home_currency)
                            
                            amenity_badges = "".join([f'<span class="amenity-tag">{amenity}</span>' for amenity in hotel.amenities])
                            
                            st.markdown(
                                f"""
                                <div class="ota-card" style="{border_color}">
                                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                        <div>
                                            <strong>{hotel.hotel_name}</strong><br/>
                                            <span style="font-size:0.8rem; color:#888;">📍 {hotel.location}</span>
                                        </div>
                                        <span class="rating-badge">{hotel.rating} ★</span>
                                    </div>
                                    <div style="margin:8px 0;">{amenity_badges}</div>
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span style="font-size:0.8rem; color:#888;">{hotel.check_in} to {hotel.check_out}</span>
                                        <div style="text-align:right;">
                                            {f'<span class="original-price">{original_home} {state.user_preferences.home_currency}</span>' if discount_rate > 0 else ""}
                                            <span class="discount-price" style="color:#10B981;">{hotel.price_home} {state.user_preferences.home_currency}</span>
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            if st.button(f"Select Hotel {hotel.hotel_name}", key=f"sel_h_{idx}"):
                                # Save dictionary to session state
                                st.session_state.selected_hotel = hotel.model_dump()
                                st.rerun()
                    else:
                        st.write("No hotels found.")
                        
                # RENDER BOOKING SUMMARY PANEL (If selections exist)
                st.markdown("---")
                st.markdown("### 🛒 Booking Summary Checkout")
                
                sel_f_dict = st.session_state.selected_flight
                sel_h_dict = st.session_state.selected_hotel
                
                if not sel_f_dict or not sel_h_dict:
                    st.info("Please select both a flight and a hotel from the results grid to proceed to checkout.")
                else:
                    # Selections exist, compile models
                    sel_flight = FlightOption(**sel_f_dict)
                    sel_hotel = HotelOption(**sel_h_dict)
                    
                    hotel_total_home = round(sel_hotel.price_home * duration, 2)
                    total_package_home = round(sel_flight.price_home + hotel_total_home, 2)
                    
                    # Update active state selections
                    state.selected_flight = sel_flight
                    state.selected_hotel = sel_hotel
                    state.total_cost_home = total_package_home
                    
                    # Re-run graph calculations
                    orchestrator = FlySyncGraphOrchestrator()
                    orchestrator.run_sync_coordinator_node(state, travel_date.strftime("%Y-%m-%d"), duration)
                    
                    st.markdown("##### 🎫 Booking RAG FAQ Help Desk")
                    support_query = st.text_input("Ask a support question (e.g. cancellation fees, baggage allowance):", key="booking_support_query")
                    
                    orchestrator.run_sentinel_node(state, support_query if support_query else None)
                    
                    # Columns for details
                    col_summ, col_verify = st.columns(2)
                    
                    with col_summ:
                        st.markdown(
                            f"""
                            <div class="card-container">
                                <h5>Flight Summary</h5>
                                <strong>Carrier:</strong> {sel_flight.airline} ({sel_flight.flight_number})<br/>
                                <strong>Route:</strong> {sel_flight.origin} → {sel_flight.destination} on {travel_date}<br/>
                                <strong>Price:</strong> {sel_flight.price_home} {state.user_preferences.home_currency}<br/>
                                <br/>
                                <h5>Hotel Summary</h5>
                                <strong>Accommodation:</strong> {sel_hotel.hotel_name}<br/>
                                <strong>Duration:</strong> {duration} Nights<br/>
                                <strong>Price:</strong> {hotel_total_home} {state.user_preferences.home_currency} ({sel_hotel.price_home}/night)<br/>
                                <hr style="margin:10px 0; border-color:#374151;"/>
                                <div style="display:flex; justify-content:space-between; font-size:1.15rem;">
                                    <strong>Total:</strong>
                                    <strong class="text-neon-blue">{total_package_home} {state.user_preferences.home_currency}</strong>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    with col_verify:
                        loyalty = state.loyalty_details
                        price_analysis = state.price_analysis
                        
                        budget_ok = (total_package_home <= state.user_preferences.max_budget)
                        shield_class = "text-neon-green" if budget_ok else "text-neon-amber"
                        shield_msg = "PASSED: Within budget limit." if budget_ok else "BREACHED: Exceeds budget shield limit!"
                        
                        trend_class = "text-neon-green" if price_analysis.price_status == "Low" else ("text-neon-blue" if price_analysis.price_status == "Average" else "text-neon-amber")
                        
                        st.markdown(
                            f"""
                            <div class="card-container">
                                <h5>Sentinel Verification</h5>
                                <strong>Smart Budget Shield:</strong> <span class="{shield_class}">{shield_msg}</span><br/>
                                <strong>Pricing Trend:</strong> <span class="{trend_class}">{price_analysis.price_status}</span><br/>
                                <strong>Forecast Verdict:</strong> <span class="text-neon-blue">{price_analysis.buying_verdict}</span><br/>
                                <span style="font-size:0.85rem; color:#888;">{price_analysis.justification}</span><br/>
                                <hr style="margin:10px 0; border-color:#374151;"/>
                                <strong>FlyPoints Accruing:</strong> <span class="text-neon-blue">{loyalty.points_accrued if loyalty else 0.0} Points</span><br/>
                                <span style="font-size:0.85rem; color:#888;">Perks Unlocked: {', '.join(loyalty.perks_unlocked) if loyalty else ""}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if state.calendar_conflicts:
                            for conflict in state.calendar_conflicts:
                                st.warning(f"🚨 {conflict}")
                                
                    # Confirm Booking Button (Adds points to profile and updates tier)
                    if st.button("⚡ Confirm Package Booking", key="btn_confirm_booking", use_container_width=True):
                        pnr_code = f"{sel_flight.airline[:2].upper()}-{random.randint(10000, 99999)}"
                        res_code = f"RES-{random.randint(10000, 99999)}"
                        
                        st.session_state.booked_state = {
                            "pnr": pnr_code,
                            "h_pnr": res_code,
                            "flight": sel_flight.flight_number,
                            "airline": sel_flight.airline,
                            "hotel": sel_hotel.hotel_name,
                            "total": total_package_home,
                            "currency": state.user_preferences.home_currency
                        }
                        
                        # Add accrued points to user session state
                        pts_earned = loyalty.points_accrued if loyalty else 0.0
                        st.session_state.points_balance += pts_earned
                        check_tier_upgrade()
                        
                        state.execution_trace.append(f"[Sentinel Node] confirmed booking: {sel_flight.airline} PNR {pnr_code}, Hotel Reservation {res_code}. Added {pts_earned} points to profile.")
                        st.success(f"🎉 Booking Confirmed! Flight PNR: {pnr_code} | Hotel Res: {res_code}. Points updated!")
                        st.rerun()
                        
                    # Display booking confirmation box
                    if st.session_state.booked_state:
                        booking = st.session_state.booked_state
                        st.markdown(
                            f"""
                            <div class="card-container" style="border: 2px solid #10B981; background-color: rgba(16,185,129,0.08);">
                                <h4 style="margin:0 0 10px 0; color:#10B981;">🎟️ Active Booking Itinerary</h4>
                                <strong>Airline:</strong> {booking['airline']}<br/>
                                <strong>Flight PNR:</strong> {booking['pnr']}<br/>
                                <strong>Hotel:</strong> {booking['hotel']} (Res ID: {booking['h_pnr']})<br/>
                                <strong>Total Charged:</strong> <span class="text-neon-green">{booking['total']} {booking['currency']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    # Support faq responses
                    if state.support_tickets:
                        st.markdown("##### 🎫 Active Support Tickets")
                        for ticket in state.support_tickets:
                            st.markdown(
                                f"""
                                <div class="card-container" style="border-left: 3px solid #3B82F6; padding:15px; margin-bottom:10px;">
                                    <strong>Ticket: {ticket.ticket_id} ({ticket.status.upper()})</strong><br/>
                                    <span style="font-size:0.9rem;">Query: {ticket.user_query}</span><br/>
                                    <span style="font-size:0.9rem; color:#888;">Answer: {ticket.agent_response}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # Collapsible traces
                    st.markdown("#### 🔍 Live Trace Paths (Observability)")
                    with st.expander("Show Executed Graph Node Logs", expanded=False):
                        st.code("\n".join(state.execution_trace), language="log")

        # TAB 2: DEALS & OFFERS
        with tab_deals_list:
            st.markdown("### 🔥 Curated Airline & Hotel Offers")
            st.write("Save instantly on your bookings using active promotions from real-world travel operators.")
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.markdown(
                    """
                    <div class="deal-voucher">
                        <div class="deal-badge">ACTIVE</div>
                        <h4 style="color:#E21A22; margin:0 0 5px 0;">Emirates Dubai Global Sale</h4>
                        <p style="font-size:0.9rem; margin-bottom:10px;">Save 15% on direct flights out of Dubai (DXB) to London LHR, Paris CDG, or Singapore SIN.</p>
                        <strong>Voucher Code:</strong> <span class="text-neon-blue">FLYEMIRATES15</span><br/>
                        <span style="font-size:0.8rem; color:#888;">*Minimum spend $1000 USD. Valid on Business and Economy cabins.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    """
                    <div class="deal-voucher">
                        <div class="deal-badge">ACTIVE</div>
                        <h4 style="color:#D97706; margin:0 0 5px 0;">Gulf Air Companion Discount</h4>
                        <p style="font-size:0.9rem; margin-bottom:10px;">Book one passenger and get the second passenger ticket at 50% discount on selected routes.</p>
                        <strong>Voucher Code:</strong> <span class="text-neon-blue">GFCOMPANION50</span><br/>
                        <span style="font-size:0.8rem; color:#888;">*Applies to flights connecting via Bahrain Hub (BAH).</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_d2:
                st.markdown(
                    """
                    <div class="deal-voucher">
                        <div class="deal-badge">ACTIVE</div>
                        <h4 style="color:#00247D; margin:0 0 5px 0;">British Airways LHR Stopover Offer</h4>
                        <p style="font-size:0.9rem; margin-bottom:10px;">Earn double Avios/FlyPoints and receive a complimentary lounge pass for departures from London Heathrow (LHR).</p>
                        <strong>Voucher Code:</strong> <span class="text-neon-blue">BALHROFFER</span><br/>
                        <span style="font-size:0.8rem; color:#888;">*Applies to flySilver, flyGold and flyDiamond tier status holders.</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    """
                    <div class="deal-voucher">
                        <div class="deal-badge">ACTIVE</div>
                        <h4 style="color:#10B981; margin:0 0 5px 0;">Booking.com Partner Hotel Discounts</h4>
                        <p style="font-size:0.9rem; margin-bottom:10px;">Get up to 20% off on 5-Star accommodations, including Burj Al Arab, Marina Bay Sands and The Savoy.</p>
                        <strong>Discount:</strong> <span class="text-neon-green">Automatic Member Discount Applied</span><br/>
                        <span style="font-size:0.8rem; color:#888;">*Linked directly to your membership level (10% Silver, 15% Gold, 20% Diamond).</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # TAB 3: LOYALTY PROGRAM REWARDS
        with tab_rewards_chart:
            st.markdown("### 👑 FlySync Loyalty Program Benefits")
            st.write("Earn FlyPoints on every booking and unlock elite travel perks.")
            
            col_l1, col_l2, col_l3, col_l4 = st.columns(4)
            
            with col_l1:
                st.markdown(
                    """
                    <div class="card-container" style="border-top:4px solid #B45309;">
                        <h4 style="color:#B45309; text-align:center;">flyBronze</h4>
                        <p style="text-align:center; font-size:0.9rem; color:#888;">1.0x Point Multiplier</p>
                        <hr style="margin:10px 0; border-color:#374151;"/>
                        <ul>
                            <li style="font-size:0.85rem;">10 base points per $1 USD spent</li>
                            <li style="font-size:0.85rem;">Standard baggage allowance</li>
                            <li style="font-size:0.85rem;">Standard support queue</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_l2:
                st.markdown(
                    """
                    <div class="card-container" style="border-top:4px solid #64748B;">
                        <h4 style="color:#64748B; text-align:center;">flySilver</h4>
                        <p style="text-align:center; font-size:0.9rem; color:#888;">1.2x Point Multiplier</p>
                        <hr style="margin:10px 0; border-color:#374151;"/>
                        <ul>
                            <li style="font-size:0.85rem;">12 points per $1 USD spent</li>
                            <li style="font-size:0.85rem;"><strong>10% Discount on Hotels</strong></li>
                            <li style="font-size:0.85rem;">Priority airport check-in</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_l3:
                st.markdown(
                    """
                    <div class="card-container" style="border-top:4px solid #D97706;">
                        <h4 style="color:#D97706; text-align:center;">flyGold</h4>
                        <p style="text-align:center; font-size:0.9rem; color:#888;">1.5x Point Multiplier</p>
                        <hr style="margin:10px 0; border-color:#374151;"/>
                        <ul>
                            <li style="font-size:0.85rem;">15 points per $1 USD spent</li>
                            <li style="font-size:0.85rem;"><strong>15% Discount on Hotels</strong></li>
                            <li style="font-size:0.85rem;">Airport Lounge Access</li>
                            <li style="font-size:0.85rem;"><strong>Free breakfast at hotels</strong></li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_l4:
                st.markdown(
                    """
                    <div class="card-container" style="border-top:4px solid #1D4ED8; box-shadow: 0 0 10px rgba(29,78,216,0.35);">
                        <h4 style="color:#3B82F6; text-align:center;">flyDiamond</h4>
                        <p style="text-align:center; font-size:0.9rem; color:#888;">2.0x Point Multiplier</p>
                        <hr style="margin:10px 0; border-color:#374151;"/>
                        <ul>
                            <li style="font-size:0.85rem;">20 points per $1 USD spent</li>
                            <li style="font-size:0.85rem;"><strong>20% Discount on Hotels</strong></li>
                            <li style="font-size:0.85rem;">VIP Lounge Access</li>
                            <li style="font-size:0.85rem;">Free breakfast + priority room upgrades</li>
                            <li style="font-size:0.85rem;"><strong>Priority Support Routing</strong></li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Interactive points estimation tool
            st.markdown("#### ⚡ Real-Time Loyalty Point Estimator")
            est_price = st.number_input("Package Cost ($ USD equivalent)", min_value=0.0, value=1200.0, step=100.0)
            est_tier = st.selectbox("Calculator Tier Status", ["flyBronze", "flySilver", "flyGold", "flyDiamond"], index=3)
            
            est_multiplier = {"flyBronze": 1.0, "flySilver": 1.2, "flyGold": 1.5, "flyDiamond": 2.0}[est_tier]
            est_points = round(est_price * 10.0 * est_multiplier, 2)
            hotel_discount_pct = {"flyBronze": 0, "flySilver": 10, "flyGold": 15, "flyDiamond": 20}[est_tier]
            
            st.success(f"👑 Under **{est_tier}** status, a **${est_price} USD** purchase will earn you **{est_points} FlyPoints** and save you **{hotel_discount_pct}%** on hotel stays!")
