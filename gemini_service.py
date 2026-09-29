from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------------------------------------------------
# Generate 7-Day Workout Plan
# ---------------------------------------------------------

def generate_workout_gemini(
    age,
    weight,
    goal,
    level,
    intensity,
    available_time
):

    prompt = f"""
You are FitBuddy, a friendly and safe fitness planning assistant.

Create a personalized 7-day general fitness plan.

USER INFORMATION:
Age: {age}
Weight: {weight} kg
Goal: {goal}
Fitness Level: {level}
Workout Intensity: {intensity}
Available Time: {available_time}

Create a workout plan from Day 1 through Day 7.

For EACH day include:

- Title
- Warm-up
- Main activity or exercises
- Sets and repetitions OR duration
- Rest
- Cool-down
- Notes

Include suitable rest or recovery days.

The plan should be simple, safe and appropriate for
the user's fitness level and selected intensity.

Do not recommend:
- Extreme exercise
- Unsafe activities
- Restrictive dieting
- Calorie targets
- Supplements
- Skipping meals

Use exactly this structure:

DAY 1
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 2
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 3
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 4
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 5
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 6
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 7
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

RECOVERY
Give 2 or 3 short general recovery tips.

Return ONLY the workout plan and recovery section.
Keep the language simple and easy to understand.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal"
                )
            )
        )

        return response.text

    except Exception as e:

        print("Gemini Workout Error:", e)

        return "Gemini Workout Error: " + str(e)


# ---------------------------------------------------------
# Generate Nutrition Tip
# ---------------------------------------------------------

def generate_nutrition_tip_with_flash(goal):

    prompt = f"""
You are FitBuddy, a friendly fitness assistant.

The user's fitness goal is:

{goal}

Give 3 or 4 short and practical healthy eating,
hydration and recovery tips suitable for this goal.

Do not provide:
- Calorie targets
- Restrictive diets
- Supplements
- Meal skipping

Keep the advice simple and general.

Return only the nutrition and recovery tips.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal"
                )
            )
        )

        return response.text

    except Exception as e:

        print("Gemini Nutrition Error:", e)

        return "Gemini Nutrition Error: " + str(e)


# ---------------------------------------------------------
# Update Workout Plan Using Feedback
# ---------------------------------------------------------

def update_workout_plan(original_plan, feedback):

    prompt = f"""
You are FitBuddy, a friendly and safe fitness planning assistant.

ORIGINAL 7-DAY WORKOUT PLAN:

{original_plan}

USER FEEDBACK:

{feedback}

Update the workout plan according to the user's feedback.

Keep the updated plan:

- Safe
- Simple
- Appropriate for the fitness level
- Easy to understand

Do not recommend extreme exercise or unsafe activities.

Use exactly this structure:

DAY 1
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 2
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 3
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 4
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 5
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 6
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

DAY 7
Title:
Warm-up:
Activity:
Sets/Reps or Duration:
Rest:
Cool-down:
Notes:

RECOVERY
Give 2 or 3 short recovery tips.

Return ONLY the updated workout plan.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal"
                )
            )
        )

        return response.text

    except Exception as e:

        print("Gemini Update Error:", e)

        return original_plan