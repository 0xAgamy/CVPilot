# CVPilot

**AI-Powered CV Optimization Multi-Agent System**

CVPilot is an intelligent, collaborative multi-agent system built with **LangGraph** and **FastAPI**. It evaluates resumes, identifies weaknesses, optimizes content for Applicant Tracking Systems (ATS), and customizes applications for target roles using structured, type-safe LLM outputs.

## ✨ Features

- 🤖 **Multi-Agent Architecture**: Specialized agents (Analyser, Optimizer, Critic, Parser) working together in a LangGraph workflow.
- 🎯 **ATS Optimization**: Tailors your CV to match specific job descriptions with actionable, iterative feedback.
- 🔄 **Smart Critique Loop**: The Critic agent evaluates the optimized CV and loops back to the Optimizer until a quality score threshold is met.
- 📐 **Structured Outputs**: Leverages the `instructor` library to guarantee reliable, parseable Pydantic models instead of fragile raw text parsing.
- ⚡ **Async FastAPI Backend**: High-performance API ready for integration with any frontend
- 💻 **Built-in Streamlit UI**: A clean, user-friendly interface to upload your CV, paste the job description, and download the optimized result.

- 📄 **Document Processing**: Automatically converts `.docx` and other supported formats to Markdown for LLM processing using `markitdown`.

## 🏗️ Architecture

The core intelligence is powered by a LangGraph state machine:
1. **START** → **Analyser**: Analyzes the input CV against the Job Description (JD).
2. **Optimizer**: Generates an improved version of the CV based on the analysis.
3. **Critic**: Scores the optimized CV (0.0 - 1.0). 
   - If `score >= threshold` (default `0.85`) or `max_iterations` (default `3`) is reached → proceeds to **Parser**.
   - Otherwise → loops back to **Optimizer** with specific critique feedback appended to the state.
4. **Parser**: Converts the final optimized Markdown into a clean, structured format (e.g., LaTeX).
5. **END**

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/0xAgamy/CVPilot.git
cd CVPilot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a .env file in the root directory (you can copy from .env.example):
```bash
cp .env.example .env

```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---


<div align="center">
Built with ❤️ by <a href="https://github.com/0xAgamy">Mohamed Elagamy</a>
</div>