# import os
# from dotenv import load_dotenv
# from agents import Agent, Runner, function_tool
# from agents.extensions.models.litellm_model import LitellmModel

# # 🔐 Load ENV
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # 🛠️ Career Roadmap Tool
# @function_tool
# def get_career_roadmap(field: str) -> str:
#     print(f"[Tool] Generating roadmap for: {field}")
#     field = field.lower()
#     if "frontend" in field:
#         return (
#             "📘 Frontend Developer Roadmap:\n"
#             "1. HTML, CSS, JS Basics\n"
#             "2. Responsive Design (Flex/Grid)\n"
#             "3. Frameworks: React/Next.js\n"
#             "4. Tailwind CSS, State Management\n"
#             "5. Build Projects + Deploy\n"
#         )
#     elif "data science" in field:
#         return (
#             "📊 Data Science Roadmap:\n"
#             "1. Python, NumPy, Pandas\n"
#             "2. Data Cleaning & Visualization\n"
#             "3. ML with Scikit-learn\n"
#             "4. Deep Learning (TensorFlow)\n"
#             "5. Real-world datasets practice\n"
#         )
#     else:
#         return f"⚠️ Sorry, no roadmap found for '{field}'. Try 'frontend' or 'data science'."

# # 🧠 Career Agent
# agent = Agent(
#     name="CareerAgent",
#     instructions="You are a career mentor. Use tools to suggest skill roadmaps. Keep it clear and helpful.",
#     tools=[get_career_roadmap],
#     model=LitellmModel(
#         model="gemini/gemini-2.0-flash",
#         api_key=GEMINI_API_KEY,
#     )
# )

# # 🏃 Runner
# if __name__ == "__main__":
#     user_input = "Can you give me a roadmap for backend development?"
#     result = Runner.run_sync(agent, user_input)
#     print("[Agent Reply] ", result.final_output)

#! ---------------------------------------------------------------------------- #
#!                              code with handsoff                              #
#! ---------------------------------------------------------------------------- #

import os
from dotenv import load_dotenv
from agents import Agent, AgentContext, HandoffRequest, Runner, function_tool
from agents.extensions.models.litellm_model import LitellmModel
from agents.types import HandoffRequest
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 🛠️ TOOL: get_career_roadmap
@function_tool
def get_career_roadmap(field: str) -> str:
    field = field.lower()
    if "frontend" in field:
        return (
            "📘 Frontend Developer Roadmap:\n"
            "1. HTML, CSS, JS\n"
            "2. Responsive Design\n"
            "3. React/Next.js\n"
            "4. Tailwind CSS\n"
            "5. Build Projects"
        )
    return f"No roadmap for '{field}'"

# 🧠 SKILL AGENT (receives handoff)
skill_agent = Agent(
    name="SkillAgent",
    instructions="You provide skill roadmaps using tools like get_career_roadmap.",
    tools=[get_career_roadmap],
    model=LitellmModel(
        model="gemini/gemini-2.0-flash",
        api_key=GEMINI_API_KEY,
    )
)

# 🎓 CAREER AGENT (does handoff)
async def career_agent_logic(ctx: AgentContext):
    msg = ctx.chat_history[-1]["content"].lower()
    if "frontend" in msg or "roadmap" in msg:
        # 🪙 Handoff to SkillAgent
        return HandoffRequest(
            to="SkillAgent",
            input="frontend"
        )
    return "Based on your interest, I suggest Frontend Development!"

career_agent = Agent(
    name="CareerAgent",
    instructions="You guide students to career fields. If user asks for roadmap, hand off to SkillAgent.",
    model=LitellmModel(
        model="gemini/gemini-2.0-flash",
        api_key=GEMINI_API_KEY,
    ),
    logic=career_agent_logic
)

# 🏃 RUNNER
if __name__ == "__main__":
    result = Runner.run_sync([career_agent, skill_agent], "I want a roadmap for frontend development")
    print("\n[💬 Final Response] ", result.final_output)
