
import base64
import json
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
GROQ_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL", "qwen/qwen3.8-27b"
).strip()
FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN", "http://localhost:5173"
).strip()

app = FastAPI(title="FoodVerse AI API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list({
        FRONTEND_ORIGIN,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def groq_client():
    """Create the Groq API client."""
    if not GROQ_API_KEY:
        return None

    try:
        from groq import Groq
        return Groq(
            api_key=GROQ_API_KEY,
            timeout=90.0,
            max_retries=2,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not initialize Groq client: {str(exc)[:200]}",
        )


def ask_ai(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> str:
    """Generate a text answer or analyze an image using Groq."""
    client = groq_client()

    if client is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Groq AI is not configured. Add GROQ_API_KEY "
                "to backend/.env and restart the backend."
            ),
        )

    model = GROQ_VISION_MODEL if image_bytes else GROQ_MODEL

    try:
        if image_bytes:
            encoded = base64.b64encode(image_bytes).decode("utf-8")
            image_type = mime_type or "image/jpeg"

            user_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            f"data:{image_type};base64,{encoded}"
                        )
                    },
                },
            ]
        else:
            user_content = prompt

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are FoodVerse AI, a helpful food assistant. "
                        "Follow the user's requested output format. "
                        "When asked for JSON, return valid JSON without "
                        "Markdown fences. Nutrition and cost values are "
                        "estimates, not medical measurements."
                    ),
                },
                {"role": "user", "content": user_content},
            ],
            max_completion_tokens=4096,
        )

        answer = response.choices[0].message.content
        if not answer or not answer.strip():
            raise HTTPException(
                status_code=502,
                detail="Groq returned an empty response. Please try again.",
            )

        return answer.strip()

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Groq request failed: {str(exc)[:300]}",
        )


def extract_json(raw: str):
    """Parse a JSON object, including one wrapped in Markdown fences."""
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end < start:
        raise ValueError("No JSON object found in the model response")

    return json.loads(cleaned[start:end + 1])


class RecipeRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1, max_length=30)
    cuisine: str = "Any"
    meal_type: str = "Any"
    diet: str = "None"
    max_minutes: int = Field(default=45, ge=5, le=360)
    servings: int = Field(default=2, ge=1, le=20)
    budget_inr: Optional[float] = Field(default=None, ge=0)
    spice_level: str = "Medium"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[dict] = Field(default_factory=list)


class NutritionRequest(BaseModel):
    food: str = Field(min_length=1, max_length=500)
    quantity: str = "1 serving"


@app.get("/")
def root():
    return {
        "service": "FoodVerse AI API",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FoodVerse AI API",
        "ai_configured": bool(GROQ_API_KEY),
        "model": GROQ_MODEL,
        "vision_model": GROQ_VISION_MODEL,
    }


@app.post("/api/recipes")
def recipes(payload: RecipeRequest):
    if not GROQ_API_KEY:
        return {
            "mode": "demo",
            "notice": (
                "Sample response: configure GROQ_API_KEY in "
                "backend/.env to enable live AI recipes."
            ),
            "recipes": [
                {
                    "name": (
                        f"Quick {payload.cuisine if payload.cuisine != 'Any' else 'Everyday'} "
                        "Ingredient Bowl"
                    ),
                    "description": (
                        "A flexible sample recipe using your ingredients."
                    ),
                    "cuisine": payload.cuisine,
                    "meal_type": payload.meal_type,
                    "prep_minutes": 10,
                    "cook_minutes": min(20, payload.max_minutes),
                    "difficulty": "Easy",
                    "servings": payload.servings,
                    "diet": payload.diet,
                    "ingredients": [
                        {"item": x, "quantity": "as needed"}
                        for x in payload.ingredients
                    ],
                    "extra_ingredients": ["Oil", "Salt", "Pepper or spices"],
                    "steps": [
                        "Wash and prepare the ingredients.",
                        "Heat a pan and add a little oil if needed.",
                        "Cook the ingredients until tender and season.",
                        "Serve warm and adjust seasoning.",
                    ],
                    "substitutions": [
                        "Use similar vegetables or pulses you have available."
                    ],
                    "nutrition_estimate": {
                        "calories_kcal": 320,
                        "protein_g": 12,
                        "carbs_g": 42,
                        "fat_g": 11,
                    },
                    "estimated_cost_inr_per_serving": None,
                    "why_it_matches": (
                        "Uses your available ingredients and keeps preparation simple."
                    ),
                }
            ],
        }

    prompt = f"""You are FoodVerse AI, a careful recipe assistant.
Create exactly 3 practical recipe suggestions.

Return ONLY valid JSON using this structure:
{{"recipes":[{{"name":"string","description":"string","cuisine":"string","meal_type":"string","prep_minutes":10,"cook_minutes":20,"difficulty":"Easy|Medium|Hard","servings":2,"diet":"string","ingredients":[{{"item":"string","quantity":"string"}}],"extra_ingredients":["string"],"steps":["instruction text"],"substitutions":["string"],"nutrition_estimate":{{"calories_kcal":300,"protein_g":10,"carbs_g":40,"fat_g":10}},"estimated_cost_inr_per_serving":100,"why_it_matches":"string"}}]}}

Available ingredients: {payload.ingredients}
Cuisine: {payload.cuisine}
Meal type: {payload.meal_type}
Diet: {payload.diet}
Maximum total time: {payload.max_minutes} minutes
Servings: {payload.servings}
Budget per serving in INR: {payload.budget_inr}
Spice level: {payload.spice_level}

Prioritize the available ingredients and respect the requested diet.
Nutrition and costs are estimates. Do not claim a recipe is allergen-free.
Provide useful quantities and clear cooking instructions."""

    raw = ask_ai(prompt)

    try:
        parsed = extract_json(raw)
        return {"mode": "live", **parsed}
    except Exception:
        return {
            "mode": "live",
            "recipes_text": raw,
            "notice": (
                "The response was not valid structured JSON; "
                "showing the generated text instead."
            ),
        }


@app.post("/api/analyze-image")
async def analyze_image(image: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp"}

    if image.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG, PNG, or WEBP image.",
        )

    data = await image.read()

    if not data:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")

    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image must be smaller than 8 MB.",
        )

    prompt = """Analyze this food or ingredient image carefully.
Return concise JSON with these keys:
likely_identification, alternatives, visible_ingredients,
likely_preparation, serving_size_estimate,
nutrition_estimate (calories_kcal, protein_g, carbs_g, fat_g),
related_recipe_ideas, uncertainty.

Nutrition values are rough estimates. If uncertain, say so.
Do not claim to verify freshness, allergens, food safety, or hygiene
from the image. If the image shows raw ingredients, suggest dishes."""

    raw = ask_ai(prompt, data, image.content_type)

    try:
        parsed = extract_json(raw)
        return {"mode": "live", **parsed}
    except Exception:
        return {"mode": "live", "analysis_text": raw}


@app.post("/api/nutrition")
def nutrition(payload: NutritionRequest):
    prompt = f"""Estimate nutrition for {payload.quantity} of: {payload.food}.

Return ONLY valid JSON:
{{"food":"string","quantity":"string","calories_kcal":0,"protein_g":0,"carbs_g":0,"fat_g":0,"fiber_g":0,"assumptions":"string","uncertainty":"string"}}

Use approximate values, state assumptions, and do not present
the values as medically verified."""

    raw = ask_ai(prompt)

    try:
        parsed = extract_json(raw)
        return {"mode": "live", **parsed}
    except Exception:
        return {"mode": "live", "result_text": raw}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    if not GROQ_API_KEY:
        return {
            "mode": "demo",
            "reply": (
                "I'm the FoodVerse AI Chef demo. Add GROQ_API_KEY to "
                "backend/.env to enable live chat. I can help plan recipes, "
                "explain cooking steps, suggest substitutions, and reduce food waste."
            ),
        }

    messages = [
        {
            "role": "system",
            "content": (
                "You are FoodVerse AI Chef: friendly, practical, and "
                "safety-conscious. Help with recipes, cooking steps, ingredient "
                "substitutions, and reducing food waste. Do not claim to verify "
                "freshness, allergens, or food safety from images. Nutrition is "
                "approximate. Reply in readable Markdown."
            ),
        }
    ]

    for item in payload.history[-10:]:
        role = item.get("role", "user")
        content = str(item.get("content", ""))[:1000]

        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": payload.message})

    client = groq_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Groq AI is not configured. Add GROQ_API_KEY to backend/.env.",
        )

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_completion_tokens=2048,
        )

        answer = response.choices[0].message.content
        if not answer:
            raise HTTPException(
                status_code=502,
                detail="Groq returned an empty chat response.",
            )

        return {"mode": "live", "reply": answer}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Groq chat request failed: {str(exc)[:300]}",
        )
