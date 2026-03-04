import os
import asyncio
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not all([OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME]):
    raise ValueError("Missing required environment variables")

# --------------------------------------------------
# Initialize Pinecone
# --------------------------------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# --------------------------------------------------
# Initialize models
# --------------------------------------------------
embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

# --------------------------------------------------
# Prompt
# --------------------------------------------------
prompt = PromptTemplate.from_template("""
You are a helpful medical assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say you don't have enough information.

Question:
{question}

Context:
{context}
""")

rag_chain = prompt | llm

# --------------------------------------------------
# RAG Query Function
# --------------------------------------------------
async def answer_query(message: str, role: str | None = None):

    try:
        # 1️⃣ Embed query
        query_vector = await asyncio.to_thread(
            embed_model.embed_query,
            message
        )

        # 2️⃣ Search Pinecone (NO namespace needed)
        results = await asyncio.to_thread(
            index.query,
            vector=query_vector,
            top_k=5,
            include_metadata=True
        )

        matches = results.get("matches", [])

        if not matches:
            return {"response": "No relevant documents found."}

        contexts = []
        sources = set()

        # 3️⃣ Extract content
        for match in matches:
            metadata = match.get("metadata", {})

            # Role filtering
            if role:
                if metadata.get("role") != role:
                    continue

            text = metadata.get("text")

            if text:
                contexts.append(text)
                sources.add(metadata.get("source", "Unknown"))

        if not contexts:
            return {"response": "No relevant content found after filtering."}

        full_context = "\n\n---\n\n".join(contexts)

        # 4️⃣ Generate answer
        response = await asyncio.to_thread(
            rag_chain.invoke,
            {
                "question": message,
                "context": full_context
            }
        )

        return {
            "answer": response.content,
            "sources": list(sources)
        }

    except Exception as e:
        return {
            "response": f"Error occurred: {str(e)}"
        }
    