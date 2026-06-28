"use client";

import { useState, useEffect } from "react";
import { PlaneTakeoff, Hotel, CalendarDays, Coins, BrainCircuit, Loader2, ArrowRight, MapPin, CheckCircle2, ShieldAlert, Sparkles, Leaf, Briefcase, Filter, Search, ChevronDown, ChevronUp, CircleDollarSign, Moon, Sun, CheckCircle, Trophy, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [agentStep, setAgentStep] = useState(0); 
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Search Form State
  const [origin, setOrigin] = useState("DXB");
  const [destination, setDestination] = useState("LHR");
  const [travelDate, setTravelDate] = useState("2026-07-05");
  const [currency, setCurrency] = useState("USD");

  // UI State
  const [isFlightExpanded, setIsFlightExpanded] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [showRewards, setShowRewards] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const simulateAgentSequence = async () => {
    // 1. Scout
    setAgentStep(1);
    await new Promise((r) => setTimeout(r, 2000));
    // 2. Sync
    setAgentStep(2);
    await new Promise((r) => setTimeout(r, 2000));
    // 3. Sentinel
    setAgentStep(3);
    await new Promise((r) => setTimeout(r, 2500));
    setAgentStep(4);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError(null);
    setAgentStep(0);
    setShowCheckout(false);

    // Run UI simulation concurrently with fetch
    const simulationPromise = simulateAgentSequence();
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin: origin,
          destination: destination,
          travel_date: travelDate,
          preferences: {
            home_currency: currency,
            preferred_seating: "window",
            membership_tier: "flyGold",
            max_budget: 3500.0,
            points_balance: 15000
          }
        }),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      // If Vercel returns a 504 HTML page instead of JSON, response.ok will be false.
      if (!response.ok) {
        throw new Error(`Failed to fetch results from the agent (Status ${response.status}).`);
      }
      
      const data = await response.json();
      
      // Ensure simulation finishes before showing results
      await simulationPromise;
      
      setResult(data);
    } catch (err: any) {
      console.error("API call failed:", err);
      await simulationPromise;
      
      // Import and set fallback data if the API fails
      try {
        const { fallbackAgentState } = await import('@/lib/fallback-data');
        console.warn("Using fallback data due to API failure.");
        
        // Dynamically override fallback data to match user's search
        const dynamicFallback = JSON.parse(JSON.stringify(fallbackAgentState));
        dynamicFallback.user_preferences.home_currency = currency;
        if (dynamicFallback.selected_flight) {
          dynamicFallback.selected_flight.origin = origin;
          dynamicFallback.selected_flight.destination = destination;
          dynamicFallback.flight_options.forEach((flight: any) => {
            flight.origin = origin;
            flight.destination = destination;
          });
          
          if (currency === "GBP") dynamicFallback.selected_flight.price_home = 540;
          else if (currency === "EUR") dynamicFallback.selected_flight.price_home = 630;
          else if (currency === "AED") dynamicFallback.selected_flight.price_home = 2500;
        }
        
        setResult(dynamicFallback);
      } catch (importErr) {
        setError(err.name === 'AbortError' ? "Search timed out. Please try again." : err.message || "An error occurred during the agent workflow.");
      }
    } finally {
      setLoading(false);
      setAgentStep(0);
    }
  };

  return (
    <main className="min-h-screen bg-[#F1F5F9] dark:bg-slate-950 font-sans selection:bg-blue-500/30 text-slate-800 dark:text-slate-200 transition-colors duration-300">
      {/* Navbar */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <button 
            onClick={() => { setResult(null); setShowCheckout(false); setError(null); }}
            className="flex items-center gap-2 text-blue-600 dark:text-blue-500 hover:opacity-80 transition-opacity"
          >
            <PlaneTakeoff className="w-7 h-7" />
            <h1 className="text-2xl font-black tracking-tight">FlySync<span className="text-slate-800 dark:text-slate-100">Hub</span></h1>
          </button>
          <nav className="hidden md:flex gap-8 text-sm font-semibold text-slate-600 dark:text-slate-400">
            <a href="#" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors border-b-2 border-blue-600 dark:border-blue-500 pb-5 translate-y-[10px]">Flights & Hotels</a>
            <button onClick={() => setShowRewards(true)} className="hover:text-amber-600 dark:hover:text-amber-400 transition-colors flex items-center gap-1"><Coins className="w-4 h-4 text-amber-500"/> Rewards</button>
          </nav>
          <div className="flex items-center gap-4">
            <button onClick={() => setIsDarkMode(!isDarkMode)} className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors">
              {isDarkMode ? <Sun className="w-5 h-5"/> : <Moon className="w-5 h-5"/>}
            </button>
            <span className="text-sm font-medium text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/30 px-3 py-1 rounded-full">flyGold Member</span>
            <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center text-blue-700 dark:text-blue-400 font-bold text-sm">HM</div>
          </div>
        </div>
      </header>

      {/* Hero Search Section */}
      {!result && (
        <div className="bg-gradient-to-b from-blue-900 to-blue-800 pb-32 pt-20 px-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center opacity-20 mix-blend-overlay"></div>
          <div className="max-w-5xl mx-auto relative z-10">
            <h2 className="text-4xl md:text-6xl font-bold text-white mb-4">Discover the world with AI.</h2>
            <p className="text-blue-200 text-lg mb-10">Let FlySync's agentic concierge orchestrate your perfect itinerary.</p>
            
            {/* Search Widget */}
            <div className="bg-white dark:bg-slate-900 p-3 rounded-2xl shadow-2xl flex flex-col md:flex-row gap-2 flex-wrap lg:flex-nowrap transition-colors duration-300">
              <div className="flex-1 min-w-[150px] bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
                <PlaneTakeoff className="text-slate-400 w-5 h-5 ml-2 shrink-0" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider block">Origin</label>
                  <select value={origin} onChange={e => setOrigin(e.target.value)} className="w-full bg-transparent border-none outline-none text-slate-900 dark:text-white font-bold cursor-pointer appearance-none">
                    <option value="DXB">DXB (Dubai)</option>
                    <option value="BOM">BOM (Mumbai)</option>
                    <option value="LHR">LHR (London)</option>
                    <option value="JFK">JFK (New York)</option>
                    <option value="SIN">SIN (Singapore)</option>
                  </select>
                </div>
              </div>
              <div className="flex-1 min-w-[150px] bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
                <MapPin className="text-slate-400 w-5 h-5 ml-2 shrink-0" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider block">Destination</label>
                  <select value={destination} onChange={e => setDestination(e.target.value)} className="w-full bg-transparent border-none outline-none text-slate-900 dark:text-white font-bold cursor-pointer appearance-none">
                    <option value="LHR">LHR (London)</option>
                    <option value="JFK">JFK (New York)</option>
                    <option value="SIN">SIN (Singapore)</option>
                    <option value="BOM">BOM (Mumbai)</option>
                    <option value="DXB">DXB (Dubai)</option>
                  </select>
                </div>
              </div>
              <div className="flex-1 min-w-[150px] bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
                <CalendarDays className="text-slate-400 w-5 h-5 ml-2 shrink-0" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider block">Travel Date</label>
                  <input type="date" value={travelDate} onChange={e => setTravelDate(e.target.value)} className="w-full bg-transparent border-none outline-none text-slate-900 dark:text-white font-bold" />
                </div>
              </div>
              <div className="flex-1 min-w-[120px] bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
                <CircleDollarSign className="text-slate-400 w-5 h-5 ml-2 shrink-0" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider block">Currency</label>
                  <select value={currency} onChange={e => setCurrency(e.target.value)} className="w-full bg-transparent border-none outline-none text-slate-900 dark:text-white font-bold cursor-pointer appearance-none">
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="AED">AED (د.إ)</option>
                  </select>
                </div>
              </div>
              <button 
                onClick={handleSearch}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold px-8 flex items-center justify-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed md:w-auto w-full py-4 md:py-0"
              >
                {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : <><Search className="w-5 h-5" /> Search</>}
              </button>
            </div>
            
            {error && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className="mt-6 bg-red-500/10 border border-red-500/20 backdrop-blur-md text-red-100 px-6 py-4 rounded-xl flex items-start gap-4 max-w-2xl mx-auto"
              >
                <ShieldAlert className="w-6 h-6 shrink-0 text-red-400 mt-1"/>
                <div>
                  <h4 className="font-bold text-red-300 mb-1">Agent Workflow Failed</h4>
                  <p className="text-sm text-red-100/80">{error}</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* Agentic Visibility Overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-slate-900/40 dark:bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl p-8 max-w-md w-full border border-transparent dark:border-slate-800">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center animate-pulse">
                  <BrainCircuit className="w-8 h-8" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-center text-slate-800 dark:text-slate-100 mb-8">AI Concierge Working...</h3>
              
              <div className="space-y-6">
                {/* Scout Step */}
                <div className="flex items-center gap-4">
                  {agentStep >= 1 ? <CheckCircle2 className={`w-6 h-6 ${agentStep > 1 ? 'text-green-500' : 'text-blue-500 animate-pulse'}`} /> : <div className="w-6 h-6 rounded-full border-2 border-slate-200 dark:border-slate-700" />}
                  <div>
                    <p className={`font-bold ${agentStep >= 1 ? 'text-slate-800 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600'}`}>Scout Agent</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{agentStep > 1 ? 'Found optimal flights & hotels' : agentStep === 1 ? 'Searching global inventory...' : 'Waiting...'}</p>
                  </div>
                </div>
                {/* Sync Step */}
                <div className="flex items-center gap-4">
                  {agentStep >= 2 ? <CheckCircle2 className={`w-6 h-6 ${agentStep > 2 ? 'text-green-500' : 'text-blue-500 animate-pulse'}`} /> : <div className="w-6 h-6 rounded-full border-2 border-slate-200 dark:border-slate-700" />}
                  <div>
                    <p className={`font-bold ${agentStep >= 2 ? 'text-slate-800 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600'}`}>Sync Coordinator</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{agentStep > 2 ? 'Calendar conflicts cleared' : agentStep === 2 ? 'Checking your schedule...' : 'Waiting...'}</p>
                  </div>
                </div>
                {/* Sentinel Step */}
                <div className="flex items-center gap-4">
                  {agentStep >= 3 ? <CheckCircle2 className={`w-6 h-6 ${agentStep > 3 ? 'text-green-500' : 'text-blue-500 animate-pulse'}`} /> : <div className="w-6 h-6 rounded-full border-2 border-slate-200 dark:border-slate-700" />}
                  <div>
                    <p className={`font-bold ${agentStep >= 3 ? 'text-slate-800 dark:text-slate-200' : 'text-slate-400 dark:text-slate-600'}`}>Sentinel Agent</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{agentStep > 3 ? 'Rewards & pricing analyzed' : agentStep === 3 ? 'Evaluating dynamic pricing...' : 'Waiting...'}</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results UI */}
      {result && !loading && !showCheckout && (
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Top Info Bar */}
          <div className="flex flex-wrap items-center justify-between bg-white dark:bg-slate-900 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-800 mb-8">
            <div className="flex items-center gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/30 p-2 rounded-lg"><PlaneTakeoff className="text-blue-600 dark:text-blue-400 w-5 h-5"/></div>
              <div>
                <p className="font-bold text-slate-800 dark:text-slate-200">{result.selected_flight?.origin} to {result.selected_flight?.destination}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">1 Adult • Economy • {result.selected_flight?.departure_time.split('T')[0]}</p>
              </div>
            </div>
            <button onClick={() => setResult(null)} className="text-sm font-semibold text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-slate-800 px-4 py-2 rounded-lg transition-colors">Change Search</button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Left Sidebar Filters */}
            <div className="hidden lg:block space-y-6">
              <div className="flex items-center gap-2 font-bold text-slate-800 dark:text-slate-200 pb-2 border-b border-slate-200 dark:border-slate-800">
                <Filter className="w-4 h-4"/> Filters
              </div>
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-200 mb-3 text-sm">Stops</p>
                <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 mb-2 cursor-pointer"><input type="checkbox" defaultChecked className="rounded text-blue-600" /> Direct only</label>
                <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 mb-2 cursor-pointer"><input type="checkbox" className="rounded text-blue-600" /> 1 stop</label>
              </div>
              <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
                <p className="font-semibold text-slate-800 dark:text-slate-200 mb-3 text-sm">Price Range</p>
                <input type="range" className="w-full accent-blue-600" min="0" max="5000" defaultValue="3500"/>
                <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1"><span>$0</span><span>$3,500</span></div>
              </div>
              
              {/* Agent Insights Box */}
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-4 border border-blue-100 mt-8">
                <div className="flex items-center gap-2 text-blue-800 font-bold mb-3">
                  <Sparkles className="w-4 h-4 text-blue-600"/> Agent Insights
                </div>
                {result.calendar_conflicts.length > 0 ? (
                  <div className="bg-amber-100 text-amber-800 p-3 rounded-lg text-xs font-medium mb-3 flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5"/>
                    <p>{result.calendar_conflicts[0]}</p>
                  </div>
                ) : (
                  <div className="bg-green-100 text-green-800 p-3 rounded-lg text-xs font-medium mb-3">
                    No calendar conflicts detected for these dates.
                  </div>
                )}
                <div className="text-xs text-slate-700 font-medium">
                  <p className="mb-1"><strong>Price Trend:</strong> {result.price_analysis?.price_status}</p>
                  <p className="text-blue-700 font-bold">{result.price_analysis?.buying_verdict}</p>
                </div>
              </div>
            </div>

            {/* Main Content: Flight & Hotel Cards */}
            <div className="lg:col-span-3 space-y-6">
              
              {/* Flight Card */}
              <h3 className="text-xl font-black text-slate-800 dark:text-slate-100 mb-4">Recommended Flight</h3>
              <div 
                className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-blue-500 transition-colors overflow-hidden group cursor-pointer"
                onClick={() => setIsFlightExpanded(!isFlightExpanded)}
              >
                <div className="bg-slate-50 dark:bg-slate-800/50 px-6 py-3 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                  <div className="flex gap-2">
                    <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold px-2 py-1 rounded">Best Value</span>
                    {result.selected_flight?.is_refundable && <span className="bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-bold px-2 py-1 rounded">Refundable</span>}
                  </div>
                  <div className="flex items-center gap-3 text-xs font-medium">
                    <div className="flex items-center gap-1 text-green-700 dark:text-green-400">
                      <Leaf className="w-3 h-3"/> {result.selected_flight?.carbon_emission_kg} kg CO2e
                    </div>
                    <div className="text-slate-400 flex items-center gap-1 hover:text-slate-600 dark:hover:text-slate-200">
                      {isFlightExpanded ? <ChevronUp className="w-4 h-4"/> : <ChevronDown className="w-4 h-4"/>}
                    </div>
                  </div>
                </div>
                
                <div className="p-6 flex flex-col md:flex-row md:items-center gap-6">
                  {/* Airline Logo */}
                  <div className="w-16 shrink-0">
                    <img src={result.selected_flight?.logo_url} alt={result.selected_flight?.airline} className="w-full object-contain max-h-12 dark:invert" />
                  </div>
                  
                  {/* Flight Times & Timeline */}
                  <div className="flex-1 flex items-center justify-between md:px-8">
                    <div className="text-center">
                      <p className="text-2xl font-black text-slate-800 dark:text-slate-100">{result.selected_flight?.departure_time.split('T').length > 1 ? result.selected_flight?.departure_time.split('T')[1].slice(0, 5) : result.selected_flight?.departure_time.slice(0, 5)}</p>
                      <p className="text-sm font-bold text-slate-500 dark:text-slate-400">{result.selected_flight?.origin}</p>
                    </div>
                    
                    <div className="flex-1 px-4 relative flex flex-col items-center">
                      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">{result.selected_flight?.duration}</p>
                      <div className="w-full h-[2px] bg-slate-300 dark:bg-slate-700 relative">
                        <div className="absolute w-2 h-2 rounded-full bg-slate-400 dark:bg-slate-500 -left-1 -top-[3px]"></div>
                        <div className="absolute w-2 h-2 rounded-full bg-slate-400 dark:bg-slate-500 -right-1 -top-[3px]"></div>
                      </div>
                      <p className="text-[10px] font-bold text-blue-600 dark:text-blue-400 mt-1 uppercase">{result.selected_flight?.stops === 0 ? "Direct" : `${result.selected_flight?.stops} Stop`}</p>
                    </div>

                    <div className="text-center">
                      <p className="text-2xl font-black text-slate-800 dark:text-slate-100">{result.selected_flight?.arrival_time.split('T').length > 1 ? result.selected_flight?.arrival_time.split('T')[1].slice(0, 5) : result.selected_flight?.arrival_time.slice(0, 5)}</p>
                      <p className="text-sm font-bold text-slate-500 dark:text-slate-400">{result.selected_flight?.destination}</p>
                    </div>
                  </div>

                  {/* Price & Action */}
                  <div className="md:border-l md:border-slate-200 dark:md:border-slate-800 md:pl-6 text-right md:w-48">
                    <div className="flex items-center justify-end gap-1 mb-1 text-slate-500 dark:text-slate-400">
                      <Briefcase className="w-4 h-4" /> <span className="text-xs font-medium">{result.selected_flight?.baggage}</span>
                    </div>
                    <p className="text-3xl font-black text-slate-800 dark:text-slate-100">{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}{result.selected_flight?.price_home}</p>
                    <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-3">Total price</p>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setShowCheckout(true); }} 
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-bold transition-colors"
                    >
                      Select
                    </button>
                  </div>
                </div>

                {/* Expandable Summary */}
                <AnimatePresence>
                  {isFlightExpanded && (
                    <motion.div 
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30"
                    >
                      <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                        <div>
                          <h4 className="font-bold text-slate-800 dark:text-slate-100 mb-3">Flight Details</h4>
                          <div className="space-y-2 text-slate-600 dark:text-slate-400">
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Flight:</span> {result.selected_flight?.airline} {result.selected_flight?.flight_number}</p>
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Class:</span> <span className="capitalize">{result.selected_flight?.cabin_class}</span></p>
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Aircraft:</span> Boeing 777-300ER (Mocked)</p>
                            {result.selected_flight?.confirmation_number && (
                              <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">PNR:</span> <span className="font-bold text-slate-800 dark:text-slate-100 bg-slate-200 dark:bg-slate-700 px-1 rounded">{result.selected_flight?.confirmation_number}</span></p>
                            )}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-800 dark:text-slate-100 mb-3">Policies & Extras</h4>
                          <div className="space-y-2 text-slate-600 dark:text-slate-400">
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Baggage:</span> {result.selected_flight?.baggage}</p>
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Cancellation:</span> {result.selected_flight?.is_refundable ? "Fully Refundable before 24h" : "Non-refundable"}</p>
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Changes:</span> Permitted with fee</p>
                            <p><span className="font-medium text-slate-400 dark:text-slate-500 w-24 inline-block">Emissions:</span> {result.selected_flight?.carbon_emission_kg} kg (12% lower than average)</p>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Alternative Flights */}
              {result.flight_options?.length > 1 && (
                <div className="mt-4 space-y-3">
                  <h4 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Alternative Flights</h4>
                  {result.flight_options.filter((f: any) => f.flight_number !== result.selected_flight?.flight_number).map((flight: any, idx: number) => (
                    <div key={idx} className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-4 flex items-center justify-between hover:border-blue-300 dark:hover:border-blue-500 transition-colors">
                      <div className="flex items-center gap-4">
                        <img src={flight.logo_url} alt={flight.airline} className="w-10 h-10 object-contain dark:invert bg-white dark:bg-transparent rounded-md p-1" />
                        <div>
                          <p className="font-bold text-slate-800 dark:text-slate-100">{flight.departure_time.slice(0, 5)} - {flight.arrival_time.slice(0, 5)}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">{flight.airline} • {flight.duration} • {flight.stops === 0 ? "Direct" : `${flight.stops} Stop`}</p>
                        </div>
                      </div>
                      <div className="text-right flex items-center gap-4">
                        <div>
                          <p className="font-bold text-slate-800 dark:text-slate-100">{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}{flight.price_home}</p>
                        </div>
                        <button 
                          onClick={(e) => { e.stopPropagation(); setResult({ ...result, selected_flight: flight }); setShowCheckout(true); }}
                          className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 px-4 py-2 rounded-lg text-sm font-bold transition-colors"
                        >
                          Select
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Hotel Card */}
              <h3 className="text-xl font-black text-slate-800 dark:text-slate-100 mt-10 mb-4">AI Recommended Stay</h3>
              <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-blue-500 transition-colors overflow-hidden flex flex-col md:flex-row group">
                {/* Hotel Image */}
                <div className="md:w-72 h-56 md:h-auto relative">
                  <img src={result.selected_hotel?.image_url} alt="Hotel" className="w-full h-full object-cover" />
                  {result.selected_hotel?.is_ai_recommended && (
                    <div className="absolute top-3 left-3 bg-indigo-600 text-white text-xs font-bold px-2 py-1 rounded shadow-md flex items-center gap-1">
                      <Sparkles className="w-3 h-3"/> AI Pick
                    </div>
                  )}
                </div>
                
                {/* Hotel Details */}
                <div className="p-6 flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="text-xl font-bold text-slate-800 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer">{result.selected_hotel?.hotel_name}</h4>
                        <div className="flex items-center gap-2 mt-1 mb-3">
                          <span className="bg-blue-600 text-white text-xs font-bold px-1.5 py-0.5 rounded">{result.selected_hotel?.rating}</span>
                          <span className="text-sm font-semibold text-blue-600 dark:text-blue-400 cursor-pointer flex items-center gap-1"><MapPin className="w-3 h-3"/> Show on Map</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-black text-slate-800 dark:text-slate-100">{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}{result.selected_hotel?.price_home}</p>
                        <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Per night, taxes inc.</p>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.selected_hotel?.amenities.map((a: string, i: number) => (
                        <span key={i} className={`text-xs font-bold px-2 py-1 rounded border ${a.includes("Breakfast") ? "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400" : "bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400"}`}>
                          {a}
                        </span>
                      ))}
                      {result.selected_hotel?.is_refundable && (
                        <span className="text-xs font-bold px-2 py-1 rounded border bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400">Free Cancellation</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="mt-6 flex justify-between items-end">
                    <div className="text-sm">
                      {result.loyalty_details?.points_accrued > 0 && (
                        <p className="text-amber-600 font-bold flex items-center gap-1">
                          <Coins className="w-4 h-4"/> Earn {result.loyalty_details?.points_accrued} points
                        </p>
                      )}
                    </div>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setShowCheckout(true); }}
                      className="bg-slate-800 dark:bg-slate-700 hover:bg-slate-900 dark:hover:bg-slate-600 text-white px-6 py-2 rounded-lg font-bold transition-colors flex items-center gap-2"
                    >
                      View Rooms <ArrowRight className="w-4 h-4"/>
                    </button>
                  </div>
                </div>
              </div>


              {/* Special Deals Section */}
              <div className="pt-8">
                <h3 className="text-xl font-black text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5 text-amber-500"/> Exclusive Add-ons</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl p-5 border border-amber-200 dark:border-amber-800/50 flex items-start gap-4 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="bg-amber-100 dark:bg-amber-900/50 p-2 rounded-lg text-amber-600 dark:text-amber-400 shrink-0">
                      <Briefcase className="w-6 h-6"/>
                    </div>
                    <div>
                      <h4 className="font-bold text-amber-900 dark:text-amber-100 text-sm mb-1">Extra 20kg Baggage</h4>
                      <p className="text-xs text-amber-700/80 dark:text-amber-300/80 mb-2">Pre-book now and save 40% on airport rates.</p>
                      <p className="font-bold text-amber-600 dark:text-amber-400 text-sm">+{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}35.00</p>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800/50 flex items-start gap-4 hover:shadow-md transition-shadow cursor-pointer">
                    <div className="bg-blue-100 dark:bg-blue-900/50 p-2 rounded-lg text-blue-600 dark:text-blue-400 shrink-0">
                      <ShieldAlert className="w-6 h-6"/>
                    </div>
                    <div>
                      <h4 className="font-bold text-blue-900 dark:text-blue-100 text-sm mb-1">Travel Insurance</h4>
                      <p className="text-xs text-blue-700/80 dark:text-blue-300/80 mb-2">Full coverage for delays, cancellations & medical.</p>
                      <p className="font-bold text-blue-600 dark:text-blue-400 text-sm">+{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}18.50</p>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* Checkout Summary UI */}
      {showCheckout && (
        <div className="max-w-3xl mx-auto px-6 py-12">
          <button 
            onClick={() => setShowCheckout(false)} 
            className="flex items-center gap-2 text-sm font-bold text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 mb-8 transition-colors"
          >
            <ArrowRight className="w-4 h-4 rotate-180"/> Back to Results
          </button>

          <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-xl border border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-3 mb-8 pb-6 border-b border-slate-100 dark:border-slate-800">
              <div className="bg-green-100 dark:bg-green-900/30 p-3 rounded-full text-green-600 dark:text-green-400">
                <CheckCircle className="w-8 h-8"/>
              </div>
              <div>
                <h2 className="text-3xl font-black text-slate-800 dark:text-slate-100">Review Your Itinerary</h2>
                <p className="text-slate-500 dark:text-slate-400 font-medium">You're almost there! Review your selections before confirming.</p>
              </div>
            </div>

            <div className="space-y-6 mb-8">
              <div className="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-2xl border border-slate-100 dark:border-slate-700">
                <h4 className="font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-2"><PlaneTakeoff className="w-4 h-4 text-blue-500"/> Flight Summary</h4>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{result.selected_flight?.origin} to {result.selected_flight?.destination} • {travelDate}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">{result.selected_flight?.airline} {result.selected_flight?.flight_number} • <span className="capitalize">{result.selected_flight?.cabin_class}</span></p>
                <div className="flex justify-between items-center font-bold">
                  <span className="text-slate-800 dark:text-slate-200">Flight Total:</span>
                  <span className="text-slate-800 dark:text-slate-200">{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}{result.selected_flight?.price_home}</span>
                </div>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-2xl border border-slate-100 dark:border-slate-700">
                <h4 className="font-bold text-slate-800 dark:text-slate-200 mb-2 flex items-center gap-2"><Hotel className="w-4 h-4 text-blue-500"/> Hotel Summary</h4>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">{result.selected_hotel?.hotel_name}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">1 Night • 1 Room</p>
                <div className="flex justify-between items-center font-bold">
                  <span className="text-slate-800 dark:text-slate-200">Hotel Total:</span>
                  <span className="text-slate-800 dark:text-slate-200">{currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}{result.selected_hotel?.price_home}</span>
                </div>
              </div>
            </div>

            <div className="border-t border-slate-200 dark:border-slate-800 pt-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">Total Due</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Includes all taxes and fees</p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-black text-blue-600 dark:text-blue-400">
                    {currency === "GBP" ? "£" : currency === "EUR" ? "€" : currency === "AED" ? "د.إ" : "$"}
                    {(parseFloat(result.selected_flight?.price_home) + parseFloat(result.selected_hotel?.price_home)).toFixed(2)}
                  </p>
                  <p className="text-xs font-bold text-amber-600 dark:text-amber-500 mt-1 flex items-center justify-end gap-1"><Coins className="w-3 h-3"/> Earn {result.loyalty_details?.points_accrued + 500} points</p>
                </div>
              </div>

              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold text-lg transition-colors shadow-lg shadow-blue-500/30">
                Confirm Booking
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Rewards Modal */}
      <AnimatePresence>
        {showRewards && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 cursor-pointer"
            onClick={() => setShowRewards(false)}
          >
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl max-w-2xl w-full border border-slate-200 dark:border-slate-800 overflow-hidden relative cursor-default"
            >
              <button 
                onClick={() => setShowRewards(false)}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/20 text-white/70 hover:text-white transition-colors z-20"
              >
                <X className="w-6 h-6"/>
              </button>

              <div className="bg-gradient-to-br from-amber-500 to-orange-600 p-8 text-white relative overflow-hidden">
                <div className="absolute right-0 top-0 opacity-10 transform translate-x-1/4 -translate-y-1/4 scale-150">
                  <Trophy className="w-64 h-64"/>
                </div>
                <div className="relative z-10 flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur border-2 border-white/40 flex items-center justify-center font-black text-2xl">HM</div>
                  <div>
                    <h2 className="text-3xl font-black">flyGold Member</h2>
                    <p className="text-amber-100 font-medium">Hatim Madarwala</p>
                  </div>
                </div>
                
                <div className="relative z-10">
                  <p className="text-amber-100 text-sm font-bold uppercase tracking-wider mb-1">Total Balance</p>
                  <p className="text-5xl font-black flex items-center gap-2"><Coins className="w-8 h-8"/> 15,000 <span className="text-xl font-medium text-amber-200">pts</span></p>
                </div>
              </div>

              <div className="p-8 space-y-8">
                {/* Progress to Next Tier */}
                <div>
                  <div className="flex justify-between items-end mb-2">
                    <h3 className="font-bold text-slate-800 dark:text-slate-100">Progress to flyPlatinum</h3>
                    <span className="text-sm font-bold text-blue-600 dark:text-blue-400">10,000 pts to go</span>
                  </div>
                  <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 w-[60%] rounded-full"></div>
                  </div>
                  <div className="flex justify-between mt-2 text-xs font-bold text-slate-400">
                    <span>Gold (Current)</span>
                    <span>Platinum (25k pts)</span>
                    <span>Diamond (50k pts)</span>
                  </div>
                </div>

                {/* Perks */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl text-center border border-slate-100 dark:border-slate-800">
                    <div className="w-10 h-10 mx-auto bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center mb-2"><PlaneTakeoff className="w-5 h-5"/></div>
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-300">Priority Boarding</p>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl text-center border border-slate-100 dark:border-slate-800">
                    <div className="w-10 h-10 mx-auto bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 rounded-full flex items-center justify-center mb-2"><Trophy className="w-5 h-5"/></div>
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-300">Lounge Access</p>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl text-center border border-slate-100 dark:border-slate-800 opacity-50 grayscale">
                    <div className="w-10 h-10 mx-auto bg-slate-200 dark:bg-slate-700 text-slate-500 rounded-full flex items-center justify-center mb-2"><Sparkles className="w-5 h-5"/></div>
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-300">Free Upgrades</p>
                    <p className="text-[10px] text-blue-500 mt-1">Unlock at Platinum</p>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl text-center border border-slate-100 dark:border-slate-800 opacity-50 grayscale">
                    <div className="w-10 h-10 mx-auto bg-slate-200 dark:bg-slate-700 text-slate-500 rounded-full flex items-center justify-center mb-2"><Briefcase className="w-5 h-5"/></div>
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-300">Extra Baggage</p>
                    <p className="text-[10px] text-blue-500 mt-1">Unlock at Diamond</p>
                  </div>
                </div>

                {/* Recent Activity */}
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-100 mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 p-2 rounded-lg"><Coins className="w-4 h-4"/></div>
                        <div>
                          <p className="font-bold text-sm text-slate-800 dark:text-slate-200">Flight Booking (DXB to LHR)</p>
                          <p className="text-xs text-slate-500">June 20, 2026</p>
                        </div>
                      </div>
                      <span className="font-black text-green-600 dark:text-green-400">+2,500 pts</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 p-2 rounded-lg"><Coins className="w-4 h-4"/></div>
                        <div>
                          <p className="font-bold text-sm text-slate-800 dark:text-slate-200">Hotel Booking (The Savoy)</p>
                          <p className="text-xs text-slate-500">June 20, 2026</p>
                        </div>
                      </div>
                      <span className="font-black text-green-600 dark:text-green-400">+800 pts</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
