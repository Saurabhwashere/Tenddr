# Hybrid chunk classifier - uses keyword matching for speed, LLM for accuracy
# This is fast for most chunks, accurate for critical ones

import re
import json
from typing import List, Dict
from risk_catalog import CATEGORY_KEYWORDS, CLAUSE_TYPE_PATTERNS, RISK_DEFINITIONS
from rag import get_deepseek_client

def find_keyword_matches(text: str, keywords: List[str]) -> List[str]:
    """Find which keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    matches = []
    
    for keyword in keywords:
        # Look for whole words only (not partial matches)
        pattern = rf"\b{re.escape(keyword.lower())}\b"
        if re.search(pattern, text_lower):
            matches.append(keyword)
    
    return matches

def classify_chunk(chunk_text: str) -> Dict:
    """
    Classify a chunk of text by looking for keywords.
    
    Returns a simple dictionary with:
    - primary_category: main category (financial, legal, etc.)
    - clause_type: specific clause type (payment_terms, etc.)
    - risk_tags: list of risk IDs this chunk might relate to
    - keywords: list of keywords found in this chunk
    """
    if not chunk_text:
        return {
            "primary_category": "general",
            "clause_type": "unknown", 
            "risk_tags": [],
            "keywords": []
        }
    
    # Step 1: Find the category with most keyword matches
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = find_keyword_matches(chunk_text, keywords)
        category_scores[category] = len(matches)
    
    # Pick the category with most matches
    if category_scores:
        primary_category = max(category_scores, key=category_scores.get)
        if category_scores[primary_category] == 0:
            primary_category = "general"
    else:
        primary_category = "general"
    
    # Step 2: Find the clause type with most matches
    clause_type = "unknown"
    best_score = 0
    
    for clause, patterns in CLAUSE_TYPE_PATTERNS.items():
        matches = find_keyword_matches(chunk_text, patterns)
        if len(matches) > best_score:
            clause_type = clause
            best_score = len(matches)
    
    # Step 3: Find which risks this chunk might relate to
    risk_tags = []
    for risk_def in RISK_DEFINITIONS:
        matches = find_keyword_matches(chunk_text, risk_def["keywords"])
        if matches:  # If we found any keywords for this risk
            risk_tags.append(risk_def["risk_id"])
    
    # Step 4: Collect all keywords found
    all_keywords = set()
    
    # From categories
    for keywords in CATEGORY_KEYWORDS.values():
        matches = find_keyword_matches(chunk_text, keywords)
        all_keywords.update(matches)
    
    # From clause patterns  
    for patterns in CLAUSE_TYPE_PATTERNS.values():
        matches = find_keyword_matches(chunk_text, patterns)
        all_keywords.update(matches)
    
    return {
        "primary_category": primary_category,
        "clause_type": clause_type,
        "risk_tags": risk_tags,
        "keywords": sorted(list(all_keywords))
    }

def contains_high_value_content(text: str) -> bool:
    """Check if chunk contains financial/legal indicators that need accurate classification."""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Financial indicators
    financial_patterns = [
        r'\$[\d,]+',  # Dollar amounts
        r'[\d,]+\s*(?:dollars|aud|usd)',  # Written amounts
        r'\d+%',  # Percentages
        r'net\s+\d+',  # Net payment terms
        r'\d+\s+days',  # Time periods
        r'payment|invoice|retention|damages',  # Financial keywords
    ]
    
    # Legal indicators
    legal_patterns = [
        r'shall|must|will\s+not|prohibited',  # Legal obligations
        r'liable|liability|indemnify|indemnit',  # Liability terms
        r'terminate|termination',  # Termination
        r'dispute|arbitrat',  # Dispute resolution
    ]
    
    for pattern in financial_patterns + legal_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def classify_chunk_with_llm(chunk_text: str) -> Dict:
    """
    Use LLM (DeepSeek) to classify chunk with high accuracy.
    This is slower but more accurate than keyword matching.
    """
    client = get_deepseek_client()
    
    # Truncate if too long (keep first 800 chars for context)
    if len(chunk_text) > 800:
        chunk_text = chunk_text[:800] + "..."
    
    prompt = f"""Analyze this construction contract chunk and classify it.

Chunk: "{chunk_text}"

Return JSON with:
{{
    "primary_category": "financial|legal|compliance|project|operational|timeline|general",
    "clause_type": "payment_terms|liquidated_damages|retention|liability_indemnity|variations|termination_for_convenience|latent_conditions|whs_safety|insurance|unknown",
    "risk_level": "high|medium|low|none",
    "topics": ["list", "of", "specific", "topics"],
    "contains_numbers": true or false
}}

Categories:
- financial: payments, invoices, costs, penalties
- legal: liability, indemnity, termination, disputes
- compliance: safety, regulations, certifications
- project: scope, deliverables, specifications
- operational: processes, procedures, responsibilities
- timeline: dates, milestones, schedules
- general: other content

Return ONLY the JSON, no explanation."""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies contract text. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Also generate risk tags based on keywords (hybrid approach)
        risk_tags = []
        for risk_def in RISK_DEFINITIONS:
            matches = find_keyword_matches(chunk_text, risk_def["keywords"])
            if matches:
                risk_tags.append(risk_def["risk_id"])
        
        result["risk_tags"] = risk_tags
        result["keywords"] = []  # LLM provides topics instead
        
        return result
        
    except Exception as e:
        print(f"⚠️  LLM classification failed: {e}, falling back to keywords")
        # Fallback to keyword-based if LLM fails
        return classify_chunk(chunk_text)

def classify_chunk_hybrid(chunk_text: str) -> Dict:
    """
    Hybrid classification: Use keywords first, LLM for uncertain/critical cases.
    
    This is the main function to use - it's smart about when to use LLM.
    """
    # Step 1: Try keyword-based classification (fast, free)
    keyword_result = classify_chunk(chunk_text)
    
    # Step 2: Decide if we need LLM classification
    needs_llm = (
        # Case 1: Keyword approach is uncertain
        keyword_result["primary_category"] == "general" or
        keyword_result["clause_type"] == "unknown" or
        
        # Case 2: High-value content (financial/legal with numbers)
        (keyword_result["primary_category"] in ["financial", "legal"] and 
         contains_high_value_content(chunk_text)) or
        
        # Case 3: Multiple risk tags (complex clause)
        len(keyword_result["risk_tags"]) >= 2
    )
    
    # Step 3: Use LLM if needed, otherwise return keyword result
    if needs_llm:
        print(f"  🤖 Using LLM for high-value chunk (category: {keyword_result['primary_category']})")
        return classify_chunk_with_llm(chunk_text)
    else:
        return keyword_result


def classify_chunks_batch(chunks: list[dict], use_hybrid: bool = True) -> list[dict]:
    """
    Classify multiple chunks in parallel for 10x speedup.
    
    Keeps LLM classification for accuracy but processes chunks simultaneously.
    
    Args:
        chunks: List of chunk dicts with 'text' field
        use_hybrid: If True, use hybrid classification (LLM for important chunks)
    
    Returns:
        List of chunks with classification metadata added
    """
    import concurrent.futures
    from copy import deepcopy
    
    print(f"📝 Classifying {len(chunks)} chunks in parallel...")
    
    classified_chunks = []
    llm_count = 0
    
    def classify_one(chunk):
        """Classify a single chunk."""
        chunk_copy = deepcopy(chunk)
        if use_hybrid:
            classification = classify_chunk_hybrid(chunk_copy["text"])
            # Check if LLM was used (has 'topics' field)
            used_llm = "topics" in classification and classification.get("topics")
        else:
            classification = classify_chunk(chunk_copy["text"])
            used_llm = False
        
        chunk_copy.update(classification)
        return chunk_copy, used_llm
    
    # Process chunks in parallel (10 at a time to avoid rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_chunk = {
            executor.submit(classify_one, chunk): chunk 
            for chunk in chunks
        }
        
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                classified_chunk, used_llm = future.result()
                classified_chunks.append(classified_chunk)
                if used_llm:
                    llm_count += 1
            except Exception as e:
                # On error, use keyword-only classification
                original_chunk = future_to_chunk[future]
                chunk_copy = deepcopy(original_chunk)
                chunk_copy.update(classify_chunk(original_chunk["text"]))
                classified_chunks.append(chunk_copy)
                print(f"  ⚠️  Classification error, using keywords: {str(e)[:50]}")
    
    print(f"  ✅ Classified {len(classified_chunks)} chunks ({llm_count} used LLM for accuracy)")
    return classified_chunks
