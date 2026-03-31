# 🇮🇳 VoiceAI India

**India-first Voice AI Agent Platform for SMEs**

An affordable, self-serve voice AI platform built specifically for Indian small businesses. SMEs pick an industry template, connect a phone number, and get a Hindi-speaking AI agent handling calls — fully TRAI-compliant, at ₹5,000-25,000/month.

> **The India SME Void:** 63M+ MSMEs in India have zero affordable options for AI calling. Global platforms price in USD, require technical setup, and ignore Indian telephony/compliance. Enterprise Indian players need ₹50K+ budgets. We fill this gap.

---

## 🚀 Features

### Voice AI Agent
- **Multilingual**: Hindi, English, Telugu, Tamil + natural Hinglish code-switching
- **Industry Templates**: Pre-built agents for clinics, restaurants, real estate, e-commerce
- **Smart Conversations**: Appointment booking, FAQ handling, lead qualification, order status
- **Powered by**: Google Gemini 2.5 Flash (LLM) + Deepgram (STT/TTS) + LiveKit (WebRTC)

### TRAI Compliance Engine
- **Calling Hours**: 10 AM - 7 PM IST enforcement with safety buffer
- **DND/NCPR**: Automatic Do Not Disturb registry checking before every call
- **AI Disclosure**: Mandatory bot identification at call start (Hindi + English)
- **Opt-Out**: Multi-language keyword detection (Hindi, English, Telugu, Tamil)
- **Number Series**: Automatic 140-series (promotional) vs 1600-series (service) routing
- **Audit Trail**: Every call logged with compliance metadata

### Self-Serve Dashboard
- **Business Registration**: Sign up → pick industry → get AI agent in 30 minutes
- **Call Analytics**: Total calls, answer rate, duration, leads, opt-outs
- **Industry Templates**: 5 pre-built templates with one-click activation
- **INR Billing**: Razorpay integration (planned)

### Backend API
- **12 REST endpoints** with Swagger documentation
- **Multi-tenant**: Each business gets isolated config, data, and agent
- **SQLite**: Zero-config database, auto-created on first run

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  Customer Touchpoints                            │
│  Phone (SIP) · WhatsApp · Web Widget · Mobile    │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  LiveKit Media Server (WebRTC)                   │
│  SIP Gateway · Rooms · Media Routing             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  Voice Agent (Python)                            │
│  STT (Deepgram) → LLM (Gemini) → TTS (Deepgram)│
│  + TRAI Compliance Engine                        │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  FastAPI Backend                                 │
│  Business API · Campaigns · Analytics · Logs     │
│  SQLite Database                                 │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│  Next.js Dashboard                               │
│  Registration · Agent Config · Analytics         │
└─────────────────────────────────────────────────┘
```

---

## 📦 Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| LLM (Brain) | Google Gemini 2.5 Flash | Free |
| STT (Speech→Text) | Deepgram Nova-3 | $200 free credit |
| TTS (Text→Speech) | Deepgram Aura | $200 free credit |
| Voice Transport | LiveKit Cloud | Free tier |
| Backend | FastAPI + SQLite | Free |
| Dashboard | Next.js + Tailwind | Free |
| Compliance | Custom Python engine | Free |
| Hosting | Railway + Vercel | Free tier |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Git

### 1. Clone and setup
```bash
git clone https://github.com/SivaShankargunti/voiceai-india.git
cd voiceai-india
```

### 2. Install Python dependencies
```bash
pip install uv
uv sync
```

### 3. Get free API keys
- **Google Gemini**: https://aistudio.google.com → Get API Key
- **Deepgram**: https://console.deepgram.com → Sign up ($200 free credit)
- **LiveKit**: https://cloud.livekit.io → New Project

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Start the backend
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 6. Start the voice agent
```bash
uv run python agent.py dev
```

### 7. Start the dashboard
```bash
cd dashboard
npm install
npm run dev
```

### 8. Test your agent
- Open https://agents-playground.livekit.io
- Connect to your project
- Say "Namaste!" 🎉

---

## 📁 Project Structure

```
voiceai-india/
├── agent.py                    # Voice AI agent (LiveKit + Gemini + Deepgram)
├── agent/
│   └── templates/              # Industry-specific agent templates
│       ├── clinic.py           # Healthcare / clinic receptionist
│       ├── restaurant.py       # Restaurant reservations & menu
│       ├── real_estate.py      # Property inquiries & site visits
│       ├── ecommerce.py        # Order status & returns
│       └── general.py          # General business assistant
├── compliance/
│   └── trai.py                 # TRAI compliance engine
├── backend/
│   ├── main.py                 # FastAPI server (12 endpoints)
│   ├── database.py             # SQLite database layer
│   └── voiceai.db              # Auto-created database
├── dashboard/                  # Next.js self-serve UI
│   └── app/page.tsx            # Main dashboard page
├── .env                        # API keys (not committed)
└── pyproject.toml              # Python dependencies
```

---

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/business/register` | Register a new SME business |
| GET | `/api/business/{id}` | Get business details |
| GET | `/api/businesses` | List all businesses |
| POST | `/api/business/{id}/contacts` | Add a contact |
| GET | `/api/business/{id}/contacts` | Get contacts |
| POST | `/api/business/{id}/campaigns` | Create a campaign |
| GET | `/api/business/{id}/campaigns` | Get campaigns |
| POST | `/api/compliance/check` | Pre-call TRAI compliance check |
| GET | `/api/compliance/calling-hours` | Check TRAI calling window |
| POST | `/api/compliance/opt-out/{phone}` | Process opt-out |
| POST | `/api/business/{id}/calls/log` | Log a call (audit) |
| GET | `/api/business/{id}/analytics` | Get call analytics |
| GET | `/api/templates` | List industry templates |

Full Swagger docs at: `http://localhost:8000/docs`

---

## 🎯 Market Opportunity

- **63M+ MSMEs** in India with zero affordable AI calling options
- India's conversational AI market: **$455M (2024) → $1.85B (2030)**
- Even **0.1% adoption = 63,000 paying customers**
- **10,000 SMEs × ₹15,000/mo = ₹150Cr ARR (~$18M)**

---

## 🛡️ Compliance

This platform is built with Indian telecom compliance as a core feature, not an afterthought:

- **TRAI TCCCPR**: Full compliance with Telecom Commercial Communications Customer Preference Regulations
- **DND/NCPR**: Automatic National Customer Preference Register checking
- **DPDPA Ready**: Architecture supports Digital Personal Data Protection Act requirements
- **DLT Ready**: Distributed Ledger Technology template registration support
- **Audit Trail**: Every call logged with timestamp, duration, outcome, consent status

---

## 🗺️ Roadmap

- [x] Voice AI agent (Hindi/English/Hinglish)
- [x] TRAI compliance engine
- [x] FastAPI backend with multi-tenant support
- [x] Industry templates (5 verticals)
- [x] Next.js self-serve dashboard
- [x] Call analytics
- [ ] SIP phone calling (Indian provider)
- [ ] WhatsApp Business API integration
- [ ] Razorpay billing integration
- [ ] Cloud deployment (Railway + Vercel)
- [ ] Mobile app SDK
- [ ] Advanced analytics with sentiment analysis

---

## 👨‍💻 Author

**Siva Shankar Gunti** — Building the future of voice AI for Indian businesses.

- GitHub: [@SivaShankargunti](https://github.com/SivaShankargunti)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.