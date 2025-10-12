# RAG logic (LangChain)
import os
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "contracts"

# Initialize clients lazily
_openai_client = None
_pinecone_client = None

def get_openai_client():
    """Get or create OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client

def get_pinecone_client():
    """Get or create Pinecone client."""
    global _pinecone_client
    if _pinecone_client is None:
        _pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return _pinecone_client

def get_or_create_index():
    """Get existing index or create new one."""
    pc = get_pinecone_client()
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1536,  # OpenAI embedding size
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

def create_embeddings(texts: list[str]) -> list[list[float]]:
    """Create embeddings using OpenAI."""
    client = get_openai_client()
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        embeddings.append(response.data[0].embedding)
    return embeddings

def store_in_pinecone(contract_id: str, chunks: list[dict]):
    """
    Store contract chunks in Pinecone with metadata.
    
    Args:
        contract_id: Unique identifier for the contract
        chunks: List of chunk dictionaries with 'text' and optional metadata
    """
    index = get_or_create_index()
    
    # Extract text for embeddings
    chunk_texts = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk in chunks]
    embeddings = create_embeddings(chunk_texts)
    
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Handle both dict chunks (with metadata) and string chunks (legacy)
        if isinstance(chunk, dict):
            metadata = {
                "text": chunk["text"],
                "contract_id": contract_id,
                "page_number": chunk.get("page_number", 0),
                "chunk_index": chunk.get("chunk_index", i),
                "word_count": chunk.get("word_count", 0),
                
                # NEW: Enhanced metadata for filtering
                "primary_category": chunk.get("primary_category", "general"),
                "clause_type": chunk.get("clause_type", "unknown"),
                "risk_tags": chunk.get("risk_tags", []),
                "keywords": chunk.get("keywords", [])
            }
        else:
            metadata = {
                "text": chunk,
                "contract_id": contract_id,
                "page_number": 0,
                "chunk_index": i,
                
                # NEW: Default values for string chunks
                "primary_category": "general",
                "clause_type": "unknown", 
                "risk_tags": [],
                "keywords": []
            }
        
        vectors.append({
            "id": f"{contract_id}_{i}",
            "values": embedding,
            "metadata": metadata
        })
    
    index.upsert(vectors=vectors)

def rerank_with_zeroentropy(query: str, documents: list[dict]) -> list[dict]:
    """
    Rerank documents using ZeroEntropy SDK.
    
    How it works:
    1. Uses ZeroEntropy Python SDK (not REST API)
    2. API scores each document for relevance to query
    3. Returns documents reordered by relevance (best first)
    
    Args:
        query: The user's question
        documents: List of dicts with 'text' and 'page_number'
    
    Returns:
        Reranked list of documents with scores
    """
    import os
    
    api_key = os.getenv("ZEROENTROPY_API_KEY")
    if not api_key:
        # If no API key, return documents as-is (no reranking)
        print("   ⚠️  No ZeroEntropy API key - using Pinecone order")
        return documents
    
    try:
        # Import and initialize ZeroEntropy SDK
        from zeroentropy import ZeroEntropy
        
        zclient = ZeroEntropy(api_key=api_key)
        
        # Extract just the text for reranking
        doc_texts = [doc["text"] for doc in documents]
        
        print(f"   🔄 Sending {len(doc_texts)} docs to ZeroEntropy...")
        
        # Call rerank using the SDK
        response = zclient.models.rerank(
            model="zerank-1",  # Correct model name from docs
            query=query,
            documents=doc_texts
        )
        
        # Reorder documents based on reranking scores
        reranked = []
        for result in response.results:
            # result has: index, document, relevance_score
            idx = result.index
            score = result.relevance_score
            
            if idx < len(documents):
                doc = documents[idx].copy()
                doc["rerank_score"] = score
                reranked.append(doc)
        
        if reranked:
            print(f"   ✅ Reranked! Top score: {reranked[0].get('rerank_score', 'N/A')}")
            return reranked[:20]  # Return top 10
        else:
            print(f"   ⚠️  No results after reranking - using Pinecone order")
            return documents
            
    except ImportError:
        print(f"   ⚠️  ZeroEntropy SDK not installed - run: pip install zeroentropy")
        return documents
    except Exception as e:
        print(f"   ⚠️  Reranking error: {e} - using Pinecone order")
        return documents

def query_contract(contract_id: str, question: str, top_k: int = 50, metadata_filter: dict = None) -> list[str]:
    """
    Query contract using RAG with improved retrieval and reranking.
    
    Pipeline:
    1. Convert question to embedding (vector)
    2. Search Pinecone for similar chunks (k=50) with optional metadata filtering
    3. Filter chunks by score > 0.5
    4. Rerank with ZeroEntropy for better relevance
    5. Return top 10 chunks with page citations
    
    Args:
        contract_id: The contract to search
        question: The user's question
        top_k: Number of candidates to retrieve (default: 50)
        metadata_filter: Optional Pinecone metadata filter (e.g., {"primary_category": {"$in": ["financial"]}})
    
    Returns:
        List of relevant text chunks with page citations
    """
    print(f"\n  🔍 Q&A Query: '{question[:60]}{'...' if len(question) > 60 else ''}'")
    
    index = get_or_create_index()
    
    # Step 1: Create embedding for question
    print(f"  📝 Creating embedding for question...")
    question_embedding = create_embeddings([question])[0]
    
    # Step 2: Query Pinecone with many candidates (cast wide net)
    print(f"  🔎 Searching Pinecone (k={top_k})...")
    
    # Build the filter - start with contract_id, add metadata filter if provided
    pinecone_filter = {"contract_id": contract_id}
    if metadata_filter:
        pinecone_filter.update(metadata_filter)
        print(f"  🎯 Using metadata filter: {metadata_filter}")
    
    results = index.query(
        vector=question_embedding,
        top_k=top_k,  # Get 50 candidates
        filter=pinecone_filter,
        include_metadata=True
    )
    
    total_retrieved = len(results["matches"])
    print(f"  📊 Pinecone returned {total_retrieved} chunks")
    
    # Step 3: Prepare documents for reranking (filter by threshold)
    documents = []
    for match in results["matches"]:
        # Lower threshold to catch more potential matches
        if match["score"] > 0.5:  # More lenient initial filter
            documents.append({
                "text": match["metadata"]["text"],
                "page_number": match["metadata"].get("page_number", 0),
                "pinecone_score": match["score"]
            })
    
    print(f"  ✂️  Filtered to {len(documents)} chunks (score > 0.5)")
    
    if not documents:
        print(f"  ⚠️  No chunks passed filter! Try a different question.")
        return []
    
    # Step 4: Rerank using ZeroEntropy
    print(f"  🤖 Reranking...")
    reranked_docs = rerank_with_zeroentropy(question, documents)
    
    # Step 5: Format with page numbers
    relevant_chunks = []
    for i, doc in enumerate(reranked_docs[:20]):  # Top 10 after reranking
        text = doc["text"]
        page_num = doc.get("page_number", 0)
        pinecone_score = doc.get("pinecone_score", 0)
        rerank_score = doc.get("rerank_score", None)
        
        # Add page citation if available
        if page_num > 0:
            formatted_chunk = f"[Page {page_num}] {text}"
        else:
            formatted_chunk = text
        
        relevant_chunks.append(formatted_chunk)
        
        # Log first 3 chunks for visibility
        if i < 3:
            score_info = f"rerank={rerank_score:.3f}, " if rerank_score else ""
            print(f"     #{i+1}: {score_info}pinecone={pinecone_score:.3f}, page={page_num}")
    
    print(f"  ✅ Returning {len(relevant_chunks)} chunks to LLM\n")
    return relevant_chunks

def generate_response(prompt: str) -> str:
    """Generate AI response using OpenAI."""
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content
