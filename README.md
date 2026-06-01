Richard Feynman Digital Twin
AIMS DTU Summer Project 2026 Submission
An advanced, production-grade cognitive AI agent that emulates Richard Feynman, mirroring not just his academic knowledge, but his distinct reasoning patterns, famous teaching pedagogy, and conversational mannerisms[cite: 1]. Moving beyond generic chat interfaces, this system pairs a high-precision Retrieval-Augmented Generation (RAG) architecture with multi-tiered memory loops and custom hardware audio features[cite: 1].

🌌 System Architecture
The application is engineered as a decoupled monorepo containing a high-throughput FastAPI asynchronous backend and a responsive Next.js App Router client dashboard.

Plaintext
                  ┌────────────────────────────────────────────────────────┐
                  │               Next.js Client Dashboard                 │
                  └───────────────┬────────────────────────▲───────────────┘
                                  │                        │
                    HTTP REST /   │                        │ Server-Sent Events
               Memory Operations  │                        │ (SSE Token Stream)
                                  ▼                        │
                  ┌────────────────────────────────────────┴───────────────┐
                  │               FastAPI Routing Gateway                  │
                  └───────────────┬────────────────────────▲───────────────┘
                                  │                        │
       Vector Match / SQL Queries │                        │ Embedded Context /
                                  ▼                        │ Extracted Insights
                  ┌────────────────────────────────────────┴───────────────┐
                  │     Cloud Neon PostgreSQL (pgvector) + SQLAlchemy      │
                  └───────────────────────────────┬────────────────────────┘
                                                  │
                                                  │ SDK Inferences
                                                  ▼
                  ┌────────────────────────────────────────────────────────┐
                  │             Gemini 2.5 Flash Core Engine               │
                  └────────────────────────────────────────────────────────┘
🛠️ Core Pillars & Implementation Approach
1. The Persona & Reasoning Engine
The Method: Guided by structural system prompts running on Gemini 2.5 Flash, the agent uses the iconic Feynman Technique[cite: 1]. It handles complex topics by breaking them into intuitive analogies, avoiding jargon, and building concepts from the ground up[cite: 1].

Timeline Awareness: The agent maintains a stable temporal anchor, accurately positioning its answers relative to his 1965 Nobel Prize win, historical interactions, and contemporaries[cite: 1].

2. The Vector RAG Pipeline
Data Ingestion: Raw historical lecture transcripts, autobiographical records ("Surely You're Joking, Mr. Feynman!"), scientific papers, and physics documentation are processed via pypdf chunking filters.

Vector Mechanics: Structural text chunks are converted to multi-dimensional embeddings and indexed inside Cloud Neon PostgreSQL leveraging the pgvector extension, enabling semantic similarity matching over production data scales.

3. Multi-Tiered Memory Infrastructure
Short-Term Session Memory: Leverages Server-Sent Events (SSE) to manage live multi-turn conversations, maintaining tracking indices without state loss[cite: 1].

Long-Term Memory Synthesis: As conversations progress, an asynchronous background routine evaluates the text, extracts key user profiles, physics concepts, or chronological timeline anchors, and pushes them into an operational long-term database state[cite: 1].

🌟 Bonus Features Implemented
Voice Interaction System: Integrates responsive text-to-speech engine layers (gTTS), enabling users to hear conceptual answers spoken back using localized audio playback parameters[cite: 1].

Memory Visualization Dashboard: A dedicated UI section displaying real-time data from Neon PostgreSQL. It reveals what the agent has discovered about you, classified by category (e.g., User Profile, Physics Concept, Timeline Anchor) alongside importance scores[cite: 1].

📂 Repository Structure
Plaintext
feynman-digital-twin/
├── backend/                  # Asynchronous FastAPI Engine
│   ├── app/
│   │   ├── main.py           # API Gateway & Lifecycle Initialization
│   │   ├── feynman_agent.py  # Prompt Architecture & Gemini SDK Loops
│   │   ├── database.py       # SQLAlchemy ORM Engine Configurations
│   │   └── models.py         # Schema Declarations for Vectors & Memories
│   ├── requirements.txt      # Production Python Dependency Mapping
│   └── README.md
└── frontend/                 # Next.js Production Client Dashboard
    ├── app/
    │   ├── page.js           # Lab Dashboard Interface View
    │   └── layout.js         # Tailwind Application Container global
    ├── hooks/
    │   └── useFeynmanStream.js # SSE Audio/Text Stream Event Consuming Hook
    ├── package.json          # Node Core System Dependency Mapping
    └── tailwind.config.js    # Modern Visual Theme Parameters
🚀 Step-by-Step Installation & Local Execution
Prerequisites
Python 3.11 installed locally.

Node.js (v18 or v20+) installed locally.

A Neon PostgreSQL database instance with pgvector enabled.

A Google Gemini API Key.

1. Backend Setup
Navigate into the backend folder, initialize a virtual environment, and install dependencies:

Bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
Create a .env file inside the backend/ directory:

Code snippet
DATABASE_URL=postgresql://<user>:<password>@<neon-host>/feynman_db?sslmode=require
GEMINI_API_KEY=your_google_gemini_api_key_here
Launch the local development server:

Bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
2. Frontend Setup
Open a new terminal window, navigate into the frontend folder, and install your packages:

Bash
cd frontend
npm install
Create a .env.local file inside the frontend/ directory:

Code snippet
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
Boot the Next.js local server:

Bash
npm run dev
Open your browser to http://localhost:3000 to interact with the platform locally.

📋 Sample Scenarios & Verification Tests
Here are test cases that showcase persona consistency, RAG grounding, and memory recall[cite: 1]:

Test Case 1: Complex Concept Simplification (The Feynman Pedagogy)
User Input: "Can you explain quantum electrodynamics without using heavy math equations?"

Feynman Twin: "Think of it like this. Light wants to go from point A to point B, and you’d think it takes a straight line. But quantum mechanics tells us it takes every possible path at once! It sniffs out all paths..."[cite: 1]

Verification: Verifies that the agent avoids generic textbook boilerplate and instead uses physical analogies[cite: 1].

Test Case 2: Timeline Anchoring & Historic Accuracy
User Input: "How did you feel when you received your Nobel Prize in 1965?"

Feynman Twin: "To be honest with you, I didn't care much for the honors. The prize is the pleasure of finding things out! I got woken up at 3:30 in the morning by some reporter, and I thought, 'I could have just skipped all this fuss'..."[cite: 1]

Verification: Confirms the agent's timeline awareness and alignment with his historical perspective on academic accolades[cite: 1].

Test Case 3: Cross-Session Long-Term Memory Synthesis
Turn 1: "My name is Vaatsalya, and I'm designing a high-speed VLSI circuit architecture."

Turn 2 (Several turns later): "What sort of advice do you have for my current research project?"

Feynman Twin: "Well, Vaatsalya, when you're looking at those dense VLSI architectures, the first principle is not to fool yourself. You have to trace those signals through your components just like tracking particles..."

Verification: Confirm that your name and background appear instantly inside the Memory Visualization Dashboard matrix, demonstrating long-term retrieval across multi-turn conversations[cite: 1].

🚀 Production Deployment Roadmap
The system is configured for cloud hosting using this decoupled deployment pattern:

Database Platform: Hosted on Neon Serverless Postgres to support high-performance vector calculations using pgvector.

Backend Engine Gateway: Deployed via Render Web Services using a Python 3.11 runtime container, mapping directly to environmental secret variables.

User Experience Frontend: Deployed on Vercel with a optimized build cache. It interfaces directly with the Render API gateway URL via the NEXT_PUBLIC_API_URL environment variable configuration.

🎓 Acknowledgments
Developed for the AIMS DTU Summer Project 2026[cite: 1]. Special thanks to the ACM-DTU community for collaboration guidelines. “What I cannot create, I do not understand.”
