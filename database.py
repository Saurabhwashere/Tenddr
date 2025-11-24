# Database Operations for Contracts
# Simple CRUD operations using Supabase

from typing import Optional, List, Dict
from datetime import datetime
from supabase_client import get_supabase_client

def create_contract(
    contract_id: str,
    filename: str,
    storage_path: str,
    file_hash: str,
    file_size: int,
    user_id: str
) -> Dict:
    """
    Create a new contract record in database.
    
    Returns: Created contract record
    """
    supabase = get_supabase_client()
    
    data = {
        "id": contract_id,
        "filename": filename,
        "original_filename": filename,
        "storage_path": storage_path,
        "file_hash": file_hash,
        "file_size_bytes": file_size,
        "status": "processing",
        "uploaded_by": user_id,
        "uploaded_at": datetime.now().isoformat()
    }
    
    result = supabase.table("contracts").insert(data).execute()
    return result.data[0] if result.data else None

def update_contract_status(
    contract_id: str,
    status: str,
    error: Optional[str] = None
) -> None:
    """Update contract processing status."""
    supabase = get_supabase_client()
    
    update_data = {
        "status": status,
        "processed_at": datetime.now().isoformat()
    }
    
    if error:
        update_data["processing_error"] = error
    
    supabase.table("contracts").update(update_data).eq("id", contract_id).execute()

def save_contract_analysis(
    contract_id: str,
    analysis_results: Dict,
    validation: Dict,
    user_id: str
) -> None:
    """Save comprehensive analysis results (5 types + overview)."""
    supabase = get_supabase_client()
    
    data = {
        "contract_id": contract_id,
        "user_id": user_id,
        "contract_overview": analysis_results.get("contract_overview"),
        "scope_alignment": analysis_results.get("scope_alignment"),
        "timeline_milestones": analysis_results.get("timeline_milestones"),
        "financial_risks": analysis_results.get("financial_risks"),
        "bid_qualifying_criteria": analysis_results.get("bid_qualifying_criteria"),
        "validation": validation
    }
    
    # Upsert (insert or update) - match on contract_id
    supabase.table("contract_analyses").upsert(data, on_conflict="contract_id").execute()

def save_risk_analysis(
    contract_id: str,
    risk_results: Dict,
    user_id: str
) -> None:
    """Save risk detection results."""
    supabase = get_supabase_client()
    
    data = {
        "contract_id": contract_id,
        "user_id": user_id,
        "summary": risk_results.get("summary", {}),
        "risks_by_severity": risk_results.get("risks_by_severity", {}),
        "all_risks": risk_results.get("all_risks", []),
        "risks_checked": risk_results.get("summary", {}).get("total_risks_checked", 0)
    }
    
    # Upsert (insert or update) - match on contract_id
    supabase.table("risk_analyses").upsert(data, on_conflict="contract_id").execute()

def get_contract_complete(contract_id: str) -> Optional[Dict]:
    """
    Get contract with all analyses using the view.
    
    Returns: Complete contract data or None if not found
    """
    supabase = get_supabase_client()
    
    result = supabase.from_("contract_complete").select("*").eq("id", contract_id).execute()
    
    return result.data[0] if result.data else None

def list_all_contracts() -> List[Dict]:
    """List all contracts (not deleted) with summary info."""
    supabase = get_supabase_client()
    
    result = supabase.from_("contracts_dashboard").select("*").execute()
    
    return result.data if result.data else []

def list_contracts_by_user(user_id: str) -> List[Dict]:
    """List contracts for a specific user."""
    supabase = get_supabase_client()
    
    result = supabase.table("contracts")\
        .select("*")\
        .eq("uploaded_by", user_id)\
        .is_("deleted_at", "null")\
        .order("uploaded_at", desc=True)\
        .execute()
    
    return result.data if result.data else []

def check_duplicate_by_hash(file_hash: str, user_id: str) -> Optional[str]:
    """
    Check if a file with this hash already exists for this user.
    
    Returns: Contract ID if duplicate found, None otherwise
    """
    supabase = get_supabase_client()
    
    result = supabase.table("contracts")\
        .select("id")\
        .eq("file_hash", file_hash)\
        .eq("uploaded_by", user_id)\
        .is_("deleted_at", "null")\
        .limit(1)\
        .execute()
    
    return result.data[0]["id"] if result.data else None

def save_user_question(
    contract_id: str,
    question: str,
    answer: str,
    chunks_used: Optional[List] = None
) -> None:
    """Save a user question and answer to history."""
    supabase = get_supabase_client()
    
    data = {
        "contract_id": contract_id,
        "question": question,
        "answer": answer,
        "chunks_used": chunks_used or []
    }
    
    supabase.table("user_questions").insert(data).execute()

def get_contract_questions(contract_id: str) -> List[Dict]:
    """Get all questions asked about a contract."""
    supabase = get_supabase_client()
    
    result = supabase.table("user_questions")\
        .select("*")\
        .eq("contract_id", contract_id)\
        .order("asked_at", desc=True)\
        .execute()
    
    return result.data if result.data else []

def update_pinecone_status(contract_id: str, indexed: bool = True) -> None:
    """Mark contract as indexed in Pinecone."""
    supabase = get_supabase_client()
    
    supabase.table("contracts")\
        .update({"pinecone_indexed": indexed})\
        .eq("id", contract_id)\
        .execute()

def delete_contract_and_analyses(contract_id: str) -> bool:
    """
    Delete contract and all related data from Supabase.
    This includes:
    - Contract record (contracts table)
    - Risk analysis (risk_analyses table)
    - Contract analyses (contract_analyses table)
    - User questions (user_questions table)
    
    Returns: True if successful
    """
    supabase = get_supabase_client()
    
    try:
        # Delete user questions/Q&A history
        try:
            supabase.table("user_questions").delete().eq("contract_id", contract_id).execute()
            print(f"🗑️  Deleted user questions for contract {contract_id}")
        except Exception as e:
            print(f"ℹ️  Skipping user questions deletion: {e}")
        
        # Delete risk analysis
        try:
            supabase.table("risk_analyses").delete().eq("contract_id", contract_id).execute()
            print(f"🗑️  Deleted risk analysis for contract {contract_id}")
        except Exception as e:
            print(f"ℹ️  Skipping risk analysis deletion: {e}")
        
        # Delete contract analyses
        try:
            supabase.table("contract_analyses").delete().eq("contract_id", contract_id).execute()
            print(f"🗑️  Deleted contract analyses for contract {contract_id}")
        except Exception as e:
            print(f"ℹ️  Skipping contract analyses deletion: {e}")
        
        # Delete main contract record (this should always exist)
        supabase.table("contracts").delete().eq("id", contract_id).execute()
        print(f"🗑️  Deleted contract record {contract_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting contract from database: {e}")
        return False


def get_contract_storage_path(contract_id: str) -> Optional[str]:
    """Get the storage path for a contract's PDF."""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("contracts")\
            .select("storage_path")\
            .eq("id", contract_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0].get("storage_path")
        return None
        
    except Exception as e:
        print(f"❌ Error getting storage path: {e}")
        return None

