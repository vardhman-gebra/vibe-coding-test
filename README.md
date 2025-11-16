# Vibe Coding

A full-stack application with FastAPI backend and React frontend.

## Project Structure

```
vibe-coding/
├── backend/          # FastAPI server
├── frontend/         # Vite + React + TypeScript
└── README.md         # This file
```

## Prerequisites

- **Python 3.8+** for backend
- **Node.js 18+** and **npm** for frontend

## Setup Instructions

### Backend Setup (FastAPI)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   # macOS/Linux
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

API documentation available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup (Vite + React + TypeScript)

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Development

### Running Both Servers Simultaneously

You can use two terminal windows:

**Terminal 1 (Backend):**

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 (Frontend):**

```bash
cd frontend
npm run dev
```

## Building for Production

### Backend

```bash
cd backend
# FastAPI applications are typically deployed using Docker or ASGI servers like Gunicorn
```

### Frontend

```bash
cd frontend
npm run build
# Output will be in the dist/ directory
```

## Tech Stack

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Frontend

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **ESLint** - Code linting

## License

MIT
