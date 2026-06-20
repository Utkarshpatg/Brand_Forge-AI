# BrandForge AI FastAPI Backend

## Local client/server connection

The React client calls the FastAPI server at:

```txt
http://localhost:5000/api/generate-brand
```

Useful backend endpoints:

```txt
GET  /api/health
GET  /api/agents
POST /api/generate-brand
POST /api/generate
```

Run the backend:

```bash
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

Run the frontend in a second terminal:

```bash
cd client
npm run dev
```

To point the client at a deployed backend, set `VITE_API_URL` in the client environment.
