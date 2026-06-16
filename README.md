# Brand_Forge-AI (OriginMint AI)

**Transform Your Startup Idea Into A Complete Brand Identity** using AI-powered multi-agent collaboration.

OriginMint AI is an intelligent branding platform that uses a sequential workflow of specialized AI agents to gather insights about your startup and generate a comprehensive brand identity including name, mission, voice, visual design, colors, typography, and logo prompts.


## Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Architecture](#-project-architecture)
- [User Flow](#-user-flow)
- [Component Structure](#-component-structure)
- [Technology Stack](#-technology-stack)
- [API Integration](#-api-integration)
- [Installation & Setup](#-installation--setup)
- [Environment Variables](#-environment-variables)
- [Running the Project](#-running-the-project)
- [Project Structure](#-project-structure)
- [Features Deep Dive](#-features-deep-dive)
- [Demo Mode](#-demo-mode)
- [Troubleshooting](#-troubleshooting)

---

## Features

- Multi-Agent Workflow: 4 specialized AI agents work sequentially to gather insights
  - Discovery Agent: Analyzes target audience and market research
  - Strategy Agent: Defines brand voice, positioning, and core messages
  - Visual Agent: Generates color palettes, typography, and design direction
  - Validator Agent: Ensures brand consistency and alignment

-  Real-time Conversation: Interactive chat-like interface for agent-user dialogue
-  Visual Progress Tracking: Timeline showing which agent is currently active
-  Complete Brand Output: 6 comprehensive cards displaying:
  - Brand Overview (name, mission, target audience)
  - Strategy Insights (voice, positioning, key messages)
  - Color Palette (with hex codes and usage rules)
  - Typography Guide (fonts, scales, and application)
  - Logo AI Prompt (ready to feed into image generators)
  - Validation Report (consistency score and audit)

- **Brand History**: Save and reload previous brands from localStorage
- **Export to PDF**: Download complete brand guidelines as PDF
- **Dark/Light Theme**: Toggle between dark and light modes
- **Demo Mode**: Client-side simulation when backend is unavailable
- **Fully Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Suggested Examples**: Pre-loaded startup ideas for quick testing

---

## Quick Start

```bash
# 1. Navigate to client folder
cd client

# 2. Install dependencies
npm install

# 3. Create .env.local file with backend URL
echo "VITE_API_BASE_URL=http://localhost:5000" > .env.local

# 4. Start development server
npm run dev

# 5. Open browser and visit
http://localhost:5173
```

**Note**: Backend server should be running on `http://localhost:5000` for full functionality. Use Demo Mode if backend is unavailable.

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│              BRANDFORGE AI (Frontend)                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐          ┌──────────────┐             │
│  │   Header     │          │    Hero      │             │
│  │ (Nav, Logo)  │          │ (Intro + 4   │             │
│  │              │          │  Agent Info) │             │
│  └──────────────┘          └──────────────┘             │
│         ▲                          ▲                      │
│         │                          │                      │
│  ┌──────────────────────────────────────────┐            │
│  │            Home.jsx (Orchestrator)       │            │
│  │  Manages state, API calls, workflow flow │            │
│  └──────────────────────────────────────────┘            │
│         ▲                          ▲                      │
│         │                          │                      │
│  ┌──────────────┐     ┌────────────────────┐             │
│  │ IdeaInput    │     │ AgentTimeline      │             │
│  │ (Textarea +  │     │ (Progress tracker) │             │
│  │  Suggestions)│     │                    │             │
│  └──────────────┘     └────────────────────┘             │
│         ▲                          ▲                      │
│         │                          │                      │
│  ┌──────────────────────────────────────────┐            │
│  │      ConversationPanel (Chat UI)         │            │
│  │  - Display agent questions                │            │
│  │  - User input + send button               │            │
│  │  - Message history                        │            │
│  └──────────────────────────────────────────┘            │
│         ▲                          ▲                      │
│         │                          │                      │
│  ┌──────────────────────────────────────────┐            │
│  │      Result Cards (When Complete)        │            │
│  │  - BrandOverviewCard                     │            │
│  │  - StrategyCard                          │            │
│  │  - ColorPaletteCard                      │            │
│  │  - TypographyCard                        │            │
│  │  - LogoPromptCard                        │            │
│  │  - ValidatorCard                         │            │
│  └──────────────────────────────────────────┘            │
│         ▲                          ▲                      │
│         │                          │                      │
│  ┌──────────────────────────────────────────┐            │
│  │        API Service Layer (api.js)        │            │
│  │  - getBackendHealth()                    │            │
│  │  - getAgents()                           │            │
│  │  - generateBrand()                       │            │
│  └──────────────────────────────────────────┘            │
│         ▲                          ▲                      │
└─────────┼──────────────────────────┼──────────────────────┘
          │                          │
          └──────────────┬───────────┘
                         │
                  ┌──────▼──────┐
                  │   Backend   │
                  │  API Server │
                  │  :5000      │
                  └─────────────┘
```

---

## User Flow

### **Phase 1️: Initialization**

```
User Enters Startup Idea
         ↓
   [IdeaInput Component]
         ↓
   Clicks "Generate Brand"
         ↓
   handleStartWorkflow() → API Call
   generateBrand(idea, {}, "")
         ↓
   API Response with Discovery Agent Question
         ↓
   Question Displayed in ConversationPanel
```

### **Phase 2️: Multi-Agent Dialogue Loop** (Repeats 4 times)

```
Current Agent Asks Question
         ↓
   [ConversationPanel Shows Question]
         ↓
   User Types Answer & Submits
         ↓
   handleSendAnswer() triggered
         ↓
   Answer Saved to `answers` state
         ↓
   API Call with Accumulated Answers
   generateBrand(idea, answers, currentAgent)
         ↓
   Next Agent Activated
         ↓
   AgentTimeline Updates Progress
         ↓
   New Question Displayed
         ↓
   Loop Again (or Complete)
```

### **Phase 3️: Completion & Display**

```
Validator Agent Completes
         ↓
   currentAgent = "completed"
   brandData populated
         ↓
   Render 6 Result Cards:
   - BrandOverviewCard
   - StrategyCard
   - ColorPaletteCard
   - TypographyCard
   - LogoPromptCard
   - ValidatorCard
         ↓
   Show Action Buttons:
   - Download PDF
   - Share Brand
   - New Brand
```

### **Agent Sequence**

| Step | Agent | Focus | Sample Question |
|------|-------|-------|-----------------|
| 1 | **Discovery** | Target Audience & Market Research | "Who is your primary target audience?" |
| 2 | **Strategy** | Brand Voice & Positioning | "What brand personality should this represent: premium, friendly, innovative, or playful?" |
| 3 | **Visual** | Design Direction & Aesthetics | "What design style do you prefer: modern, futuristic, minimalist, or luxury?" |
| 4 | **Validator** | Consistency & Alignment Check | Validates all inputs and ensures brand coherence |

---

## Component Structure

### **Core Components**

#### **Home.jsx** (Orchestrator)
Central state management and workflow control.

**Key State Variables:**
```javascript
const [idea, setIdea] = useState("");              // User's startup idea
const [currentAgent, setCurrentAgent] = useState(""); // Active agent
const [question, setQuestion] = useState("");      // Agent's current question
const [agentHistory, setAgentHistory] = useState([]); // Chat message log
const [answers, setAnswers] = useState({});        // Accumulated answers
const [brandData, setBrandData] = useState(null);  // Final brand output
const [loading, setLoading] = useState(false);     // API loading state
const [demoMode, setDemoMode] = useState(false);   // Demo mode toggle
const [darkMode, setDarkMode] = useState(true);    // Theme toggle
const [recentSearches, setRecentSearches] = useState([]); // History
```

**Key Methods:**
- `handleStartWorkflow()`: Initiates agent workflow with startup idea
- `handleSendAnswer()`: Submits user answer, calls next agent
- `saveBrandToHistory()`: Saves completed brand to localStorage
- `handleSelectHistoryBrand()`: Loads previous brand from history
- `downloadBrandPDF()`: Exports complete brand as PDF

---

#### **Header.jsx**
Navigation, branding, and controls.

**Features:**
- Logo + App name with pulsing animation
- Recent searches dropdown (loads from history)
- Demo mode toggle switch
- Dark/Light mode toggle
- Sticky positioning at top

---

#### **Hero.jsx**
Landing section with agent showcase.

**Displays:**
- Main headline: "OriginMint AI"
- Subheadline: "Turn Your Startup Idea Into A Complete Brand Identity"
- 4 Agent cards with icons and descriptions
- Animated gradient backgrounds

---

#### **IdeaInput.jsx**
Textarea input with suggestions.

**Features:**
- Large textarea for startup idea description
- 3 pre-loaded suggestion buttons (clickable examples)
- Keyboard shortcut: Enter to submit (Shift+Enter for new line)
- Loading state management
- Responsive design

---

#### **AgentTimeline.jsx**
Visual progress tracker.

**Shows:**
- 4 agent steps in sequence
- Current active agent (highlighted)
- Completed agents (with checkmark)
- Thinking text for current agent
- Agent roles and descriptions

**Status Logic:**
- `completed`: All agents done
- `current`: Agent is asking question
- `pending`: Agent not yet reached
- `done`: Agent completed

---

#### **ConversationPanel.jsx**
Chat-like interface for agent-user interaction.

**Features:**
- Message history with timestamps
- Agent avatars (colored labels: D, S, V, OK)
- User message styling
- Agent message styling
- Auto-scroll to latest message
- User input form with Send button
- Reset step button (go back to previous agent)
- Loading indicator

---

#### **Result Cards** (Display When Generation Complete)

**BrandOverviewCard.jsx**
```
├── Brand Identity Name
├── Core Mission Statement
└── Target Audience Badge
```

**StrategyCard.jsx**
```
├── Brand Voice (personality traits)
├── Key Messages (3 core messages)
└── Positioning Statement
```

**ColorPaletteCard.jsx**
```
├── Primary Color + Hex Code
├── Secondary Color + Hex Code
├── Accent Color + Hex Code
└── Color Usage Guide
```

**TypographyCard.jsx**
```
├── Heading Font Family
├── Body Font Family
├── Font Scale
└── Usage Examples
```

**LogoPromptCard.jsx**
```
├── AI-generated Logo Prompt
├── Design Direction
└── Copy-to-clipboard Button
```

**ValidatorCard.jsx**
```
├── Consistency Score (0-100)
├── Validation Status (PASS/WARNING/FAIL)
├── Validation Report
└── Alignment Rules
```

---

#### **LoadingScreen.jsx**
Animated loader shown during API calls.

---

##  Technology Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React | 19.2.6 | UI library |
| **Build Tool** | Vite | 8.0.12 | Fast dev server & bundler |
| **Styling** | TailwindCSS | 4.3.1 | Utility-first CSS |
| **Icons** | lucide-react | 1.18.0 | UI icons |
| **Icons** | react-icons | 5.6.0 | Alternative icon set |
| **HTTP Client** | Axios | 1.17.0 | API requests |
| **Animations** | framer-motion | 12.40.0 | Smooth transitions |
| **PDF Export** | jsPDF | 4.2.1 | PDF generation |
| **HTML to Image** | html2canvas | 1.4.1 | Screenshot for PDF |
| **Code Quality** | ESLint | 10.3.0 | Linting |
| **CSS Processing** | PostCSS | 8.5.15 | CSS transformations |
| **Autoprefixer** | autoprefixer | 10.5.0 | Browser prefixes |

---

##  API Integration

### **Base Configuration** (services/api.js)

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
const GENERATE_BRAND_URL = import.meta.env.VITE_API_URL || 
  `${API_BASE_URL.replace(/\/$/, "")}/api/generate-brand`;
```

### **API Endpoints**

#### **1. Health Check** (Optional)
```
GET /api/health

Response:
{ status: "ok", message: "Backend is running" }
```

#### **2. Get Agents List** (Optional)
```
GET /api/agents

Response:
{ 
  agents: ["Discovery", "Strategy", "Visual", "Validator"]
}
```

#### **3. Generate Brand (Main Workflow)**
```
POST /api/generate-brand

Request Body:
{
  idea: "AI-powered fitness coach for busy professionals",
  answers: {
    Discovery: "Corporate professionals aged 25-45",
    Strategy: "Professional, motivating",
    Visual: "Modern, minimalist"
  },
  currentAgent: "Strategy"  // Which agent just completed
}

Response (When needs_input):
{
  status: "needs_input",
  currentAgent: "Strategy",
  question: "What brand voice should this represent?"
}

Response (When completed):
{
  status: "completed",
  brandData: {
    brandName: "FitFlow Pro",
    mission: "Empower busy professionals with AI-powered fitness coaching",
    audience: "Corporate professionals aged 25-45",
    voice: ["professional", "motivating", "supportive"],
    keyMessages: [
      "Fitness made simple for busy schedules",
      "AI coach, always available",
      "Your success is our mission"
    ],
    positioning: "The AI fitness coach for corporate professionals",
    colors: {
      primary: "#FF6B6B",
      secondary: "#4ECDC4",
      accent: "#FFE66D"
    },
    typography: {
      headings: "Jakarta",
      body: "Inter",
      fontScale: "12px / 16px / 20px / 24px / 32px"
    },
    logoPrompt: "Modern, clean logo of an AI-powered fitness coach...",
    validationReport: "All brand elements are consistent and aligned.",
    consistencyScore: 95
  }
}

Response (On Error):
{
  status: "error",
  error: "Backend error message"
}
```

### **Error Handling Strategy**

1. **Network Failure**: Automatically falls back to `simulateAgentResponse()`
2. **Backend Error**: Catches error and triggers demo mode fallback
3. **No Response**: Displays user-friendly error message
4. **Timeout**: 4-10 second timeouts with error messaging

---

##  Installation & Setup

### **Prerequisites**
- Node.js 16+ 
- npm or yarn
- Backend server running on port 5000 (optional - works in demo mode)

### **Step-by-Step Installation**

```bash
# 1. Clone or navigate to project
cd Brand_Forge-AI/client

# 2. Install dependencies
npm install

# 3. Create environment file
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:5000
VITE_API_URL=http://localhost:5000/api/generate-brand
EOF

# 4. Verify installation
npm run lint
```

---

##  Environment Variables

Create a `.env.local` file in the `client/` directory:

```bash
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:5000
VITE_API_URL=http://localhost:5000/api/generate-brand
```

**Notes:**
- If `VITE_API_BASE_URL` is not set, defaults to `http://localhost:5000`
- If `VITE_API_URL` is not set, constructs from `VITE_API_BASE_URL`
- For production, update URLs to match your deployed backend

---

##  Running the Project

### **Development Mode**
```bash
# Start Vite dev server (hot reload enabled)
npm run dev

# Open browser
http://localhost:5173
```

### **Production Build**
```bash
# Create optimized production build
npm run build

# Output: dist/ folder with minified assets
```

### **Preview Production Build**
```bash
# Serve production build locally
npm run preview
```

### **Linting**
```bash
# Check code quality
npm run lint

# Fix linting issues (auto-fixable ones)
npm run lint -- --fix
```

---

##  Project Structure

```
client/
├── index.html                      # HTML entry point
├── package.json                    # Dependencies & scripts
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # TailwindCSS config
├── postcss.config.js               # PostCSS config
├── eslint.config.js                # ESLint rules
│
├── src/
│   ├── main.jsx                    # React entry (renders App to #root)
│   ├── App.jsx                     # App wrapper (renders Home)
│   ├── index.css                   # Global CSS
│   ├── App.css                     # App-specific CSS
│   │
│   ├── pages/
│   │   └── Home.jsx                # Main orchestrator component
│   │
│   ├── components/
│   │   ├── Header.jsx              # Navigation & controls
│   │   ├── Hero.jsx                # Landing section
│   │   ├── IdeaInput.jsx           # Startup idea textarea
│   │   ├── AgentTimeline.jsx       # Progress tracker
│   │   ├── ConversationPanel.jsx   # Chat interface
│   │   ├── LoadingScreen.jsx       # Spinner/loader
│   │   ├── BrandOverviewCard.jsx   # Result: brand name & mission
│   │   ├── StrategyCard.jsx        # Result: voice & positioning
│   │   ├── ColorPaletteCard.jsx    # Result: colors
│   │   ├── TypographyCard.jsx      # Result: fonts
│   │   ├── LogoPromptCard.jsx      # Result: logo prompt
│   │   └── ValidatorCard.jsx       # Result: consistency report
│   │
│   ├── services/
│   │   └── api.js                  # API service layer
│   │
│   └── assets/                     # Images, fonts, static files
│
└── public/                         # Static public assets
```

---

##  Features Deep Dive

### **1. Multi-Agent Workflow**

The platform orchestrates 4 AI agents in sequence:

```javascript
// Agent flow in api.js
generateBrand(idea, answers, currentAgent, demoMode)
  ├─ Phase 1: Send idea alone
  │  └─ Discovery Agent activated
  ├─ Phase 2: Send idea + Discovery answer
  │  └─ Strategy Agent activated
  ├─ Phase 3: Send idea + all answers so far
  │  └─ Visual Agent activated
  └─ Phase 4: Send all data
     └─ Validator Agent reviews & completes
```

### **2. State Management Pattern**

Home.jsx uses React hooks for state:

```javascript
// Input Phase
const [idea, setIdea] = useState("");
const [question, setQuestion] = useState("");

// Workflow Phase
const [currentAgent, setCurrentAgent] = useState("");
const [agentHistory, setAgentHistory] = useState([]);
const [answers, setAnswers] = useState({});

// Output Phase
const [brandData, setBrandData] = useState(null);
const [loading, setLoading] = useState(false);

// Settings Phase
const [demoMode, setDarkMode] = useState(false);
const [darkMode, setDarkMode] = useState(true);
const [recentSearches, setRecentSearches] = useState([]);
```

### **3. Conversation History**

Messages are logged in `agentHistory` array:

```javascript
[
  { role: "user", text: "AI-powered fitness coach..." },
  { role: "agent", agent: "Discovery", text: "Who is your target audience?" },
  { role: "user", text: "Corporate professionals..." },
  { role: "agent", agent: "Strategy", text: "What brand voice..." },
  // ... more messages
]
```

### **4. Brand Persistence**

Brands are saved to localStorage:

```javascript
// Stored key: "originMint_brands"
// Format: Array of brand objects
[
  {
    brandName: "FitFlow Pro",
    idea: "AI fitness coach...",
    audience: "Corporate professionals",
    voice: ["professional", "motivating"],
    logoPrompt: "...",
    answers: { Discovery: "...", Strategy: "...", ... },
    // ... other properties
  },
  // ... more brands (max 10)
]
```

### **5. PDF Export**

Combines `html2canvas` + `jsPDF`:

```javascript
// Capture all visible cards
const canvas = await html2canvas(element);
const imgData = canvas.toDataURL('image/png');

// Create PDF with image
const pdf = new jsPDF();
pdf.addImage(imgData, 'PNG', x, y, width, height);
pdf.save('brand-identity.pdf');
```

### **6. Demo Mode Fallback**

When backend is unavailable:

```javascript
// generateBrand() catches error and calls
simulateAgentResponse(idea, answers, currentAgent)
// Returns realistic mock data without backend
```

---

##  Demo Mode

Demo Mode provides client-side agent simulation when the backend is unavailable.

### **Enable Demo Mode**
Click the **"Demo Mode"** toggle in the header.

### **What Happens**
- All API calls are intercepted
- Client-side `simulateAgentResponse()` generates realistic brand data
- No backend required - works offline
- Useful for testing, presentations, or development

### **Benefits**
 Test frontend without backend running  
 Instant responses (no network lag)  
 Consistent test data for reproducible testing  
 Perfect for presentations and demos  

---

##  Troubleshooting

### **Issue: "Failed to initialize agent workflow"**
**Solution:**
1. Check if backend server is running on `http://localhost:5000`
2. Verify `VITE_API_BASE_URL` in `.env.local`
3. Enable Demo Mode to test frontend without backend

### **Issue: API requests timing out**
**Solution:**
1. Ensure backend is responding
2. Check network connectivity
3. Increase timeout in `api.js` if needed (currently 10 seconds)
4. Switch to Demo Mode temporarily

### **Issue: Styles not loading (missing colors)**
**Solution:**
1. Run `npm run build` to generate CSS
2. Clear browser cache (Ctrl+Shift+Delete)
3. Check TailwindCSS config includes all color definitions

### **Issue: localStorage not persisting brands**
**Solution:**
1. Check browser's storage is not full
2. Ensure localStorage is enabled
3. Check browser privacy settings don't block storage

### **Issue: PDF export is blank or cut off**
**Solution:**
1. Make sure all result cards are rendered
2. Wait for all images to load
3. Try exporting from different browser
4. Check if component contains very large images

### **Issue: Dark mode not applying**
**Solution:**
1. Click dark mode toggle in header to reset
2. Check `darkMode` class is added to `<html>` element
3. Clear browser cache and reload

---

##  Usage Example

### **Step 1: Enter Your Startup Idea**
```
"An AI platform that teaches coding through gamification 
for beginners aged 16-25"
```

### **Step 2: Answer Discovery Agent**
```
Discovery Agent: "Who is your primary target audience?"
You: "Teenagers and young adults interested in learning to code"
```

### **Step 3: Answer Strategy Agent**
```
Strategy Agent: "What brand voice should represent this?"
You: "Friendly, innovative, and encouraging"
```

### **Step 4: Answer Visual Agent**
```
Visual Agent: "What design style do you prefer?"
You: "Modern and vibrant with playful elements"
```

### **Step 5: Validator Agent Completes**
```
Validator Agent: "Reviewing brand consistency..."
 Complete! All elements aligned.
```

### **Step 6: View & Export Results**
- See generated brand identity cards
- Download as PDF
- Share with team
- Save to history for later

---

##  Workflow Loop Summary

```
Input Startup Idea
    ↓
Discovery Agent (Target Audience)
    ↓
Strategy Agent (Voice & Positioning)
    ↓
Visual Agent (Design & Colors)
    ↓
Validator Agent (Consistency Check)
    ↓
Display 6 Result Cards
    ↓
Export / Share / Save to History
```

---

##  Contributing

Contributions are welcome! Please follow these guidelines:

1. Create a feature branch (`git checkout -b feature/YourFeature`)
2. Commit changes (`git commit -m 'Add YourFeature'`)
3. Push to branch (`git push origin feature/YourFeature`)
4. Open a Pull Request

---

##  License

This project is proprietary. All rights reserved.

---

##  Support

For issues, questions, or feature requests, please open an issue in the repository.

---

##  Credits

Built with  using React, Vite, TailwindCSS, and AI-powered workflows.

**OriginMint AI** - *Turn Your Startup Idea Into A Complete Brand Identity*