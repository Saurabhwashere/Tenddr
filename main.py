# FastAPI app with Supabase integration
import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

from pdf_processor import extract_text_from_pdf, extract_text_with_pages, create_chunks_with_pages, create_enhanced_chunks_with_pages
from rag import store_in_pinecone, query_contract, generate_response, get_or_create_index
from prompts import QA_SYSTEM_PROMPT
from analyzers import run_comprehensive_analysis
from risk_detector import run_risk_analysis

# Supabase integration
from database import (
    create_contract,
    update_contract_status,
    save_contract_analysis,
    save_risk_analysis,
    get_contract_complete,
    list_all_contracts,
    list_contracts_by_user,
    check_duplicate_by_hash,
    save_user_question,
    update_pinecone_status
)
from storage import (
    upload_pdf,
    download_pdf,
    calculate_file_hash,
    get_pdf_url
)

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    """Upload and process a PDF contract with user isolation."""
    
    # Validate user_id is provided
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header is required")
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Calculate file hash for duplicate detection
    file_hash = calculate_file_hash(content)
    
    # Check if file already exists for this user
    existing_id = check_duplicate_by_hash(file_hash, user_id)
    if existing_id:
        print(f"📋 Duplicate detected! Returning existing contract: {existing_id}")
        return {
            "id": existing_id,
            "message": "This contract was already uploaded",
            "is_duplicate": True
        }
    
    # Generate unique ID
    contract_id = str(uuid.uuid4())
    
    # Upload to Supabase Storage with user isolation
    storage_path = upload_pdf(contract_id, content, file.filename, user_id)
    
    # Create contract record in database
    create_contract(
        contract_id=contract_id,
        filename=file.filename,
        storage_path=storage_path,
        file_hash=file_hash,
        file_size=file_size,
        user_id=user_id
    )
    
    # Save file temporarily for processing
    temp_path = f"/tmp/{contract_id}.pdf"
    with open(temp_path, "wb") as f:
        f.write(content)
    
    try:
        # Extract text with page numbers
        pages_data = extract_text_with_pages(temp_path)
        
        # Create full text for checklist/risk analysis
        text = "\n\n".join([page["text"] for page in pages_data])
        
        # Create enhanced chunks with metadata for better filtering
        chunks = create_enhanced_chunks_with_pages(pages_data, chunk_size=500, overlap=100)
        
        # Store in Pinecone with user isolation
        store_in_pinecone(contract_id, chunks, user_id)
        update_pinecone_status(contract_id, indexed=True)

        # Default empty risk analysis (used if risk detection fails)
        empty_risk_analysis = {
            "risks_by_severity": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            },
            "all_risks": [],
            "summary": {
                "total_risks_checked": 0,
                "total_risks_found": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "overall_risk_level": "unknown"
            }
        }

        # Run automated risk detection (uses RAG to search entire contract)
        try:
            print(f"🔍 Running automated risk detection...")
            risk_results = run_risk_analysis(contract_id, user_id, model="gpt-4o")
        except Exception as e:
            # If risk detection fails, log error but continue with other analyses
            print(f"⚠️ Risk detection failed: {e}")
            risk_results = empty_risk_analysis

        # Run comprehensive analysis (all 7 types) using RAG
        print(f"📄 Analyzing contract: {file.filename}")
        # Use RAG-only (no full text) to avoid 300K token limit
        analysis_results = run_comprehensive_analysis(contract_id, "", user_id)
        
        # Save analysis results to database
        save_contract_analysis(
            contract_id=contract_id,
            analysis_results=analysis_results,
            validation=analysis_results["validation"],
            user_id=user_id
        )
        
        # Save risk analysis to database
        save_risk_analysis(contract_id=contract_id, risk_results=risk_results, user_id=user_id)
        
        # Update contract status to completed
        update_contract_status(contract_id, status="completed")
        
        # Clean up temp file
        os.remove(temp_path)
        
        print(f"✅ Contract processed successfully: {contract_id}")
        
        # Return upload success with risk summary for quick feedback
        return {
            "id": contract_id,
            "filename": file.filename,
            "risk_summary": {
                "critical_count": risk_results["summary"]["critical_count"],
                "high_count": risk_results["summary"]["high_count"],
                "medium_count": risk_results["summary"]["medium_count"],
                "overall_risk_level": risk_results["summary"]["overall_risk_level"]
            }
        }
        
    except Exception as e:
        # If processing fails, update status and clean up
        print(f"❌ Processing failed: {e}")
        update_contract_status(contract_id, status="failed", error=str(e))
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/reanalyze/{contract_id}")
async def reanalyze_contract(contract_id: str):
    """Re-run analysis on an existing contract (useful when analysis logic improves)."""
    
    # Check if contract exists
    contract = get_contract_complete(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    print(f"🔄 Re-analyzing contract: {contract_id}")
    
    # Initialize temp_path outside try block
    temp_path = f"/tmp/{contract_id}_reanalyze.pdf"
    
    try:
        # Update status to processing (not "reprocessing" - that's not in the allowed values)
        update_contract_status(contract_id, status="processing")
        
        # Get storage path from contract record
        storage_path = contract.get("storage_path")
        if not storage_path:
            raise HTTPException(
                status_code=400, 
                detail="Contract has no stored PDF file. This contract may have been uploaded before Supabase integration. Please re-upload the contract."
            )
        
        # Download PDF from Supabase Storage
        from storage import download_pdf
        pdf_content = download_pdf(storage_path)
        
        # Save temporarily (temp_path already defined above)
        with open(temp_path, "wb") as f:
            f.write(pdf_content)
        
        # Extract text with page numbers
        pages_data = extract_text_with_pages(temp_path)
        text = "\n\n".join([page["text"] for page in pages_data])
        
        # Re-create enhanced chunks with metadata
        chunks = create_enhanced_chunks_with_pages(pages_data, chunk_size=500, overlap=100)
        
        # Delete old vectors from Pinecone and store new ones
        print("🗑️  Deleting old vectors from Pinecone...")
        index = get_or_create_index()
        try:
            index.delete(filter={"contract_id": contract_id})
            print("   ✓ Old vectors deleted")
        except Exception as e:
            print(f"   ⚠️  Could not delete old vectors: {str(e)[:100]}")
            print("   → Proceeding with upsert (will overwrite by ID)")
        
        # Store new chunks with updated metadata
        print("💾 Storing new chunks with updated metadata...")
        store_in_pinecone(contract_id, chunks, contract["uploaded_by"])
        update_pinecone_status(contract_id, indexed=True)
        
        # Default empty risk analysis (used if risk detection fails)
        empty_risk_analysis = {
            "risks_by_severity": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            },
            "all_risks": [],
            "summary": {
                "total_risks_checked": 0,
                "total_risks_found": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "overall_risk_level": "unknown"
            }
        }
        
        # Run automated risk detection
        try:
            print(f"🔍 Re-running automated risk detection...")
            risk_results = run_risk_analysis(contract_id, contract["uploaded_by"], model="gpt-4o")
        except Exception as e:
            print(f"⚠️ Risk detection failed: {e}")
            risk_results = empty_risk_analysis
        
        # Run comprehensive analysis
        print(f"📄 Re-analyzing contract...")
        # Use RAG-only (no full text) to avoid 300K token limit
        analysis_results = run_comprehensive_analysis(contract_id, "", contract["uploaded_by"])
        
        # Save updated analysis results
        save_contract_analysis(
            contract_id=contract_id,
            analysis_results=analysis_results,
            validation=analysis_results["validation"],
            user_id=contract["uploaded_by"]
        )
        
        # Save updated risk analysis
        save_risk_analysis(contract_id, risk_results, contract["uploaded_by"])
        
        # Update status to completed
        update_contract_status(contract_id, status="completed")
        
        # Clean up temp file
        os.remove(temp_path)
        
        print(f"✅ Re-analysis complete: {contract_id}")
        
        return {
            "id": contract_id,
            "message": "Re-analysis completed successfully",
            "risk_summary": {
                "critical_count": risk_results["summary"]["critical_count"],
                "high_count": risk_results["summary"]["high_count"],
                "medium_count": risk_results["summary"]["medium_count"],
                "overall_risk_level": risk_results["summary"]["overall_risk_level"]
            }
        }
        
    except Exception as e:
        print(f"❌ Re-analysis failed: {e}")
        update_contract_status(contract_id, status="failed", error=str(e))
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        raise HTTPException(status_code=500, detail=f"Re-analysis failed: {str(e)}")

@app.get("/results/{contract_id}")
async def get_results(contract_id: str):
    """Get comprehensive analysis results for a contract from Supabase."""
    # Get contract with all analyses from database
    data = get_contract_complete(contract_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Default empty risk analysis for backward compatibility
    empty_risk_analysis = {
        "risks_by_severity": {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        },
        "all_risks": [],
        "summary": {
            "total_risks_checked": 0,
            "total_risks_found": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "overall_risk_level": "unknown"
        }
    }
    
    # Return formatted response
    return {
        "id": data.get("id"),
        "filename": data.get("filename", "Unknown"),
        # Risk analysis
        "risk_analysis": {
            "summary": data.get("risk_summary") or empty_risk_analysis["summary"],
            "risks_by_severity": data.get("risks_by_severity") or empty_risk_analysis["risks_by_severity"],
            "all_risks": data.get("all_risks") or empty_risk_analysis["all_risks"]
        },
        # All 7 comprehensive analysis results
        "compliance_checklist": data.get("compliance_checklist") or "Analysis not available.",
        "clause_summaries": data.get("clause_summaries") or "Analysis not available.",
        "scope_alignment": data.get("scope_alignment") or "Analysis not available.",
        "completeness_check": data.get("completeness_check") or "Analysis not available.",
        "timeline_milestones": data.get("timeline_milestones") or "Analysis not available.",
        "financial_risks": data.get("financial_risks") or "Analysis not available.",
        "audit_trail": data.get("audit_trail") or "Analysis not available.",
        "validation": data.get("validation") or {
            "completeness_score": 0.0,
            "status": "INCOMPLETE",
            "sections_completed": 0,
            "total_sections": 7,
            "recommendation": "Analysis not available"
        }
    }

@app.post("/qa/{contract_id}")
async def ask_question(contract_id: str, request: QuestionRequest, user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """
    Ask a question about a contract and save to history.
    Uses hybrid multi-query strategy for comprehensive answers.
    """
    
    # Validate user_id is provided
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header is required")
    try:
        # Verify contract exists
        contract = get_contract_complete(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Use hybrid multi-query retrieval for better coverage
        from query_expansion import hybrid_multi_query_retrieval
        
        print(f"\n🎯 Q&A Request: {request.question[:100]}...")
        context_chunks = hybrid_multi_query_retrieval(
            contract_id, 
            request.question, 
            user_id,
            top_k_per_query=15  # Increased from 10 to 15 for better coverage
        )
        
        # Check if we got any results
        if not context_chunks:
            raise HTTPException(
                status_code=404, 
                detail="Contract not found in vector database. Please re-upload the document."
            )
        
        context = "\n\n".join(context_chunks[:30])
        
        # Generate answer
        prompt = QA_SYSTEM_PROMPT.format(context=context, question=request.question)
        answer = generate_response(prompt)
        
        # Save question and answer to database
        save_user_question(
            contract_id=contract_id,
            question=request.question,
            answer=answer,
            chunks_used=context_chunks[:5]  # Save top 5 chunks for reference
        )
        
        print(f"✅ Answer generated successfully\n")
        
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

@app.get("/debug/user")
async def debug_user(user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Debug endpoint to check user_id and list all contracts."""
    if not user_id:
        return {"error": "X-User-Id header is required"}
    
    try:
        # Get all contracts (for debugging)
        all_contracts = list_all_contracts()
        user_contracts = list_contracts_by_user(user_id)
        
        return {
            "user_id": user_id,
            "total_contracts": len(all_contracts),
            "user_contracts": len(user_contracts),
            "all_contracts": [{"id": c["id"], "uploaded_by": c.get("uploaded_by"), "filename": c["filename"]} for c in all_contracts],
            "user_contracts_data": [{"id": c["id"], "uploaded_by": c.get("uploaded_by"), "filename": c["filename"]} for c in user_contracts]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/contracts")
async def list_contracts(user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """List contracts for authenticated user only."""
    
    # Validate user_id is provided
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header is required")
    
    try:
        contracts = list_contracts_by_user(user_id)
        return {
            "contracts": contracts,
            "count": len(contracts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing contracts: {str(e)}")

@app.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str):
    """
    Permanently delete a contract and all associated data.
    
    This will delete:
    1. PDF file from Supabase Storage
    2. All database records (contract, analyses, risks, Q&A)
    3. All embeddings from Pinecone
    """
    try:
        print(f"\n🗑️  DELETE REQUEST for contract: {contract_id}")
        
        # Step 1: Get storage path before deleting from database
        from database import get_contract_storage_path
        storage_path = get_contract_storage_path(contract_id)
        
        if not storage_path:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Step 2: Delete from Pinecone (vector embeddings)
        from rag import delete_from_pinecone
        pinecone_deleted = delete_from_pinecone(contract_id)
        
        # Step 3: Delete from Supabase Storage (PDF file)
        from storage import delete_pdf
        storage_deleted = delete_pdf(storage_path)
        
        # Step 4: Delete from Supabase Database (all tables)
        from database import delete_contract_and_analyses
        db_deleted = delete_contract_and_analyses(contract_id)
        
        # Check if all deletions were successful
        if db_deleted and storage_deleted and pinecone_deleted:
            print(f"✅ Successfully deleted contract {contract_id}")
            return {
                "success": True,
                "message": "Contract permanently deleted",
                "deleted": {
                    "database": db_deleted,
                    "storage": storage_deleted,
                    "pinecone": pinecone_deleted
                }
            }
        else:
            return {
                "success": False,
                "message": "Partial deletion - some operations failed",
                "deleted": {
                    "database": db_deleted,
                    "storage": storage_deleted,
                    "pinecone": pinecone_deleted
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting contract: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete contract: {str(e)}")

@app.get("/pdf/{contract_id}")
async def get_pdf(contract_id: str):
    """Serve PDF file for viewing."""
    try:
        # Get contract from database
        contract = get_contract_complete(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Download PDF from storage
        pdf_bytes = download_pdf(contract["storage_path"])
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{contract["filename"]}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving PDF: {str(e)}")

@app.get("/debug/contracts")
async def debug_contracts():
    """Debug endpoint: Show database and Pinecone status."""
    from rag import get_pinecone_client
    
    try:
        # Get database counts
        contracts = list_all_contracts()
        
        # Get Pinecone status
        pc = get_pinecone_client()
        indexes = pc.list_indexes()
        
        return {
            "database_contracts": len(contracts),
            "pinecone_indexes": indexes.names(),
            "recent_contracts": [
                {
                    "id": c["id"],
                    "filename": c["filename"],
                    "status": contracts[0].get("risk_level", "N/A") if contracts else "N/A",
                    "uploaded": c["uploaded_at"]
                }
                for c in contracts[:5]  # Show last 5
            ],
            "note": "All contract data persists in Supabase + Pinecone"
        }
    except Exception as e:
        return {"error": str(e)}

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

@app.get("/debug/metadata/{contract_id}")
async def debug_metadata(contract_id: str):
    """Debug endpoint to inspect metadata for a contract."""
    try:
        from rag import get_or_create_index
        index = get_or_create_index()
        
        # Fetch a sample of vectors for this contract
        results = index.query(
            vector=[0]*1536,  # dummy vector for filter-only query
            top_k=10,
            filter={"contract_id": contract_id},
            include_metadata=True
        )
        
        return [
            {
                "page": match["metadata"].get("page_number"),
                "category": match["metadata"].get("primary_category"),
                "clause_type": match["metadata"].get("clause_type"),
                "risk_tags": match["metadata"].get("risk_tags", []),
                "keywords": match["metadata"].get("keywords", []),
                "preview": match["metadata"].get("text", "")[:160] + "..."
            }
            for match in results.get("matches", [])
        ]
    except Exception as e:
        return {"error": str(e)}
