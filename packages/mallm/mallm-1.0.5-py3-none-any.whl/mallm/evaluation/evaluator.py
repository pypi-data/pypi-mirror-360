import json
import logging
from pathlib import Path
from typing import Any, Optional

import fire
import json_repair
from tqdm import tqdm

from mallm.evaluation.metrics.bertscore import BERTScore
from mallm.evaluation.metrics.bleu import BLEU
from mallm.evaluation.metrics.ifeval import IFEval
from mallm.evaluation.metrics.meteor import METEOR
from mallm.evaluation.metrics.metric import Metric
from mallm.evaluation.metrics.qa import (
    AnswerabilityBoolean,
    IncludesAnswer,
    MultiChoiceBoolean,
    SquadScore,
)
from mallm.evaluation.metrics.rouge import ROUGE
from mallm.evaluation.plotting.plots import create_plots_for_path

ALL_METRICS = [
    AnswerabilityBoolean(),
    BERTScore(),
    BLEU(),
    METEOR(),
    MultiChoiceBoolean(),
    ROUGE(),
    SquadScore(),
    IncludesAnswer(),
    IFEval(),
]

logger = logging.getLogger("mallm")


class Evaluator:
    def __init__(
        self,
        input_file_path: str,
        output_dir_path: Optional[str] = None,
        metrics: Optional[list[str]] = None,
        extensive: bool = False,
    ) -> None:
        self.input_file_path = Path(input_file_path)
        if not self.input_file_path.exists() or not self.input_file_path.is_file():
            raise FileNotFoundError(f"Input file not found: {self.input_file_path}")

        if output_dir_path:
            output_dir = Path(output_dir_path)
            output_file_path = output_dir
        else:
            output_file_path = self.input_file_path

        self.stats_file_path = output_file_path.with_name(
            output_file_path.stem + "-stats.json"
        )
        self.eval_file_path = output_file_path.with_name(
            output_file_path.stem + "-eval.json"
        )

        self.data = self._load_data()
        self.metrics = self._initialize_metrics(metrics)
        self.extensive = extensive

    def _load_data(self) -> list[dict[str, Any]]:
        data_str = Path(self.input_file_path).read_text()
        data: list[dict[str, Any]] = json_repair.repair_json(
            data_str, return_objects=True
        )
        return data

    @staticmethod
    def _initialize_metrics(metrics: Optional[list[str]]) -> list[Any]:
        if metrics is None:
            metrics = ["multichoice"]

        metrics = [m.lower() for m in metrics]
        selected_metrics = [
            metric_class
            for metric_class in ALL_METRICS
            if metric_class.name.lower() in metrics
        ]
        if len(selected_metrics) != len(metrics):
            logger.warning(f"Some metrics not found in {metrics}")
        if not selected_metrics:
            raise ValueError(f"No metrics found for {metrics}")
        logger.info(f"Metrics to calculate: {[m.name for m in selected_metrics]}")
        return selected_metrics

    @staticmethod
    def calculate_score(
        answer: str,
        references: list[str],
        metric: Metric,
        dataset_id: Optional[str] = None,
    ) -> dict[str, Any]:
        return next(iter(metric.evaluate(answer, references, dataset_id).values()))

    def calculate_scores(
        self,
        answer: str,
        references: list[str],
        metric_alteration: str = "",
        dataset_id: Optional[str] = None,
    ) -> dict[str, Any]:
        metrics = []
        if references:
            metrics.extend(self.metrics)
        else:
            if any(metric.name == "answerability" for metric in self.metrics):
                metrics.append(AnswerabilityBoolean())
            if any(metric.name == "squad" for metric in self.metrics):
                metrics.append(SquadScore())
            if any(metric.name == "IFEval" for metric in self.metrics):
                metrics.append(IFEval())
        if not metrics:
            logger.warning(f"No metrics to evaluate against references {references}.")
            return {}

        return {
            f"{k}{f'-{metric_alteration}' if metric_alteration else ''}": v
            for metric in metrics
            for k, v in metric.evaluate(answer, references, dataset_id).items()
        }

    def add_scores(self) -> None:
        for item in tqdm(
            self.data, desc=f"Calculating scores of {self.input_file_path}: "
        ):
            main_answer = item.get("finalAnswer", "")
            references = item.get("references", [])
            dataset_id = item.get("datasetId", None)
            if main_answer:
                item["scores"] = self.calculate_scores(
                    main_answer, references, "", dataset_id
                )

            votes_each_turn = item.get("votesEachTurn", None)
            if votes_each_turn:
                alterations: dict[str, Any] = votes_each_turn[
                    max(votes_each_turn.keys())
                ].get("alterations", "")
                if alterations and len(alterations) >= 1:
                    for alteration in list(alterations.keys()):
                        answer = alterations[alteration].get("final_answer", "")
                        if answer and "scores" not in item:
                            item["scores"] = self.calculate_scores(
                                answer, references, alteration, dataset_id
                            )
                        elif answer:
                            item["scores"].update(
                                self.calculate_scores(answer, references, alteration, dataset_id)
                            )

            challenged_answers: Any = item.get("challengedAnswers", None)
            if challenged_answers:
                if "scores" not in item:
                    continue
                if "correct" not in item["scores"] and "f1" not in item["scores"]:
                    continue
                if challenged_answers["challenged_answers"]:
                    self.analyze_challenged_answers(
                        "normal",
                        challenged_answers["challenged_answers"],
                        item,
                        references,
                        item["scores"],
                        dataset_id
                    )
                if challenged_answers["challenged_answers_wrong"]:
                    self.analyze_challenged_answers(
                        "wrong",
                        challenged_answers["challenged_answers_wrong"],
                        item,
                        references,
                        self.calculate_scores(
                            challenged_answers["wrong_answer"], references, "", dataset_id
                        ),
                        dataset_id
                    )
                if challenged_answers["challenged_answers_irrelevant"]:
                    self.analyze_challenged_answers(
                        "irrelevant",
                        challenged_answers["challenged_answers_irrelevant"],
                        item,
                        references,
                        self.calculate_scores(
                            challenged_answers["irrelevant_answer"], references, "", dataset_id
                        ),
                        dataset_id
                    )
                if challenged_answers["challenged_answers_history"]:
                    self.analyze_challenged_answers(
                        "history",
                        challenged_answers["challenged_answers_history"],
                        item,
                        references,
                        item["scores"],
                        dataset_id
                    )
                if challenged_answers["challenged_answers_additional_information"]:
                    self.analyze_challenged_answers(
                        "information",
                        challenged_answers["challenged_answers_additional_information"],
                        item,
                        references,
                        item["scores"],
                        dataset_id
                    )

    def analyze_challenged_answers(
        self,
        name: str,
        challenged_answers: dict[str, Optional[str]],
        item: Any,
        references: list[str],
        previous_score: Any,
        dataset_id: Optional[str] = None,
    ) -> None:
        new_answer = {
            f"{name}_no_challenge": True,
            f"{name}_challenge_failed": False,
            f"{name}_challenge_higher": False,
            f"{name}_challenge_lower": False,
            f"{name}_challenge_same": False,
        }
        previous_score = (
            previous_score.get("f1")
            if previous_score.get("f1", None) is not None
            else previous_score.get("correct", None)
        )

        answer = next(iter(challenged_answers.values()))
        if answer:
            score = self.calculate_scores(answer, references, "", dataset_id)
            current_score = (
                score.get("f1")
                if score.get("f1", None) is not None
                else score.get("correct", None)
            )
            if current_score is None or previous_score is None:
                new_answer[f"{name}_challenge_failed"] = True
            elif current_score > previous_score:
                new_answer[f"{name}_challenge_higher"] = True
            elif current_score < previous_score:
                new_answer[f"{name}_challenge_lower"] = True
            elif current_score == previous_score:
                new_answer[f"{name}_challenge_same"] = True
            new_answer[f"{name}_no_challenge"] = False
        item["scores"].update(new_answer)

    def add_scores_extensive(self) -> None:
        for item in tqdm(self.data, desc="Extensive scores: "):
            references = item.get("references", [])
            dataset_id = item.get("datasetId", None)
            votes_each_turn = item.get("votesEachTurn", None)
            alterations: dict[str, Any] = {}
            if votes_each_turn:
                alterations = votes_each_turn[
                    max(votes_each_turn.keys())
                ].get("alterations", None)
            for mem in item.get("globalMemory", []):
                solution = mem.get("solution", "")
                if solution and alterations:
                    for alteration in list(alterations.keys()):
                        if "scores" not in mem:
                            mem["scores"] = self.calculate_scores(
                                solution, references, alteration, dataset_id
                            )
                        else:
                            mem["scores"].update(
                                self.calculate_scores(solution, references, alteration, dataset_id)
                            )
                elif solution:
                    score = self.calculate_scores(solution, references, "", dataset_id)
                    mem["scores"] = score

            if votes_each_turn:
                for turn in votes_each_turn:
                    if alterations:
                        for alteration in list(alterations.keys()):
                            item["votesEachTurn"][turn]["alterations"][alteration][
                                "score"
                            ] = self.calculate_scores(
                                item["votesEachTurn"][turn]["alterations"][alteration][
                                    "final_answer"
                                ],
                                references,
                                alteration,
                                dataset_id
                            )

    def calculate_statistics(self) -> dict[str, Any]:
        reported_metrics = set()
        for item in self.data:
            if "scores" in item:
                reported_metrics.update(item["scores"].keys())

        if not reported_metrics:
            logger.error("No elements with scores found in the data.")
            raise Exception("No elements with scores found in the data.")

        logger.info(f"Reported metrics: {reported_metrics}")

        stats = {}
        for metric in reported_metrics:
            scores = [item.get("scores", {}).get(metric) for item in self.data]
            scores = [
                score
                for score in scores
                if isinstance(score, (int, float)) and score is not None
            ]

            if not scores:
                logger.warning(f"No numeric scores found for {metric}")
                continue

            average_score = sum(scores) / len(scores)
            if len(scores) > 1:
                std_dev_score = (
                    sum((score - average_score) ** 2 for score in scores)
                    / (len(scores) - 1)
                ) ** 0.5
            else:
                std_dev_score = 0

            avg_scores_per_turn = {}
            if self.extensive:
                for item in self.data:
                    for mem in item.get("globalMemory", []):
                        turn = mem.get("turn", 0)
                        if turn not in avg_scores_per_turn:
                            avg_scores_per_turn[turn] = float(0)
                        turn_score = mem.get("scores", {}).get(metric, 0)
                        if turn_score:
                            avg_scores_per_turn[turn] += turn_score

                max_turns = max(item.get("turns", 0) for item in self.data)
                for turn in range(max_turns + 1)[1:]:
                    num_scores = sum(
                        1
                        for item in self.data
                        for mem in item.get("globalMemory", [])
                        if mem.get("turn", 0) == turn
                        and metric in mem.get("scores", {})
                    )
                    if num_scores == 0:
                        num_scores = 1
                    avg_scores_per_turn[turn] /= num_scores
                    avg_scores_per_turn[turn] = round(avg_scores_per_turn[turn], 4)

            stats[metric] = {
                "dataSize": len(self.data),
                "sampleSize": len(scores),
                "scores": scores,
                "averageScore": round(average_score, 4),
                "stdDevScore": round(std_dev_score, 4),
                "averageScoresPerTurnAggregated": avg_scores_per_turn,
            }

        return stats

    def save_results(self, stats: dict[str, Any]) -> None:
        self.stats_file_path.write_text(json.dumps(stats, indent=4))
        self.eval_file_path.write_text(json.dumps(self.data, indent=4))
        logger.info(f"Statistics saved to {self.stats_file_path}")
        logger.info(f"Eval saved to {self.eval_file_path}")

    def process(self) -> None:
        self.add_scores()
        if self.extensive:
            self.add_scores_extensive()
        stats = self.calculate_statistics()
        self.save_results(stats)


def batch_process_dir_path(
    input_dir_path: str,
    output_dir_path: Optional[str] = None,
    metrics: Optional[list[str]] = None,
    extensive: bool = False,
) -> None:
    input_path = Path(input_dir_path)
    output_path = Path(output_dir_path) if output_dir_path else input_path
    if not output_path.exists() or not output_path.is_dir():
        print(f"Creating output directory: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
    if not input_path.exists() or not input_path.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_path}")
    print(f"Processing files in {input_path} and saving results to {output_path}")
    print(f"Metrics to calculate: {metrics}")
    print(f"Files to process: {len(list(input_path.glob('*.json')))}")
    files = list(input_path.glob("*.json"))
    for file in files:
        if file.stem.endswith(("-eval", "-stats")):
            continue

        output_file = output_path / file.name
        logger.info(f"Processing {file}")

        evaluator = Evaluator(str(file), str(output_file), metrics, extensive)
        evaluator.process()

    logger.info("Batch processing completed.")
    logger.info("Creating plots...")
    plot_path = str(output_path).removesuffix("/")
    create_plots_for_path(plot_path, plot_path)
    logger.info("Plots created.")


def run_evaluator(
    input_json_file_path: str,
    output_dir_path: Optional[str] = None,
    metrics: Optional[list[str]] = None,
    extensive: bool = False,
) -> None:
    if Path(input_json_file_path).is_dir():
        print(f"Processing directory: {input_json_file_path}")
        batch_process_dir_path(
            input_json_file_path, output_dir_path, metrics, extensive
        )
    else:
        print(f"Processing file: {input_json_file_path}")
        evaluator = Evaluator(input_json_file_path, output_dir_path, metrics, extensive)
        evaluator.process()


def main() -> None:
    fire.Fire(run_evaluator)


if __name__ == "__main__":
    main()
