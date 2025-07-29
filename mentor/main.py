import os
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool

# --------- Load Env ---------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# --------- Client & Model ---------
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client
)

# --------- Tools ---------
@function_tool
def get_career_roadmap(field: str) -> str:
    """Provides skill roadmap for a given career field."""
    field = field.lower()
    if "frontend" in field:
        return (
            "📘 Frontend Developer Roadmap:\n"
            "1. HTML, CSS, JS Basics\n"
            "2. Responsive Design (Flex/Grid)\n"
            "3. React/Next.js\n"
            "4. Tailwind CSS, State Management\n"
            "5. Build Projects + Deploy"
        )
    elif "data science" in field:
        return (
            "📊 Data Science Roadmap:\n"
            "1. Python, NumPy, Pandas\n"
            "2. Data Cleaning & Visualization\n"
            "3. ML with Scikit-learn\n"
            "4. Deep Learning (TensorFlow)\n"
            "5. Real-world datasets practice"
            "6. Frontend Development"
        )
    else:
        return f"⚠️ Sorry, no roadmap found for '{field}'. Try 'frontend' or 'data science'."

# --------- Agents ---------
skill_agent = Agent(
    name="SkillAgent",
    instructions="""
    You provide skill roadmaps using tools like get_career_roadmap.
    """,
    model=model,
    tools=[get_career_roadmap]
)

career_agent = Agent(
    name="CareerAgent",
    instructions="""
    Guide students to career fields based on their interests.
    If user specifically asks for a skill roadmap or mentions frontend/data science,
    hand off to SkillAgent for detailed steps.
    """,
    model=model,
    handoffs=[skill_agent]
)

mentor_agent = Agent(
    name="CareerMentorAgent",
    instructions="""
    Full career guidance experience:
    - Use CareerAgent for suggesting career paths.
    - Use SkillAgent for roadmap details.
    Perform handoffs accordingly.
    """,
    model=model,
    handoffs=[career_agent, skill_agent]
)

# --------- Run ---------
if __name__ == "__main__":
    query = "I want a roadmap for frontend development"
    result = Runner.run_sync(mentor_agent, query)

    print("\n---- FINAL OUTPUT ----")
    print(result.final_output)

    steps = getattr(result, "steps", None)  # type: ignore
    if steps:
        print("\n---- AGENT USED ----")
        print(steps[-1].agent_name)
    else:
        print("\nNo steps found (SDK version may vary).")
