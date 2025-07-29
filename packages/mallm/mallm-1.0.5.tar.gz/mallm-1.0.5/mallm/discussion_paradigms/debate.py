from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from rich.progress import Console

from mallm.agents.draftProposer import DraftProposer
from mallm.agents.judge import Judge
from mallm.agents.panelist import Panelist
from mallm.discussion_paradigms.paradigm import DiscussionParadigm
from mallm.utils.types import Agreement, TemplateFilling, VotingResultList

if TYPE_CHECKING:
    from mallm.coordinator import Coordinator
    from mallm.utils.config import Config

logger = logging.getLogger("mallm")


class DiscussionDebate(DiscussionParadigm):
    def draft_proposer_call(
        self,
        draft_proposer: DraftProposer,
        coordinator: Coordinator,
        agent_index: int,
        memory_ids: list[int],
        template_filling: TemplateFilling,
    ) -> None:
        pass

    def panelist_call(
        self,
        agent: Panelist,
        coordinator: Coordinator,
        agent_index: int,
        memory_ids: list[int],
        template_filling: TemplateFilling,
    ) -> None:
        pass

    def __init__(self, debate_rounds: int = 1):
        super().__init__("")
        self.debate_rounds = debate_rounds

    def discuss(
        self,
        coordinator: Coordinator,
        task_instruction: str,
        input_str: str,
        solution: str,
        config: Config,
        console: Optional[Console] = None,
    ) -> tuple[Optional[str], int, list[Agreement], bool, dict[int, Any]]:
        unique_id = 0
        memories = []
        voting_process_string = ""
        voting_results_per_turn: dict[int, Optional[VotingResultList]] = {}
        if console is None:
            console = Console()
        logger.info(
            f"""Paradigm: Debate (rounds: {config.debate_rounds})
                            ┌───┐
                  ┌────────►│A 1│◄────────┐
                  │         └───┘         │
                  │                       │
                  │                       │
                  │                       │
                ┌─┴─┬──────────────────►┌─┴─┐
                │A 3│                   │A 2│
                └───┘◄──────────────────┴───┘
                """
        )

        logger.info(
            "Debate rounds between agents A2, ..., An: " + str(config.debate_rounds)
        )

        while (
            not self.decision or config.skip_decision_making
        ) and self.turn < config.max_turns:
            self.turn += 1
            logger.debug("Ongoing. Current turn: " + str(self.turn))

            # ---- Agent A1
            discussion_history, memory_ids, current_draft = coordinator.agents[
                0
            ].get_discussion_history(
                context_length=config.visible_turns_in_memory,
                turn=self.turn,
            )
            if (
                self.turn == 1 and config.all_agents_generate_first_draft
            ) or config.all_agents_generate_draft:
                current_draft = None
                discussion_history = None
            template_filling = TemplateFilling(
                task_instruction=task_instruction,
                input_str=input_str,
                current_draft=current_draft,
                persona=coordinator.agents[0].persona,
                persona_description=coordinator.agents[0].persona_description,
                agent_memory=discussion_history,
            )
            _res, memory, self.agreements = coordinator.agents[0].draft(
                unique_id=unique_id,
                turn=self.turn,
                memory_ids=memory_ids,
                template_filling=template_filling,
                agreements=self.agreements,
                is_neutral=True,
            )
            memories.append(memory)
            coordinator.update_memories(memories, coordinator.agents)
            memories = []
            unique_id += 1

            # ---- Agents A2, A3, ...
            for r in range(config.debate_rounds):
                logger.debug(
                    f"Discussion {coordinator.id} goes into debate round: {r!s}"
                )
                if r == 0:
                    debate_agreements = self.agreements
                for i, a in enumerate(
                    coordinator.agents[1:]
                ):  # similar to relay paradigm
                    # Because we should only iterate over Panelists with [1:]
                    # We call participate() below, which is a method of Panelist

                    discussion_history, memory_ids, current_draft = (
                        a.get_discussion_history(
                            context_length=config.visible_turns_in_memory,
                            turn=self.turn,
                        )
                    )
                    next_a = i + 2
                    if i == len(coordinator.agents[1:]) - 1:
                        next_a = 1  # start again with agent 1 (loop)
                    if (
                        self.turn == 1
                        and r == 1
                        and config.all_agents_generate_first_draft
                    ):
                        current_draft = None
                        discussion_history = None
                    template_filling = TemplateFilling(
                        task_instruction=task_instruction,
                        input_str=input_str,
                        current_draft=current_draft,
                        persona=a.persona,
                        persona_description=a.persona_description,
                        agent_memory=discussion_history,
                    )

                    if r == config.debate_rounds - 1:  # last debate round
                        agents_to_update = [
                            coordinator.agents[0],
                            a,
                            coordinator.agents[next_a],
                        ]
                    else:
                        agents_to_update = [a, coordinator.agents[next_a]]

                    if isinstance(a, DraftProposer):
                        _res, _debate_memory, debate_agreements = a.draft(
                            unique_id=unique_id,
                            turn=self.turn,
                            memory_ids=memory_ids,
                            template_filling=template_filling,
                            agreements=debate_agreements,
                            is_neutral=True,
                        )
                    elif isinstance(a, Panelist):
                        debate_agreements = a.participate(
                            memories=memories,
                            unique_id=unique_id,
                            turn=self.turn,
                            memory_ids=memory_ids,
                            template_filling=template_filling,
                            agents_to_update=agents_to_update,
                            agreements=debate_agreements,
                        )
                    elif isinstance(a, Judge):
                        continue    # executes after decision protocol
                    else:
                        logger.error("Agent type not recognized.")
                        raise Exception("Agent type not recognized.")

                    if len(debate_agreements) > len(coordinator.agents) - 1:
                        debate_agreements = debate_agreements[
                            1 - len(coordinator.agents) :
                        ]
                    unique_id += 1

            self.agreements += debate_agreements

            if coordinator.decision_protocol is None:
                logger.error("No decision protocol module found.")
                raise Exception("No decision protocol module found.")

            (
                self.draft,
                self.decision,
                self.agreements,
                voting_process_string,
                additional_voting_results,
            ) = coordinator.decision_protocol.make_decision(
                self.agreements,
                self.turn,
                len(coordinator.agents),
                task_instruction,
                input_str,
                config,
            )
            if additional_voting_results:
                voting_results_per_turn[self.turn] = additional_voting_results
            else:
                voting_results_per_turn[self.turn] = None

            if self.decision:
                break

            if coordinator.judge:
                template_filling = TemplateFilling(
                    task_instruction=task_instruction,
                    input_str=input_str,
                    current_draft=self.draft,
                    persona=coordinator.judge.persona,
                    persona_description=coordinator.judge.persona_description,
                    agent_memory=discussion_history,
                )
                self.unique_id, self.turn = coordinator.judge.intervention(self.unique_id, self.turn, memory_ids, template_filling, self.draft, always_intervene=config.judge_always_intervene)

            self.print_messages(coordinator, input_str, task_instruction)

        self.print_messages(
            coordinator,
            input_str,
            task_instruction,
            False,
            solution,
            voting_process_string,
            console=console,
        )
        return (
            self.draft,
            self.turn,
            self.agreements,
            self.decision,
            voting_results_per_turn
        )
