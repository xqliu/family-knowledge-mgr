#!/bin/bash

# Complete AI Infrastructure Testing with Real APIs
# Requires: PostgreSQL + pgvector, real API keys
# Use for production readiness testing

set -e  # Exit on any error

echo "🚀 Production AI Infrastructure Testing"
echo "======================================"

# Check for required API keys
if [[ -z "$OPENAI_API_KEY" || "$OPENAI_API_KEY" == "test-key-placeholder" ]]; then
    echo "❌ OPENAI_API_KEY not set. Required for embedding generation."
    echo "   Set with: export OPENAI_API_KEY=your_key_here"
    exit 1
fi

if [[ -z "$ANTHROPIC_API_KEY" || "$ANTHROPIC_API_KEY" == "test-key-placeholder" ]]; then
    echo "❌ ANTHROPIC_API_KEY not set. Required for chat responses."
    echo "   Set with: export ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi

# Activate virtual environment
source family_venv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings

echo "🔑 API keys configured - running production tests"

echo "📋 Running Unit Tests..."
echo "------------------------"

# Run unit tests with coverage
python -m pytest ai_integration/tests/ -v --cov=ai_integration --cov-report=term-missing

echo ""
echo "🧪 Running Integration Tests..."
echo "--------------------------------"

# Run comprehensive integration test
python manage.py test_ai_system --skip-embeddings

echo ""
echo "⚡ Running Performance Tests..."
echo "-------------------------------"

# Test with actual embedding generation (if API keys available)
if [[ -n "$OPENAI_API_KEY" && "$OPENAI_API_KEY" != "test-key-placeholder" ]]; then
    echo "🔑 API keys detected - running full embedding tests"
    python manage.py test_ai_system --cleanup
else
    echo "⚠️  No API keys - skipping embedding generation tests"
    python manage.py test_ai_system --skip-embeddings --cleanup
fi

echo ""
echo "🌐 Testing API Endpoints..."
echo "---------------------------"

# Start Django server in background for API testing
python manage.py runserver 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test API endpoints
echo "Testing chat endpoint..."
curl -s -X POST http://localhost:8000/api/ai/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about family traditions"}' | jq '.'

echo ""
echo "Testing search endpoint..."
curl -s -X POST http://localhost:8000/api/ai/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "cooking recipes"}' | jq '.'

# Stop the server
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "📊 Running Django Tests..."
echo "--------------------------"

# Run Django's built-in tests for AI integration
python manage.py test ai_integration --verbosity=2

echo ""
echo "✅ All tests completed!"
echo "======================="

echo "📁 Test artifacts generated:"
echo "   - htmlcov/index.html (test coverage report)"
echo "   - AI integration test results above"
echo ""

if [[ -f "htmlcov/index.html" ]]; then
    echo "🔗 Open htmlcov/index.html to view detailed coverage report"
fi

echo "🎉 AI infrastructure testing complete!"