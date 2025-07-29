#!/bin/bash

echo "🔍 Checking for markdown file changes..."

md_files_changed=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.md$' || true)

if [ -n "$md_files_changed" ]; then
    echo "📝 Markdown files changed:"
    echo "$md_files_changed" | sed 's/^/  - /'
    echo ""
    echo "🔄 Updating documentation..."
    
    mkdir -p content
    
    if command -v update-docs &> /dev/null; then
        update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
        update_result=$?
    else
        echo "⚠️  update-docs command not found, trying Python import..."
        python3 -c "
try:
    from update_docs.core import update_content_system
    update_content_system('docs', 'content/Content.json', 'content/Description_for_agents.md')
    print('✅ Documentation updated via Python import')
except ImportError as e:
    print(f'❌ Failed to import update_docs: {e}')
    print('💡 Please install: pip install update-docs-system')
    exit(1)
except Exception as e:
    print(f'❌ Error updating documentation: {e}')
    exit(1)
"
        update_result=$?
    fi
    
    if [ $update_result -eq 0 ]; then
        git add content/Content.json content/Description_for_agents.md docs/ 2>/dev/null || true
        echo "✅ Documentation updated and staged"
    else
        echo "❌ Failed to update documentation"
        echo "💡 Please check that update-docs-system is installed:"
        echo "   pip install update-docs-system"
        exit 1
    fi
else
    echo "ℹ️  No markdown files changed, skipping documentation update"
fi

echo "🚀 Pre-commit check completed"
