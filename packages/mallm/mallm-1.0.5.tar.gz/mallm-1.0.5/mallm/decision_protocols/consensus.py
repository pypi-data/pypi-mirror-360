import logging
from typing import Any, Optional

from mallm.agents.panelist import Panelist
from mallm.decision_protocols.protocol import DecisionProtocol
from mallm.utils.config import Config
from mallm.utils.enums import DecisionAlteration
from mallm.utils.types import Agreement, VotingResult, VotingResultList, WorkerFunctions

logger = logging.getLogger("mallm")


class ThresholdConsensus(DecisionProtocol):

    _name = "threshold_consensus"

    def process_votes(
        self,
        final_answers: list[str],
        panelist: Panelist,
        vote_str: str,
        vote: Any,
        voting_process_string: str,
    ) -> tuple[str, Any, bool, str]:
        raise NotImplementedError

    def process_results(
        self,
        all_votes: dict[str, VotingResult],
        alteration: DecisionAlteration,
        final_answers: list[str],
        votes: Any,
    ) -> dict[str, VotingResult]:
        raise NotImplementedError

    def __init__(
        self,
        panelists: list[Panelist],
        num_neutral_agents: int,
        worker_functions: WorkerFunctions,
        threshold_percent: float = 0.5,
        threshold_turn: Optional[int] = None,
        threshold_agents: Optional[int] = None,
    ) -> None:
        super().__init__(panelists, num_neutral_agents, worker_functions)
        self.threshold_turn = threshold_turn
        self.threshold_agents = threshold_agents
        self.threshold_percent = threshold_percent

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
        reversed_agreements = agreements[::-1]

        num_agreements, current_agreement = next(
            (
                (i, agreement)
                for i, agreement in enumerate(reversed_agreements, 1)
                if agreement.solution
            ),
            (None, None),
        )

        # so we have at least some output if the discussion does not converge
        if not current_agreement or not num_agreements:
            draftProposer_agreement = next(
                (a for a in reversed_agreements if a.agreement is None), None
            )
            if draftProposer_agreement:
                return draftProposer_agreement.solution, False, agreements, "", None
            recent_panelist_agreement = next(
                (a for a in reversed_agreements if not a.agreement), None
            )
            if recent_panelist_agreement:
                return recent_panelist_agreement.solution, False, agreements, "", None
            logger.warning(
                "Failed gathering the most recent disagreement. Returning None as current solution."
            )
            return "None", False, agreements, "", None

        if (self.threshold_agents and len(self.panelists) <= self.threshold_agents) or (
            self.threshold_turn and turn < self.threshold_turn
        ):
            # all agents need to agree in the first <threshold_turn> turns
            # all agents need to agree if there are less than <threshold_agents> agents
            return (
                current_agreement.solution,
                num_agreements / self.total_agents >= 1,
                agreements,
                "",
                None,
            )
        # more than <threshold_percent> of the agents need to agree
        return (
            current_agreement.solution,
            num_agreements / self.total_agents >= self.threshold_percent,
            agreements,
            "",
            None,
        )


class MajorityConsensus(ThresholdConsensus):

    _name = "majority_consensus"

    def __init__(
        self,
        panelists: list[Panelist],
        num_neutral_agents: int,
        worker_functions: WorkerFunctions,
    ):
        super().__init__(
            panelists, num_neutral_agents, worker_functions, 0.5, None, None
        )


class UnanimityConsensus(ThresholdConsensus):

    _name = "unanimity_consensus"

    def __init__(
        self,
        panelists: list[Panelist],
        num_neutral_agents: int,
        worker_functions: WorkerFunctions,
    ):
        super().__init__(
            panelists, num_neutral_agents, worker_functions, 1.0, None, None
        )


class SupermajorityConsensus(ThresholdConsensus):

    _name = "supermajority_consensus"

    def __init__(
        self,
        panelists: list[Panelist],
        num_neutral_agents: int,
        worker_functions: WorkerFunctions,
    ):
        super().__init__(
            panelists, num_neutral_agents, worker_functions, 0.66, None, None
        )


class HybridMajorityConsensus(ThresholdConsensus):
    """
    The Hybrid Majority Consensus imitates the implementation by Yin et. al.
    Paper: https://arxiv.org/abs/2312.01823
    """

    _name = "hybrid_majority_consensus"

    def __init__(
        self,
        panelists: list[Panelist],
        num_neutral_agents: int,
        worker_functions: WorkerFunctions,
    ):
        super().__init__(panelists, num_neutral_agents, worker_functions, 0.75, 5, 3)
