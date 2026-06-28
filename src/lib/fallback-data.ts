export const fallbackAgentState = {
  user_preferences: {
    home_currency: "USD",
    preferred_seating: "window",
    membership_tier: "flyGold",
    max_budget: 3500.0,
    preferred_airline: null,
    seating_class: "economy",
    points_balance: 15000
  },
  flight_options: [
    {
      flight_number: "EK-007",
      airline: "Emirates",
      origin: "DXB",
      destination: "LHR",
      departure_time: "08:00 AM",
      arrival_time: "12:30 PM",
      duration: "7h 30m",
      price_native: 2500,
      currency_native: "AED",
      price_home: 680,
      stops: 0,
      cabin_class: "economy",
      baggage: "1x23kg, 1x7kg",
      is_refundable: true,
      carbon_emission_kg: 210,
      logo_url: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=100&auto=format&fit=crop",
      confirmation_number: null
    }
  ],
  selected_flight: {
      flight_number: "EK-007",
      airline: "Emirates",
      origin: "DXB",
      destination: "LHR",
      departure_time: "08:00 AM",
      arrival_time: "12:30 PM",
      duration: "7h 30m",
      price_native: 2500,
      currency_native: "AED",
      price_home: 680,
      stops: 0,
      cabin_class: "economy",
      baggage: "1x23kg, 1x7kg",
      is_refundable: true,
      carbon_emission_kg: 210,
      logo_url: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=100&auto=format&fit=crop",
      confirmation_number: "EK-X7890B"
  },
  hotel_options: [
    {
      hotel_name: "The Savoy",
      location: "Strand, London",
      price_native: 450,
      currency_native: "GBP",
      price_home: 570,
      rating: 4.9,
      amenities: ["Free WiFi", "Spa", "Pool"],
      check_in: "2026-07-05",
      check_out: "2026-07-10",
      room_type: "deluxe",
      image_url: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop",
      is_refundable: false,
      is_ai_recommended: true,
      map_coordinates: "51.5101, -0.1202",
      confirmation_number: null
    }
  ],
  selected_hotel: {
      hotel_name: "The Savoy",
      location: "Strand, London",
      price_native: 450,
      currency_native: "GBP",
      price_home: 570,
      rating: 4.9,
      amenities: ["Free WiFi", "Spa", "Pool"],
      check_in: "2026-07-05",
      check_out: "2026-07-10",
      room_type: "deluxe",
      image_url: "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&auto=format&fit=crop",
      is_refundable: false,
      is_ai_recommended: true,
      map_coordinates: "51.5101, -0.1202",
      confirmation_number: "SAV-12345"
  },
  calendar_conflicts: [],
  price_analysis: {
    current_fare: 680,
    seasonal_baseline: 750,
    price_status: "Low",
    buying_verdict: "BUY NOW",
    justification: "Prices are 10% below the seasonal average."
  },
  loyalty_details: {
    tier: "flyGold",
    points_accrued: 2500,
    discount_applied: 50.0,
    perks_unlocked: ["Lounge Access", "Priority Boarding"]
  },
  support_tickets: [],
  execution_trace: ["Scout found optimal flights.", "Sync confirmed clear schedule.", "Sentinel applied 50 USD loyalty discount."],
  total_cost_home: 1200.0,
  status_message: "Completed with fallback data due to timeout."
};
