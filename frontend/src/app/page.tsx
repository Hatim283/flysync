"use client";

import { useState } from "react";
import { PlaneTakeoff, Hotel, CalendarDays, Coins, BrainCircuit, Loader2, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

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
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen hero-gradient font-sans selection:bg-primary/30 text-slate-100">
      {/* Header */}
      <header className="fixed top-0 w-full z-50 glass-panel border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PlaneTakeoff className="text-primary w-8 h-8" />
            <h1 className="text-2xl font-bold tracking-tight">FlySync<span className="text-success">Hub</span></h1>
          </div>
          <nav className="hidden md:flex gap-8 text-sm font-medium text-slate-300">
            <a href="#" className="hover:text-white transition-colors">Flights</a>
            <a href="#" className="hover:text-white transition-colors">Hotels</a>
            <a href="#" className="hover:text-white transition-colors flex items-center gap-1"><Coins className="w-4 h-4 text-warning"/> Rewards</a>
          </nav>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">flyGold Member</span>
            <button className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-full text-sm font-semibold transition-all">Sign In</button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="pt-32 pb-20 px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-medium mb-6">
              <BrainCircuit className="w-4 h-4" /> Agentic AI Concierge
            </span>
            <h2 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
              Where do you want to <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400">sync</span> to next?
            </h2>
            <p className="text-lg text-slate-400">
              Our Multi-Agent AI scouts the best flights, negotiates hotels, checks your calendar, and maximizes your loyalty rewards—all in real-time.
            </p>
          </motion.div>
        </div>

        {/* Search Widget */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}
          className="glass-panel rounded-3xl p-6 md:p-8 shadow-2xl max-w-5xl mx-auto"
        >
          <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-3 flex items-center gap-3">
              <PlaneTakeoff className="text-slate-400 w-5 h-5 ml-2" />
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-bold">From</label>
                <input type="text" defaultValue="DXB (Dubai)" className="w-full bg-transparent border-none outline-none text-white font-semibold" />
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-3 flex items-center gap-3">
              <PlaneTakeoff className="text-slate-400 w-5 h-5 ml-2" />
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-bold">To</label>
                <input type="text" defaultValue="LHR (London)" className="w-full bg-transparent border-none outline-none text-white font-semibold" />
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-3 flex items-center gap-3">
              <CalendarDays className="text-slate-400 w-5 h-5 ml-2" />
              <div>
                <label className="text-xs text-slate-400 uppercase tracking-wider font-bold">Date</label>
                <input type="date" defaultValue="2026-07-05" className="w-full bg-transparent border-none outline-none text-white font-semibold [color-scheme:dark]" />
              </div>
            </div>
            <button 
              type="submit" 
              disabled={loading}
              className="bg-primary hover:bg-blue-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><BrainCircuit className="w-5 h-5" /> Unleash Agents</>}
            </button>
          </form>
        </motion.div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="max-w-7xl mx-auto px-6 pb-32">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Col: Main Results */}
            <div className="lg:col-span-2 space-y-6">
              <h3 className="text-2xl font-bold flex items-center gap-2">
                <PlaneTakeoff className="w-6 h-6 text-primary" /> Curated Flight
              </h3>
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-panel rounded-2xl p-6 border-l-4 border-l-primary">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-xl font-bold">{result.selected_flight.airline}</h4>
                    <p className="text-sm text-slate-400">Flight {result.selected_flight.flight_number}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-success">${result.selected_flight.price_home}</p>
                    <p className="text-xs text-slate-400">Total Price</p>
                  </div>
                </div>
                <div className="flex items-center justify-between text-center pt-4 border-t border-white/10">
                  <div>
                    <p className="text-xl font-bold">{result.selected_flight.departure_time.split('T')[1]}</p>
                    <p className="text-sm text-slate-400">{result.selected_flight.origin}</p>
                  </div>
                  <div className="flex-1 px-8 relative">
                    <div className="h-[2px] bg-white/20 w-full absolute top-1/2 -translate-y-1/2"></div>
                    <PlaneTakeoff className="w-4 h-4 absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2 text-slate-400 bg-background px-1" />
                  </div>
                  <div>
                    <p className="text-xl font-bold">{result.selected_flight.arrival_time.split('T')[1]}</p>
                    <p className="text-sm text-slate-400">{result.selected_flight.destination}</p>
                  </div>
                </div>
              </motion.div>

              <h3 className="text-2xl font-bold flex items-center gap-2 mt-12">
                <Hotel className="w-6 h-6 text-success" /> Selected Accommodation
              </h3>
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="glass-panel rounded-2xl p-6 border-l-4 border-l-success">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-xl font-bold">{result.selected_hotel.hotel_name}</h4>
                    <p className="text-sm text-slate-400">{result.selected_hotel.rating} ★ Rating</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-success">${result.selected_hotel.price_home}</p>
                    <p className="text-xs text-slate-400">Per Night</p>
                  </div>
                </div>
                <div className="flex gap-2 flex-wrap mt-4">
                  {result.selected_hotel.amenities.map((a: string, i: number) => (
                    <span key={i} className="bg-white/10 px-3 py-1 rounded-full text-xs">{a}</span>
                  ))}
                </div>
              </motion.div>
            </div>

            {/* Right Col: Agent Reasoning Visualization */}
            <div className="lg:col-span-1 space-y-6">
              <div className="glass-panel rounded-2xl p-6 sticky top-28 bg-blue-900/10 border-blue-500/20">
                <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-blue-400">
                  <BrainCircuit className="w-5 h-5" /> Agent Execution Trace
                </h3>
                <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                  {result.execution_trace.map((trace: string, idx: number) => (
                    <motion.div 
                      key={idx} 
                      initial={{ opacity: 0, y: 10 }} 
                      animate={{ opacity: 1, y: 0 }} 
                      transition={{ delay: idx * 0.1 }}
                      className="text-sm border-l-2 border-white/10 pl-3 py-1"
                    >
                      {trace.includes("CRITICAL") ? (
                        <span className="text-red-400 font-semibold">{trace}</span>
                      ) : trace.includes("ALERT") ? (
                        <span className="text-warning font-semibold">{trace}</span>
                      ) : trace.includes("Agent") ? (
                        <span className="text-slate-300"><span className="text-primary font-bold">{trace.split(']')[0]}]</span>{trace.split(']')[1]}</span>
                      ) : (
                        <span className="text-slate-400 font-mono text-xs">{trace}</span>
                      )}
                    </motion.div>
                  ))}
                </div>
                
                <div className="mt-6 pt-4 border-t border-white/10">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-slate-400">Points Earned:</span>
                    <span className="font-bold text-warning flex items-center gap-1"><Coins className="w-4 h-4"/> +{result.loyalty_details?.points_accrued || 0}</span>
                  </div>
                  <button className="w-full mt-4 bg-white text-black hover:bg-slate-200 py-3 rounded-xl font-bold flex justify-center items-center gap-2 transition-all">
                    Confirm Booking <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}
    </main>
  );
}
