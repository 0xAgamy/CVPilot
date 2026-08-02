import requests
import streamlit as st

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="CV Optimization Assistant",
    page_icon="📄",
    layout="wide",
)

# --------------------------------------------------
# Custom CSS for minor UI polish
# --------------------------------------------------
st.markdown("""
    <style>
    /* Improve spacing and typography */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    /* Style the pipeline steps in sidebar */
    .pipeline-step {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        padding: 10px;
        border-radius: 6px;
        background-color: #f0f2f6;
        transition: background-color 0.2s;
    }
    .pipeline-step:hover {
        background-color: #e6e9ef;
    }
    .pipeline-step span {
        margin-right: 12px;
        font-size: 1.3em;
    }
    </style>
""", unsafe_allow_html=True)



# --------------------------------------------------
# API Function
# --------------------------------------------------
def optimize_cv(cv_file, job_description):
    files = {
        "cv": (
            cv_file.name,
            cv_file,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }

    data = {
        "jd": job_description,
    }

    try:
        response = requests.post(
            "http://localhost:8000/agent_call",
            files=files,
            data=data,
            timeout=600,
        )

        if response.ok:
            return True, response.json()
        else:
            return False, f"Server returned {response.status_code}: {response.text}"

    except requests.exceptions.ConnectionError:
        return False, "Unable to connect to the backend. Is the server running on http://localhost:8000?"
    except requests.exceptions.Timeout:
        return False, "Request timed out. The multi-agent pipeline might be taking longer than expected."
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"


# --------------------------------------------------
# Main Area
# --------------------------------------------------
st.title("🚀 Multi-Agent CV Optimization")
st.markdown(
    "Upload your current CV, paste the target Job Description, "
    "and let our AI agents generate an optimized, ATS-friendly LaTeX resume."
)

st.divider()

# Input Section
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 1. Upload your CV")
    cv_file = st.file_uploader(
        "Drop your .docx file here",
        type=["docx"],
        help="Ensure your CV is in .docx format for optimal parsing by the CV Parser agent."
    )
    if cv_file is not None:
        st.success(f"✅ Successfully uploaded: **{cv_file.name}**")

with col2:
    st.markdown("### 📋 2. Target Job Description")
    job_description = st.text_area(
        "Paste the Job Description",
        height=350,
        placeholder="e.g., We are looking for a Senior Data Scientist with 5+ years of experience in Python, machine learning, and cloud deployment...",
        help="Paste the full job description to allow the JD Analyzer to extract all relevant keywords and requirements."
    )

st.divider()

# Action Button
optimize = st.button(
    "🚀 Optimize CV",
    use_container_width=True,
    type="primary",
)

# --------------------------------------------------
# Run Pipeline
# --------------------------------------------------
if optimize:
    if cv_file is None:
        st.error("⚠️ **Missing File:** Please upload a `.docx` CV before proceeding.")
        st.stop()

    if not job_description.strip():
        st.error("⚠️ **Missing Information:** Please provide a Job Description.")
        st.stop()

    with st.status("🔄 Initializing multi-agent pipeline...", expanded=True) as status:
        
        success, result = optimize_cv(
            cv_file=cv_file,
            job_description=job_description,
        )

        if success:
            status.update(
                label="✅ Optimization completed successfully!",
                state="complete",
            )
            
            st.balloons() # Celebrate success!
            
            # Use tabs for a clean, organized results view
            tab_analysis, tab_latex, tab_download = st.tabs([
                "📊 Analysis & Suggestions", 
                "📝 LaTeX Code", 
                "📥 Download"
            ])
            
            with tab_analysis:
                col_metric, col_sugg = st.columns([1, 2])
                
                with col_metric:
                    score = result.get("score", "N/A")
                    # Try to format as a number for a better metric display
                    try:
                        score_val = float(score)
                        st.metric(
                            label="🎯 ATS Match Score", 
                            value=f"{score_val}/100",
                            delta=f"+{score_val - 70}%" if score_val >= 70 else f"{score_val - 70}%",
                            delta_color="normal" if score_val >= 70 else "inverse"
                        )
                    except (ValueError, TypeError):
                        st.metric(label="🎯 Optimization Score", value=score)
                        
                with col_sugg:
                    st.markdown("#### 💡 Optimization Suggestions")
                    # Render as rich markdown instead of a code block for better readability
                    suggestions = result.get("optimization_suggestions", "No suggestions provided.")
                    st.markdown(suggestions, unsafe_allow_html=True)
            
            with tab_latex:
                st.markdown("#### Optimized LaTeX Code")
                st.info("You can copy this code and paste it into [Overleaf](https://www.overleaf.com/) or your local LaTeX editor.")
                latex_code = result.get("optimized_cv", "")
                st.code(latex_code, language="latex")
                
            with tab_download:
                st.markdown("#### 📥 Download Your Optimized CV")
                st.info("Download the `.tex` file and compile it using your preferred LaTeX environment.")
                
                latex_code = result.get("optimized_cv", "")
                st.download_button(
                    label="📥 Download optimized_cv.tex",
                    data=latex_code,
                    file_name="optimized_cv.tex",
                    mime="application/x-tex",
                    use_container_width=True,
                    type="primary",
                )
                
        else:
            status.update(
                label="❌ Optimization failed.",
                state="error",
            )
            st.error(f"**Error:** {result}")
            st.info(
                "💡 **Troubleshooting:**\n"
                "- Ensure the backend server is running on `http://localhost:8000`.\n"
                "- Check that the `/agent_call` endpoint is accessible and functioning correctly.\n"
                "- Verify your `.docx` file is not corrupted or password-protected."
            )