import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

import requests

from mallm.utils.task_instructions import TASK_INSTRUCTIONS

logger = logging.getLogger("mallm")


@dataclass
class Config:
    # DO NOT overwrite these values once assigned.
    input_json_file_path: str
    output_json_file_path: str
    task_instruction_prompt: str = ""
    task_instruction_prompt_template: Optional[str] = None
    endpoint_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-3.5-turbo"
    api_key: str = "-"
    max_turns: int = 10
    skip_decision_making: bool = False
    discussion_paradigm: str = "memory"
    response_generator: str = "simple"
    decision_protocol: str = "hybrid_consensus"
    visible_turns_in_memory: int = 2
    debate_rounds: int = 2
    concurrent_api_requests: int = 100
    use_baseline: bool = False
    use_chain_of_thought: bool = True
    num_agents: int = 3
    num_neutral_agents: int = 0
    agent_generator: str = "expert"
    agent_generators_list: list[str] = field(default_factory=list[str])
    trust_remote_code: bool = False
    num_samples: Optional[int] = None
    hf_dataset_split: Optional[str] = "test"
    hf_token: Optional[str] = None
    hf_dataset_version: Optional[str] = None
    hf_dataset_input_column: Optional[str] = None
    hf_dataset_reference_column: Optional[str] = None
    hf_dataset_context_column: Optional[str] = None
    use_ablation: bool = False
    shuffle_input_samples: bool = False
    all_agents_generate_first_draft: bool = False
    all_agents_generate_draft: bool = False
    voting_protocols_with_alterations: bool = False
    calculate_persona_diversity: bool = False
    challenge_final_results: bool = False
    judge_intervention: Optional[str] = None
    judge_metric: Optional[str] = None
    judge_endpoint_url: Optional[str] = None
    judge_model_name: Optional[str] = None
    judge_api_key: str = "-"
    judge_always_intervene: bool = False

    def __post_init__(self) -> None:
        if (
            not self.task_instruction_prompt
            and self.task_instruction_prompt_template in TASK_INSTRUCTIONS
        ):
            self.task_instruction_prompt = TASK_INSTRUCTIONS[
                self.task_instruction_prompt_template
            ]

    def check_config(self) -> None:
        # TODO: make this more robust and conclusive. All arguments should be checked for validity, making the use of MALLM as fool-proof as possible.
        if not self.task_instruction_prompt:
            logger.error(
                "Please provide an instruction using the --task_instruction_prompt argument or a template using --task_instruction_prompt_template."
            )
            sys.exit(1)
        if os.path.isfile(self.input_json_file_path):
            if not self.input_json_file_path.endswith(".json"):
                logger.error("The dataset path does not seem to be a json file.")
                sys.exit(1)
        else:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            response = requests.get(
                f"https://datasets-server.huggingface.co/is-valid?dataset={self.input_json_file_path}",
                headers=headers,
            )
            if "preview" not in response.json() or not response.json()["preview"]:
                logger.error("The huggingface dataset cannot be loaded.")
                sys.exit(1)

        if not self.output_json_file_path.endswith(".json"):
            logger.error(
                "The output file does not seem to be a json file. Please specify a file path using --output_json_file_path."
            )
            sys.exit(1)

        if "api.openai.com" in self.endpoint_url and self.api_key == "-":
            logger.error(
                "When using the OpenAI API, you need to provide a key with the argument: --api_key=<your key>"
            )
            sys.exit(1)
        if self.judge_intervention and not self.judge_metric:
            logger.error(
                "When using judge intervention, you need to provide a metric with the argument: --judge_metric=<your metric>."
            )
            sys.exit(1)
        if not self.agent_generators_list:
            self.agent_generators_list = [
                self.agent_generator for i in range(self.num_agents)
            ]
        if (
            self.agent_generators_list
            and len(self.agent_generators_list) != self.num_agents
        ):
            logger.warning(
                f"The length of the provided agent generators ({self.agent_generators_list}) does not match the number of agents (3). Setting num_agents={len(self.agent_generators_list)}."
            )
            self.num_agents = len(self.agent_generators_list)
        if self.endpoint_url.endswith("/"):
            logger.warning("Removing trailing / from the endpoint url.")
            self.endpoint_url = self.endpoint_url[:-1]
        if self.concurrent_api_requests > 250:
            logger.warning(
                "concurrent_api_requests is very large. Please make sure the API endpoint you are using can handle that many simultaneous requests."
            )
        # import here to avoid circular imports
        from mallm.utils.dicts import (  # noqa PLC0415
            DECISION_PROTOCOLS,
            DISCUSSION_PARADIGMS,
            RESPONSE_GENERATORS,
        )

        if self.response_generator not in RESPONSE_GENERATORS:
            logger.error(
                f"Invalid response generator: {self.response_generator}. Available options are: {RESPONSE_GENERATORS.keys()}."
            )
            sys.exit(1)
        if self.discussion_paradigm not in DISCUSSION_PARADIGMS:
            logger.error(
                f"Invalid discussion paradigm: {self.discussion_paradigm}. Available options are: {DISCUSSION_PARADIGMS.keys()}."
            )
            sys.exit(1)
        if self.decision_protocol not in DECISION_PROTOCOLS:
            logger.error(
                f"Invalid decision protocol: {self.decision_protocol}. Available options are: {DECISION_PROTOCOLS.keys()}."
            )
            sys.exit(1)
