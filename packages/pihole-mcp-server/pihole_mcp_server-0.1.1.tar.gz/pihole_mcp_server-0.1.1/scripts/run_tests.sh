#!/bin/bash

# Run tests with coverage for pihole-mcp-server
# Usage: ./scripts/run_tests.sh [options]

set -e

echo "🧪 Running pihole-mcp-server tests with coverage..."

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider activating one first."
fi

# Install dev dependencies if not already installed
echo "📦 Installing development dependencies..."
pip install -e ".[dev]" --quiet

# Create reports directory if it doesn't exist
mkdir -p htmlcov
mkdir -p reports

# Run tests with coverage
echo "🏃 Running tests..."
python -m pytest \
    --cov=pihole_mcp_server \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml:reports/coverage.xml \
    --cov-fail-under=80 \
    --strict-markers \
    -v \
    "$@"

echo "✅ Tests completed successfully!"
echo "📊 Coverage report available at: htmlcov/index.html"
echo "📋 XML coverage report available at: reports/coverage.xml"

# Open coverage report if running on macOS and no CI
if [[ "$OSTYPE" == "darwin"* ]] && [[ -z "$CI" ]]; then
    echo "🌐 Opening coverage report in browser..."
    open htmlcov/index.html
fi 