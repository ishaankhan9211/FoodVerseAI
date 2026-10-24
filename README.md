# FoodVerse AI — Multimodal Food Intelligence Assistant

FoodVerse AI is a full-stack AI-powered food assistant that helps users discover recipes, analyze food images, estimate nutrition, and interact with an AI Chef. It uses React and Vite for the frontend, FastAPI for the backend, and Groq for AI-powered responses.

## Features

- **Discover Recipes:** Generate recipes from available ingredients and preferences such as cuisine, diet, preparation time, servings, budget, and spice level.
- **Ingredient Scanner:** Analyze JPG, PNG, or WEBP images to identify visible food and ingredients and suggest related recipes.
- **Nutrition Insights:** Get approximate nutrition estimates for a food and serving size.
- **AI Chef:** Ask questions about recipes, cooking techniques, ingredient substitutions, and reducing food waste.
- **REST API:** FastAPI endpoints for recipes, image analysis, nutrition, and chat.
- **Interactive API Documentation:** Explore and test endpoints through Swagger UI.

> Nutrition values, recipe costs, and image-based identifications are estimates. They are not medical advice or verified food-safety assessments.

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- Groq Python SDK

### AI
- Groq API for text generation
- A Groq vision-capable model for image analysis

## Project Structure

```text
FoodVerseAI/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── .env
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   └── src/
├── .gitignore
└── README.md
```

Additional files may exist in your project.

## Prerequisites

- Python 3.10 or later, compatible with your dependencies
- Node.js and npm
- A Groq account and API key
- Git for version control

Create a Groq API key at: https://console.groq.com/keys

## Installation and Setup

### 1. Clone the repository

If you are setting up the project on another computer:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FoodVerseAI
```

If you already have the project locally, open its folder in VS Code instead.

### 2. Configure the backend

Open Git Bash in VS Code and run:

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Create a file named `.env` inside the `backend` folder. Add your own Groq API key and configuration:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
GROQ_VISION_MODEL=qwen/qwen3.8-27b
FRONTEND_ORIGIN=http://localhost:5173
```

Replace the placeholder with your own API key. Check the currently available models at https://console.groq.com/docs/models if a model is unavailable to your account.

Start the backend from the `backend` directory:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The backend should run at:

- API: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger documentation: http://127.0.0.1:8000/docs

Keep this terminal open.

### 3. Configure and run the frontend

Open a **second terminal** in VS Code:

```bash
cd frontend
npm install
npm run dev
```

Open the URL displayed by Vite, usually:

http://localhost:5173

Keep both the frontend and backend running during local development.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Basic API information |
| GET | `/health` | Backend health and AI configuration |
| POST | `/api/recipes` | Generate recipe suggestions |
| POST | `/api/analyze-image` | Analyze a food or ingredient image |
| POST | `/api/nutrition` | Estimate nutrition information |
| POST | `/api/chat` | Chat with the AI Chef |

Visit http://127.0.0.1:8000/docs to inspect request schemas and test API endpoints.

## Troubleshooting

### Groq API key is not configured

- Confirm the file is named `backend/.env`.
- Check that `GROQ_API_KEY` contains your own valid key.
- Restart the backend after editing `.env`.

### Model unavailable or invalid

- Check the model identifier in the Groq models documentation.
- Update `GROQ_MODEL` or `GROQ_VISION_MODEL` in `backend/.env`.
- Restart the backend.

### Rate-limit or quota errors

Check your Groq account's limits and usage. Wait for the applicable limit to reset or use another model available to your account.

### Frontend cannot connect to backend

- Confirm the backend is running on port `8000`.
- Confirm the frontend is running on port `5173`.
- Check the `FRONTEND_ORIGIN` setting.
- Inspect the browser console and backend terminal for errors.

### `pip` is not recognized

Use Python to run pip:

```bash
python -m pip install -r requirements.txt
```

### Image scanning fails

Image analysis requires a vision-capable model. Confirm that the configured vision model is supported and available to your Groq account.

## Security

- Never commit API keys or other secrets.
- Keep the actual `.env` file out of GitHub.
- Commit `.env.example` only with blank values or placeholders.
- Exclude `.venv/`, `node_modules/`, and build output from version control.
- Revoke and replace any API key exposed in a screenshot or public repository.
- Keep API keys on the backend, not in frontend code.

## Development

The frontend and backend run as separate development servers. API usage depends on your Groq account's available models, quotas, and rate limits.

For production deployment, configure environment variables securely on your hosting provider and set the appropriate frontend origin.

## License

## Author

~ Ishaan Khan