import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import io
from fpdf import FPDF
import os
from openai import OpenAI

# --- Load API Key ---
# For Streamlit Cloud: set OPENAI_API_KEY in Secrets tab
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Generate Report Using OpenAI ---
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

# --- Optional: Custom Styling ---
def local_css(file_name: str):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Skip if CSS file doesn't exist

# --- Main Page ---
def main_page():
    local_css("./style.css")

    if "report_text" not in st.session_state:
        st.session_state.report_text = "Your report will show up here."

    st.title("📄 AI Report Assistant + Data Visualizer")

    # --- Report Generation ---
    st.header("Generate a Report from Bullet Points")
    bullet_points = st.text_area("Enter bullet points for the report:")

    if st.button("Generate Report"):
        st.session_state.report_text = generate_report(bullet_points)

    st.text_area("Generated Report", value=st.session_state.report_text, height=300)

    # --- Download Options ---
    st.subheader("Download Report")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Download as .txt"):
            with open("report.txt", "w", encoding="utf-8") as file:
                file.write(st.session_state.report_text)
            st.success("Report saved successfully!")

    with col2:
        if st.button("Download as .docx"):
            doc = Document()
            doc.add_paragraph(st.session_state.report_text)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.download_button(
                label="Download .docx",
                data=buffer,
                file_name="report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    if st.button("Download as PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, st.session_state.report_text)
        pdf_output = pdf.output(dest="S").encode("latin-1")
        st.download_button(
            label="Download as PDF",
            data=pdf_output,
            file_name="report.pdf",
            mime="application/pdf"
        )

    # --- Data Visualization ---
    st.header("📊 Upload CSV and Visualize Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("Data Preview", data.head())

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

# --- Authentication (Simple Placeholder) ---
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True  # Set to False if you add real login logic

check_authentication()

if st.session_state.authenticated:
    main_page()
else:
    st.error("You must log in first! Please go to the Login page.")
