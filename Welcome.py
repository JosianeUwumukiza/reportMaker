import streamlit as st


def main():
    st.title("Welcome to the AI-Powered Report making helper App!")
    st.markdown("""
    ### Overview
    This application helps you:
    1. **Generate detailed reports** from bullet points using AI.
    2. **Visualize your data** with interactive charts.
    3. **Download** your final reports in multiple formats.

    ---
    
    ### How to Use
    - **Step 1**: Go to the **Login** page (in the sidebar) to authenticate.
    - **Step 2**: Navigate to the **Home** page to generate reports and visualize data.
    - **Step 3**: Download your final reports as `.txt`, `.docx`, or `.pdf`.

    We hope you find this app useful and intuitive. Feel free to explore the features and 
    provide any feedback you may have!

    ---
    """)

    st.info("Use the sidebar to navigate between pages.")

if __name__ == "__main__":
    main()
