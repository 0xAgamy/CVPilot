import tempfile
import unittest
from pathlib import Path

from src.agents.parser.parser_node import ParserNode
from src.agents.prompts.prompt_management import prompt_template_config
from src.helpers.helpers import (
    get_cv_source_format,
    read_cv_text,
    validate_latex_output,
)
from src.models.models import AgentInputs, AgentState, ResumeArtifacts


class LatexInputTests(unittest.TestCase):
    def test_recognizes_tex_and_tax_extensions_case_insensitively(self):
        self.assertEqual(get_cv_source_format("resume.tex"), "latex")
        self.assertEqual(get_cv_source_format("resume.TEX"), "latex")
        self.assertEqual(get_cv_source_format("resume.tax"), "latex")
        self.assertEqual(get_cv_source_format("resume.docx"), "markdown")
        self.assertIsNone(get_cv_source_format("resume.pdf"))

    def test_latex_source_is_read_without_conversion(self):
        source = (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\section*{Experience}\n"
            "Built a CV % unchanged\n"
            "\\end{document}\n"
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resume.tex"
            path.write_text(source, encoding="utf-8")
            self.assertEqual(read_cv_text(str(path), path.name), source)

    def test_optimizer_prompt_preserves_latex_template(self):
        template = prompt_template_config(
            "src/agents/prompts/optimizer_agent.yaml",
            "optimizer_agent",
        )
        prompt = template.render(
            jd="Python engineer",
            analysis_report="Report",
            old_resume="\\documentclass{article}",
            critique="None",
            source_format="latex",
        )

        self.assertIn("complete raw LaTeX CV", prompt)
        self.assertIn("do not replace the template", prompt)

    def test_latex_output_must_keep_source_preamble(self):
        source = (
            "\\documentclass{moderncv}\n"
            "\\usepackage{fontspec}\n"
            "\\begin{document}\n"
            "Original content\n"
            "\\end{document}\n"
        )
        validate_latex_output(
            source,
            source.replace("Original content", "Optimized content"),
        )

        with self.assertRaises(ValueError):
            validate_latex_output(
                source,
                "\\documentclass{article}\n"
                "\\begin{document}\n"
                "Optimized content\n"
                "\\end{document}\n",
            )

        with self.assertRaises(ValueError):
            validate_latex_output(source, "# Markdown instead of LaTeX")

    def test_parser_bypasses_generic_formatter_for_latex_source(self):
        optimized_latex = (
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\section*{Experience}\n"
            "Optimized content\n"
            "\\end{document}\n"
        )
        state = AgentState(
            inputs=AgentInputs(
                job_description="Python engineer",
                source_cv=optimized_latex,
                source_format="latex",
            ),
            artifacts=ResumeArtifacts(optimized_cv=optimized_latex),
        )

        # The LaTeX path returns before touching the parser's LLM/template.
        node = object.__new__(ParserNode)
        update = node(state)

        self.assertEqual(update["artifacts"].parsed_cv, optimized_latex)


if __name__ == "__main__":
    unittest.main()
