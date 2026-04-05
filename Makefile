.PHONY: install dev test lint run-cli run-web clean help

help: ## Show this help message
	@echo "Available targets:"
	@echo "  install   - Install production dependencies"
	@echo "  dev       - Install development dependencies"
	@echo "  test      - Run test suite"
	@echo "  coverage  - Run tests with coverage"
	@echo "  run-cli   - Run CLI interface"
	@echo "  run-web   - Run Streamlit web interface"
	@echo "  clean     - Remove build artifacts"

install: ## Install production dependencies
	pip install -r requirements.txt

dev: ## Install development dependencies
	pip install -e ".[dev]"

test: ## Run test suite
	pytest tests/ -v

coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=src/diary_organizer --cov-report=term-missing

run-cli: ## Run the CLI application
	python -m diary_organizer.cli

run-web: ## Run the Streamlit web interface
	streamlit run src/diary_organizer/web_ui.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
