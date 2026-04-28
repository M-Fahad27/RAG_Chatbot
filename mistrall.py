import os
import fitz
import docx
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


ollama_url = "http://localhost:11434/api/generate"


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)  # Embedding Model


def generate_ai_response(context, query):
    prompt = f"""
            You are a highly intelligent AI assistant.

             Use ONLY the information provided below to answer the question.
            If the answer is not in the context, say "I don't know".

            Context:
            {context}

            Question:
            {query}

            Answer clearly and concisely:
            """

    payload = {"model": "mistral", "prompt": prompt, "stream": False}
    response = requests.post(ollama_url, json=payload)
    data = response.json()
    return data["response"]


def search_and_generate_repsonse(query, db_path="chroma_db"):
    vectorstore = Chroma(
        collection_name="documents",
        persist_directory=db_path,
        embedding_function=embedding_model,
    )
    results = vectorstore.max_marginal_relevance_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in results])

    ai_response = generate_ai_response(context, query)
    print("Ai Powered Answer")
    print(ai_response)


def process_document(file_path):
    text = extract_text(file_path)
    if not text:
        return None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)
    texts = text_splitter.split_text(text)
    return texts


def store_embeddings(texts, db_path="chroma_db"):
    vectorstore = Chroma(
        collection_name="documents",
        persist_directory=db_path,
        embedding_function=embedding_model,
    )
    vectorstore.add_texts(texts)
    print("Embedding Stored Successfully")


def search_documents(query, db_path="chroma_db"):
    vectorstore = Chroma(
        collection_name="documents",
        persist_directory=db_path,
        embedding_function=embedding_model,
    )
    results = vectorstore.similarity_search(query, k=2)
    for idx, result in enumerate(results):
        print(f"\n Result {idx+1}: ")
        print(result.page_content)
    return results


def extract_text_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error Reading PDF {pdf_path}:{e}")
    return text


def extract_text_word(doc_path):
    text = ""
    try:
        doc = docx.Document(doc_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error Reading Docx File {doc_path}: {e}")
    return text


def extract_text_txt(txt_path):
    text = ""
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
    except Exception as e:
        print(f"Error Reading File {txt_path}: {e}")
    return text


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_word(file_path)
    elif file_path.endswith(".txt"):
        return extract_text_txt(file_path)
    else:
        print(f"Unsupported File Format: {file_path}")
    return ""


if __name__ == "__main__":
    texts = process_document("FYP_proposal.pdf")
    if texts:
        store_embeddings(texts)
        embeddings = embedding_model.embed_documents(texts)
        print("Number of embeddings:", len(embeddings))
        print("Length of one embedding:", len(embeddings[0]))
        print("First embedding:", embeddings[0][:5])
    query = input("Enter Your Search Query").strip()
    results = search_documents(query)
    search_and_generate_repsonse(query)
