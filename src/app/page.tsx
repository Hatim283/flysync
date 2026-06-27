"use client";

import { useState } from "react";
import { PlaneTakeoff, Hotel, CalendarDays, Coins, BrainCircuit, Loader2, ArrowRight, MapPin, CheckCircle2, ShieldAlert, Sparkles, Leaf, Briefcase, Filter, Search } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [agentStep, setAgentStep] = useState(0); 
  const [result, setResult] = useState<any>(null);

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
    setAgentStep(0);

    // Run UI simulation concurrently with fetch
    const simulationPromise = simulateAgentSequence();
    
    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin: "DXB",
          destination: "LHR",
          travel_date: "2026-07-05",
          preferences: {
            home_currency: "USD",
            preferred_seating: "window",
            membership_tier: "flyGold",
            max_budget: 3500.0,
            points_balance: 15000
          }
        }),
      });
      const data = await response.json();
      
      // Ensure simulation finishes before showing results
      await simulationPromise;
      setResult(data);
    } catch (err) {
      console.error(err);
      await simulationPromise;
    } finally {
      setLoading(false);
      setAgentStep(0);
    }
  };

  return (
    <main className="min-h-screen bg-[#F1F5F9] font-sans selection:bg-blue-500/30 text-slate-800">
      {/* Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-600">
            <PlaneTakeoff className="w-7 h-7" />
            <h1 className="text-2xl font-black tracking-tight">FlySync<span className="text-slate-800">Hub</span></h1>
          </div>
          <nav className="hidden md:flex gap-8 text-sm font-semibold text-slate-600">
            <a href="#" className="hover:text-blue-600 transition-colors border-b-2 border-blue-600 pb-5 translate-y-[10px]">Flights & Hotels</a>
            <a href="#" className="hover:text-blue-600 transition-colors flex items-center gap-1"><Coins className="w-4 h-4 text-amber-500"/> Rewards</a>
          </nav>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-amber-600 bg-amber-50 px-3 py-1 rounded-full">flyGold Member</span>
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm">HM</div>
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
            <div className="bg-white p-3 rounded-2xl shadow-2xl flex flex-col md:flex-row gap-2">
              <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 transition-colors">
                <PlaneTakeoff className="text-slate-400 w-5 h-5 ml-2" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 uppercase font-bold tracking-wider block">Origin</label>
                  <input type="text" defaultValue="DXB (Dubai)" className="w-full bg-transparent border-none outline-none text-slate-900 font-bold" />
                </div>
              </div>
              <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 transition-colors">
                <MapPin className="text-slate-400 w-5 h-5 ml-2" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 uppercase font-bold tracking-wider block">Destination</label>
                  <input type="text" defaultValue="LHR (London)" className="w-full bg-transparent border-none outline-none text-slate-900 font-bold" />
                </div>
              </div>
              <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center gap-3 hover:border-blue-400 transition-colors">
                <CalendarDays className="text-slate-400 w-5 h-5 ml-2" />
                <div className="flex-1">
                  <label className="text-[10px] text-slate-500 uppercase font-bold tracking-wider block">Travel Date</label>
                  <input type="date" defaultValue="2026-07-05" className="w-full bg-transparent border-none outline-none text-slate-900 font-bold" />
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
          </div>
        </div>
      )}

      {/* Agentic Visibility Overlay */}
      <AnimatePresence>
        {loading && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full">
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center animate-pulse">
                  <BrainCircuit className="w-8 h-8" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-center text-slate-800 mb-8">AI Concierge Working...</h3>
              
              <div className="space-y-6">
                {/* Scout Step */}
                <div className="flex items-center gap-4">
                  {agentStep >= 1 ? <CheckCircle2 className={`w-6 h-6 ${agentStep > 1 ? 'text-green-500' : 'text-blue-500 animate-pulse'}`} /> : <div className="w-6 h-6 rounded-full border-2 border-slate-200" />}
                  <div>
                    <p className={`font-bold ${agentStep >= 1 ? 'text-slate-800' : 'text-slate-400'}`}>Scout Agent</p>
                    <p className="text-sm text-slate-500">{agentStep > 1 ? 'Found optimal flights & hotels' : agentStep === 1 ? 'Searching global inventory...' : 'Waiting...'}</p>
                  </div>
                </div>
                {/* Sync Step */}
                <div className="flex items-center gap-4">
                  {agentStep >= 2 ? <CheckCircle2 className={`w-6 h-6 ${agentStep > 2 ? 'text-green-500' : 'text-blue-500 animate-pulse'}`} /> : <div className="w-6 h-6 rounded-full border-2 border-slate-200" />}
                  <div>
                    <p className={`font-bold ${agentStep >= 2 ? 'text-slate-800' : 'text-slate-400'}`}>Sync Coordinator</p>
                    <p className="text-sm text-slate-500">{agentStep > 2 ? 'Calendar conflicts cleared' : agentStep === 2 ? 'Checking your schedule...' : 'Waiting...'}</p>
                  </div>
                </div>
                {/* Sentinel Step */}
                <div className="flex items-center gap-4">
                  {agentStep >= 3 ? <CheckCircle2 className={`w-6 h-6 ${agentStep > 3 ? 'text-green-500' : 'text-blue-500 animate-pulse'}`} /> : <div className="w-6 h-6 rounded-full border-2 border-slate-200" />}
                  <div>
                    <p className={`font-bold ${agentStep >= 3 ? 'text-slate-800' : 'text-slate-400'}`}>Sentinel Agent</p>
                    <p className="text-sm text-slate-500">{agentStep > 3 ? 'Rewards & pricing analyzed' : agentStep === 3 ? 'Evaluating dynamic pricing...' : 'Waiting...'}</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results UI */}
      {result && !loading && (
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Top Info Bar */}
          <div className="flex flex-wrap items-center justify-between bg-white rounded-xl p-4 shadow-sm border border-slate-200 mb-8">
            <div className="flex items-center gap-4">
              <div className="bg-blue-50 p-2 rounded-lg"><PlaneTakeoff className="text-blue-600 w-5 h-5"/></div>
              <div>
                <p className="font-bold text-slate-800">{result.selected_flight?.origin} to {result.selected_flight?.destination}</p>
                <p className="text-xs text-slate-500">1 Adult • Economy • {result.selected_flight?.departure_time.split('T')[0]}</p>
              </div>
            </div>
            <button onClick={() => setResult(null)} className="text-sm font-semibold text-blue-600 hover:bg-blue-50 px-4 py-2 rounded-lg transition-colors">Change Search</button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Left Sidebar Filters */}
            <div className="hidden lg:block space-y-6">
              <div className="flex items-center gap-2 font-bold text-slate-800 pb-2 border-b border-slate-200">
                <Filter className="w-4 h-4"/> Filters
              </div>
              <div>
                <p className="font-semibold text-slate-800 mb-3 text-sm">Stops</p>
                <label className="flex items-center gap-2 text-sm text-slate-600 mb-2 cursor-pointer"><input type="checkbox" defaultChecked className="rounded text-blue-600" /> Direct only</label>
                <label className="flex items-center gap-2 text-sm text-slate-600 mb-2 cursor-pointer"><input type="checkbox" className="rounded text-blue-600" /> 1 stop</label>
              </div>
              <div className="pt-4 border-t border-slate-200">
                <p className="font-semibold text-slate-800 mb-3 text-sm">Price Range</p>
                <input type="range" className="w-full accent-blue-600" min="0" max="5000" defaultValue="3500"/>
                <div className="flex justify-between text-xs text-slate-500 mt-1"><span>$0</span><span>$3,500</span></div>
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
              <h3 className="text-xl font-black text-slate-800 mb-4">Recommended Flight</h3>
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 hover:border-blue-300 transition-colors overflow-hidden group">
                <div className="bg-slate-50 px-6 py-3 border-b border-slate-200 flex justify-between items-center">
                  <div className="flex gap-2">
                    <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded">Best Value</span>
                    {result.selected_flight?.is_refundable && <span className="bg-slate-200 text-slate-700 text-xs font-bold px-2 py-1 rounded">Refundable</span>}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-green-700 font-medium">
                    <Leaf className="w-3 h-3"/> {result.selected_flight?.carbon_emission_kg} kg CO2e
                  </div>
                </div>
                
                <div className="p-6 flex flex-col md:flex-row md:items-center gap-6">
                  {/* Airline Logo */}
                  <div className="w-16 shrink-0">
                    <img src={result.selected_flight?.logo_url} alt={result.selected_flight?.airline} className="w-full object-contain max-h-12" />
                  </div>
                  
                  {/* Flight Times & Timeline */}
                  <div className="flex-1 flex items-center justify-between md:px-8">
                    <div className="text-center">
                      <p className="text-2xl font-black text-slate-800">{result.selected_flight?.departure_time.split('T')[1].slice(0, 5)}</p>
                      <p className="text-sm font-bold text-slate-500">{result.selected_flight?.origin}</p>
                    </div>
                    
                    <div className="flex-1 px-4 relative flex flex-col items-center">
                      <p className="text-xs font-medium text-slate-500 mb-1">{result.selected_flight?.duration}</p>
                      <div className="w-full h-[2px] bg-slate-300 relative">
                        <div className="absolute w-2 h-2 rounded-full bg-slate-400 -left-1 -top-[3px]"></div>
                        <div className="absolute w-2 h-2 rounded-full bg-slate-400 -right-1 -top-[3px]"></div>
                      </div>
                      <p className="text-[10px] font-bold text-blue-600 mt-1 uppercase">{result.selected_flight?.stops === 0 ? "Direct" : `${result.selected_flight?.stops} Stop`}</p>
                    </div>

                    <div className="text-center">
                      <p className="text-2xl font-black text-slate-800">{result.selected_flight?.arrival_time.split('T')[1].slice(0, 5)}</p>
                      <p className="text-sm font-bold text-slate-500">{result.selected_flight?.destination}</p>
                    </div>
                  </div>

                  {/* Price & Action */}
                  <div className="md:border-l md:border-slate-200 md:pl-6 text-right md:w-48">
                    <div className="flex items-center justify-end gap-1 mb-1 text-slate-500">
                      <Briefcase className="w-4 h-4" /> <span className="text-xs font-medium">{result.selected_flight?.baggage}</span>
                    </div>
                    <p className="text-3xl font-black text-slate-800">${result.selected_flight?.price_home}</p>
                    <p className="text-xs font-medium text-slate-500 mb-3">Total price</p>
                    <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-bold transition-colors">Select</button>
                  </div>
                </div>
              </div>

              {/* Hotel Card */}
              <h3 className="text-xl font-black text-slate-800 mt-10 mb-4">AI Recommended Stay</h3>
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 hover:border-blue-300 transition-colors overflow-hidden flex flex-col md:flex-row group">
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
                        <h4 className="text-xl font-bold text-slate-800 hover:text-blue-600 cursor-pointer">{result.selected_hotel?.hotel_name}</h4>
                        <div className="flex items-center gap-2 mt-1 mb-3">
                          <span className="bg-blue-600 text-white text-xs font-bold px-1.5 py-0.5 rounded">{result.selected_hotel?.rating}</span>
                          <span className="text-sm font-semibold text-blue-600 cursor-pointer flex items-center gap-1"><MapPin className="w-3 h-3"/> Show on Map</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-black text-slate-800">${result.selected_hotel?.price_home}</p>
                        <p className="text-xs font-medium text-slate-500">Per night, taxes inc.</p>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-2 mt-2">
                      {result.selected_hotel?.amenities.map((a: string, i: number) => (
                        <span key={i} className={`text-xs font-bold px-2 py-1 rounded border ${a.includes("Breakfast") ? "bg-green-50 border-green-200 text-green-700" : "bg-slate-50 border-slate-200 text-slate-600"}`}>
                          {a}
                        </span>
                      ))}
                      {result.selected_hotel?.is_refundable && (
                        <span className="text-xs font-bold px-2 py-1 rounded border bg-blue-50 border-blue-200 text-blue-700">Free Cancellation</span>
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
                    <button className="bg-slate-800 hover:bg-slate-900 text-white px-6 py-2 rounded-lg font-bold transition-colors flex items-center gap-2">
                      View Rooms <ArrowRight className="w-4 h-4"/>
                    </button>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      )}
    </main>
  );
}
