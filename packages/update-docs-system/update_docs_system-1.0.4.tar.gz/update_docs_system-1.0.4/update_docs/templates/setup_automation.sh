#!/bin/bash

set -e

echo "🚀 Setting up update-docs automation..."
echo "📁 Current directory: $(pwd)"
echo ""

print_status() {
    echo "✅ $1"
}

print_warning() {
    echo "⚠️  $1"
}

print_error() {
    echo "❌ $1"
}

if [ ! -d ".git" ]; then
    print_error "This is not a git repository!"
    echo "💡 Please run this script from the root of your git repository"
    exit 1
fi

print_status "Git repository detected"

echo "📦 Installing update-docs-system..."
if pip install update-docs-system; then
    print_status "update-docs-system installed"
else
    print_error "Failed to install update-docs-system"
    echo "💡 Please check your Python/pip installation"
    exit 1
fi

echo "📁 Creating directories..."
mkdir -p .github/workflows
mkdir -p scripts
mkdir -p content
mkdir -p docs

print_status "Directories created"

if [ ! "$(ls -A docs)" ]; then
    echo "📝 Creating sample documentation..."
    cat > docs/README.md << 'EOF'

Welcome to the project documentation!


This documentation is automatically managed by update-docs-system.


- [Setup Guide](setup.md)
- [API Reference](api/README.md)

---
[🏠 Домой](../README.md)
EOF

    mkdir -p docs/api
    cat > docs/api/README.md << 'EOF'

This section contains API documentation.


- GET /api/health
- POST /api/data

---
[🏠 Домой](../../README.md) | [⬆️ Назад](../README.md)
EOF

    cat > docs/setup.md << 'EOF'

Instructions for setting up the project.


- Python 3.7+
- Git


1. Clone the repository
2. Install dependencies
3. Run the application

---
[🏠 Домой](../README.md) | [⬆️ Назад](README.md)
EOF

    print_status "Sample documentation created"
fi

echo "⚙️  Setting up GitHub Actions..."
python3 -c "
import pkg_resources
import shutil

try:
    template_path = pkg_resources.resource_filename('update_docs', 'templates/github_workflow.yml')
    shutil.copy(template_path, '.github/workflows/update-docs.yml')
    print('✅ GitHub Actions workflow copied')
except Exception as e:
    print(f'❌ Error copying workflow: {e}')
    exit(1)
"

echo "🪝 Setting up pre-commit hook..."
python3 -c "
import pkg_resources
import shutil
import os

try:
    template_path = pkg_resources.resource_filename('update_docs', 'templates/pre_commit_hook.sh')
    shutil.copy(template_path, '.git/hooks/pre-commit')
    os.chmod('.git/hooks/pre-commit', 0o755)
    print('✅ Pre-commit hook installed')
except Exception as e:
    print(f'❌ Error installing hook: {e}')
    exit(1)
"

echo "👀 Setting up file watcher..."
python3 -c "
import pkg_resources
import shutil

try:
    template_path = pkg_resources.resource_filename('update_docs', 'templates/watch_docs.py')
    shutil.copy(template_path, 'scripts/watch_docs.py')
    print('✅ File watcher created')
except Exception as e:
    print(f'❌ Error copying watcher: {e}')
    exit(1)
"

chmod +x scripts/watch_docs.py

echo "🔄 Running initial documentation update..."
if update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md; then
    print_status "Initial documentation generated"
else
    print_warning "Initial update failed, but setup is complete"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "  1. Commit the generated files: git add . && git commit -m 'Setup update-docs automation'"
echo "  2. Push to enable GitHub Actions: git push"
echo "  3. For development, run: python scripts/watch_docs.py"
echo ""
echo "📚 Documentation will now auto-update when you modify .md files!"
