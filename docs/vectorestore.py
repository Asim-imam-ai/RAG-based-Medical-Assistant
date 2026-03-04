import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# Pinecone (official client)
from pinecone import Pinecone, ServerlessSpec

# LangChain
from langchain_community.document_loaders import PyPDFLoader

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["PINECONE_ENVIRONMENT"] = PINECONE_ENVIRONMENT

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

pc = Pinecone(api_key=PINECONE_API_KEY)

spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_ENVIRONMENT
)

existing_indexes = [i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        serverless=spec
    )

index = pc.Index(PINECONE_INDEX_NAME)



def load_vectoresrore(uplaoded_files,role:str,doc_id:str):
    embed_model = OpenAIEmbeddings()

    for file in uplaoded_files:
        save_path =Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        loader = PyPDFLoader(save_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(documents)
        
        texts = [chunk.page_content for chunk in docs]
        ids = [doc_id for chunk in range(len(docs))]
      
        metadatas = [
            {
                "source": file.filename,
                "role": role,
                "id": doc_id,
                "page": chunk.metadata.get("page", 0)
            }
            for chunk in docs
        ]
        embeddings = embed_model.embed_documents(texts)
        print("uploading to pinecone")
        
        with tqdm (total=len(embeddings), desc="uploading to pinecone") as progress:
            index.upsert(vectors=zip(ids, embeddings, metadatas))
            progress.update(len(embeddings))
            
        print(f"upload complete for {file.filename}")
            
 
