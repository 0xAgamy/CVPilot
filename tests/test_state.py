import unittest

from pydantic import ValidationError

from src.models.models import (
    AgentInputs,
    AgentState,
    AnalyserResponseModel,
    CriticResponseModel,
    CritiqueResult,
    ResumeArtifacts,
    WorkflowConfig,
)


class AgentStateTests(unittest.TestCase):
    def make_state(self) -> AgentState:
        return AgentState(
            inputs=AgentInputs(
                job_description="Target role",
                source_cv="# Candidate",
            )
        )

    def test_groups_inputs_workflow_and_artifacts(self):
        state = self.make_state()

        self.assertEqual(state.inputs.job_description, "Target role")
        self.assertEqual(state.workflow.max_iterations, 3)
        self.assertIsNone(state.artifacts.optimized_cv)
        self.assertIsNone(state.review)
        self.assertEqual(state.critique_history, [])

    def test_accepts_legacy_input_aliases(self):
        inputs = AgentInputs(jd="Target role", cv="# Candidate")

        self.assertEqual(inputs.job_description, "Target role")
        self.assertEqual(inputs.source_cv, "# Candidate")

    def test_history_defaults_are_not_shared(self):
        first = self.make_state()
        second = self.make_state()

        first.critique_history.append(
            CritiqueResult(
                iteration=1,
                score=0.5,
                critique="Add evidence",
                approved=False,
            )
        )

        self.assertEqual(second.critique_history, [])

    def test_rejected_review_requires_actionable_critique(self):
        with self.assertRaises(ValidationError):
            CritiqueResult(
                iteration=1,
                score=0.5,
                critique="",
                approved=False,
            )

    def test_workflow_values_are_bounded(self):
        for field, value in (
            ("score_threshold", -0.1),
            ("score_threshold", 1.1),
            ("max_iterations", 0),
        ):
            with (
                self.subTest(field=field, value=value),
                self.assertRaises(ValidationError),
            ):
                WorkflowConfig(**{field: value})

    def test_llm_responses_are_strict(self):
        with self.assertRaises(ValidationError):
            AnalyserResponseModel(analysing_report="   ")

        for score in (-0.1, 1.1):
            with (
                self.subTest(score=score),
                self.assertRaises(ValidationError),
            ):
                CriticResponseModel(
                    score=score,
                    approved=False,
                    critique="Add evidence",
                )

    def test_finalization_rules(self):
        state = self.make_state()
        self.assertFalse(state.should_finalize)

        state.review = CritiqueResult(
            iteration=1,
            score=0.5,
            critique="Add evidence",
            approved=False,
        )
        self.assertFalse(state.should_finalize)

        state.review.score = state.workflow.score_threshold
        self.assertTrue(state.should_finalize)

        state.review.score = 0.5
        state.review.approved = True
        self.assertTrue(state.should_finalize)

        state.review.approved = False
        state.review.iteration = state.workflow.max_iterations
        self.assertTrue(state.should_finalize)

    def test_final_cv_prefers_parsed_output(self):
        state = self.make_state()
        state.artifacts = ResumeArtifacts(optimized_cv="# Optimized")
        self.assertEqual(state.final_cv, "# Optimized")

        state.artifacts.parsed_cv = r"\documentclass{article}\end{document}"
        self.assertEqual(state.final_cv, r"\documentclass{article}\end{document}")


if __name__ == "__main__":
    unittest.main()
