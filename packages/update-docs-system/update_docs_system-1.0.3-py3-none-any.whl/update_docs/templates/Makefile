.PHONY: docs-update docs-watch docs-install help

help:
	@echo "📚 Documentation Commands:"
	@echo "  docs-install  - Install update-docs-system"
	@echo "  docs-update   - Update documentation once"
	@echo "  docs-watch    - Start file watcher for live updates"

docs-install:
	@echo "📦 Installing update-docs-system..."
	@pip install update-docs-system

docs-update:
	@echo "📚 Updating documentation..."
	@update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
	@echo "✅ Documentation updated"

docs-watch:
	@echo "👀 Starting documentation watcher..."
	@python scripts/watch_docs.py

docs-setup:
	@echo "🚀 Setting up update-docs automation..."
	@bash scripts/setup_automation.sh
