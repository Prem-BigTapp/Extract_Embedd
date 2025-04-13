import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from groq import Groq
import fitz
import re

# API Keys and MongoDB
GROQ_API_KEY = "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"
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "pdf_data"
COLLECTION_NAME = "embedded_pdfs"

def extract_text_from_pdf(pdf_file_path):
    """1. Extract Text from PDF."""
    try:
        pdf_document = fitz.open(pdf_file_path)
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
        pdf_document.close()
        text = ' '.join(text.split())
        return text
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_file_path}")
        return None
    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")
        return None

def groq_llama_extract_tc(text):
    """2. LLM Processing: Identify Terms and Conditions."""
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
        Use the following context to extract the Terms and Conditions section. You need to check for the keyword Terms and Conditions and any sections that outlines the terms and conditions. 
        Context:
        {text}

        Extracted Terms and Conditions:
        """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=8192,
        )
        extracted_content = chat_completion.choices[0].message.content.strip()
        tc_text = extracted_content #<----- Reassignment.
        return tc_text

    except Exception as e:
        print(f"Error during Groq Llama API call: {e}")
        return None

def embed_and_store_tc(tc_text, document_name):
    """3. Embedding and 4. Storage (MongoDB)."""
    model = SentenceTransformer('all-mpnet-base-v2')
    try:
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', tc_text) # for better embedding.
        chunks = []
        chunk_size = 3
        overlap = 1
        for i in range(0, len(sentences), chunk_size - overlap):
            chunk = " ".join(sentences[i:i + chunk_size])
            chunks.append(chunk)

        embeddings = model.encode(chunks).tolist()

        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        pdf_collection = db[COLLECTION_NAME]

        pdf_collection.insert_one({
            "document_name": document_name,
            "chunks": chunks,
            "embeddings": embeddings,
        })
        print(f"Data inserted into database: {db.name}, collection: {pdf_collection.name}")
        return f"Extracted, embedded, and stored {len(chunks)} chunks from {document_name} in MongoDB."
    except Exception as e:
        print(f"Error embedding and storing: {e}")
        return f"Error embedding and storing: {e}"
    finally:
        if 'client' in locals() and client:
            client.close()

def process_pdf(pdf_file_path):
    """Main function to orchestrate the workflow."""
    print(f"Processing PDF: {pdf_file_path}")
    text = extract_text_from_pdf(pdf_file_path)
    if not text:
        return False

    print("Extracted Text (Preview):")
    print(text[:500] + "...")

    tc_text = groq_llama_extract_tc(text)
    if not tc_text:
        print(f"Could not identify Terms and Conditions in {pdf_file_path}")
        return False

    result = embed_and_store_tc(tc_text, os.path.basename(pdf_file_path))
    print(result)
    return True

# Example usage
pdf_path = "D://BigTapp//Company Work//Agentic AI//PDFtoVector//T&C-Datasets//tandc-aws.pdf"
process_pdf(pdf_path)