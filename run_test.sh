#!/bin/bash
# Script to run hybrid RAG tests with proper virtual environment

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "🧪 Running Hybrid RAG Test Suite..."
echo ""

python test_hybrid_rag.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ Tests completed successfully!"
else
    echo ""
    echo "❌ Tests failed with exit code: $exit_code"
fi

exit $exit_code
