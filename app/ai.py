import json
from typing import Any
from .config import settings

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None

class AIService:
    def __init__(self):
        self.client = None
        if settings.gemini_api_key and genai:
            self.client = genai.Client(api_key=settings.gemini_api_key)

    def _generate(self, model: str, prompt: str, temperature: float = 0.6) -> str:
        if settings.mock_ai or not self.client:
            return self._mock_response(prompt)
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=5000,
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()

    @staticmethod
    def _mock_response(prompt: str) -> str:
        if "nutrition" in prompt.lower() or "recovery tip" in prompt.lower():
            return "Prioritize a balanced meal after training with a protein source, whole-food carbohydrates, vegetables, and enough water. Adjust portions to your goal and activity level."
        if "feedback" in prompt.lower() or "revise" in prompt.lower():
            return (
                "Day 1 — Full Body\nWarm-up: 7 min brisk walk + mobility\n"
                "Main: Squats 3x10, Push-ups 3x8, Rows 3x10\nCooldown: 5 min easy stretching\n\n"
                "Day 2 — Cardio\nWarm-up: 5 min easy pace\nMain: 25 min moderate cardio\nCooldown: 5 min walk\n\n"
                "Day 3 — Recovery\n20–30 min gentle walking and mobility.\n\n"
                "Day 4 — Lower Body\nWarm-up: 7 min\nMain: Lunges 3x10/side, Hip hinge 3x10, Calf raises 3x15\nCooldown: 5 min stretching\n\n"
                "Day 5 — Upper Body\nMain: Push-ups 3x8, Rows 3x10, Shoulder press 3x10\nCooldown: 5 min stretching\n\n"
                "Day 6 — Cardio + Core\nMain: 20 min cardio + plank 3x30 sec + dead bug 3x10\nCooldown: 5 min easy movement\n\n"
                "Day 7 — Rest\nEasy walk and recovery."
            )
        return (
            "Day 1 — Full Body\nWarm-up: 7 min brisk walk + mobility\n"
            "Main: Squats 3x10, Push-ups 3x8, Rows 3x10\nCooldown: 5 min easy stretching\n\n"
            "Day 2 — Cardio\nWarm-up: 5 min easy pace\nMain: 25 min moderate cardio\nCooldown: 5 min walk\n\n"
            "Day 3 — Recovery\n20–30 min gentle walking and mobility.\n\n"
            "Day 4 — Lower Body\nWarm-up: 7 min\nMain: Lunges 3x10/side, Hip hinge 3x10, Calf raises 3x15\nCooldown: 5 min stretching\n\n"
            "Day 5 — Upper Body\nMain: Push-ups 3x8, Rows 3x10, Shoulder press 3x10\nCooldown: 5 min stretching\n\n"
            "Day 6 — Cardio + Core\nMain: 20 min cardio + plank 3x30 sec + dead bug 3x10\nCooldown: 5 min easy movement\n\n"
            "Day 7 — Rest\nEasy walk and recovery."
        )

    def generate_workout(self, user: Any) -> str:
        prompt = f"""
You are FitBuddy, a conservative fitness-planning assistant.
Create a practical 7-day workout plan for:
Name: {user.name}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Preferred intensity: {user.intensity}

Return exactly seven labeled days. For each day include:
- Focus
- Warm-up (5–10 minutes)
- Main workout with exercise names and sets/reps or duration
- Cooldown/recovery
Use realistic progression and include at least one recovery/rest day.
Do not diagnose medical conditions or prescribe treatment. Tell the user to stop if they feel pain and consult a qualified professional when appropriate.
Keep the plan easy to scan in plain text.
"""
        return self._generate(settings.workout_model, prompt, 0.55)

    def generate_nutrition_tip(self, goal: str) -> str:
        prompt = f"""
Give one concise, practical nutrition or recovery tip for someone whose fitness goal is "{goal}".
Avoid individualized medical nutrition prescriptions. Mention hydration, balanced meals, protein,
fiber or recovery only when relevant. Keep it under 80 words.
"""
        return self._generate(settings.nutrition_model, prompt, 0.4)

    def update_workout(self, user: Any, original_plan: str, feedback: str) -> str:
        prompt = f"""
Revise this FitBuddy 7-day workout plan using the user's feedback.

User profile:
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Original plan:
{original_plan}

Feedback:
{feedback}

Return a complete revised seven-day plan, not a list of changes.
Preserve useful parts of the original while applying the feedback.
Keep the same safety boundaries: no diagnosis or treatment; recommend professional advice when appropriate.
"""
        return self._generate(settings.workout_model, prompt, 0.55)

ai_service = AIService()
