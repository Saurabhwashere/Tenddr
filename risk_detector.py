# LLM-Powered Risk Detection System with RAG
# Detects critical risks in construction contracts using GPT-4 + Pinecone search

import json
from typing import Dict, List
from rag import query_contract, get_openai_client
from risk_catalog import RISK_DEFINITIONS

# Use risk definitions from the catalog
# RISK_DEFINITIONS is now imported from risk_catalog.py


def detect_risk_with_llm(
    contract_id: str,
    risk_definition: Dict,
    model: str = "gpt-4o"
) -> Dict:
    """
    Detect a specific risk using RAG + GPT-4o analysis.

    How it works:
    1. Use RAG to search entire contract for relevant sections (Pinecone + reranking)
    2. If relevant chunks found, send to LLM for analysis
    3. LLM identifies risk, assesses severity, extracts evidence
    4. Return structured results

    Args:
        contract_id: Contract ID to search in Pinecone
        risk_definition: Risk definition dict from RISK_DEFINITIONS
        model: OpenAI model to use (default: gpt-4o)

    Returns:
        Dict with structured risk analysis results
    """
    # Step 1: Use RAG to find relevant contract sections with metadata filtering
    search_query = risk_definition["search_query"]
    
    # Build metadata filter based on risk definition
    # Build Pinecone metadata filter from risk definition (use OR logic for better matching)
    metadata_filter = {
        "$or": [
            {"primary_category": {"$in": [risk_definition.get("category", "general")]}},
            {"clause_type": {"$eq": risk_definition.get("clause_type", "unknown")}}
        ]
    }
    
    print(f"     🎯 Filtering by category: {risk_definition.get('category')}, clause_type: {risk_definition.get('clause_type')}")
    relevant_chunks = query_contract(contract_id, search_query, top_k=30, metadata_filter=metadata_filter)

    # Optimization: If no relevant chunks found, skip LLM call
    if not relevant_chunks or len(relevant_chunks) == 0:
        print(f"     ℹ️  No relevant sections found for '{risk_definition['risk_name']}'")
        return {
            "found": False,
            "risk_id": risk_definition["risk_id"],
            "risk_name": risk_definition["risk_name"],
            "severity": "low",
            "evidence": "N/A",
            "explanation": "No relevant contract sections found containing this risk",
            "financial_impact": "N/A",
            "comparison": "Unable to assess - relevant clauses not found",
            "recommendation": "No action needed for this risk"
        }

    # Step 2: Combine chunks into contract text for analysis (limit to ~3000 chars)
    contract_text = "\n\n".join(relevant_chunks[:10])  # Top 10 chunks after reranking
    if len(contract_text) > 3000:
        contract_text = contract_text[:3000]

    # Step 3: Build the LLM prompt
    client = get_openai_client()

    prompt = f"""You are a construction contract risk analyst with expertise in identifying financial and legal risks.

Analyze this contract section for the following risk:

RISK: {risk_definition['risk_name']}
DESCRIPTION: {risk_definition['definition'].strip()}
INDUSTRY BENCHMARK: {risk_definition['benchmarks']}

SEVERITY CRITERIA:
{json.dumps(risk_definition['severity_rules'], indent=2)}

INDUSTRY RECOMMENDATIONS:
{risk_definition.get('recommendations', 'No specific recommendations available')}

CONTRACT TEXT (Retrieved via semantic search):
{contract_text}

Your task:
1. Determine if this risk is present in the contract (yes/no)
2. If yes, assess the severity level (critical/high/medium/low) based on the criteria above
3. Extract the specific evidence - quote the EXACT clause(s) that contain this risk, including clause numbers/titles if mentioned
4. Explain why this is risky for the contractor
5. Estimate the financial impact in concrete dollar terms if possible (or state "N/A" if not quantifiable)
6. Compare the contract terms to the industry standard benchmark
7. Provide specific, actionable negotiation advice (reference the industry recommendations above when relevant)

IMPORTANT: In your evidence field, include:
- The clause number or section title (e.g., "Clause 3.2: Payment Terms" or "Section 5: Liquidated Damages")
- The page number reference (already in the text as [Page X])
- The exact problematic text

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just raw JSON):
{{
  "found": true or false,
  "severity": "critical" or "high" or "medium" or "low",
  "evidence": "Clause/Section reference + exact quote from contract with [Page X] citations",
  "explanation": "clear explanation of why this is risky",
  "financial_impact": "estimated cost in dollars or 'N/A'",
  "comparison": "how contract terms compare to industry standard",
  "recommendation": "specific negotiation advice referencing industry best practices"
}}

If the risk is NOT found, return:
{{
  "found": false,
  "severity": "low",
  "evidence": "N/A",
  "explanation": "This risk was not identified in the contract text",
  "financial_impact": "N/A",
  "comparison": "Terms appear acceptable",
  "recommendation": "No action needed for this risk"
}}
"""

    try:
        # Step 4: Call GPT-4 with JSON mode for structured output
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Consistent results
            response_format={"type": "json_object"}  # Force JSON output
        )

        # Step 5: Parse the JSON response
        result = json.loads(response.choices[0].message.content)

        # Add metadata
        result["risk_id"] = risk_definition["risk_id"]
        result["risk_name"] = risk_definition["risk_name"]

        return result

    except json.JSONDecodeError as e:
        print(f"     ⚠️  JSON parsing error: {e}")
        return {
            "found": False,
            "risk_id": risk_definition["risk_id"],
            "risk_name": risk_definition["risk_name"],
            "severity": "low",
            "evidence": "N/A",
            "explanation": "Error analyzing this risk",
            "financial_impact": "N/A",
            "comparison": "N/A",
            "recommendation": "Manual review recommended"
        }
    except Exception as e:
        print(f"     ⚠️  Error analyzing: {e}")
        return {
            "found": False,
            "risk_id": risk_definition["risk_id"],
            "risk_name": risk_definition["risk_name"],
            "severity": "low",
            "evidence": "N/A",
            "explanation": f"Error: {str(e)}",
            "financial_impact": "N/A",
            "comparison": "N/A",
            "recommendation": "Manual review recommended"
        }


def run_risk_analysis(contract_id: str, model: str = "gpt-4o") -> Dict:
    """
    Run all risk detection checks on a contract using RAG.

    Uses Pinecone to search entire contract for each risk type,
    then analyzes relevant sections with GPT-4o.

    Args:
        contract_id: Contract ID in Pinecone
        model: OpenAI model to use (default: gpt-4o)

    Returns:
        Dict with:
        - risks_by_severity: Dict organized by severity level
        - all_risks: List of all risk analysis results
        - summary: High-level statistics
    """
    print("\n🔍 Running LLM-powered risk detection with RAG...")
    print(f"📄 Contract ID: {contract_id}")
    print(f"🤖 Model: {model}")
    print(f"🔎 Searching entire contract using Pinecone + reranking\n")

    all_risks = []
    risks_found = 0

    # Run detection for each risk
    for i, risk_def in enumerate(RISK_DEFINITIONS, 1):
        print(f"  [{i}/{len(RISK_DEFINITIONS)}] Checking: {risk_def['risk_name']}...")

        result = detect_risk_with_llm(
            contract_id=contract_id,
            risk_definition=risk_def,
            model=model
        )

        all_risks.append(result)

        if result["found"]:
            risks_found += 1
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(result["severity"], "⚪")
            print(f"     {severity_emoji} FOUND - Severity: {result['severity'].upper()}")
        else:
            print(f"     ✅ Not detected")

    # Organize risks by severity
    risks_by_severity = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }

    for risk in all_risks:
        if risk["found"]:
            severity = risk.get("severity", "low")
            risks_by_severity[severity].append(risk)

    # Generate summary
    summary = {
        "total_risks_checked": len(RISK_DEFINITIONS),
        "total_risks_found": risks_found,
        "critical_count": len(risks_by_severity["critical"]),
        "high_count": len(risks_by_severity["high"]),
        "medium_count": len(risks_by_severity["medium"]),
        "low_count": len(risks_by_severity["low"]),
        "overall_risk_level": _calculate_overall_risk_level(risks_by_severity)
    }

    print(f"\n✅ Risk analysis complete!")
    print(f"   Found {risks_found}/{len(RISK_DEFINITIONS)} risks")
    print(f"   🔴 Critical: {summary['critical_count']}")
    print(f"   🟠 High: {summary['high_count']}")
    print(f"   🟡 Medium: {summary['medium_count']}")
    print(f"   Overall risk level: {summary['overall_risk_level'].upper()}\n")

    return {
        "risks_by_severity": risks_by_severity,
        "all_risks": all_risks,
        "summary": summary
    }


def _calculate_overall_risk_level(risks_by_severity: Dict) -> str:
    """
    Calculate overall risk level based on detected risks.

    Logic:
    - Any critical risk = CRITICAL overall
    - 2+ high risks = CRITICAL overall
    - 1 high risk = HIGH overall
    - 2+ medium risks = HIGH overall
    - 1 medium risk = MEDIUM overall
    - Otherwise = LOW overall
    """
    if len(risks_by_severity["critical"]) > 0:
        return "critical"
    elif len(risks_by_severity["high"]) >= 2:
        return "critical"
    elif len(risks_by_severity["high"]) == 1:
        return "high"
    elif len(risks_by_severity["medium"]) >= 2:
        return "high"
    elif len(risks_by_severity["medium"]) == 1:
        return "medium"
    else:
        return "low"
