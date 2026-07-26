from openai import OpenAI
from cohere import ClientV2
from dotenv import load_dotenv
import os
from models.models import AgentState, AnalyserResponseModel,OptimizerResponseModel, ParserResponseModel
from langgraph.graph import START, StateGraph, END
from jinja2 import Template
import instructor
import aspose.words as aw
from helpers.config import get_settings
st=get_settings()
MODEL_NAME=st.MODEL_NAME

gen_client= OpenAI(
    base_url=st.BASE_URL,
    api_key=st.API_KEY
)

client= instructor.from_openai(gen_client)
with open("../files/output_template.md", "r", encoding="utf-8") as file:
    markdown_tamplate = file.read()

def Analyser_node(state: AgentState) -> dict:
    prompt_template="""You are a Resume Analysis Engine specialized in evaluating candidate resumes against job descriptions.

    Your responsibility is NOT to rewrite the resume. Your responsibility is to deeply analyze the relationship between:

    1. A Job Description (JD)
    2. A Candidate Resume

    You provide structured insights that another AI agent will use to optimize the resume.

    Your analysis must be accurate, evidence-based, and never assume missing information.

    ---

    # Primary Objectives

    Analyze:

    - Job requirements
    - Candidate qualifications
    - Skill alignment
    - Experience relevance
    - ATS keyword coverage
    - Strengths
    - Weaknesses
    - Missing requirements
    - Improvement opportunities
    - unreleated skills or projects
    

    The goal is to create a full analysing Report and identify exactly what should be optimized.

    while remaining completely truthful and preserving factual accuracy.
    """.strip()
    prompt= Template(prompt_template)
    prompt=prompt.render()
    query_template= """

     ### job description
    {{ job_description }}


    ### markdown Resume
    {{ resume }}

    """.strip()

    query_prompt= Template(query_template)
    
    query=query_prompt.render(
        job_description=state.jd,
        resume= state.cv
    )
    response, raw_response= client.chat.completions.create_with_completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}

        ],
        response_model=AnalyserResponseModel,
    )

    return {
        "optimization_suggestion":response.optimization_suggestion,
        "score": response.score
    }


def Optimizer_node(state: AgentState) -> dict:
    prompt_template="""You are an Expert Resume Optimization Engine specialized in ATS (Applicant Tracking System) parsing, recruiter psychology, and job-specific tailoring.

    Your task is to transform the Original Resume into a highly targeted, ATS-friendly Optimized Resume using the Target Job Description and the Resume Analysis Report.

    ### CORE DIRECTIVES
    1. ZERO HALLUCINATION: You are strictly forbidden from inventing new jobs, degrees, skills, or metrics. You may only rephrase, restructure, and emphasize existing facts.
    2. IMPACT-DRIVEN BULLETS: Rewrite experience bullets using the "Action Verb + Task + Result/Metric" formula. Quantify achievements where possible based on the original text.
    3. ATS KEYWORD INTEGRATION: Naturally weave exact-match keywords and phrases from the Target Job Description into the Summary, Skills, and Experience sections. Do not "keyword stuff"; ensure it reads naturally.
    4. GAP HANDLING: If the JD requires a skill the candidate lacks, DO NOT lie. Instead, emphasize closely related transferable skills or highlight their ability to learn quickly.
    5. STANDARD FORMATTING: Use standard, ATS-readable section headers (e.g., "Professional Experience", "Education", "Skills"). Do not use tables, columns, or complex formatting.
    6. REMOVE unreleated Skills or project
    ### INPUTS

    <jd>
    {{ jd }}
    </jd>

    <analysis_report>
    {{ analysis_report }}
    </analysis_report>


    <old_resume>
    {{ old_resume }}
    </old_resume>
    """.strip()

    template=Template(prompt_template)
    prompt=template.render(
        jd= state.jd,
        analysis_report=state.optimization_suggestion,
        old_resume=state.cv
    )

    response, raw_response= client.chat.completions.create_with_completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "help me please"},

        ],
        response_model=OptimizerResponseModel,
    )

    return {
        "optimized_cv": response.optimized_cv,
        "score": float(response.score)
    }



def Parser_node(state: AgentState)-> dict:
    prompt_template=r"""
    You are the "Visual Stylist Agent," an expert typesetter and LaTeX developer specializing in document typography, layout, and professional resume/CV design. Your sole responsibility in this multi-agent pipeline is to take a fully optimized, plain-text Markdown CV and transform it into a visually stunning, highly readable, and professionally styled, compilable LaTeX document.

    # OBJECTIVE
    Transform the provided Markdown CV into a beautifully formatted LaTeX document. You must translate the Markdown syntax into proper LaTeX structures while enhancing the visual hierarchy, typography, and spacing without altering a single word, fact, or structural element of the original content.

    # STRICT CONSTRAINTS (CRITICAL)
    1. ZERO CONTENT MODIFICATION: Do not add, remove, rewrite, or summarize any text. Do not change dates, job titles, skills, or bullet points. The content is already optimized; your only job is to format and style it.
    2. NO CONVERSATIONAL FILLER: Do not output greetings, explanations, or concluding remarks (e.g., "Here is your styled CV"). Output ONLY the final, raw LaTeX code.
    3. ATS & READABILITY FIRST: The design must remain clean, professional, and easily parsable by both human eyes and Applicant Tracking Systems (ATS). Avoid overly complex TikZ graphics, background images, or distracting elements.
    4. COMPILATION READY: Keep in mind that your output will be directly compiled into a PDF. The code must be 100% syntactically correct, with all special characters (like &, %, $, #, _, {, }) properly escaped.

    # DESIGN SYSTEM & LATEX GUIDELINES
    Apply a "Modern Professional" design theme using the following specifications:

    ## Typography
    - Font Family: Use a clean, modern sans-serif font stack (e.g., using the `helvet` package for standard pdflatex, or `fontspec` with a modern font like Lato/Roboto if using xelatex/lualatex).
    - Base Font Size: 10pt to 11pt for body text (set in `\documentclass`).
    - Line Spacing: Use the `setspace` package for optimal readability (e.g., `\setstretch{1.15}` or `\onehalfspacing`).
    - Headings: Use the `titlesec` package to customize section formats. Use distinct font weights and sizes (e.g., Large/bfseries for sections, large/mdseries/itshape for subsections) to create hierarchy.

    ## Color Palette
    - Use the `xcolor` package with HTML hex codes.
    - Background: Pure white (default).
    - Primary Text: Dark charcoal (e.g., `\definecolor{primarytext}{HTML}{1F2937}`).
    - Secondary Text: Medium gray for dates, locations, and subtitles (e.g., `\definecolor{secondarytext}{HTML}{6B7280}`).
    - Accent Color: A professional, subtle color for headings, links, and dividers (e.g., Deep Navy `\definecolor{accent}{HTML}{1E3A8A}`).

    ## Spacing & Layout
    - Page Geometry: Use the `geometry` package to set comfortable margins (e.g., `margin=0.75in` or `top=0.6in, bottom=0.6in, left=0.75in, right=0.75in`) to maximize space without looking cramped.
    - Section Spacing: Use `titlesec` to add generous but tight spacing before and after sections (e.g., `\titlespacing*{\section}{0pt}{12pt}{6pt}`).
    - Lists: Use the `enumitem` package to create tight, clean bullet points (e.g., `\begin{itemize}[nosep, leftmargin=1.5em]`).

    # TECHNICAL IMPLEMENTATION INSTRUCTIONS
    You must translate the Markdown input into a complete, standalone LaTeX document:

    1. **The Preamble:** Begin with `\documentclass[11pt, a4paper]{article}`. Include all necessary packages (`geometry`, `xcolor`, `titlesec`, `enumitem`, `hyperref`, `setspace`, `helvet`/`fontspec`). Define your custom colors and section formats here.
    2. **Document Structure:** Wrap the content in `\begin{document}` and `\end{document}`. 
    3. **Header/Contact Info:** Create a clean, centered header for the name and contact info. Use `\href{url}{text}` for emails and links. Use a `tabular` environment or simple centered text with `\textcolor{secondarytext}{}` for contact details.
    4. **Sections & Content:** 
    - Convert Markdown `## Headers` to `\section{}`.
    - Convert Markdown `### Subheaders` to `\subsection{}` or custom formatted text (e.g., `\textbf{Job Title} \hfill \textcolor{secondarytext}{Date}`).
    - Convert Markdown `- bullets` to `\begin{itemize} \item ... \end{itemize}`.
    - Convert Markdown `**bold**` to `\textbf{}` and `*italic*` to `\textit{}`.

    # OUTPUT FORMAT
    Your output must be a single, continuous code block containing the complete, compilable LaTeX document. Do not wrap it in markdown code blocks (like ```latex), just output the raw LaTeX text directly so it can be parsed.

    Structure your output exactly like this:

    \documentclass[11pt, a4paper]{article}
    % --- PACKAGES ---
    \usepackage[utf8]{inputenc}
    \usepackage[margin=0.75in]{geometry}
    \usepackage{xcolor}
    \usepackage{titlesec}
    \usepackage{enumitem}
    \usepackage{hyperref}
    \usepackage{setspace}
    \usepackage{helvet} % or fontspec for xelatex
    \renewcommand{\familydefault}{\sfdefault}

    % --- COLORS ---
    \definecolor{primarytext}{HTML}{1F2937}
    \definecolor{secondarytext}{HTML}{6B7280}
    \definecolor{accent}{HTML}{1E3A8A}
    \color{primarytext}

    % --- TYPOGRAPHY & SECTIONS ---
    \titleformat{\section}{\Large\bfseries\color{accent}}{}{0em}{}[\titlerule]
    \titlespacing*{\section}{0pt}{12pt}{6pt}
    \setstretch{1.15}

    \begin{document}

    % --- HEADER ---
    \begin{center}
        {\Huge\bfseries\color{accent} [Name]} \\
        \vspace{4pt}
        \textcolor{secondarytext}{[Contact Info / Links separated by $\cdot$ or |]}
    \end{center}
    \vspace{8pt}

    % --- SUMMARY ---
    \section{[Section Title]}
    [Content]

    % --- EXPERIENCE ---
    \section{[Section Title]}
    \subsection*{\textbf{[Job Title]} \hfill \textcolor{secondarytext}{[Date]}}
    \textit{\textcolor{secondarytext}{[Company] | [Location]}}
    \vspace{2pt}
    \begin{itemize}[nosep, leftmargin=1.5em]
        \item [Bullet point]
        \item [Bullet point]
    \end{itemize}

    % ... [Continue for the rest of the CV] ...

    \end{document}

    # INPUT
    You will now receive the optimized Markdown CV and a template. Process it immediately according to these rules, translating the Markdown into the LaTeX structure defined above.

    ### here is the optimized CV
    {{ optimized_cv }}

    ### here is the template
    {{ markdown_tamplate }}
    """.strip()
    template= Template(prompt_template)
    prompt=template.render(
        optimized_cv= state.optimized_cv,
        markdown_template=markdown_tamplate
    )

    response, raw_response= client.chat.completions.create_with_completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "help me please"},

        ],
        response_model=ParserResponseModel,
    )
    with open("../output/optimized_cv.tex", 'w', encoding="utf-8") as file:
        file.write(response.parsed_cv)
    return{
        "optimized_cv":response.parsed_cv,
        "output_file_path":"../output/optimized_cv.tex"
    }
