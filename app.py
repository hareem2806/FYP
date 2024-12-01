import os
import json
import re
from bs4 import BeautifulSoup
import requests
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
import nltk
from urllib.parse import urljoin, urlparse

# Load environment variables (if needed for API keys)
load_dotenv()

# Initialize HuggingFace Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Download NLTK stopwords
nltk.download('stopwords')
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words('english'))

# Text Preprocessing Function
def preprocess_text(text):
    text = re.sub(r'[^A-Za-z\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    text = text.lower()  # Convert to lowercase
    tokens = text.split()
    cleaned_text = " ".join([word for word in tokens if word not in STOPWORDS])  # Remove stopwords
    return cleaned_text

# Scrape Website with BeautifulSoup
def scrape_website(url):
    visited_urls = set()
    scraped_data = {}

    def scrape_page(url):
        if url in visited_urls:
            return
        visited_urls.add(url)

        try:
          headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}
          response = requests.get(url, headers=headers)

        except requests.RequestException as e:
            st.error(f"Failed to retrieve {url}: {e}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract relevant content
        relevant_tags = ['p', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div']
        content = []
        for tag in relevant_tags:
            for element in soup.find_all(tag):
                text = element.get_text(strip=True)
                if text:
                    content.append(text)

        if content:
            scraped_data[url] = " ".join(content)

        # Find and process all internal links on the page
        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if urlparse(next_url).netloc == urlparse(url).netloc and next_url not in visited_urls:
                scrape_page(next_url)

    scrape_page(url)
    return scraped_data

# PDF Text Extraction
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Handle None
    return preprocess_text(text)

# Split Text into Manageable Chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

# Create FAISS Vector Store
def get_vector_store(text_chunks):
    vector_store = FAISS.from_texts(text_chunks, embeddings)  # Create FAISS from chunks
    vector_store.save_local('./faiss_index')  # Save locally

# Build Conversational Chain
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer is not in
    provided context, just say, "answer is not available in the context." Don't provide the wrong answer.\n\n
    Context:\n {context}\n
    Question: \n{question}\n

    Answer:
    """
    model = Ollama(model="llama3.2")  # Initialize LLaMA model
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

# Handle User Input and Process Questions
def user_input(user_question):
    new_db = FAISS.load_local('./faiss_index', embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    st.write("Reply: ", response["output_text"])

# Main Function for Streamlit App
def main():
    st.set_page_config("Chat PDF & URL", layout="wide")
    st.header("Chat with PDF or URL using Ollama 💁")

    user_question = st.text_input("Ask a Question from the Processed Data")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        # User selects between PDF or URL
        option = st.radio("Choose input type:", ("PDF", "URL"))

        if option == "PDF":
            pdf_docs = st.file_uploader("Upload PDF Files:", accept_multiple_files=True)
            if st.button("Submit & Process"):
                with st.spinner("Processing..."):
                    if pdf_docs:
                        raw_text = get_pdf_text(pdf_docs)
                        text_chunks = get_text_chunks(raw_text)
                        get_vector_store(text_chunks)
                        st.success("PDF data is ready for queries!")
                    else:
                        st.error("No PDF files were uploaded.")

        elif option == "URL":
            url_input = st.text_input("Enter a URL to scrape text:")
            if st.button("Submit & Process"):
                with st.spinner("Processing..."):
                    if url_input:
                        try:
                            # Run BeautifulSoup and get scraped data
                            scraped_data = scrape_website(url_input)

                            # Combine and preprocess scraped data
                            raw_text = preprocess_text(" ".join(scraped_data.values()))

                            # Split text into chunks and index in FAISS
                            text_chunks = get_text_chunks(raw_text)
                            get_vector_store(text_chunks)

                            st.success("Scraped data is ready for queries!")
                        except Exception as e:
                            st.error(f"Failed to scrape or process data: {e}")
                    else:
                        st.error("No URL was provided.")

if __name__ == "__main__":
    main()
