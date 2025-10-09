# Contract Analysis Functions
# Simple, clear functions for comprehensive contract analysis

from rag import generate_response, query_contract
from prompts import (
    COMPLIANCE_CHECKLIST_PROMPT,
    CLAUSE_SUMMARY_PROMPT,
    SCOPE_ALIGNMENT_PROMPT,
    COMPLETENESS_CHECK_PROMPT,
    TIMELINE_PROMPT,
    FINANCIAL_RISK_PROMPT,
    AUDIT_TRAIL_PROMPT
)

def get_context(contract_id: str, query: str) -> str:
    """
    Get context using RAG only - no fallback.
    Retrieves relevant chunks from entire contract.
    """
    chunks = query_contract(contract_id, query, top_k=20)
    return "\n\n".join(chunks) if chunks else ""

def analyze_compliance(contract_id: str, text: str) -> str:
    """Extract compliance checklist using RAG to find info anywhere in contract."""
    query = "compliance requirements mandatory documents licenses certifications eligibility"
    context = get_context(contract_id, query)
    prompt = COMPLIANCE_CHECKLIST_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_clauses(contract_id: str, text: str) -> str:
    """Summarize contract clauses using RAG."""
    query = "contract clauses terms conditions obligations liabilities scope of work"
    context = get_context(contract_id, query)
    prompt = CLAUSE_SUMMARY_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_scope_alignment(contract_id: str, text: str) -> str:
    """Check scope alignment using RAG."""
    query = "scope of work bill of quantities BOQ specifications technical requirements"
    context = get_context(contract_id, query)
    prompt = SCOPE_ALIGNMENT_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def check_completeness(contract_id: str, text: str) -> str:
    """Check submission completeness using RAG."""
    query = "submission requirements documents formats annexures appendices schedules"
    context = get_context(contract_id, query)
    prompt = COMPLETENESS_CHECK_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def extract_timeline(contract_id: str, text: str) -> str:
    """Extract timeline using RAG."""
    query = "timeline milestones deadlines schedule completion date delivery period"
    context = get_context(contract_id, query)
    prompt = TIMELINE_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_financial_risks(contract_id: str, text: str) -> str:
    """Analyze financial risks using RAG."""
    query = "payment price cost penalties liquidated damages financial obligations security"
    context = get_context(contract_id, query)
    prompt = FINANCIAL_RISK_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def generate_audit_trail(contract_id: str, text: str) -> str:
    """Generate audit trail using RAG."""
    query = "version amendments modifications changes revisions audit history"
    context = get_context(contract_id, query)
    prompt = AUDIT_TRAIL_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def run_comprehensive_analysis(contract_id: str, text: str) -> dict:
    """
    Run all 7 analyses using RAG for better accuracy.
    
    Uses RAG to find relevant sections anywhere in contract,
    not just first few pages.
    
    Args:
        contract_id: Contract ID for Pinecone queries
        text: Full contract text (fallback)
    
    Returns:
        dict with 7 analysis results + validation info
    """
    print("🔍 Running comprehensive contract analysis with RAG...")
    
    results = {}
    
    # Run each analysis with RAG
    print("  ✓ Analyzing compliance checklist...")
    results["compliance_checklist"] = analyze_compliance(contract_id, text)
    
    print("  ✓ Analyzing contract clauses...")
    results["clause_summaries"] = analyze_clauses(contract_id, text)
    
    print("  ✓ Checking scope alignment...")
    results["scope_alignment"] = analyze_scope_alignment(contract_id, text)
    
    print("  ✓ Verifying submission completeness...")
    results["completeness_check"] = check_completeness(contract_id, text)
    
    print("  ✓ Extracting timeline & milestones...")
    results["timeline_milestones"] = extract_timeline(contract_id, text)
    
    print("  ✓ Analyzing financial risks...")
    results["financial_risks"] = analyze_financial_risks(contract_id, text)
    
    print("  ✓ Generating audit trail...")
    results["audit_trail"] = generate_audit_trail(contract_id, text)
    
    # Simple validation: check all sections have content
    validation = validate_analysis_completeness(results)
    results["validation"] = validation
    
    print(f"✅ Analysis complete! Completeness: {validation['completeness_score']:.0%}")
    
    return results

def validate_analysis_completeness(results: dict) -> dict:
    """
    Simple validation to check all analyses completed.
    
    Returns validation report with completeness score.
    """
    required_sections = [
        "compliance_checklist",
        "clause_summaries", 
        "scope_alignment",
        "completeness_check",
        "timeline_milestones",
        "financial_risks",
        "audit_trail"
    ]
    
    # Check which sections have content
    present = []
    missing = []
    
    for section in required_sections:
        if section in results and results[section] and len(results[section]) > 50:
            present.append(section)
        else:
            missing.append(section)
    
    completeness_score = len(present) / len(required_sections)
    
    return {
        "completeness_score": completeness_score,
        "sections_completed": len(present),
        "total_sections": len(required_sections),
        "present": present,
        "missing": missing,
        "status": "COMPLETE" if completeness_score >= 0.9 else "INCOMPLETE",
        "recommendation": "Ready for review" if completeness_score >= 0.9 else "Some sections incomplete - manual review needed"
    }

