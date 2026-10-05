from langchain_core.messages import HumanMessage, SystemMessage

from skills.experience_research import experience_research_skill
from skills.project_research import project_research_skill
from skills.skills_research import skills_research_skill


SKILLS = {
    "project": project_research_skill,
    "experience": experience_research_skill,
    "skills": skills_research_skill,
}


SKILL_SELECTOR_PROMPT = """
Determine whether the user's question requires a specialized portfolio research skill.

Available skills:

- project:
  Questions about Michael's projects, including project purpose,
  implementation, architecture, technologies, and technical decisions.

- experience:
  Questions about Michael's work, research, responsibilities,
  contributions, and experience.

- skills:
  Questions about Michael's programming languages, frameworks,
  databases, cloud technologies, AI/ML technologies, or technical skills.

If a specialized skill is appropriate, return its name:
project, experience, or skills.

If no specialized skill is needed, return "none".

Return only the skill name.
"""


async def select_skill(model, user_message: str) -> str:
    response = await model.ainvoke(
        [
            SystemMessage(content=SKILL_SELECTOR_PROMPT),
            HumanMessage(content=user_message),
        ]
    )

    return response.content[0]["text"].strip().lower()


def get_skill(skill_name: str) -> str | None:
    skill = SKILLS.get(skill_name)

    if skill is None:
        return None

    return skill()

