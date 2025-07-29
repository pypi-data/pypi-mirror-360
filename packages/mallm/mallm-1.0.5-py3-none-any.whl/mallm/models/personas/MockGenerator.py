from mallm.models.Chat import Chat
from mallm.models.personas.PersonaGenerator import PersonaGenerator
from mallm.utils.types import InputExample


class MockGenerator(PersonaGenerator):
    """
    The MockGenerator class is a placeholder PersonaGenerator that generates a simple persona based on the number of already generated personas..
    """

    def __init__(self, llm: Chat):
        pass

    @staticmethod
    def generate_persona(
        task_description: str,
        already_generated_personas: list[dict[str, str]],
        sample: InputExample,
    ) -> dict[str, str]:
        return {
            "role": f"Participant {len(already_generated_personas) + 1}",
            "description": "generic",
        }
