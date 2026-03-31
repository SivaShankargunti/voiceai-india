"use client";
import { useState, useEffect } from "react";

const API = "http://localhost:8000";

type Business = {
  id: string;
  name: string;
  industry: string;
  plan: string;
  is_active: number;
  created_at: string;
};

type Analytics = {
  total_calls: number;
  calls_answered: number;
  calls_missed: number;
  calls_opted_out: number;
  avg_duration_seconds: number;
  total_minutes_used: number;
  hot_leads: number;
  answer_rate: string;
  business_name: string;
  plan: string;
  minutes_limit: number;
};

type Template = {
  id: string;
  name: string;
  description: string;
  icon: string;
};

export default function Dashboard() {
  const [page, setPage] = useState<"home" | "register" | "dashboard">("home");
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBiz, setSelectedBiz] = useState<Business | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);

  // Registration form
  const [formName, setFormName] = useState("");
  const [formIndustry, setFormIndustry] = useState("clinic");
  const [formOwner, setFormOwner] = useState("");
  const [formPhone, setFormPhone] = useState("");
  const [formEmail, setFormEmail] = useState("");
  const [formLanguage, setFormLanguage] = useState("hi");

  useEffect(() => {
    fetchBusinesses();
    fetchTemplates();
  }, []);

  async function fetchBusinesses() {
    try {
      const res = await fetch(`${API}/api/businesses`);
      const data = await res.json();
      setBusinesses(data);
    } catch (e) {
      console.error("Backend not running?", e);
    }
  }

  async function fetchTemplates() {
    try {
      const res = await fetch(`${API}/api/templates`);
      const data = await res.json();
      setTemplates(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchAnalytics(bizId: string) {
    try {
      const res = await fetch(`${API}/api/business/${bizId}/analytics`);
      const data = await res.json();
      setAnalytics(data);
    } catch (e) {
      console.error(e);
    }
  }

  async function registerBusiness() {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/business/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formName,
          industry: formIndustry,
          owner_name: formOwner,
          owner_phone: formPhone,
          owner_email: formEmail,
          language: formLanguage,
        }),
      });
      const data = await res.json();
      if (data.success) {
        await fetchBusinesses();
        setPage("home");
        setFormName("");
        setFormOwner("");
        setFormPhone("");
        setFormEmail("");
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }

  function selectBusiness(biz: Business) {
    setSelectedBiz(biz);
    fetchAnalytics(biz.id);
    setPage("dashboard");
  }

  const industryIcons: Record<string, string> = {
    clinic: "",
    restaurant: "",
    real_estate: "",
    ecommerce: "",
    general: "",
  };

  // ===== HOME PAGE =====
  if (page === "home") {
    return (
      <div className="min-h-screen bg-gray-950 text-white">
        {/* Header */}
        <header className="border-b border-gray-800 px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-cyan-400">VoiceAI India</h1>
            <p className="text-xs text-gray-500">India-first Voice AI for SMEs</p>
          </div>
          <button
            onClick={() => setPage("register")}
            className="bg-cyan-500 hover:bg-cyan-600 text-black font-semibold px-4 py-2 rounded-lg text-sm"
          >
            + Register Business
          </button>
        </header>

        {/* Stats */}
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-gray-500 text-xs">Total Businesses</p>
              <p className="text-2xl font-bold text-white">{businesses.length}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-gray-500 text-xs">Templates Available</p>
              <p className="text-2xl font-bold text-white">{templates.length}</p>
            </div>
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <p className="text-gray-500 text-xs">Platform Status</p>
              <p className="text-sm font-bold text-green-400 mt-1">● Live</p>
            </div>
          </div>

          {/* Business List */}
          <h2 className="text-lg font-semibold mb-4 text-gray-300">Your Businesses</h2>
          {businesses.length === 0 ? (
            <div className="bg-gray-900 rounded-xl p-8 text-center border border-gray-800">
              <p className="text-gray-500">No businesses registered yet.</p>
              <button
                onClick={() => setPage("register")}
                className="mt-4 bg-cyan-500 hover:bg-cyan-600 text-black font-semibold px-4 py-2 rounded-lg text-sm"
              >
                Register Your First Business
              </button>
            </div>
          ) : (
            <div className="grid gap-3">
              {businesses.map((biz) => (
                <div
                  key={biz.id}
                  onClick={() => selectBusiness(biz)}
                  className="bg-gray-900 rounded-xl p-4 border border-gray-800 hover:border-cyan-500 cursor-pointer flex justify-between items-center transition"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{industryIcons[biz.industry] || ""}</span>
                    <div>
                      <p className="font-semibold text-white">{biz.name}</p>
                      <p className="text-xs text-gray-500">
                        {biz.industry} · {biz.plan} plan · {biz.id}
                      </p>
                    </div>
                  </div>
                  <span className="text-cyan-400 text-sm">View →</span>
                </div>
              ))}
            </div>
          )}

          {/* Templates Section */}
          <h2 className="text-lg font-semibold mt-8 mb-4 text-gray-300">Industry Templates</h2>
          <div className="grid grid-cols-2 gap-3">
            {templates.map((t) => (
              <div key={t.id} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                <p className="font-semibold text-white">{industryIcons[t.id] || ""} {t.name}</p>
                <p className="text-xs text-gray-500 mt-1">{t.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ===== REGISTER PAGE =====
  if (page === "register") {
    return (
      <div className="min-h-screen bg-gray-950 text-white">
        <header className="border-b border-gray-800 px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-cyan-400">VoiceAI India</h1>
          <button onClick={() => setPage("home")} className="text-gray-400 text-sm hover:text-white">
            ← Back
          </button>
        </header>

        <div className="max-w-md mx-auto px-6 py-8">
          <h2 className="text-xl font-bold mb-6">Register Your Business</h2>

          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-400 block mb-1">Business Name</label>
              <input
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 outline-none"
                placeholder="e.g. Sharma Clinic"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Industry</label>
              <select
                value={formIndustry}
                onChange={(e) => setFormIndustry(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 outline-none"
              >
                <option value="clinic"> Clinic & Healthcare</option>
                <option value="restaurant"> Restaurant & Food</option>
                <option value="real_estate"> Real Estate</option>
                <option value="ecommerce"> E-commerce & D2C</option>
                <option value="general"> General Business</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Owner Name</label>
              <input
                value={formOwner}
                onChange={(e) => setFormOwner(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 outline-none"
                placeholder="Your name"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Phone Number</label>
              <input
                value={formPhone}
                onChange={(e) => setFormPhone(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 outline-none"
                placeholder="+91 98765 43210"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Email</label>
              <input
                value={formEmail}
                onChange={(e) => setFormEmail(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 outline-none"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="text-sm text-gray-400 block mb-1">Agent Language</label>
              <select
                value={formLanguage}
                onChange={(e) => setFormLanguage(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-cyan-500 outline-none"
              >
                <option value="hi">Hindi + English</option>
                <option value="en">English Only</option>
                <option value="te">Telugu + English</option>
                <option value="ta">Tamil + English</option>
              </select>
            </div>

            <button
              onClick={registerBusiness}
              disabled={loading || !formName || !formOwner || !formPhone}
              className="w-full bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-700 text-black font-semibold py-3 rounded-lg text-sm mt-4 transition"
            >
              {loading ? "Registering..." : "Register & Get AI Agent"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ===== BUSINESS DASHBOARD =====
  if (page === "dashboard" && selectedBiz) {
    return (
      <div className="min-h-screen bg-gray-950 text-white">
        <header className="border-b border-gray-800 px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-cyan-400">VoiceAI India</h1>
            <p className="text-xs text-gray-500">{selectedBiz.name} · {selectedBiz.industry}</p>
          </div>
          <button onClick={() => setPage("home")} className="text-gray-400 text-sm hover:text-white">
            ← All Businesses
          </button>
        </header>

        <div className="max-w-5xl mx-auto px-6 py-8">
          {/* Business Header */}
          <div className="flex items-center gap-4 mb-8">
            <span className="text-4xl">{industryIcons[selectedBiz.industry] || ""}</span>
            <div>
              <h2 className="text-2xl font-bold">{selectedBiz.name}</h2>
              <p className="text-gray-500 text-sm">{selectedBiz.industry} · {selectedBiz.plan} plan · ID: {selectedBiz.id}</p>
            </div>
          </div>

          {/* Analytics Cards */}
          {analytics && (
            <>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Call Analytics</h3>
              <div className="grid grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Total Calls</p>
                  <p className="text-2xl font-bold text-white">{analytics.total_calls}</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Answered</p>
                  <p className="text-2xl font-bold text-green-400">{analytics.calls_answered}</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Answer Rate</p>
                  <p className="text-2xl font-bold text-cyan-400">{analytics.answer_rate}</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Minutes Used</p>
                  <p className="text-2xl font-bold text-white">
                    {analytics.total_minutes_used}/{analytics.minutes_limit}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Avg Duration</p>
                  <p className="text-xl font-bold text-white">{analytics.avg_duration_seconds}s</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Hot Leads</p>
                  <p className="text-xl font-bold text-amber-400">{analytics.hot_leads}</p>
                </div>
                <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-xs">Opted Out</p>
                  <p className="text-xl font-bold text-red-400">{analytics.calls_opted_out}</p>
                </div>
              </div>
            </>
          )}

          {/* Quick Actions */}
          <h3 className="text-lg font-semibold mb-4 text-gray-300">Quick Actions</h3>
          <div className="grid grid-cols-2 gap-3">
            <a
              href="https://agents-playground.livekit.io"
              target="_blank"
              className="bg-gray-900 rounded-xl p-4 border border-gray-800 hover:border-cyan-500 cursor-pointer transition text-center"
            >
              <p className="font-semibold text-cyan-400">Test Your Agent</p>
              <p className="text-xs text-gray-500 mt-1">Open LiveKit Playground</p>
            </a>
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 text-center">
              <p className="font-semibold text-gray-400">Connect Phone</p>
              <p className="text-xs text-gray-500 mt-1">Coming in Session 4</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}