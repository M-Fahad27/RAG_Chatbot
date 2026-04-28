from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama 
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter


app = FastAPI(title="Mistral RAG API")

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "documents"


llm = ChatOllama(
    model="mistral",
    temperature=0,
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=str(CHROMA_DIR),
    embedding_function=embedding_model,
)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful AI assistant.

Use only the provided context to answer the user's question.
If the answer is not available in the context, say:
"I don't know based on the provided documents."

Do not invent information.

Context:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class SourceDocument(BaseModel):
    content: str
    metadata: dict[str, Any]


class QueryResponse(BaseModel):
    query: str
    response: str
    sources: list[SourceDocument]


def format_documents(docs) -> str:
    if not docs:
        return "No relevant documents were found."

    return "\n\n".join(
        f"Document {index + 1}:\n{doc.page_content}" for index, doc in enumerate(docs)
    )


def load_documents_from_folder(folder_path: Path):
    docs = []
    for file in folder_path.iterdir():
        if file.is_file():
            if file.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file))
            elif file.suffix.lower() == ".txt":
                loader = TextLoader(str(file))
            elif file.suffix.lower() == ".docx":
                loader = Docx2txtLoader(str(file))
            else:
                continue
            docs.extend(loader.load())
    return docs


@app.post("/ingest")
def ingest_documents():
    global vectorstore, retriever
    
    folder_path = BASE_DIR / "Uploaded Files"
    if not folder_path.exists():
        return {"message": "No uploaded files folder found."}
    docs = load_documents_from_folder(folder_path)
    if docs:
        # Delete the existing collection to clear old documents
        vectorstore.delete_collection()
        # Reinitialize the vectorstore
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(CHROMA_DIR),
            embedding_function=embedding_model,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Add new documents
        split_docs = text_splitter.split_documents(docs)
        vectorstore.add_documents(split_docs)
        return {"message": f"Successfully ingested {len(split_docs)} document chunks."}
    else:
        return {"message": "No documents found to ingest."}


@app.post("/query", response_model=QueryResponse)
def search_and_generate_response(request: QueryRequest):
    try:
        question = request.query.strip()

        docs = retriever.invoke(question)
        context = format_documents(docs)

        messages = prompt.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        ai_message = llm.invoke(messages)
        answer = ai_message.content

        sources = [
            SourceDocument(
                content=doc.page_content[:500],
                metadata=doc.metadata,
            )
            for doc in docs
        ]

        return QueryResponse(
            query=question,
            response=answer,
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def home():
    return {"message": "Mistral AI API is running"}
