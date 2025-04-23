import streamlit as st
import os
import pandas as pd
from datetime import datetime
from crewai import Agent, Task, Process, Crew
from crewai_tools import SerperDevTool
from crewai import LLM

# Set page configuration
st.set_page_config(
    page_title="Compliance Bot MARK III",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better looks
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput, .stSelectbox, .stNumberInput {
        margin-bottom: 20px;
    }
    .report-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .header-container {
        background-color: #4b6584;
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .subheader {
        font-size: 20px;
        margin-bottom: 20px;
    }
    .question-label {
        font-weight: 500;
        margin-bottom: 5px;
        color: #2c3e50;
    }
    .form-container {
        background-color: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 0 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #4b6584;
        color: white;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #3c526d;
    }
    .input-container {
        margin-bottom: 15px;
        padding: 5px;
        border-radius: 5px;
    }
    .input-container:hover {
        background-color: #f0f2f5;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1>Compliance Bot MARK III</h1>
    <p class="subheader">Automated Compliance Reporting for Companies Act, 2013</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for API keys
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
if 'serper_api_key' not in st.session_state:
    st.session_state.serper_api_key = os.environ.get("SERPER_API_KEY", "")
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = ""

# Sidebar with API key inputs
with st.sidebar:
    st.header("API Configuration")
    
    st.session_state.openai_api_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        value=st.session_state.openai_api_key
    )
    
    st.session_state.serper_api_key = st.text_input(
        "Serper API Key", 
        type="password", 
        value=st.session_state.serper_api_key
    )
    
    st.session_state.groq_api_key = st.text_input(
        "Groq API Key", 
        type="password", 
        value=st.session_state.groq_api_key
    )
    
    if st.button("Save API Keys"):
        if st.session_state.openai_api_key:
            os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
            st.success("OpenAI API key saved!")
        if st.session_state.serper_api_key:
            os.environ["SERPER_API_KEY"] = st.session_state.serper_api_key
            st.success("Serper API key saved!")
        if st.session_state.groq_api_key:
            st.success("Groq API key saved!")
        
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Compliance Bot MARK III automatically analyzes your company details and generates a comprehensive report of applicable compliance obligations under the Companies Act, 2013.")

# Main content
st.markdown("### Company Compliance Questionnaire")
st.markdown("Please provide the following information about your company to determine your compliance requirements.")

# Compliance questions in a form
compliance_questions = [
    "1. What is the type of your company?",
    "2. Is your company listed on a stock exchange?",
    "3. Is your company a Small Company under the Companies Act?",
    "4. Is your company a One Person Company (OPC)?",
    "5. Is your company a Section 8 (Not-for-profit) Company?",
    "6. Is your company a Holding or Subsidiary of another company?",
    "7. What is your company's Paid-up Share Capital? (in ₹ Crores)",
    "8. What is your company's Turnover? (in ₹ Crores)",
    "9. What is your company's Net Profit (Profit Before Tax)? (in ₹ Crores)",
    "10. What is the total amount of your borrowings from banks or public financial institutions? (in ₹ Crores)",
    "11. Do you have any public deposits outstanding?",
    "12. Are there any debentures issued and outstanding?",
    "13. How many shareholders / debenture holders / other security holders does your company have?",
    "14. Do you already maintain e-form records electronically under section 120?",
    "15. Does your company already file financials in XBRL format?",
    "16. What is the total number of employees in your company?"
]

question_hints = [
    "(Private / Public / Listed / Unlisted / Government / OPC / Section 8 / Dormant / Small)",
    "(Yes / No)",
    "(Yes / No / Not Sure)",
    "(Yes / No)",
    "(Yes / No)",
    "(Yes / No)",
    "",
    "",
    "",
    "",
    "(Yes / No)",
    "(Yes / No)",
    "",
    "(Yes / No)",
    "(Yes / No / Not Sure)",
    ""
]

st.markdown('<div class="form-container">', unsafe_allow_html=True)
with st.form("compliance_form"):
    compliance_answers = []
    col1, col2 = st.columns(2)
    
    for i, (question, hint) in enumerate(zip(compliance_questions, question_hints)):
        if i % 2 == 0:
            with col1:
                st.markdown(f'<div class="input-container">', unsafe_allow_html=True)
                st.markdown(f'<p class="question-label">{question}</p>', unsafe_allow_html=True)
                if hint:
                    answer = st.text_input(f"{hint}", key=f"q{i}", label_visibility="collapsed")
                else:
                    answer = st.text_input("", key=f"q{i}", label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            with col2:
                st.markdown(f'<div class="input-container">', unsafe_allow_html=True)
                st.markdown(f'<p class="question-label">{question}</p>', unsafe_allow_html=True)
                if hint:
                    answer = st.text_input(f"{hint}", key=f"q{i}", label_visibility="collapsed")
                else:
                    answer = st.text_input("", key=f"q{i}", label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Store the original question with the hint
        full_question = f"{question} {hint}"
        compliance_answers.append({"question": full_question, "answer": answer})
    
    # Date input for compliance deadline calculations
    st.markdown(f'<p class="question-label">Reference Date for Compliance Deadlines</p>', unsafe_allow_html=True)
    reference_date = st.date_input("", datetime.now(), label_visibility="collapsed")
    
    submitted = st.form_submit_button("Generate Compliance Report", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Processing when form is submitted
if submitted:
    with st.spinner("Generating your compliance report... This may take a few minutes..."):
        try:
            # Setup CrewAI components
            search_tool = SerperDevTool()
            
            # Set up LLM - Use the saved Groq API key from session state
            llm_deepseek = LLM(
                model="groq/deepseek-r1-distill-llama-70b",
                api_key=st.session_state.groq_api_key if st.session_state.groq_api_key else "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"
            )
            
            # Create agent
            compliance_agent = Agent(
                role="Regulatory Compliance Analyst",
                goal="To analyze company details and generate a comprehensive markdown report of applicable compliance obligations under the Companies Act, 2013.",
                backstory=(
                    "You are a top-tier regulatory compliance analyst specializing in Indian corporate law. "
                    "You are highly skilled at interpreting company-specific information to determine which sections of the Companies Act, 2013 apply. "
                    "You always rely on official government sources and use the Ministry of Corporate Affairs website (https://www.mca.gov.in) as your only source of truth. "
                    "You use search tools to find relevant thresholds, forms, and deadlines, and present your findings in a clear, tabular markdown report "
                    "suitable for audit or legal review."
                ),
                llm=llm_deepseek,
                tools=[search_tool],
                memory=True,
                verbose=True
            )
            
            # Create task
            compliance_lookup_task = Task(
                description=(
                    "You are provided with structured compliance intake data from a company (see: {data}) "
                    "and the current reference date (see: {date}). "
                    "Your task is to determine which legal compliance obligations apply to the company under the Companies Act, 2013. "
                    "You must use only official sources from the Ministry of Corporate Affairs (https://www.mca.gov.in) to validate all thresholds, conditions, forms, and deadlines."
                ),
                expected_output=(
                    "Generate a well-structured **Markdown (.md)** table that includes a full compliance summary for the company. "
                    "You must not just list applicable compliances — also show inapplicable, missing, or error-prone cases to help the user correct them.\n\n"

                    "**The markdown table must contain the following columns:**\n"
                    "- Compliance Area (e.g., CSR Committee, Secretarial Audit)\n"
                    "- Section (e.g., 135(1), 204(1))\n"
                    "- Form (if applicable, e.g., MR-3, MGT-8)\n"
                    "- Applicable (✅/❌)\n"
                    "- Trigger or Reason (e.g., 'Net Profit > ₹5 Cr', or 'Does not meet XBRL condition')\n"
                    "- Legal Deadline (e.g., 'within 180 days of financial year end')\n"
                    "- Due Date (calculated from {date})\n"
                    "- Status/Error (e.g., 'Compliant', 'Missing input: Paid-up Capital', 'Exempted due to Small Company')\n"
                    "- Source (URL from mca.gov.in)\n\n"

                    "**You must handle the following cases:**\n"
                    "- ✅ Clearly applicable compliances with due dates.\n"
                    "- ❌ Inapplicable ones with reasons why they do not apply.\n"
                    "- ⚠️ Missing or invalid inputs (e.g., blank fields, ambiguous entries).\n"
                    "- ❗ Any edge cases, exemptions (e.g., OPC, Section 8 Company), or potential legal risks.\n\n"

                    "🛑 **Important Rules:**\n"
                    "- Use only content found via 'site:mca.gov.in' search queries.\n"
                    "- The table must be a clean, valid markdown table viewable on GitHub.\n"
                    "- For each entry, provide a real MCA.gov.in URL as the source.\n"
                    "- Do not guess thresholds — look them up.\n"
                    "- Ensure all legal deadlines are calculated from the current date ({date}).\n"
                    "- Do not omit entries — even inapplicable ones must be recorded."
                    "- The report generated should be beautifully presented."
                ),
                agent=compliance_agent,
                output_file="compliance.md"
            )
            
            # Create and run crew
            crew = Crew(
                agents=[compliance_agent],
                tasks=[compliance_lookup_task],
                process=Process.sequential
            )
            
            # Format the date as DD-MM-YYYY
            formatted_date = reference_date.strftime("%d-%m-%Y")
            
            # Run the crew
            result = crew.kickoff({"data": compliance_answers, "date": formatted_date})
            
            # Display the result
            st.markdown("<div class='report-container'>", unsafe_allow_html=True)
            st.markdown("## Your Compliance Report")
            st.markdown(result)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Download button for the report
            st.download_button(
                label="Download Compliance Report",
                data=result,
                file_name="compliance_report.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error("Please check your API keys and try again.")

# Footer
st.markdown("---")
st.markdown("© 2025 Compliance Bot MARK III. This tool is for informational purposes only and does not constitute legal advice.")
