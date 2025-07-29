import json
import logging

from json_repair import repair_json

from mallm.models.Chat import Chat
from mallm.models.personas.PersonaGenerator import PersonaGenerator
from mallm.utils.types import InputExample

logger = logging.getLogger("mallm")


class ExpertGenerator(PersonaGenerator):
    """
    The ExpertGenerator class is a specialized PersonaGenerator designed to generate expert personas for a given task or discussion. It is capable of identifying the necessary participants, their roles, and descriptions to foster a rich and informative discussion.
    """

    def __init__(self, llm: Chat):
        self.llm = llm
        self.base_prompt = {
            "role": "system",
            "content": """
When faced with a task, begin by identifying the participants who will contribute to solving the task. Provide role and description of the participants, describing their expertise or needs, formatted using the provided JSON schema.
Generate one participant at a time, complementing the existing participants to foster a rich discussion.

Example 1:
Task: Explain the basics of machine learning to high school students.
New Participant:
{"role": "Educator", "description": "An experienced teacher who simplifies complex topics for teenagers."}

Example 2:
Task: Develop a new mobile app for tracking daily exercise.
Already Generated Participants:
{"role": "Fitness Coach", "description": "A person that has high knowledge about sports and fitness."}
New Participant:
{"role": "Software Developer", "description": "A creative developer with experience in mobile applications and user interface design."}

Example 3:
Task: Write a guide on how to cook Italian food for beginners.
Already Generated Participants:
{"role": "Italian Native", "description": "An average home cook that lived in italy for 30 years."}
{"role": "Food Scientist", "description": "An educated scientist that knows which flavor combinations result in the best taste."}
New Participant:
{"role": "Chef", "description": "A professional chef specializing in Italian cuisine who enjoys teaching cooking techniques."}
        """,
        }

    def generate_persona(
        self,
        task_description: str,
        already_generated_personas: list[dict[str, str]],
        sample: InputExample,
    ) -> dict[str, str]:
        current_prompt = [
            self.base_prompt,
            {
                "role": "user",
                "content": f"\nNow generate a participant to discuss the following task:\nTask: {task_description}\n",
            },
        ]
        if already_generated_personas:
            current_prompt.append(
                {
                    "role": "system",
                    "content": "Already Generated Participants:\n"
                    + "\n".join(
                        [
                            str(generated_persona)
                            for generated_persona in already_generated_personas
                        ]
                    ),
                }
            )

        retry = 0
        while retry < 5:
            # Send the prompt to the InferenceClient
            response = self.llm.invoke(
                [
                    *current_prompt,
                    {
                        "role": "user",
                        "content": "Please use the following examples to generate a useful persona for the task! Only answer with the JSON for the next persona!",
                    },
                ]
            )
            try:
                new_agent = json.loads(repair_json(response))
                if isinstance(new_agent, list):
                    new_agent = new_agent[0]
                if (
                    "role" not in new_agent
                    or "description" not in new_agent
                    or not new_agent["role"]
                    or not new_agent["description"]
                ):
                    continue
                agent: dict[str, str] = new_agent
                break
            except (json.decoder.JSONDecodeError, TypeError) as e:
                retry += 1
                logger.debug(
                    f"Could not decode json (will attempt retry no. {retry!s}): "
                    + str(e)
                    + "\nResponse string: "
                    + str(response)
                )
                continue
        return agent
