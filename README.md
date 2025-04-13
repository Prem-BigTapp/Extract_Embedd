 PDF Terms & Conditions Extractor and Embedder using Groq + Agno

This project extracts the "Terms and Conditions" section from a PDF file, processes it with a Groq LLM (LLaMA-3), embeds the result using SentenceTransformers, and stores it in MongoDB for retrieval and future usage.

 Features

-  Extracts text from PDF using PyMuPDF
-  Identifies Terms and Conditions section using Groq LLaMA-3.3-70B
-  Embeds text using SentenceTransformer (`all-mpnet-base-v2`)
-  Stores sentence chunks and embeddings in MongoDB

---
