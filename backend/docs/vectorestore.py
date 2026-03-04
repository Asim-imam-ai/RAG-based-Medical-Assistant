import os
from pathlib import Path
from dotenv import load_dotenv

# Pinecone
from pinecone import Pinecone, ServerlessSpec

# LangChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not all([OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME]):
    raise ValueError("Missing required environment variables")


# --------------------------------------------------
# File Storage Setup
# --------------------------------------------------
UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --------------------------------------------------
# Initialize Pinecone
# --------------------------------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)

spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_ENVIRONMENT
)

existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,  # text-embedding-3-small dimension
        metric="cosine",
        spec=spec
    )

index = pc.Index(PINECONE_INDEX_NAME)


# --------------------------------------------------
# Upload & Store Function
# --------------------------------------------------
def load_vectorstore(uploaded_file, role: str, doc_id: str):

    embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # Save uploaded file
    save_path = Path(UPLOAD_DIR) / uploaded_file.filename

    with open(save_path, "wb") as f:
        f.write(uploaded_file.file.read())

    # Load PDF
    loader = PyPDFLoader(str(save_path))
    documents = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    docs = text_splitter.split_documents(documents)

    texts = [chunk.page_content for chunk in docs]

    # Unique vector IDs
    ids = [f"{doc_id}_{i}" for i in range(len(docs))]

    # Metadata
    metadatas = [
        {
            "text": chunk.page_content,
            "source": uploaded_file.filename,
            "role": role,
            "doc_id": doc_id,
            "page": chunk.metadata.get("page", 0)
        }
        for chunk in docs
    ]

    # Create embeddings
    embeddings = embed_model.embed_documents(texts)

    print(f"Uploading {uploaded_file.filename} to Pinecone...")

    # Upsert into Pinecone
    index.upsert(
        vectors=zip(ids, embeddings, metadatas)
    )

    print(f"Upload complete for {uploaded_file.filename}")