import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import io
import os
from openai import OpenAI
from streamlit_quill import st_quill
import markdown2


# --- Load API Key ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Report Generator Function ---
def generate_report(bullet_points: str) -> str:
    try:
        if client.api_key:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": f"Generate a detailed report based on these bullet points: {bullet_points}"}
                ]
            )
            return response.choices[0].message.content.strip()
        else:
            return "Error: OpenAI API key not found."
    except Exception as e:
        return f"Error generating report: {str(e)}"
#styling
def local_css(file_name: str):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# --- Main Page ---
def main_page():
    local_css("./style.css")

    if "report_text" not in st.session_state:
        st.session_state.report_text = ""
    if "generated" not in st.session_state:
        st.session_state.generated = False

    st.title(" AI Report Assistant +  Data Visualizer")

    # --- Report Generation Section ---
    st.header(" Generate a Report from Bullet Points")
    bullet_points = st.text_area("Enter bullet points:")

    if st.button("Generate Report"):
        with st.spinner("Generating your report..."):
            st.session_state.report_text = generate_report(bullet_points)
            st.session_state.generated = True

    st.markdown("### Edit or Finalize Your Report")

    initial_value = st.session_state.report_text if st.session_state.get("generated") else ""
    markdown_html = markdown2.markdown(st.session_state.report_text)
    quill_key = "editor" if not st.session_state.get("generated") else "editor_updated"

    quill_content = st_quill(value=markdown_html, html=True, key=quill_key)
    st.session_state.final_report = quill_content

    # Store final report for exporting

    # --- Download Options ---
    st.subheader(" Download Your Report")
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.get("final_report"):
            st.download_button(
                label="Download as HTML",
                data=st.session_state.final_report.encode("utf-8"),
                file_name="formatted_report.html",
                mime="text/html"
            )

    with col2:
        if st.session_state.get("final_report"):
            doc = Document()
            doc.add_paragraph(st.session_state.final_report)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download .docx",
                data=buffer,
                file_name="formatted_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # --- Data Visualization Section ---
    st.header(" Upload a CSV for Visualization")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write(" Data Preview", data.head())

        x_column = st.selectbox("Select X-axis", data.columns)
        y_column = st.selectbox("Select Y-axis", data.columns)

        chart_type = st.selectbox("Chart Type", [
            "Line Chart", "Bar Chart", "Pie Chart", "Scatter Plot", "Sankey Chart"
        ])

        if st.button("Generate Chart"):
            if chart_type == "Line Chart":
                fig = px.line(data, x=x_column, y=y_column)
            elif chart_type == "Bar Chart":
                fig = px.bar(data, x=x_column, y=y_column)
            elif chart_type == "Pie Chart":
                fig = px.pie(data, names=x_column, values=y_column)
            elif chart_type == "Scatter Plot":
                fig = px.scatter(data, x=x_column, y=y_column)
            elif chart_type == "Sankey Chart":
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=data[x_column].unique().tolist(),
                        color="blue"
                    ),
                    link=dict(
                        source=[0, 1, 0, 2, 3],
                        target=[1, 2, 3, 4, 4],
                        value=[1, 2, 2, 2, 1]
                    )
                )])
                fig.update_layout(title_text="Sankey Chart", font_size=10)

            st.plotly_chart(fig)

# --- Authentication Logic ---
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

check_authentication()

if st.session_state.authenticated:
    main_page()
else:
    st.error("🔒 You must log in first! Please go to the Login page.")
