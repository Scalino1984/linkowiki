.PHONY: help validate test install clean check

help:
	@echo "LinkoWiki - Makefile Commands"
	@echo "=============================="
	@echo "make install    - Install dependencies"
	@echo "make validate   - Validate providers.json against schema"
	@echo "make test       - Run PydanticAI v2 conformance tests"
	@echo "make check      - Validate + Test (CI pipeline)"
	@echo "make clean      - Remove cache and temp files"

install:
	pip install -r requirements.txt

validate:
	@echo "Validating providers.json..."
	@python tools/validate_providers.py

test:
	@echo "Running conformance tests..."
	@python tests/test_pydantic_ai_conformance.py

check: validate test
	@echo "✓ All checks passed"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f .linkowiki-session.json
