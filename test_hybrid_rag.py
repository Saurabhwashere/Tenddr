#!/usr/bin/env python3
"""
Test script for Hybrid RAG Implementation
Tests the new multi-query, domain classification, and smart reranking
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query_expansion import (
    decompose_question_with_llm,
    classify_question_type,
    expand_query_by_domain,
    hybrid_multi_query_retrieval
)
from rag import query_contract, get_or_create_index, create_embeddings

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_question_decomposition(question):
    """Test LLM-based question decomposition"""
    print_section("TEST 1: LLM Question Decomposition")
    
    print(f"\n📝 Original Question:")
    print(f"   {question}")
    
    print(f"\n🧠 Decomposing with LLM...")
    try:
        queries = decompose_question_with_llm(question)
        
        print(f"\n✅ Generated {len(queries)} diverse queries:")
        for i, q in enumerate(queries, 1):
            print(f"   {i}. {q}")
        
        return queries
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return []

def test_domain_classification(question):
    """Test domain classification"""
    print_section("TEST 2: Domain Classification")
    
    print(f"\n📝 Question: {question}")
    
    try:
        domain = classify_question_type(question)
        
        print(f"\n✅ Classified as: {domain.upper()}")
        
        # Show what this means
        domain_descriptions = {
            'financial': 'Payments, costs, penalties, interest, retention',
            'timeline': 'Dates, deadlines, milestones, completion',
            'compliance': 'Regulations, certifications, licenses',
            'scope': 'Work scope, deliverables, specifications',
            'risk': 'Liability, indemnity, insurance, termination',
            'general': 'Other topics'
        }
        
        print(f"   Meaning: {domain_descriptions.get(domain, 'Unknown')}")
        
        return domain
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return "general"

def test_domain_expansion(question, domain):
    """Test domain-specific query expansion"""
    print_section("TEST 3: Domain-Specific Expansion")
    
    print(f"\n📝 Question: {question}")
    print(f"📂 Domain: {domain}")
    
    try:
        expanded = expand_query_by_domain(question, domain)
        
        print(f"\n✅ Generated {len(expanded)} domain-specific queries:")
        for i, q in enumerate(expanded, 1):
            print(f"   {i}. {q[:100]}{'...' if len(q) > 100 else ''}")
        
        return expanded
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return [question]

def test_single_query_retrieval(contract_id, question, user_id):
    """Test traditional single-query retrieval (baseline)"""
    print_section("TEST 4: Baseline Single-Query Retrieval")
    
    print(f"\n📝 Question: {question}")
    print(f"🔍 Using traditional single-query approach...")
    
    try:
        chunks = query_contract(contract_id, question, user_id, top_k=50)
        
        print(f"\n✅ Retrieved {len(chunks)} chunks")
        
        if chunks:
            print(f"\n📄 Top 3 chunks:")
            for i, chunk in enumerate(chunks[:3], 1):
                # Extract page number
                import re
                page_match = re.search(r'\[Page (\d+(?:\.\d+)?)\]', chunk)
                page = page_match.group(1) if page_match else "?"
                
                preview = chunk[:200].replace('\n', ' ')
                print(f"\n   {i}. [Page {page}]")
                print(f"      {preview}...")
        
        return len(chunks)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_hybrid_retrieval(contract_id, question, user_id):
    """Test new hybrid multi-query retrieval"""
    print_section("TEST 5: Hybrid Multi-Query Retrieval")
    
    print(f"\n📝 Question: {question}")
    print(f"🔀 Using NEW hybrid approach...")
    
    try:
        chunks = hybrid_multi_query_retrieval(
            contract_id,
            question,
            user_id,
            top_k_per_query=12
        )
        
        print(f"\n✅ Retrieved {len(chunks)} unique chunks")
        
        if chunks:
            print(f"\n📄 Top 5 chunks:")
            for i, chunk in enumerate(chunks[:5], 1):
                # Extract page number
                import re
                page_match = re.search(r'\[Page (\d+(?:\.\d+)?)\]', chunk)
                page = page_match.group(1) if page_match else "?"
                
                preview = chunk[:200].replace('\n', ' ')
                print(f"\n   {i}. [Page {page}]")
                print(f"      {preview}...")
        
        return len(chunks)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_specific_clause_finding(contract_id, user_id):
    """Test if hybrid approach finds specific critical clauses"""
    print_section("TEST 6: Critical Clause Detection")
    
    # Test for specific clauses that ContraVault found
    test_cases = [
        {
            "name": "No Interest on Withheld Amounts",
            "query": "no interest whatsoever shall be payable on any amount withheld",
            "expected_keywords": ["no interest", "withheld", "payable"]
        },
        {
            "name": "Withholding and Lien Provisions",
            "query": "withholding and retain any sum or sums payable to the contractor",
            "expected_keywords": ["withhold", "retain", "lien", "sums payable"]
        },
        {
            "name": "Recovery of Overpayments",
            "query": "audit overpayment recovery refund examination final bill",
            "expected_keywords": ["audit", "overpayment", "recovery", "refund"]
        },
        {
            "name": "Cross-Contract Lien",
            "query": "lien in respect of claims in other contracts",
            "expected_keywords": ["lien", "other contract", "cross-contract"]
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   Query: {test['query'][:80]}...")
        
        try:
            chunks = query_contract(contract_id, test['query'], user_id, top_k=5)
            
            if chunks:
                # Check if any expected keywords are in the results
                found_keywords = []
                for keyword in test['expected_keywords']:
                    for chunk in chunks:
                        if keyword.lower() in chunk.lower():
                            found_keywords.append(keyword)
                            break
                
                success = len(found_keywords) > 0
                results.append({
                    "name": test['name'],
                    "found": success,
                    "keywords_found": found_keywords,
                    "chunks_retrieved": len(chunks)
                })
                
                if success:
                    print(f"   ✅ FOUND - Keywords: {', '.join(found_keywords)}")
                else:
                    print(f"   ❌ NOT FOUND")
            else:
                print(f"   ❌ No chunks retrieved")
                results.append({
                    "name": test['name'],
                    "found": False,
                    "keywords_found": [],
                    "chunks_retrieved": 0
                })
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "name": test['name'],
                "found": False,
                "keywords_found": [],
                "chunks_retrieved": 0
            })
    
    # Summary
    print(f"\n📊 Summary:")
    found_count = sum(1 for r in results if r['found'])
    print(f"   Found {found_count}/{len(test_cases)} critical clauses")
    
    return results

def compare_approaches(contract_id, question, user_id):
    """Compare single-query vs hybrid approach"""
    print_section("TEST 7: Comparison - Single vs Hybrid")
    
    print(f"\n📝 Question: {question}")
    
    # Test single query
    print(f"\n1️⃣ Single-Query Approach:")
    single_count = 0
    try:
        single_chunks = query_contract(contract_id, question, user_id, top_k=50)
        single_count = len(single_chunks)
        print(f"   Retrieved: {single_count} chunks")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test hybrid
    print(f"\n2️⃣ Hybrid Multi-Query Approach:")
    hybrid_count = 0
    try:
        hybrid_chunks = hybrid_multi_query_retrieval(contract_id, question, user_id)
        hybrid_count = len(hybrid_chunks)
        print(f"   Retrieved: {hybrid_count} chunks")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Compare
    print(f"\n📊 Comparison:")
    print(f"   Single-Query: {single_count} chunks")
    print(f"   Hybrid:       {hybrid_count} chunks")
    
    if hybrid_count > single_count:
        improvement = ((hybrid_count - single_count) / single_count * 100) if single_count > 0 else 0
        print(f"   ✅ Hybrid found {improvement:.1f}% more chunks")
    elif hybrid_count == single_count:
        print(f"   ⚖️  Both approaches found same number of chunks")
    else:
        print(f"   ⚠️  Single-query found more (but hybrid has better diversity)")

def run_full_test(contract_id, user_id, question=None):
    """Run complete test suite"""
    
    print("\n" + "🚀"*40)
    print("  HYBRID RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🚀"*40)
    
    print(f"\n📋 Test Configuration:")
    print(f"   Contract ID: {contract_id}")
    print(f"   User ID: {user_id}")
    
    # Default test question
    if not question:
        question = "What are the penalties for delayed payments by the client? Give reasons why some of these can be unfair for the contractor?"
    
    print(f"   Question: {question[:100]}{'...' if len(question) > 100 else ''}")
    
    # Run all tests
    try:
        # Test 1: Question Decomposition
        llm_queries = test_question_decomposition(question)
        
        # Test 2: Domain Classification
        domain = test_domain_classification(question)
        
        # Test 3: Domain Expansion
        domain_queries = test_domain_expansion(question, domain)
        
        # Test 4: Single Query (Baseline)
        single_count = test_single_query_retrieval(contract_id, question, user_id)
        
        # Test 5: Hybrid Retrieval
        hybrid_count = test_hybrid_retrieval(contract_id, question, user_id)
        
        # Test 6: Critical Clause Finding
        clause_results = test_specific_clause_finding(contract_id, user_id)
        
        # Test 7: Direct Comparison
        compare_approaches(contract_id, question, user_id)
        
        # Final Summary
        print_section("FINAL SUMMARY")
        
        print(f"\n✅ Test Suite Completed Successfully!")
        
        print(f"\n📊 Results:")
        print(f"   LLM Queries Generated: {len(llm_queries)}")
        print(f"   Domain Classified: {domain}")
        print(f"   Domain Expansions: {len(domain_queries)}")
        print(f"   Single-Query Chunks: {single_count}")
        print(f"   Hybrid Chunks: {hybrid_count}")
        
        found_clauses = sum(1 for r in clause_results if r['found'])
        print(f"   Critical Clauses Found: {found_clauses}/4")
        
        # Overall assessment
        print(f"\n🎯 Overall Assessment:")
        
        if found_clauses >= 3 and hybrid_count >= single_count:
            print(f"   ✅ EXCELLENT - Hybrid approach is working as expected!")
            print(f"   ✅ Finding critical clauses that match ContraVault's output")
            print(f"   ✅ System is ready for production use")
        elif found_clauses >= 2:
            print(f"   🟡 GOOD - System is working but could be improved")
            print(f"   💡 Consider adjusting query expansion or reranking")
        else:
            print(f"   ⚠️  NEEDS IMPROVEMENT - Not finding enough critical clauses")
            print(f"   💡 Check Pinecone index, embeddings, or query strategies")
        
        print(f"\n📝 Recommendation:")
        if found_clauses >= 3:
            print(f"   Ready to test with real users!")
        else:
            print(f"   Review the detailed logs above to identify issues")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_hybrid_rag.py <contract_id> <user_id> [question]")
        print("\nExample:")
        print("python test_hybrid_rag.py 6ebc93f4-c30b-41d4-b6e0-12c8ed1552ea user_xxxxx")
        print('\nOr with custom question:')
        print('python test_hybrid_rag.py CONTRACT_ID USER_ID "What are the payment terms?"')
        sys.exit(1)
    
    contract_id = sys.argv[1]
    user_id = sys.argv[2]
    question = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Run the test suite
    success = run_full_test(contract_id, user_id, question)
    
    sys.exit(0 if success else 1)

