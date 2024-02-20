import streamlit as st
import requests
import PyPDF2  # For PDFs
from docx import Document  # For DOCX files
from openai import OpenAI
import os
from os import environ
from dotenv import load_dotenv
load_dotenv()




# st. set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .appview-container .main .block-container {
        padding-top: 2rem;
        margin: 0;
    }
    .css-usj992 {
    background-color: transparent;
    }
    .subtitle {
        margin-bottom: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "<h1 style='text-align: center; padding: 10px;'>SimpliMedi-Assist</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h5 class='subtitle' style='text-align: center; padding: 2px;'>Your Health in Plain English</h5>",
    unsafe_allow_html=True
)


# Create a Streamlit file uploader widget
uploaded_file = st.file_uploader(
    "Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])


# Check if a file has been uploaded
if uploaded_file is not None:
    # Load the document
    st.write("Loading document...")

    file_extension = uploaded_file.name.split(".")[-1]

    if file_extension == "pdf":
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader (uploaded_file)
        text = "".join(
            pdf_reader.pages[page_num]. extract_text()
            for page_num in range(len(pdf_reader.pages))
        )
    elif file_extension == "docx":
        # Extract text from DOCX
        docx_document = Document(uploaded_file)
        text = "".join(paragraph.text + "\n" for paragraph in docx_document.paragraphs)
    elif file_extension == "txt":
        # Read text directly from TXT file
        text = uploaded_file.getvalue().decode("utf-8")

    # Display extracted text
    st.write("Document loaded successfully!")
    
    preview_length = 100  # Number of words for preview
    preview_text = f"{text[:1000]} ..."
    # st.text(preview_text)

    # Send extracted text via API to Flask service
    api_url = "https://simpimedi-assist.onrender.com/"
    response = requests.post(api_url, data=text.encode("utf-8"))

    # Check if the request was successful
    if response.status_code == 200:
        st.success("Extracted text sent successfully to the Flask service!")
    else:
        st.error(
            f"Failed to send extracted text to the Flask service. Status code: {response.status_code}"
        )

    # Extract the message from the response JSON
    response_json = response.json()
    message = response_json.get("response", {}).get("message", "")  

    # Split the page into two columns
    left_column, right_column = st.columns(2)

    # Content for the left column (OpenAI results)
    with left_column:
        st.subheader("OpenAI Results")
        # Add content specific to OpenAI results
        client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
        )

        query = f"""
        Assume the role of a medical doctor
        Take the medical report from {text} and explain it to my in very simple english 
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="gpt-3.5-turbo",
        )
        st.write(f"Response message: {chat_completion.choices[0].message.content}")

    # Content for the right column (OpenAI + RAG results)
    with right_column:
        st.subheader("OpenAI + RAG Results")
        # Add content for OpenAI + RAG results
        st.write(f"Response message: {message}")

    # st.write(f"Response message: {message}")