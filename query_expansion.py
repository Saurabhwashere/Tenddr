"""
Advanced Query Expansion for RAG Retrieval
Uses hybrid approach: LLM intelligence + domain knowledge
"""

import re
from typing import List, Dict
from rag import query_contract, get_deepseek_client

def decompose_question_with_llm(question: str) -> List[str]:
    """
    Use LLM to decompose a complex question into multiple search queries.
    This is generic and works for ANY question type.
    
    Args:
        question: The user's question
        
    Returns:
        List of 4-5 diverse search queries
    """
    client = get_deepseek_client()
    
    decomposition_prompt = f"""You are a contract analysis expert. A user asked this question about a construction contract:

"{question}"

To answer this comprehensively, we need to search the contract from multiple angles. Generate 4-5 diverse search queries that would help find ALL relevant information.

Rules:
1. Each query should focus on a DIFFERENT aspect or perspective
2. Include both positive queries (what exists) and negative queries (what doesn't exist)
3. Use specific contract terminology
4. Keep queries focused (10-15 words each)
5. Look for related but distinct concepts

Example:
Question: "What are the payment terms?"
Queries:
1. payment schedule milestones progress claims invoice submission
2. retention money percentage security deposit release conditions
3. interest on late delayed payments penalties compensation
4. withholding rights conditions Engineer-in-Charge approval
5. final payment completion certificate defects liability

Now generate queries for the user's question. Return ONLY the queries, one per line, no numbering."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a contract analysis expert. Generate search queries as requested."},
                {"role": "user", "content": decomposition_prompt}
            ],
            stream=False
        )
        
        # Parse the response into individual queries
        queries_text = response.choices[0].message.content
        queries = [q.strip() for q in queries_text.strip().split('\n') if q.strip()]
        
        # Remove numbering if present (1., 2., etc.)
        queries = [re.sub(r'^\d+[\.)]\s*', '', q) for q in queries]
        
        # Remove any empty queries
        queries = [q for q in queries if len(q) > 10]
        
        print(f"  🧠 LLM generated {len(queries)} diverse queries")
        return queries[:5]  # Max 5 queries
        
    except Exception as e:
        print(f"  ⚠️ Query decomposition failed: {e}, using original question")
        return [question]  # Fallback to original


def classify_question_type(question: str) -> str:
    """
    Classify the question into a domain category.
    
    Returns: 'financial', 'timeline', 'compliance', 'scope', 'risk', 'general'
    """
    client = get_deepseek_client()
    
    classification_prompt = f"""Classify this contract question into ONE category:

Question: "{question}"

Categories:
- financial: payments, costs, penalties, liquidated damages, retention, interest, withholding, audit
- timeline: dates, deadlines, milestones, completion, delays, schedule
- compliance: regulations, certifications, licenses, requirements, mandatory documents
- scope: work scope, deliverables, specifications, BOQ, technical requirements
- risk: liability, indemnity, insurance, warranties, termination, breach
- general: other topics not fitting above categories

Return ONLY the category name in lowercase, nothing else."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a contract classifier. Return only the category name."},
                {"role": "user", "content": classification_prompt}
            ],
            stream=False
        )
        
        category = response.choices[0].message.content.strip().lower()
        
        # Validate category
        valid_categories = ['financial', 'timeline', 'compliance', 'scope', 'risk', 'general']
        if category not in valid_categories:
            category = 'general'
        
        print(f"  📂 Question classified as: {category}")
        return category
        
    except Exception as e:
        print(f"  ⚠️ Classification failed: {e}, defaulting to general")
        return "general"


def expand_query_by_domain(question: str, domain: str) -> List[str]:
    """
    Expand query based on domain-specific knowledge.
    Generic rules that work for ANY contract in that domain.
    
    Args:
        question: Original question
        domain: Domain category (financial, timeline, etc.)
        
    Returns:
        List of expanded queries
    """
    base_queries = [question]  # Always include original
    
    # Domain-specific expansion patterns (generic, not contract-specific)
    expansion_rules = {
        'financial': [
            # General financial terms that apply to ANY contract
            f"{question} interest compensation penalties late payment",
            f"withholding retention lien security deposit no interest whatsoever",
            f"payment terms schedule invoice delayed payment client",
            f"audit overpayment recovery refund technical examination post payment",
            f"liquidated damages delay penalties contractor",
            f"cross-contract lien other contracts claims offset",
        ],
        'timeline': [
            f"{question} completion date schedule milestones deadlines",
            f"delay extension time liquidated damages {question}",
            f"submission deadlines approval processing {question}",
            f"defects liability period final completion {question}",
        ],
        'compliance': [
            f"{question} requirements mandatory certifications licenses",
            f"regulations standards specifications {question}",
            f"permits approval statutory {question}",
        ],
        'risk': [
            f"{question} liability indemnity insurance coverage",
            f"termination default breach consequences {question}",
            f"warranties guarantees defects {question}",
            f"force majeure disputes arbitration {question}",
        ],
        'scope': [
            f"{question} scope work deliverables specifications",
            f"bill quantities BOQ items rates {question}",
            f"technical requirements standards {question}",
            f"variations changes additions {question}",
        ],
        'general': [
            f"{question} contract terms conditions",
            f"obligations responsibilities {question}",
            f"rights duties {question}",
        ]
    }
    
    # Apply expansion rules for this domain
    if domain in expansion_rules:
        base_queries.extend(expansion_rules[domain])
    
    return base_queries[:7]  # Max 7 queries (1 original + 6 domain-specific)


def get_domain_metadata_filter(domain: str) -> Dict:
    """
    Get metadata filter for a specific domain.
    
    Args:
        domain: Domain category
        
    Returns:
        Pinecone metadata filter dict
    """
    filters = {
        'financial': {
            "$or": [
                {"primary_category": "financial"},
                {"clause_type": {"$in": ["payment_terms", "liquidated_damages", "retention"]}},
                {"keywords": {"$in": ["payment", "interest", "withholding", "lien", "penalty"]}}
            ]
        },
        'risk': {
            "$or": [
                {"primary_category": {"$in": ["legal", "compliance"]}},
                {"clause_type": {"$in": ["liability_indemnity", "termination_for_convenience", "insurance"]}}
            ]
        },
        'timeline': {
            "$or": [
                {"primary_category": "timeline"},
                {"keywords": {"$in": ["completion", "deadline", "milestone", "delay"]}}
            ]
        },
        'compliance': {
            "$or": [
                {"primary_category": "compliance"},
                {"keywords": {"$in": ["certification", "license", "approval", "regulation"]}}
            ]
        },
        'scope': {
            "$or": [
                {"primary_category": "project"},
                {"keywords": {"$in": ["scope", "BOQ", "specification", "deliverable"]}}
            ]
        },
    }
    
    return filters.get(domain, None)


def hybrid_multi_query_retrieval(
    contract_id: str, 
    question: str, 
    user_id: str,
    top_k_per_query: int = 12
) -> List[str]:
    """
    Hybrid query strategy combining LLM intelligence with domain knowledge.
    Generic and works for ANY question, ANY contract.
    
    Args:
        contract_id: Contract identifier
        question: User's question
        user_id: User identifier
        top_k_per_query: Chunks to retrieve per query
        
    Returns:
        List of unique, diverse chunks
    """
    print(f"\n  🔀 HYBRID MULTI-QUERY RETRIEVAL")
    print(f"  Question: {question[:80]}{'...' if len(question) > 80 else ''}")
    
    # Step 1: Classify domain
    domain = classify_question_type(question)
    
    # Step 2: LLM generates diverse sub-queries
    llm_queries = decompose_question_with_llm(question)
    
    # Step 3: Add domain-specific expansions
    domain_queries = expand_query_by_domain(question, domain)
    
    # Step 4: Combine and deduplicate queries
    all_queries = [question] + llm_queries + domain_queries
    
    # Simple deduplication by similarity (less aggressive for financial questions)
    unique_queries = []
    seen_words = set()
    
    for query in all_queries:
        # Create a signature from query words
        words = set(query.lower().split())
        
        # If this query has significantly different words, keep it
        # For financial domain, be less aggressive (allow more similar queries)
        threshold = 2 if domain == 'financial' else 3
        if not seen_words or len(words - seen_words) > threshold:
            unique_queries.append(query)
            seen_words.update(words)
    
    unique_queries = unique_queries[:8]  # Max 8 diverse queries for comprehensive coverage
    
    print(f"  📊 Using {len(unique_queries)} unique queries")
    
    # Step 5: Get metadata filter for domain
    metadata_filter = get_domain_metadata_filter(domain)
    
    # Step 6: Retrieve with smart deduplication
    # Allow multiple chunks per page if they're different enough
    all_chunks = []  # List of (page_num, chunk, score) tuples
    seen_content = set()  # Track unique content hashes
    
    for i, query in enumerate(unique_queries, 1):
        print(f"    Query {i}/{len(unique_queries)}: {query[:60]}...")
        
        try:
            chunks = query_contract(
                contract_id, 
                query, 
                user_id, 
                top_k=top_k_per_query,
                metadata_filter=metadata_filter
            )
            
            # Process chunks with deduplication
            for chunk in chunks:
                # Extract page number
                page_match = re.search(r'\[Page (\d+(?:\.\d+)?)\]', chunk)
                page_num = page_match.group(1) if page_match else "unknown"
                
                # Create content hash (first 200 chars for uniqueness check)
                content_hash = hash(chunk[:200])
                
                # Add if not duplicate content
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    # Store with page number for sorting
                    all_chunks.append((page_num, chunk))
        
        except Exception as e:
            print(f"      ⚠️ Query failed: {str(e)[:50]}")
            continue
    
    # Sort by page number for coherence, but keep multiple chunks per page
    try:
        sorted_chunks = sorted(
            all_chunks,
            key=lambda x: float(x[0]) if isinstance(x[0], str) and x[0].replace('.', '').isdigit() else 9999
        )
        result_chunks = [chunk for _, chunk in sorted_chunks]
    except:
        result_chunks = [chunk for _, chunk in all_chunks]
    
    print(f"  ✅ Retrieved {len(result_chunks)} unique chunks from {len(unique_queries)} queries\n")
    
    return result_chunks[:50]  # Return top 50 diverse chunks


# Legacy function for backward compatibility
def multi_query_retrieval(
    contract_id: str, 
    question: str, 
    user_id: str,
    top_k_per_query: int = 20,
    metadata_filter: Dict = None
) -> List[str]:
    """
    Legacy function - redirects to hybrid approach.
    Kept for backward compatibility.
    """
    return hybrid_multi_query_retrieval(contract_id, question, user_id, top_k_per_query)
