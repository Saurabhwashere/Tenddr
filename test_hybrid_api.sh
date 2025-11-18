#!/bin/bash
# Test Hybrid RAG via API endpoints

# Get parameters or use defaults
CONTRACT_ID="${1:-71286297-7eba-4e80-9e03-ec77c9d3ee63}"
USER_ID="${2:-user_34GbG3iFfJymevgjYYrmw4YxXBb}"
API_URL="http://localhost:8000"

echo "🚀 =========================================="
echo "   HYBRID RAG SYSTEM - API TEST SUITE"
echo "=========================================="
echo ""
echo "📋 Configuration:"
echo "   Contract ID: $CONTRACT_ID"
echo "   User ID: $USER_ID"
echo "   API URL: $API_URL"
echo ""

# Test 1: Financial Question (Main Test)
echo "=========================================="
echo "TEST 1: Financial Question (Penalties)"
echo "=========================================="
echo ""
echo "📝 Question: What are the penalties for delayed payments by the client?"
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/qa/$CONTRACT_ID" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER_ID" \
  -d '{"question": "What are the penalties for delayed payments by the client? Give reasons why some of these can be unfair for the contractor?"}')

echo "📊 Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if response contains key phrases
if echo "$RESPONSE" | grep -qi "no interest"; then
    echo "✅ Found 'no interest' clause"
else
    echo "❌ Missing 'no interest' clause"
fi

if echo "$RESPONSE" | grep -qi "withhold"; then
    echo "✅ Found 'withholding' provisions"
else
    echo "❌ Missing 'withholding' provisions"
fi

if echo "$RESPONSE" | grep -qi "page"; then
    echo "✅ Includes page citations"
else
    echo "❌ Missing page citations"
fi

if echo "$RESPONSE" | grep -qi "unfair"; then
    echo "✅ Explains unfairness"
else
    echo "❌ Missing unfairness explanation"
fi

echo ""
echo "=========================================="
echo "TEST 2: Debug Query (Pipeline Details)"
echo "=========================================="
echo ""

DEBUG_RESPONSE=$(curl -s -X POST "$API_URL/debug/query/$CONTRACT_ID" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the penalties for delayed payments by the client?"}')

echo "📊 Pipeline Summary:"
echo "$DEBUG_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps(data.get('pipeline_summary', {}), indent=2))" 2>/dev/null

echo ""
echo "📄 Top 3 Retrieved Chunks:"
echo "$DEBUG_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  {i+1}. [Page {c['page']}] Score: {c['pinecone_score']:.3f}\\n     {c['text_preview'][:100]}...\\n\") for i, c in enumerate(data.get('pinecone_top_20', [])[:3])]" 2>/dev/null

echo ""
echo "=========================================="
echo "TEST 3: Timeline Question"
echo "=========================================="
echo ""

TIMELINE_RESPONSE=$(curl -s -X POST "$API_URL/qa/$CONTRACT_ID" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER_ID" \
  -d '{"question": "What are the key deadlines and completion dates?"}')

echo "📝 Question: What are the key deadlines and completion dates?"
echo ""
echo "📊 Response Preview:"
echo "$TIMELINE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('answer', '')[:300] + '...')" 2>/dev/null
echo ""

if echo "$TIMELINE_RESPONSE" | grep -qi "date\|deadline\|completion"; then
    echo "✅ Found timeline information"
else
    echo "❌ Missing timeline information"
fi

echo ""
echo "=========================================="
echo "TEST 4: Compliance Question"
echo "=========================================="
echo ""

COMPLIANCE_RESPONSE=$(curl -s -X POST "$API_URL/qa/$CONTRACT_ID" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER_ID" \
  -d '{"question": "What certifications and licenses are required?"}')

echo "📝 Question: What certifications and licenses are required?"
echo ""
echo "📊 Response Preview:"
echo "$COMPLIANCE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('answer', '')[:300] + '...')" 2>/dev/null
echo ""

if echo "$COMPLIANCE_RESPONSE" | grep -qi "certification\|license\|requirement"; then
    echo "✅ Found compliance information"
else
    echo "❌ Missing compliance information"
fi

echo ""
echo "=========================================="
echo "FINAL SUMMARY"
echo "=========================================="
echo ""

# Count successes
SUCCESS_COUNT=0

if echo "$RESPONSE" | grep -qi "no interest"; then ((SUCCESS_COUNT++)); fi
if echo "$RESPONSE" | grep -qi "withhold"; then ((SUCCESS_COUNT++)); fi
if echo "$RESPONSE" | grep -qi "page"; then ((SUCCESS_COUNT++)); fi
if echo "$RESPONSE" | grep -qi "unfair"; then ((SUCCESS_COUNT++)); fi

echo "📊 Test Results:"
echo "   Financial Question Tests: $SUCCESS_COUNT/4 passed"

if [ $SUCCESS_COUNT -ge 3 ]; then
    echo ""
    echo "✅ EXCELLENT - Hybrid RAG is working as expected!"
    echo "✅ System is finding critical clauses"
    echo "✅ Ready for production use"
    exit 0
elif [ $SUCCESS_COUNT -ge 2 ]; then
    echo ""
    echo "🟡 GOOD - System is working but could be improved"
    echo "💡 Consider checking backend logs for more details"
    exit 0
else
    echo ""
    echo "⚠️  NEEDS ATTENTION - Not finding enough critical information"
    echo "💡 Check if backend is running and contract is indexed"
    exit 1
fi

