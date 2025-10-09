# FastAPI app
import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_processor import extract_text_from_pdf, extract_text_with_pages, create_chunks_with_pages
from rag import store_in_pinecone, query_contract, generate_response
from prompts import QA_SYSTEM_PROMPT
from analyzers import run_comprehensive_analysis

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for MVP (use database in production)
contracts_data = {}

class QuestionRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """Upload and process a PDF contract."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Generate unique ID
    contract_id = str(uuid.uuid4())
    
    # Save file temporarily
    temp_path = f"/tmp/{contract_id}.pdf"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Extract text with page numbers
    pages_data = extract_text_with_pages(temp_path)
    
    # Create full text for checklist/risk analysis
    text = "\n\n".join([page["text"] for page in pages_data])
    
    # Create overlapping chunks with page metadata for RAG
    chunks = create_chunks_with_pages(pages_data, chunk_size=500, overlap=100)
    
    # Store in Pinecone
    store_in_pinecone(contract_id, chunks)
    
    # Run comprehensive analysis (all 7 types) using RAG
    print(f"📄 Analyzing contract: {file.filename}")
    analysis_results = run_comprehensive_analysis(contract_id, text)
    
    # Store results
    contracts_data[contract_id] = {
        "id": contract_id,
        "filename": file.filename,
        "text": text,
        # All 7 analysis results
        "compliance_checklist": analysis_results["compliance_checklist"],
        "clause_summaries": analysis_results["clause_summaries"],
        "scope_alignment": analysis_results["scope_alignment"],
        "completeness_check": analysis_results["completeness_check"],
        "timeline_milestones": analysis_results["timeline_milestones"],
        "financial_risks": analysis_results["financial_risks"],
        "audit_trail": analysis_results["audit_trail"],
        "validation": analysis_results["validation"]
    }
    
    # Clean up temp file
    os.remove(temp_path)
    
    return {"id": contract_id}

@app.get("/results/{contract_id}")
async def get_results(contract_id: str):
    """Get comprehensive analysis results for a contract."""
    if contract_id not in contracts_data:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    data = contracts_data[contract_id]
    
    # Handle both old and new format contracts
    # Old format had "checklist" and "risks", new format has 7 analysis types
    return {
        "id": data.get("id", contract_id),
        "filename": data.get("filename", "Unknown"),
        # All 7 analysis results (with fallbacks for old format)
        "compliance_checklist": data.get("compliance_checklist", data.get("checklist", "Analysis not available. Please re-upload the contract.")),
        "clause_summaries": data.get("clause_summaries", data.get("risks", "Analysis not available. Please re-upload the contract.")),
        "scope_alignment": data.get("scope_alignment", "Analysis not available. Please re-upload the contract."),
        "completeness_check": data.get("completeness_check", "Analysis not available. Please re-upload the contract."),
        "timeline_milestones": data.get("timeline_milestones", "Analysis not available. Please re-upload the contract."),
        "financial_risks": data.get("financial_risks", "Analysis not available. Please re-upload the contract."),
        "audit_trail": data.get("audit_trail", "Analysis not available. Please re-upload the contract."),
        "validation": data.get("validation", {
            "completeness_score": 0.0,
            "status": "INCOMPLETE",
            "sections_completed": 0,
            "total_sections": 7,
            "recommendation": "Please re-upload for full analysis"
        })
    }

@app.post("/qa/{contract_id}")
async def ask_question(contract_id: str, request: QuestionRequest):
    """Ask a question about a contract."""
    try:
        # Get relevant context from Pinecone
        context_chunks = query_contract(contract_id, request.question)
        
        # Check if we got any results
        if not context_chunks:
            raise HTTPException(
                status_code=404, 
                detail="Contract not found in database. Please upload the document again."
            )
        
        context = "\n\n".join(context_chunks)
        
        # Generate answer
        prompt = QA_SYSTEM_PROMPT.format(context=context, question=request.question)
        answer = generate_response(prompt)
        
        return {"answer": answer}
    except Exception as e:
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise
        # Otherwise, return a generic error
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Contract Analysis API"}

@app.get("/debug/contracts")
async def list_contracts():
    """List contracts in memory and check Pinecone status."""
    from rag import get_pinecone_client
    
    try:
        pc = get_pinecone_client()
        indexes = pc.list_indexes()
        
        return {
            "in_memory_contracts": list(contracts_data.keys()),
            "in_memory_count": len(contracts_data),
            "pinecone_indexes": indexes.names(),
            "note": "If server restarted, in_memory will be empty but Pinecone data persists"
        }
    except Exception as e:
        return {
            "in_memory_contracts": list(contracts_data.keys()),
            "in_memory_count": len(contracts_data),
            "error": str(e)
        }

@app.post("/debug/query/{contract_id}")
async def debug_query(contract_id: str, request: QuestionRequest):
    """
    Debug endpoint: Shows the full RAG pipeline step-by-step.
    
    Useful for understanding:
    - What chunks Pinecone retrieves
    - Their similarity scores
    - How reranking changes the order
    - What context goes to the LLM
    """
    from rag import get_or_create_index, create_embeddings, rerank_with_zeroentropy
    
    print(f"\n{'='*70}")
    print(f"🔍 DEBUG QUERY: {request.question}")
    print(f"{'='*70}")
    
    index = get_or_create_index()
    question_embedding = create_embeddings([request.question])[0]
    
    # Step 1: Pinecone Retrieval (k=50)
    print(f"\n📊 STEP 1: Querying Pinecone (k=50)...")
    results = index.query(
        vector=question_embedding,
        top_k=50,
        filter={"contract_id": contract_id},
        include_metadata=True
    )
    
    print(f"   Retrieved {len(results['matches'])} total vectors")
    
    # Step 2: Filter by threshold (>0.5)
    print(f"\n📊 STEP 2: Filtering by score > 0.5...")
    filtered_docs = []
    for match in results["matches"]:
        if match["score"] > 0.5:
            filtered_docs.append({
                "text": match["metadata"]["text"],
                "page_number": match["metadata"].get("page_number", 0),
                "pinecone_score": match["score"]
            })
    
    print(f"   {len(filtered_docs)} chunks passed threshold")
    
    # Step 3: Reranking
    print(f"\n📊 STEP 3: Reranking with ZeroEntropy...")
    reranked_docs = rerank_with_zeroentropy(request.question, filtered_docs)
    print(f"   Reranking complete, top 10 selected")
    
    # Prepare detailed output
    pinecone_results = [
        {
            "rank": i + 1,
            "pinecone_score": doc["pinecone_score"],
            "page": doc["page_number"],
            "text_preview": doc["text"][:150] + "..."
        }
        for i, doc in enumerate(filtered_docs[:20])  # Show top 20 before reranking
    ]
    
    reranked_results = [
        {
            "rank": i + 1,
            "rerank_score": doc.get("rerank_score", "N/A"),
            "pinecone_score": doc["pinecone_score"],
            "page": doc["page_number"],
            "text_preview": doc["text"][:150] + "...",
            "moved_from_rank": next(
                (j + 1 for j, d in enumerate(filtered_docs) if d["text"] == doc["text"]),
                None
            )
        }
        for i, doc in enumerate(reranked_docs[:10])  # Top 10 after reranking
    ]
    
    print(f"\n✅ Debug complete! Check response for details.\n")
    
    return {
        "question": request.question,
        "contract_id": contract_id,
        "pipeline_summary": {
            "step_1_retrieved": len(results["matches"]),
            "step_2_filtered": len(filtered_docs),
            "step_3_reranked": len(reranked_docs),
            "final_chunks_used": min(10, len(reranked_docs))
        },
        "pinecone_top_20": pinecone_results,
        "reranked_top_10": reranked_results,
        "explanation": {
            "how_to_read": "Compare 'pinecone_top_20' vs 'reranked_top_10' to see how reranking improved relevance",
            "moved_from_rank": "Shows where each chunk ranked before reranking (if it moved up, reranking helped!)",
            "scores": "Higher = more relevant. Pinecone uses cosine similarity (0-1), reranker uses custom scoring"
        }
    }
