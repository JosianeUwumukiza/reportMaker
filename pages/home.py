import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from docx import Document
import io
from fpdf import FPDF

# --- Load custom CSS ---
def local_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main_page():
    local_css("./style.css")

    if "report_text" not in st.session_state:
        st.session_state.report_text = "Your report will show up here."

    st.title("Welcome to the Report Making Helper")

    # Report Generation Section
    st.markdown("## 📄 Report Generator")
    bullet_points = st.text_area("Enter bullet points for the report:")

    if st.button("Generate Report"):

        response = requests.post(
            "http://127.0.0.1:5000/generate_report",
            json={"bullet_points": bullet_points}
        )
        report = response.json().get("report", "No report generated.")
        st.session_state.report_text = report

    # Display Report Output
    st.markdown("## 🔍 Report Output")
    st.text_area("Generated Report", value=st.session_state.report_text, height=300)

    # ---- Download Buttons ----
    st.markdown("###Download")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Download Report as .txt"):
            with open("report.txt", "w", encoding="utf-8") as file:
                file.write(st.session_state.report_text)
            st.success("Report saved successfully!")

    with col2:
        if st.button("Download Word Document (.docx)"):
            doc = Document()
            doc.add_paragraph(st.session_state.report_text)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="Download Report (.docx)",
                data=buffer,
                file_name="report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # ---- PDF Download ----
    # We'll create a PDF from the report text using the fpdf library.
    if st.button("Download PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # multi_cell automatically wraps text
        pdf.multi_cell(0, 10, st.session_state.report_text)

        pdf_output = pdf.output(dest="S").encode("latin-1")  # 'S' = return as string
        st.download_button(
            label="Download as PDF",
            data=pdf_output,
            file_name="report.pdf",
            mime="application/pdf"
        )

    # Data Visualization Section
    st.markdown("## 📊 Data Visualization")
    uploaded_file = st.file_uploader("Choose a CSV file for visualization", type="csv", key="csv_uploader")

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("Data Preview", data.head())
        
        x_column = st.selectbox("Select X-axis column", data.columns)
        y_column = st.selectbox("Select Y-axis column", data.columns)
        
        chart_type = st.selectbox("Select Chart Type", [
            "Line Chart",
            "Bar Chart",
            "Pie Chart",
            "Scatter Plot",
            "Sankey Chart"
        ])

        if st.button("Generate Chart"):
            if chart_type == "Line Chart":
                fig = px.line(data, x=x_column, y=y_column, title="Line Chart")
            elif chart_type == "Bar Chart":
                fig = px.bar(data, x=x_column, y=y_column, title="Bar Chart")
            elif chart_type == "Pie Chart":
                fig = px.pie(data, names=x_column, values=y_column, title="Pie Chart")
            elif chart_type == "Scatter Plot":
                fig = px.scatter(data, x=x_column, y=y_column, title="Scatter Plot")
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

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

check_authentication()

if st.session_state.authenticated:
    main_page()
else:
    st.error("You must log in first! Please go to the Login page.")
