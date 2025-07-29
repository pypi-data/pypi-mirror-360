# update-docs-system

Комплексная система автоматизации документации для проектов с Markdown файлами. Поддерживает автоматическое создание оглавлений, определение авторства, русскую навигацию и интеграцию с различными системами CI/CD.

## 🚀 Возможности

- **Автоматическое создание оглавления** - сканирует Markdown файлы и создает структурированное оглавление
- **Система Content.json** - генерирует метаданные документации с определением авторства
- **Определение авторства** - классифицирует файлы как созданные человеком, ИИ или автогенератором
- **Русская навигация** - добавляет ссылки "Домой" и "Назад" для удобной навигации
- **Автогенераторы** - поддержка создания и защиты автогенерированных файлов
- **Множественные методы развертывания** - PyPI, Git Submodule, Docker, GitHub Actions
- **Автоматизация** - GitHub Actions, pre-commit hooks, file watcher

## 📦 Установка и развертывание

### Метод 1: PyPI пакет (Рекомендуется)

```bash
# Установка пакета
pip install update-docs-system

# Быстрая настройка в целевом репозитории
curl -sSL https://raw.githubusercontent.com/CoreTwin/docs_repo/main/scripts/setup_automation.sh | bash

# Или ручная настройка
update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
```

### Метод 2: Git Submodule

```bash
# В целевом репозитории
git submodule add https://github.com/CoreTwin/docs_repo.git tools/update-docs
git submodule update --init --recursive

# Использование
cd tools/update-docs
python -m update_docs.cli --docs ../../docs --content-json ../../content/Content.json --description-md ../../content/Description_for_agents.md
```

### Метод 3: Docker контейнер

```bash
# Сборка образа
docker build -t update-docs:latest https://github.com/CoreTwin/docs_repo.git

# Использование в целевом репозитории
docker run --rm -v $(pwd):/workspace update-docs:latest \
  --docs docs \
  --content-json content/Content.json \
  --description-md content/Description_for_agents.md
```

### Метод 4: GitHub Actions

Создайте `.github/workflows/update-docs.yml` в целевом репозитории:

```yaml
name: 📚 Auto Update Documentation

on:
  push:
    branches: [main, master, develop]
    paths: ['**/*.md', 'docs/**/*']
  pull_request:
    branches: [main, master, develop]
    paths: ['**/*.md', 'docs/**/*']

jobs:
  update-docs:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.GITHUB_TOKEN }}
    
    - name: 🐍 Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        cache: 'pip'
    
    - name: 📦 Install update-docs-system
      run: pip install update-docs-system
    
    - name: 🔍 Check for .md changes
      id: check_changes
      run: |
        if [ "${{ github.event_name }}" = "pull_request" ]; then
          CHANGED_FILES=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
        else
          CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")
        fi
        
        if echo "$CHANGED_FILES" | grep -E '\\.md$'; then
          echo "md_changed=true" >> $GITHUB_OUTPUT
          echo "📝 Markdown files changed, updating documentation..."
        else
          echo "md_changed=false" >> $GITHUB_OUTPUT
          echo "ℹ️  No markdown files changed"
        fi
    
    - name: 📚 Update documentation
      if: steps.check_changes.outputs.md_changed == 'true'
      run: |
        update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
        echo "✅ Documentation updated successfully"
    
    - name: 💾 Commit updated documentation
      if: steps.check_changes.outputs.md_changed == 'true'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action Bot"
        
        mkdir -p content
        git add content/Content.json content/Description_for_agents.md docs/ || true
        
        if git diff --staged --quiet; then
          echo "ℹ️  No changes to commit"
        else
          git commit -m "📚 Auto-update documentation"
          
          if [ "${{ github.event_name }}" != "pull_request" ]; then
            git push
            echo "✅ Documentation committed and pushed"
          fi
        fi
```

## 🔧 Использование

### Современная система (Content.json)

```bash
# Обновление документации с генерацией Content.json
update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md

# Автоматическое определение системы по расширениям файлов
update-docs --docs docs --toc Content.json --toc-md Description_for_agents.md
```

### Классическая система (toc.json)

```bash
# Создание JSON оглавления
update-docs --docs docs --toc toc.json

# Создание Markdown оглавления
update-docs --docs docs --toc toc.json --toc-md toc.md

# Генерация из существующего toc.json
update-docs --from-json --toc toc.json --toc-md toc.md
```

### Справка по командам

```bash
# Получить полную справку
update-docs --help

# Примеры использования
update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
update-docs --toc toc.json --toc-md toc.md
```

## 🤖 Автоматизация

### Автоматическая настройка

Используйте скрипт автоматической настройки для быстрого развертывания:

```bash
# Скачать и запустить скрипт настройки
curl -sSL https://raw.githubusercontent.com/CoreTwin/docs_repo/main/scripts/setup_automation.sh | bash

# Или локально (если репозиторий уже клонирован)
bash scripts/setup_automation.sh
```

**Скрипт автоматически:**
- Устанавливает update-docs-system
- Создает структуру папок (docs/, content/, .github/workflows/, scripts/)
- Настраивает GitHub Actions workflow
- Устанавливает pre-commit hook
- Создает file watcher для разработки
- Генерирует примеры документации
- Запускает первое обновление

### Pre-commit Hook

Создайте `.git/hooks/pre-commit`:

```bash
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
        python3 -c "
try:
    from update_docs.core import update_content_system
    update_content_system('docs', 'content/Content.json', 'content/Description_for_agents.md')
    print('✅ Documentation updated via Python import')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"
        update_result=$?
    fi
    
    if [ $update_result -eq 0 ]; then
        git add content/Content.json content/Description_for_agents.md docs/ 2>/dev/null || true
        echo "✅ Documentation updated and staged"
    else
        echo "❌ Failed to update documentation"
        exit 1
    fi
else
    echo "ℹ️  No markdown files changed, skipping documentation update"
fi
```

### File Watcher для разработки

```bash
# Установка зависимостей
pip install watchdog

# Запуск file watcher
python scripts/watch_docs.py
```

### Makefile для удобства

```makefile
.PHONY: docs-update docs-watch docs-install docs-setup help

help:
	@echo "📚 Documentation Commands:"
	@echo "  docs-install  - Install update-docs-system"
	@echo "  docs-setup    - Setup automation (GitHub Actions, hooks, watcher)"
	@echo "  docs-update   - Update documentation once"
	@echo "  docs-watch    - Start file watcher for live updates"

docs-install:
	@echo "📦 Installing update-docs-system..."
	@pip install update-docs-system

docs-setup:
	@echo "🚀 Setting up update-docs automation..."
	@bash scripts/setup_automation.sh

docs-update:
	@echo "📚 Updating documentation..."
	@update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
	@echo "✅ Documentation updated"

docs-watch:
	@echo "👀 Starting documentation watcher..."
	@python scripts/watch_docs.py
```

## 📁 Структура целевого репозитория

После настройки ваш репозиторий будет иметь следующую структуру:

```
target-repo/
├── docs/                           # Документация проекта
│   ├── README.md
│   ├── api/
│   └── guides/
├── content/                        # Метаданные документации
│   ├── Content.json               # Генерируется update-docs
│   └── Description_for_agents.md  # Генерируется update-docs
├── .github/
│   └── workflows/
│       └── update-docs.yml        # CI/CD для документации
├── scripts/
│   └── watch_docs.py              # File watcher для разработки
├── .git/hooks/
│   └── pre-commit                 # Pre-commit hook
├── Makefile                       # Команды для удобства
└── .gitignore                     # Исключения для временных файлов
```

## 🔍 Определение авторства

Система автоматически определяет тип автора для каждого файла:

- **human** - файлы, созданные человеком
- **ai** - файлы, созданные ИИ (по git истории или маркерам)
- **generator** - автогенерированные файлы (защищены от редактирования)
- **mixed** - файлы со смешанным авторством

### Маркеры автогенерации

```markdown
<!-- AUTO-GENERATED -->
<!-- AI-GENERATED -->
<!-- GENERATOR: script_name.py -->
```

## 📊 Content.json структура

```json
[
  {
    "path": "docs/README.md",
    "title": "Project Documentation",
    "author": "human",
    "editable": true,
    "file_id": "readme-a1b2c3d4",
    "headers": [
      {
        "level": 1,
        "title": "Project Documentation",
        "id": "project-documentation",
        "parent_id": null,
        "excerpt": "Welcome to the project..."
      }
    ]
  }
]
```

## 🏠 Навигационные ссылки

Система автоматически добавляет русские навигационные ссылки:

- **🏠 Домой** - ссылка на главную страницу
- **⬆️ Назад** - ссылка на родительский документ

## 🧪 Тестирование интеграции

Проверьте работу системы в вашем репозитории:

```bash
# Тест установки пакета
pip install update-docs-system

# Тест базовой функциональности
update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md

# Проверка созданных файлов
ls -la content/
cat content/Content.json | head -20

# Тест внешнего развертывания
python test_external_deployment.py
```

## 🚀 Быстрый старт

1. **Установите пакет:**
   ```bash
   pip install update-docs-system
   ```

2. **Запустите автоматическую настройку:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/CoreTwin/docs_repo/main/scripts/setup_automation.sh | bash
   ```

3. **Или настройте вручную:**
   ```bash
   # Создайте структуру папок
   mkdir -p docs content .github/workflows scripts
   
   # Запустите первое обновление
   update-docs --docs docs --content-json content/Content.json --description-md content/Description_for_agents.md
   
   # Зафиксируйте изменения
   git add .
   git commit -m "Setup update-docs automation"
   git push
   ```

## 🔧 Настройка для разных сценариев

### Для команды разработчиков
- **PyPI пакет** + **GitHub Actions** для автоматизации
- **Pre-commit hooks** для локальной проверки

### Для личных проектов
- **Git Submodule** + **локальные скрипты**
- **File watcher** для активной разработки документации

### Для CI/CD интеграции
- **Docker контейнер** для изоляции
- **GitHub Actions** с кешированием зависимостей

## 📋 Checklist для внедрения

- [ ] Выбрать способ развертывания (PyPI/Git Submodule/Docker/GitHub Actions)
- [ ] Установить update-docs-system в целевом репозитории
- [ ] Создать структуру папок (docs/, content/, scripts/)
- [ ] Настроить автоматизацию (GitHub Actions/pre-commit/file watcher)
- [ ] Запустить первое обновление документации
- [ ] Протестировать работу системы
- [ ] Обновить .gitignore для исключения временных файлов
- [ ] Документировать процесс для команды

## 🤖 Автогенераторы

Создание автогенератора:

```python
from update_docs.core import register_auto_generator

@register_auto_generator("example_generator.py")
def create_example_docs():
    return "<!-- AUTO-GENERATED -->\n# Generated Documentation"
```

## 🔧 Разработка и тестирование

### Локальная разработка

```bash
# Клонирование репозитория
git clone https://github.com/CoreTwin/docs_repo.git
cd docs_repo

# Установка в режиме разработки
pip install -e .

# Запуск тестов
python -m pytest tests/ -v

# Тестирование внешнего развертывания
python test_external_deployment.py
```

### Структура проекта

```
update_docs/
├── __init__.py          # Основной модуль
├── cli.py              # Интерфейс командной строки
├── core.py             # Основная логика
└── templates/          # Шаблоны автоматизации
    ├── github_workflow.yml
    ├── pre_commit_hook.sh
    ├── watch_docs.py
    ├── setup_automation.sh
    └── Makefile

content/                # Метаданные документации
├── Content.json        # Структурированные данные о файлах
└── Description_for_agents.md  # Описание для ИИ-систем

scripts/                # Вспомогательные скрипты
├── build_and_publish.sh    # Сборка и публикация пакета
└── setup_automation.sh     # Настройка автоматизации

tests/                  # Тесты
├── test_cli.py         # Тесты CLI
└── test_core.py        # Тесты основной логики
```

## 📋 Итоги реализации

### ✅ Завершенные функции

1. **Система Content.json** - полная замена toc.json с расширенными метаданными
2. **Определение авторства** - многоуровневая система классификации файлов
3. **Автогенераторы** - поддержка создания и защиты автогенерированных файлов
4. **Русская навигация** - ссылки "Домой" и "Назад" во всех документах
5. **Множественные методы развертывания** - PyPI, Git Submodule, Docker, GitHub Actions
6. **Автоматизация** - GitHub Actions, pre-commit hooks, file watcher
7. **Persistent file IDs** - отслеживание файлов при переименовании
8. **Иерархические заголовки** - parent_id и excerpt для каждого заголовка
9. **Внешнее развертывание** - полная изоляция от целевых репозиториев
10. **Комплексное тестирование** - интеграционные тесты для внешнего развертывания

### 🔧 Технические особенности

- Обратная совместимость с toc.json системой
- Автоматическое определение типа системы по расширениям файлов
- Защита автогенерированных файлов от случайного редактирования
- Поддержка аннотаций и дополнительной информации к заголовкам
- Интеграция с git для определения авторства по истории коммитов
- PyPI-совместимая структура пакета с шаблонами автоматизации
- Полная изоляция кода от целевых репозиториев

---

📚 **Ссылки на документацию:**
- [Content.json](content/Content.json) - Структурированные метаданные
- [Description for Agents](content/Description_for_agents.md) - Описание для ИИ-систем
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Подробное руководство по развертыванию

