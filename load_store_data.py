from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
 

# 🔑 Load environment variables (optional: use .env for secrets)
load_dotenv()  # Make sure you have a .env file with PINECONE_API_KEY
PINECONE_API_KEY = os.getenv("PINECODE_KEY")

# 📌 Set up Pinecone
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "my-index1"

# ✅ Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# 🤖 Load SentenceTransformer model
model = SentenceTransformer("all-mpnet-base-v2")

# 📄 Load PDF from local project folder
pdf_path = "example.pdf"  # Replace with your actual filename
doc = fitz.open(pdf_path)
full_text = ""
for page in doc:
    full_text += page.get_text()

# 🧩 Chunking logic
def chunk_text(text, chunk_size=250, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

chunks = chunk_text(full_text)

# 🧠 Create embeddings
embeddings = model.encode(chunks).tolist()

# 🔼 Upsert vectors into Pinecone
vectors = [{"id": f"vec{i}", "values": emb, "metadata": {"text": txt}} for i, (emb, txt) in enumerate(zip(embeddings, chunks))]
index.upsert(vectors=vectors)

# 🔍 Query

# i want to make a method which takes the query and the tok k value and return me the array of the result 

query = "What is the main topic of the document?"
top_k = 3  # Number of top results to return
async def search(query, top_k=1):
    query_vec = model.encode([query])[0].tolist()
    results = index.query(vector=query_vec, top_k=top_k, include_metadata=True)
    
    if results['matches']:
        return [{"score": match['score'], "text": match['metadata']['text']} for match in results['matches']]
    else:
        return []  # No matches found
    
 