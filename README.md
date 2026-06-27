# FlySync ✈️

FlySync is an AI-powered agentic travel platform that dynamically searches for flights and hotels, analyzes pricing, and provides tailored travel recommendations using the Gemini API.

## Features
- **Agentic Workflow**: Uses Gemini to orchestrate travel planning.
- **Flight & Hotel Search**: Generates tailored flight and hotel options based on user preferences.
- **Next.js Frontend**: Fast and responsive user interface.
- **FastAPI Backend**: Robust python backend for handling complex agentic workflows.

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.9+)
- A Gemini API Key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hatim283/flysync.git
   cd flysync
   ```

2. **Backend Setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variable
   export GEMINI_API_KEY="your_api_key_here"
   
   # Run the FastAPI server
   uvicorn backend.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Deployment on Vercel
1. Connect this repository to your Vercel account.
2. Because this is a monorepo (frontend and backend in separate folders), you may need to configure the **Root Directory** in Vercel settings to `frontend` (or keep it at root and ensure your `vercel.json` is correctly pointing to the frontend build).
3. Ensure you add `GEMINI_API_KEY` to your Vercel Project Environment Variables.

## License
This project is licensed under the MIT License.
