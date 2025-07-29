import logging
from collections import Counter
from typing import Any, Optional

from mallm.agents.panelist import Panelist
from mallm.decision_protocols.protocol import DecisionProtocol
from mallm.models.discussion.ResponseGenerator import ResponseGenerator
from mallm.utils.config import Config
from mallm.utils.enums import DecisionAlteration
from mallm.utils.types import Agreement, VotingResult, VotingResultList, WorkerFunctions

logger = logging.getLogger("mallm")


class SimpleVoting(DecisionProtocol):
    """
    The Voting decision protocol allows panelists to vote for the best answer after a certain number of turns.
    """

    _name = "simple_voting"

    def __init__(
        self,
        panelists: list[Panelist],
        num_neutral_agents: int,
        worker_functions: WorkerFunctions,
        vote_turn: int = 3,
    ) -> None:
        super().__init__(panelists, num_neutral_agents, worker_functions)
        self.vote_turn = vote_turn

    def make_decision(
        self,
        agreements: list[Agreement],
        turn: int,
        agent_index: int,
        task: str,
        question: str,
        config: Config,
    ) -> tuple[str, bool, list[Agreement], str, Optional[VotingResultList]]:
        if len(agreements) > self.total_agents:
            agreements = agreements[-self.total_agents :]
        if turn < self.vote_turn or agent_index != self.total_agents - 1:
            return "", False, agreements, "", None

        final_answers_with_confidence, voting_process_string = (
            self.generate_final_answers(agreements, question, task)
        )

        decision, final_answer, results, voting_process_string = (
            self.vote_with_alterations(
                final_answers_with_confidence,
                question,
                task,
                voting_process_string,
                self._name,
                ResponseGenerator.generate_voting_prompt,
                config.voting_protocols_with_alterations,
            )
        )
        return (
            final_answer,
            decision,
            agreements,
            voting_process_string,
            results,
        )

    def process_results(
        self,
        all_votes: dict[str, VotingResult],
        alteration: DecisionAlteration,
        final_answers: list[str],
        votes: list[int],
    ) -> dict[str, VotingResult]:
        winners = []
        most_voted = -1
        if votes:
            vote_counts = Counter(votes)
            most_common = vote_counts.most_common()
            most_voted = most_common[0][0]
            most_voted_count = most_common[0][1]

            # Check if there are multiple winners with the same vote count
            winners = [
                candidate
                for candidate, count in vote_counts.items()
                if count == most_voted_count
            ]

        if len(winners) == 1:
            all_votes[alteration.value] = VotingResult(
                votes=votes,
                most_voted=most_voted,
                final_answer=final_answers[most_voted],
                agreed=True,
            )
            logger.info(
                f"Voted for answer from agent {self.panelists[most_voted].persona}"
            )
        else:
            all_votes[alteration.value] = VotingResult(
                votes=votes,
                most_voted=-1,
                final_answer="",
                agreed=False,
            )
            logger.info("There was a tie. Going for another round of voting.")
        return all_votes

    def process_votes(
        self,
        final_answers: list[str],
        panelist: Panelist,
        vote_str: str,
        vote: Any,
        voting_process_string: str,
    ) -> tuple[str, Any, bool, str]:
        success = False
        vote_int = int("".join([x for x in vote_str if x.isnumeric()]))
        if 0 <= vote_int < len(final_answers):
            vote.append(vote_int)
            logger.info(
                f"{panelist.persona} voted for answer from {self.panelists[vote_int].persona}"
            )
            voting_process_string += f"{panelist.persona} voted for answer from {self.panelists[vote_int].persona}\n"
            success = True
        return vote_str, vote, success, voting_process_string
