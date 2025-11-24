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
    AUDIT_TRAIL_PROMPT,
    BID_QUALIFYING_CRITERIA_PROMPT
)

def get_context(contract_id: str, query: str, user_id: str) -> str:
    """
    Get context using RAG only - no fallback.
    Retrieves relevant chunks from entire contract.
    """
    chunks = query_contract(contract_id, query, user_id, top_k=50)
    return "\n\n".join(chunks) if chunks else ""

def analyze_compliance(contract_id: str, text: str, user_id: str) -> str:
    """Extract compliance checklist using RAG to find info anywhere in contract."""
    query = "compliance requirements mandatory documents licenses certifications eligibility"
    context = get_context(contract_id, query, user_id)
    prompt = COMPLIANCE_CHECKLIST_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_clauses(contract_id: str, text: str, user_id: str) -> str:
    """Summarize contract clauses using RAG."""
    query = "contract clauses terms conditions obligations liabilities scope of work"
    context = get_context(contract_id, query, user_id)
    prompt = CLAUSE_SUMMARY_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_scope_alignment(contract_id: str, text: str, user_id: str) -> str:
    """Check scope alignment using RAG."""
    query = "scope of work bill of quantities BOQ specifications technical requirements"
    context = get_context(contract_id, query, user_id)
    prompt = SCOPE_ALIGNMENT_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def check_completeness(contract_id: str, text: str, user_id: str) -> str:
    """Check submission completeness using RAG."""
    query = "submission requirements documents formats annexures appendices schedules"
    context = get_context(contract_id, query, user_id)
    prompt = COMPLETENESS_CHECK_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def extract_timeline(contract_id: str, text: str, user_id: str) -> str:
    """Extract timeline using RAG."""
    query = "timeline milestones deadlines schedule completion date delivery period"
    context = get_context(contract_id, query, user_id)
    prompt = TIMELINE_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_financial_risks(contract_id: str, text: str, user_id: str) -> str:
    """
    Analyze financial risks using hybrid multi-query RAG.
    Uses LLM-based query decomposition + domain knowledge for comprehensive coverage.
    """
    from query_expansion import hybrid_multi_query_retrieval
    
    # Use hybrid approach with a comprehensive financial question
    financial_question = """What are all the financial provisions in this contract including: 
    payment terms and schedules, penalties and liquidated damages on the contractor, 
    penalties or interest on delayed payments by the client, withholding and lien rights, 
    retention provisions, audit and overpayment recovery rights, and any cross-contract 
    lien or offset provisions?"""
    
    print("  💎 Using HYBRID multi-query strategy for comprehensive financial analysis...")
    chunks = hybrid_multi_query_retrieval(
        contract_id, 
        financial_question, 
        user_id, 
        top_k_per_query=12
    )
    
    context = "\n\n".join(chunks[:50]) if chunks else ""
    
    print(f"  ✓ Final context: {len(chunks[:50])} unique chunks")
    
    prompt = FINANCIAL_RISK_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def generate_audit_trail(contract_id: str, text: str, user_id: str) -> str:
    """Generate audit trail using RAG."""
    query = "version amendments modifications changes revisions audit history"
    context = get_context(contract_id, query, user_id)
    prompt = AUDIT_TRAIL_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_bid_qualifying_criteria(contract_id: str, text: str, user_id: str) -> str:
    """
    Analyze bid qualifying criteria using hybrid multi-query RAG.
    Identifies financial, technical, and compliance barriers to entry.
    Provides detailed assessment of whether criteria are too harsh.
    """
    from query_expansion import hybrid_multi_query_retrieval
    
    # Use hybrid approach with a comprehensive bid criteria question
    bid_criteria_question = """What are all the bid qualifying criteria in this contract including: 
    financial requirements (EMD, credit facilities, turnover, investment, bank guarantees), 
    technical experience requirements (similar works, key personnel, equipment, certifications), 
    and compliance requirements (responsiveness, conditional bids, documentation, disqualification rules)?"""
    
    print("  💎 Using HYBRID multi-query strategy for bid qualifying criteria analysis...")
    chunks = hybrid_multi_query_retrieval(
        contract_id, 
        bid_criteria_question, 
        user_id, 
        top_k_per_query=15  # More chunks for comprehensive coverage
    )
    
    context = "\n\n".join(chunks[:50]) if chunks else ""
    
    print(f"  ✓ Final context: {len(chunks[:50])} unique chunks")
    
    prompt = BID_QUALIFYING_CRITERIA_PROMPT.format(contract_text=context)
    return generate_response(prompt)

def analyze_contract_overview(contract_id: str, text: str, user_id: str) -> dict:
    """
    Extract key contract overview information during initial analysis.
    
    Returns dict with pre-populated answers for default topics:
    - Project Name
    - Project Location
    - Payment Terms
    - Estimated Values
    """
    from query_expansion import hybrid_multi_query_retrieval
    from prompts import QA_SYSTEM_PROMPT
    import re
    import traceback
    
    print("  ✓ Extracting contract overview...")
    
    # Define default topics
    default_topics = [
        {
            "id": "1",
            "title": "Project Name",
            "question": "What is the name of the project or contract?"
        },
        {
            "id": "2",
            "title": "Project Location",
            "question": "Where is the project located? Include city, state, and any specific site details."
        },
        {
            "id": "3",
            "title": "Payment Terms",
            "question": "What are the payment terms? Include payment schedule, retention, and any key financial conditions."
        },
        {
            "id": "4",
            "title": "Estimated Values",
            "question": "What is the contract value or estimated project cost?"
        }
    ]
    
    overview_data = []
    
    for topic in default_topics:
        try:
            print(f"    → Analyzing {topic['title']}...")
            
            # Use hybrid retrieval for comprehensive context
            chunks = hybrid_multi_query_retrieval(
                contract_id=contract_id,
                question=topic["question"],
                user_id=user_id,
                top_k_per_query=10
            )
            
            if not chunks:
                print(f"    ⚠️  No chunks found for {topic['title']}")
                raise Exception("No relevant content found")
            
            # Build context (chunks are strings with embedded page numbers)
            context = "\n\n".join(chunks[:15])
            
            if not context.strip():
                print(f"    ⚠️  Empty context for {topic['title']}")
                raise Exception("Empty context")
            
            # Generate answer
            prompt = QA_SYSTEM_PROMPT.format(
                question=topic["question"],
                context=context
            )
            
            answer = generate_response(prompt)
            
            # Extract all page numbers from answer
            page_matches = re.findall(r'\[Page (\d+)\]', answer)
            page_numbers = list(set(page_matches))  # Remove duplicates
            
            # Remove page references from answer for summarization
            clean_answer = re.sub(r'\[Page \d+\]', '', answer).strip()
            
            # Create concise summary (200-300 words) using LLM - direct call, no RAG
            summary_prompt = f"""Summarize the following text in 300 words or less. 
Focus on the key facts and information. Be direct and factual. 
Do not use phrases like "Based on the context" or "According to the document".
Write in a natural, conversational tone that summarizes the key points.

Text to summarize:
{clean_answer}

Concise Summary (300 words max):"""
            
            summary = generate_response(summary_prompt)
            
            overview_data.append({
                "id": topic["id"],
                "title": topic["title"],
                "question": topic["question"],
                "summary": summary,
                "pageNumbers": page_numbers  # Array of page numbers
            })
            
            print(f"    ✓ {topic['title']}: {summary[:50]}... (Pages: {', '.join(page_numbers) if page_numbers else 'N/A'})")
            
        except Exception as e:
            print(f"    ❌ Failed to analyze {topic['title']}: {e}")
            traceback.print_exc()
            # Add empty entry if analysis fails
            overview_data.append({
                "id": topic["id"],
                "title": topic["title"],
                "question": topic["question"],
                "summary": "Analysis pending - data could not be extracted from the contract.",
                "pageNumbers": []
            })
    
    print(f"  ✅ Contract overview complete: {len(overview_data)} topics processed")
    return {"topics": overview_data}

def run_comprehensive_analysis(contract_id: str, text: str, user_id: str) -> dict:
    """
    Run all 5 analyses using RAG for better accuracy - IN PARALLEL for maximum speed!
    
    Uses RAG to find relevant sections anywhere in contract,
    not just first few pages.
    
    OPTIMIZED: All analyses run concurrently using ThreadPoolExecutor for 4-6x speedup.
    
    Note: Risk detection runs separately via run_risk_analysis()
    
    Args:
        contract_id: Contract ID for Pinecone queries
        text: Full contract text (fallback)
        user_id: User ID for queries
    
    Returns:
        dict with 5 analysis results + validation info
    """
    import time
    import concurrent.futures
    
    analysis_start = time.time()
    print("🔍 Running comprehensive contract analysis with RAG (PARALLEL MODE)...")
    
    # Define all analysis tasks
    analysis_tasks = {
        'contract_overview': (analyze_contract_overview, "📊 Extracting contract overview..."),
        'scope_alignment': (analyze_scope_alignment, "✓ Checking scope alignment..."),
        'timeline_milestones': (extract_timeline, "✓ Extracting timeline & milestones..."),
        'financial_risks': (analyze_financial_risks, "✓ Analyzing financial risks..."),
        'bid_qualifying_criteria': (analyze_bid_qualifying_criteria, "✓ Analyzing bid qualifying criteria...")
    }
    
    # Run all analyses in parallel
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_key = {
            executor.submit(func, contract_id, text, user_id): (key, msg)
            for key, (func, msg) in analysis_tasks.items()
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_key):
            key, msg = future_to_key[future]
            try:
                print(f"  {msg}")
                results[key] = future.result()
                print(f"    ✅ {key} completed")
            except Exception as e:
                print(f"    ❌ {key} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                # Provide appropriate fallback based on analysis type
                if key == 'contract_overview':
                    results[key] = {"topics": []}
                else:
                    results[key] = f"Analysis failed: {str(e)}"
    
    # Simple validation: check all sections have content
    validation = validate_analysis_completeness(results)
    results["validation"] = validation
    
    # Calculate and display analysis time
    analysis_end = time.time()
    analysis_time = analysis_end - analysis_start
    minutes = int(analysis_time // 60)
    seconds = int(analysis_time % 60)
    print(f"✅ Analysis complete! Completeness: {validation['completeness_score']:.0%}")
    print(f"⏱️  Analysis time: {minutes}m {seconds}s ({analysis_time:.2f}s) - PARALLEL SPEEDUP!")
    
    return results

def validate_analysis_completeness(results: dict) -> dict:
    """
    Simple validation to check all analyses completed.
    
    Returns validation report with completeness score.
    """
    required_sections = [
        "contract_overview",
        "scope_alignment",
        "timeline_milestones",
        "financial_risks",
        "bid_qualifying_criteria"
    ]
    
    # Check which sections have content
    present = []
    missing = []
    
    for section in required_sections:
        if section in results and results[section]:
            # Special handling for contract_overview (it's a dict with "topics")
            if section == "contract_overview":
                if isinstance(results[section], dict) and "topics" in results[section]:
                    topics = results[section]["topics"]
                    # Check if we have topics with actual content (not just "Analysis pending")
                    valid_topics = [t for t in topics if t.get("summary") and "Analysis pending" not in t.get("summary", "")]
                    
                    print(f"  📊 Validation: contract_overview has {len(topics)} topics, {len(valid_topics)} valid")
                    
                    if len(valid_topics) > 0:
                        present.append(section)
                    else:
                        missing.append(section)
                else:
                    print(f"  ⚠️ Validation: contract_overview is not a dict or missing topics")
                    missing.append(section)
            # Regular string-based sections
            elif isinstance(results[section], str) and len(results[section]) > 50:
                present.append(section)
            else:
                missing.append(section)
        else:
            print(f"  ⚠️ Validation: {section} not in results or is empty")
            missing.append(section)
    
    completeness_score = len(present) / len(required_sections) if required_sections else 0
    
    return {
        "completeness_score": completeness_score,
        "sections_completed": len(present),
        "total_sections": len(required_sections),
        "present": present,
        "missing": missing,
        "status": "COMPLETE" if completeness_score >= 0.9 else "INCOMPLETE",
        "recommendation": "Ready for review" if completeness_score >= 0.9 else "Some sections incomplete - manual review needed"
    }

