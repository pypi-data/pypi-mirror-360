# update_docs/core.py

import os
import re
import json
import hashlib
import subprocess
from pathlib import Path
import difflib
from collections import defaultdict
from datetime import datetime

HEADER_RE = re.compile(
    r"^(#{1,6})\s+(.*?)\s*(?:<!--\s*id:([\w\-]+)\s*-->)?\s*$",
    re.MULTILINE,
)
INCLUDE_RE = re.compile(r"<!--\s*include:([^\s#]+)#([\w\-]+)\s*-->")

def slugify(text):
    return re.sub(r"[^\w\-]", "-", text.lower())


def generate_path_based_id(relative_path):
    """Создает уникальный идентификатор на основе пути к файлу"""
    path_id = relative_path.replace("/", "-").replace("\\", "-")
    path_id = re.sub(r"[^\w\-.]", "-", path_id.lower())
    path_id = re.sub(r"-+", "-", path_id)  # Убираем множественные дефисы
    return path_id.strip("-")


def extract_content_preview(file_path, max_chars=200):
    """Извлекает превью содержимого файла для анализа дубликатов"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r"^#.*$", "", content, flags=re.MULTILINE)
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        return content[:max_chars].strip()
    except Exception:
        return ""

def extract_headers(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    headers = []
    lines = content.splitlines()
    parent_stack = []
    
    for match in HEADER_RE.finditer(content):
        level = len(match.group(1))
        title = match.group(2).strip()
        id_tag = match.group(3) or slugify(title)
        
        start_line = content[:match.start()].count('\n')
        excerpt = ""
        for j in range(start_line + 1, min(start_line + 5, len(lines))):
            if j < len(lines) and not lines[j].strip().startswith('#'):
                excerpt += lines[j].strip() + " "
                if len(excerpt) > 100:
                    break
        excerpt = excerpt[:100].strip()
        if len(excerpt) == 100:
            excerpt += "..."
        
        while parent_stack and parent_stack[-1]['level'] >= level:
            parent_stack.pop()
        
        parent_id = parent_stack[-1]['id'] if parent_stack else None
        
        header_obj = {
            "id": id_tag,
            "level": level,
            "title": title,
            "excerpt": excerpt,
            "parent_id": parent_id
        }
        
        headers.append(header_obj)
        parent_stack.append(header_obj)
    
    return headers

def build_toc(docs_dir):
    toc = []
    header_map = {}
    for root, dirs, files in os.walk(docs_dir):
        dirs.sort()
        for file in sorted(files):
            if file.endswith(".md"):
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                headers = extract_headers(os.path.join(docs_dir, rel_path))
                if headers:
                    toc.append({
                        "file": rel_path.replace("\\", "/"),
                        "headers": headers
                    })
                    for h in headers:
                        header_map[(rel_path.replace("\\", "/"), h["id"])] = {
                            "title": h["title"],
                            "level": h["level"],
                            "file": rel_path.replace("\\", "/")
                        }
    return toc, header_map


def build_comprehensive_toc(root_dir, exclude_patterns=None):
    """Сканирует все уровни вложенности начиная с корневой папки проекта"""
    if exclude_patterns is None:
        exclude_patterns = ['.git', 'node_modules', '__pycache__', '.venv', 'build', 'dist']
    
    toc = []
    header_map = {}
    all_documents = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
        
        for file in sorted(files):
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                unique_id = generate_path_based_id(rel_path)
                
                headers = extract_headers(file_path)
                file_stats = os.stat(file_path)
                
                doc_entry = {
                    "path": file_path,
                    "relative_path": rel_path.replace("\\", "/"),
                    "unique_id": unique_id,
                    "headers": headers,
                    "size": file_stats.st_size,
                    "modified": file_stats.st_mtime,
                    "content_preview": extract_content_preview(file_path)
                }
                
                toc.append(doc_entry)
                all_documents.append(doc_entry)
                
                # Обновление header_map
                for h in headers:
                    header_map[(rel_path.replace("\\", "/"), h["id"])] = {
                        "title": h["title"],
                        "level": h["level"],
                        "file": rel_path.replace("\\", "/")
                    }
    
    return toc, header_map, all_documents

def extract_section(file_path, section_id, level):
    with open(file_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    section = []
    found = False
    current_level = None
    for i, line in enumerate(lines):
        match = HEADER_RE.match(line)
        if match:
            l = len(match.group(1))
            t = match.group(2).strip()
            id_tag = match.group(3) or slugify(t)
            if id_tag == section_id:
                found = True
                current_level = l
                continue
            if found and l <= current_level:
                break
        if found:
            section.append(line)
    return "\n".join(section).strip()

def update_includes(docs_dir, header_map):
    errors = []
    for root, dirs, files in os.walk(docs_dir):
        dirs.sort()
        for file in sorted(files):
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, docs_dir)
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                updated = content
                changed = False

                for match in INCLUDE_RE.finditer(content):
                    include_file, include_id = match.groups()
                    key = (include_file, include_id)
                    if key not in header_map:
                        errors.append(f"⚠️ include not found: {include_file}#{include_id} in {rel_path}")
                        continue

                    original_path = os.path.join(docs_dir, include_file)
                    level = header_map[key]["level"]
                    text = extract_section(original_path, include_id, level)

                    block = f"<!-- BEGIN include:{include_file}#{include_id} -->\n{text}\n<!-- END include -->"
                    block_re = re.compile(
                        rf"<!--\s*BEGIN\s+include:{re.escape(include_file)}#{re.escape(include_id)}\s*-->.*?<!--\s*END\s+include\s*-->",
                        re.DOTALL,
                    )
                    if block_re.search(updated):
                        updated = block_re.sub(block, updated)
                        changed = True
                    else:
                        insert_point = match.end()
                        updated = updated[:insert_point] + "\n" + block + updated[insert_point:]
                        changed = True

                if changed:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(updated)
    return errors


def write_markdown_toc(toc, toc_md_path):
    with open(toc_md_path, "w", encoding="utf-8") as f:
        f.write("# Table of Contents\n\n")
        for entry in toc:
            file_path = entry["file"]
            full_path = f"docs/{file_path}"
            anchor = slugify(file_path.replace("/", "-"))
            f.write(f'- <a id="{anchor}"></a>[{file_path}]({full_path})\n')




def get_file_title(entry):
    """Извлекает заголовок файла из первого заголовка или имени файла"""
    if entry["headers"]:
        return entry["headers"][0]["title"]
    return os.path.basename(entry["relative_path"])




def find_exact_header_matches(files):
    """Находит точные совпадения заголовков между файлами"""
    header_matches = defaultdict(list)
    
    for entry in files:
        for header in entry.get("headers", []):
            title = header["title"].strip()
            rel_path = entry.get("relative_path", entry.get("file", ""))
            header_matches[title].append({
                "file": rel_path,
                "header_id": header["id"],
                "level": header["level"],
                "link": f"docs/{rel_path}#{header['id']}"
            })
    
    duplicates = {title: locations for title, locations in header_matches.items() 
                 if len(locations) > 1}
    
    return duplicates

def find_project_root():
    """Находит корень проекта (папку с .git)"""
    path = Path.cwd()
    while not (path / ".git").exists():
        if path.parent == path:
            break
        path = path.parent
    return path

def get_git_file_authors(file_path, repo_root=None):
    """Извлекает информацию об авторах файла из git истории"""
    if repo_root is None:
        repo_root = find_project_root()
    
    try:
        result = subprocess.run([
            'git', 'log', '-1', '--pretty=format:%an|%ae|%at', '--', file_path
        ], cwd=repo_root, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return None
        
        if not result.stdout.strip():
            return None
            
        author_name, author_email, timestamp = result.stdout.strip().split('|')
        
        all_authors_result = subprocess.run([
            'git', 'log', '--pretty=format:%an|%ae', '--', file_path
        ], cwd=repo_root, capture_output=True, text=True, timeout=15)
        
        all_authors = []
        if all_authors_result.returncode == 0:
            for line in all_authors_result.stdout.strip().split('\n'):
                if line.strip():
                    name, email = line.split('|')
                    if (name, email) not in all_authors:
                        all_authors.append((name, email))
        
        return {
            'last_author_name': author_name,
            'last_author_email': author_email,
            'last_modified_timestamp': int(timestamp),
            'all_authors': all_authors
        }
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
        return None

def classify_author_from_git(git_info):
    """Классифицирует автора на основе git информации"""
    if not git_info:
        return "human"
    
    email = git_info['last_author_email'].lower()
    name = git_info['last_author_name'].lower()
    
    ai_patterns = [
        r'.*ai.*@.*',
        r'.*bot.*@.*', 
        r'.*gpt.*@.*',
        r'.*claude.*@.*',
        r'.*assistant.*@.*',
        r'.*devin.*@.*',
        r'.*copilot.*@.*',
        r'noreply@.*',
        r'.*automated.*@.*'
    ]
    
    generator_patterns = [
        r'.*generator.*@.*',
        r'.*auto.*@.*',
        r'.*system.*@.*',
        r'.*build.*@.*',
        r'.*ci.*@.*',
        r'.*deploy.*@.*'
    ]
    
    for pattern in ai_patterns:
        if re.match(pattern, email):
            return "ai"
    
    for pattern in generator_patterns:
        if re.match(pattern, email):
            return "generator"
    
    ai_name_patterns = ['ai', 'bot', 'gpt', 'claude', 'assistant', 'devin', 'copilot']
    generator_name_patterns = ['generator', 'auto', 'system', 'build', 'ci', 'deploy']
    
    for pattern in ai_name_patterns:
        if pattern in name:
            return "ai"
            
    for pattern in generator_name_patterns:
        if pattern in name:
            return "generator"
    
    return "human"

def detect_author_type_enhanced(file_path, content, git_info=None):
    """Расширенное определение типа автора с приоритетной системой"""
    
    generator_check = check_generator_registry(file_path)
    if generator_check:
        return "generator", "registry_lookup"
    
    auto_patterns = [
        r'<!-- AUTO-GENERATED -->',
        r'# AUTO-GENERATED',
        r'This file was automatically generated',
        r'Generated by update-docs',
        r'Generated by.*\.py',
        r'Автоматически сгенерировано',
        r'Создано автоматически',
        r'Auto-generated by',
        r'Сгенерировано скриптом',
        r'Generated by example_doc_generator\.py'
    ]
    
    for pattern in auto_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return "generator", "comment_marker"
    
    if '/auto_generated/' in file_path.replace('\\', '/'):
        return "generator", "file_location"
    
    filename = os.path.basename(file_path).lower()
    auto_filename_patterns = [
        r'.*_auto\.md$',
        r'.*_generated\.md$', 
        r'changelog_auto\.md$',
        r'api_documentation\.md$',
        r'metrics_report\.md$'
    ]
    
    for pattern in auto_filename_patterns:
        if re.match(pattern, filename):
            return "generator", "filename_pattern"
    
    ai_patterns = [
        r'<!-- AI-GENERATED -->',
        r'Generated by AI',
        r'Created by.*AI',
        r'ChatGPT|Claude|GPT-|Devin',
        r'Создано ИИ|Генерировано ИИ'
    ]
    
    for pattern in ai_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return "ai", "comment_marker"
    
    if git_info:
        git_classification = classify_author_from_git(git_info)
        if git_classification != "human":
            return git_classification, "git_history"
        
        all_authors = git_info.get('all_authors', [])
        if len(all_authors) > 1:
            author_types = set()
            for name, email in all_authors:
                temp_git_info = {'last_author_email': email, 'last_author_name': name}
                author_type = classify_author_from_git(temp_git_info)
                author_types.add(author_type)
            
            if len(author_types) > 1:
                return "mixed", "git_history"
    
    return "human", "default"

def check_generator_registry(file_path):
    """Проверяет файл в реестре автогенераторов"""
    registry_path = "docs/auto_generated/generator_registry.json"
    
    if not os.path.exists(registry_path):
        return False
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        normalized_path = file_path.replace('\\', '/')
        
        for generator in registry.get('generators', []):
            for output_file in generator.get('output_files', []):
                if normalized_path.endswith(output_file) or output_file.endswith(normalized_path):
                    return True
        
        return False
    except (json.JSONDecodeError, FileNotFoundError):
        return False

def scan_for_generator_functions():
    """Сканирует кодовую базу на предмет функций-генераторов документации"""
    generator_functions = []
    
    generator_patterns = [
        r'def.*generate.*doc',
        r'def.*create.*doc',
        r'def.*write.*doc',
        r'def.*build.*doc',
        r'def.*make.*doc'
    ]
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in generator_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line = content[match.start():content.find('\n', match.start())]
                            func_name = re.search(r'def\s+(\w+)', line)
                            if func_name:
                                generator_functions.append({
                                    'file': file_path,
                                    'function': func_name.group(1),
                                    'line': line.strip()
                                })
                
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    return generator_functions

def determine_editability(author_type, author_source):
    """Определяет возможность редактирования файла"""
    if author_type in ["generator"]:
        return False
    elif author_type == "mixed":
        return True
    else:
        return True

def generate_persistent_file_id(file_path, content=None):
    """Генерирует persistent file_id на основе содержимого файла"""
    if content is None:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    content_sample = content[:200].strip()
    content_hash = hashlib.md5(content_sample.encode()).hexdigest()[:8]
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    return f"{slugify(base_name)}-{content_hash}"

def load_existing_file_ids(content_json_path):
    """Загружает существующие file_id из Content.json для сохранения при переименовании"""
    if not os.path.exists(content_json_path):
        return {}
    
    try:
        with open(content_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return {entry.get('path', entry.get('file', '')): entry.get('file_id', '') 
                   for entry in data if entry.get('file_id')}
        else:
            return {}
    except (json.JSONDecodeError, KeyError):
        return {}

def match_file_by_content(file_path, content, existing_entries):
    """Находит существующий file_id по содержимому при переименовании файла"""
    current_hash = hashlib.md5(content[:200].encode()).hexdigest()[:8]
    
    for entry in existing_entries:
        if entry.get('file_id', '').endswith(f"-{current_hash}"):
            return entry['file_id']
    
    return None


def write_toc_from_json(toc_json_path, toc_md_path, annotations=None):
    """Создает Markdown оглавление из существующего toc.json файла с перекрестными ссылками"""
    if annotations is None:
        annotations = {}
    
    with open(toc_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "files" in data:
        files = data["files"]
        metadata = data.get("metadata", {})
    else:
        files = data
        metadata = {"total_files": len(files)}
    
    header_duplicates = find_exact_header_matches(files)
    
    with open(toc_md_path, "w", encoding="utf-8") as f:
        f.write("# Оглавление проекта\n\n")
        
        if metadata.get("generated_at"):
            f.write(f"*Сгенерировано: {metadata['generated_at']}*  \n")
        f.write(f"*Всего файлов: {metadata.get('total_files', len(files))}*\n")
        if header_duplicates:
            f.write(f"*Обнаружено повторяющихся заголовков: {len(header_duplicates)}*\n")
        f.write("\n")
        
        dir_groups = defaultdict(list)
        for entry in files:
            rel_path = entry.get("relative_path", entry.get("file", ""))
            dir_path = os.path.dirname(rel_path)
            if not dir_path:
                dir_path = "корень"
            dir_groups[dir_path].append(entry)
        
        f.write("## 📁 Структура документации\n\n")
        for dir_path in sorted(dir_groups.keys()):
            f.write(f"### {dir_path}\n\n")
            for entry in sorted(dir_groups[dir_path], key=lambda x: x.get("relative_path", x.get("file", ""))):
                rel_path = entry.get("relative_path", entry.get("file", ""))
                file_title = get_file_title_from_entry(entry)
                unique_id = entry.get("unique_id", rel_path.replace("/", "-").replace("\\", "-"))
                
                full_path = f"docs/{rel_path}"
                f.write(f"- [📄 {file_title}]({full_path})")
                
                if unique_id and unique_id != rel_path:
                    f.write(f" `{unique_id}`")
                f.write("\n")
                
                if "size" in entry:
                    size_kb = entry["size"] // 1024
                    f.write(f"  - **Размер**: {size_kb} KB\n")
                
                file_annotation = annotations.get(rel_path)
                if file_annotation:
                    f.write(f"  - **Примечание**: {file_annotation}\n")
                
                headers = entry.get("headers", [])
                if headers:
                    f.write("  - **Заголовки**:\n")
                    for header in headers:
                        indent = "    " + "  " * (header["level"] - 1)
                        header_key = f"{rel_path}#{header['id']}"
                        header_annotation = annotations.get(header_key, "")
                        title = header["title"].strip()
                        
                        if title in header_duplicates and len(header_duplicates[title]) > 1:
                            f.write(f"{indent}- [{header['title']}](docs/{rel_path}#{header['id']}) ⚠️ **Дубликат**")
                            if header_annotation:
                                f.write(f" — *{header_annotation}*")
                            f.write("\n")
                            
                            other_locations = [loc for loc in header_duplicates[title] 
                                             if loc["link"] != f"docs/{rel_path}#{header['id']}"]
                            if other_locations:
                                f.write(f"{indent}  - *Также встречается в:*\n")
                                for loc in other_locations:
                                    f.write(f"{indent}    - [{os.path.basename(loc['file'])}]({loc['link']})\n")
                        else:
                            f.write(f"{indent}- [{header['title']}](docs/{rel_path}#{header['id']})")
                            if header_annotation:
                                f.write(f" — *{header_annotation}*")
                            f.write("\n")
                
                f.write("\n")
        
        if header_duplicates:
            f.write("## 🔍 Повторяющиеся заголовки\n\n")
            f.write("*Заголовки с одинаковыми формулировками в разных документах:*\n\n")
            
            for title, locations in sorted(header_duplicates.items()):
                f.write(f"### \"{title}\"\n")
                f.write(f"*Встречается в {len(locations)} местах:*\n\n")
                
                for loc in locations:
                    f.write(f"- [{os.path.basename(loc['file'])}]({loc['link']}) (уровень {loc['level']})\n")
                f.write("\n")
        
        f.write("## 📊 Статистика\n\n")
        f.write(f"- **Всего файлов**: {metadata.get('total_files', len(files))}\n")
        total_headers = sum(len(entry.get("headers", [])) for entry in files)
        f.write(f"- **Всего заголовков**: {total_headers}\n")
        if header_duplicates:
            f.write(f"- **Повторяющихся заголовков**: {len(header_duplicates)}\n")
        if annotations:
            f.write(f"- **Аннотированных элементов**: {len(annotations)}\n")

def get_file_title_from_entry(entry):
    """Извлекает заголовок файла из записи TOC"""
    headers = entry.get("headers", [])
    if headers:
        return headers[0]["title"]
    
    rel_path = entry.get("relative_path", entry.get("file", ""))
    return os.path.basename(rel_path)

def find_exact_header_matches(files):
    """Находит точные совпадения заголовков между файлами"""
    header_matches = defaultdict(list)
    
    for entry in files:
        for header in entry.get("headers", []):
            title = header["title"].strip()
            rel_path = entry.get("relative_path", entry.get("file", ""))
            header_matches[title].append({
                "file": rel_path,
                "header_id": header["id"],
                "level": header["level"],
                "link": f"docs/{rel_path}#{header['id']}"
            })
    
    duplicates = {title: locations for title, locations in header_matches.items() 
                 if len(locations) > 1}
    
    return duplicates


def write_toc_from_json(toc_json_path, toc_md_path, annotations=None):
    """Создает Markdown оглавление из существующего toc.json файла с перекрестными ссылками"""
    if annotations is None:
        annotations = {}
    
    with open(toc_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "files" in data:
        files = data["files"]
        metadata = data.get("metadata", {})
    else:
        files = data
        metadata = {"total_files": len(files)}
    
    header_duplicates = find_exact_header_matches(files)
    
    with open(toc_md_path, "w", encoding="utf-8") as f:
        f.write("# Оглавление проекта\n\n")
        
        if metadata.get("generated_at"):
            f.write(f"*Сгенерировано: {metadata['generated_at']}*  \n")
        f.write(f"*Всего файлов: {metadata.get('total_files', len(files))}*\n")
        if header_duplicates:
            f.write(f"*Обнаружено повторяющихся заголовков: {len(header_duplicates)}*\n")
        f.write("\n")
        
        dir_groups = defaultdict(list)
        for entry in files:
            rel_path = entry.get("relative_path", entry.get("file", ""))
            dir_path = os.path.dirname(rel_path)
            if not dir_path:
                dir_path = "корень"
            dir_groups[dir_path].append(entry)
        
        f.write("## 📁 Структура документации\n\n")
        for dir_path in sorted(dir_groups.keys()):
            f.write(f"### {dir_path}\n\n")
            for entry in sorted(dir_groups[dir_path], key=lambda x: x.get("relative_path", x.get("file", ""))):
                rel_path = entry.get("relative_path", entry.get("file", ""))
                file_title = get_file_title_from_entry(entry)
                unique_id = entry.get("unique_id", rel_path.replace("/", "-").replace("\\", "-"))
                
                f.write(f"- [📄 {file_title}](docs/{rel_path})")
                
                if unique_id and unique_id != rel_path:
                    f.write(f" `{unique_id}`")
                f.write("\n")
                
                if "size" in entry:
                    size_kb = entry["size"] // 1024
                    f.write(f"  - **Размер**: {size_kb} KB\n")
                
                file_annotation = annotations.get(rel_path)
                if file_annotation:
                    f.write(f"  - **Примечание**: {file_annotation}\n")
                
                headers = entry.get("headers", [])
                if headers:
                    f.write("  - **Заголовки**:\n")
                    for header in headers:
                        indent = "    " + "  " * (header["level"] - 1)
                        header_key = f"{rel_path}#{header['id']}"
                        header_annotation = annotations.get(header_key, "")
                        title = header["title"].strip()
                        
                        if title in header_duplicates and len(header_duplicates[title]) > 1:
                            f.write(f"{indent}- [{header['title']}](docs/{rel_path}#{header['id']}) ⚠️ **Дубликат**")
                            if header_annotation:
                                f.write(f" — *{header_annotation}*")
                            f.write("\n")
                            
                            other_locations = [loc for loc in header_duplicates[title] 
                                             if loc["link"] != f"docs/{rel_path}#{header['id']}"]
                            if other_locations:
                                f.write(f"{indent}  - *Также встречается в:*\n")
                                for loc in other_locations:
                                    f.write(f"{indent}    - [{os.path.basename(loc['file'])}]({loc['link']})\n")
                        else:
                            f.write(f"{indent}- [{header['title']}](docs/{rel_path}#{header['id']})")
                            if header_annotation:
                                f.write(f" — *{header_annotation}*")
                            f.write("\n")
                
                f.write("\n")
        
        if header_duplicates:
            f.write("## 🔍 Повторяющиеся заголовки\n\n")
            f.write("*Заголовки с одинаковыми формулировками в разных документах:*\n\n")
            
            for title, locations in sorted(header_duplicates.items()):
                f.write(f"### \"{title}\"\n")
                f.write(f"*Встречается в {len(locations)} местах:*\n\n")
                
                for loc in locations:
                    f.write(f"- [{os.path.basename(loc['file'])}]({loc['link']}) (уровень {loc['level']})\n")
                f.write("\n")
        
        f.write("## 📊 Статистика\n\n")
        f.write(f"- **Всего файлов**: {metadata.get('total_files', len(files))}\n")
        total_headers = sum(len(entry.get("headers", [])) for entry in files)
        f.write(f"- **Всего заголовков**: {total_headers}\n")
        if header_duplicates:
            f.write(f"- **Повторяющихся заголовков**: {len(header_duplicates)}\n")
        if annotations:
            f.write(f"- **Аннотированных элементов**: {len(annotations)}\n")


def get_file_title_from_entry(entry):
    """Извлекает заголовок файла из записи TOC"""
    headers = entry.get("headers", [])
    if headers:
        return headers[0]["title"]
    
    rel_path = entry.get("relative_path", entry.get("file", ""))
    return os.path.basename(rel_path)


def build_content_json(docs_dir, existing_file_ids=None, existing_entries=None):
    """Создает Content.json согласно спецификации с git интеграцией"""
    if existing_file_ids is None:
        existing_file_ids = {}
    if existing_entries is None:
        existing_entries = []
    
    content_entries = []
    repo_root = find_project_root()
    
    for root, dirs, files in os.walk(docs_dir):
        dirs[:] = [d for d in dirs if d != 'content']
        dirs.sort()
        
        for file in sorted(files):
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, docs_dir).replace("\\", "/")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                git_info = get_git_file_authors(rel_path, repo_root)
                
                if rel_path in existing_file_ids:
                    file_id = existing_file_ids[rel_path]
                else:
                    matched_id = match_file_by_content(file_path, content, existing_entries)
                    if matched_id:
                        file_id = matched_id
                    else:
                        file_id = generate_persistent_file_id(file_path, content)
                
                author_type, author_source = detect_author_type_enhanced(file_path, content, git_info)
                editable = determine_editability(author_type, author_source)
                
                headers = extract_headers(file_path)
                
                title = headers[0]["title"] if headers else os.path.splitext(file)[0]
                
                entry = {
                    "file_id": file_id,
                    "title": title,
                    "path": rel_path,
                    "editable": editable,
                    "author": author_type,
                    "headers": headers
                }
                
                if git_info:
                    entry["git_info"] = {
                        "last_author": f"{git_info['last_author_name']} <{git_info['last_author_email']}>",
                        "last_modified": git_info['last_modified_timestamp'],
                        "all_authors": [f"{name} <{email}>" for name, email in git_info['all_authors']],
                        "author_source": author_source
                    }
                
                content_entries.append(entry)
    
    return content_entries

def write_description_for_agents(content_entries, output_path, docs_dir='docs'):
    """Генерирует Description_for_agents.md на основе Content.json"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 📘 Структура документации проекта\n\n")
        f.write("*Автоматически сгенерировано системой update-docs*\n\n")
        f.write("<!-- AUTO-GENERATED -->\n\n")
        
        author_stats = defaultdict(int)
        for entry in content_entries:
            author_stats[entry["author"]] += 1
        
        f.write("## 📊 Статистика авторства\n\n")
        author_icons = {"human": "👤", "ai": "🤖", "generator": "⚙️", "mixed": "🔄"}
        for author_type, count in sorted(author_stats.items()):
            icon = author_icons.get(author_type, "❓")
            f.write(f"- {icon} **{author_type}**: {count} файлов\n")
        f.write("\n")
        
        dir_groups = defaultdict(list)
        for entry in content_entries:
            dir_path = os.path.dirname(entry["path"])
            if not dir_path:
                dir_path = "корень"
            dir_groups[dir_path].append(entry)
        
        output_dir = os.path.dirname(output_path)
        
        for dir_path in sorted(dir_groups.keys()):
            f.write(f"## 📁 {dir_path}\n\n")
            
            for entry in sorted(dir_groups[dir_path], key=lambda x: x["title"]):
                editable_icon = "✏️" if entry["editable"] else "🔒"
                author_icon = author_icons.get(entry["author"], "❓")
                
                target_file_path = os.path.join(docs_dir, entry["path"])
                relative_path = os.path.relpath(target_file_path, output_dir).replace("\\", "/")
                
                if not os.path.exists(target_file_path):
                    continue
                
                f.write(f"### {editable_icon} {author_icon} [{entry['title']}]({relative_path})\n")
                f.write(f"**File ID:** `{entry['file_id']}`  \n")
                f.write(f"**Автор:** {entry['author']} | **Редактируемый:** {'Да' if entry['editable'] else 'Нет'}\n")
                
                if "git_info" in entry:
                    git_info = entry["git_info"]
                    f.write(f"**Последний автор:** {git_info['last_author']}  \n")
                    if len(git_info['all_authors']) > 1:
                        f.write(f"**Все авторы:** {', '.join(git_info['all_authors'][:3])}")
                        if len(git_info['all_authors']) > 3:
                            f.write(f" и еще {len(git_info['all_authors']) - 3}")
                        f.write("  \n")
                
                f.write("\n")
                
                if entry["headers"]:
                    f.write("**Структура заголовков:**\n")
                    for header in entry["headers"]:
                        indent = "  " * (header["level"] - 1)
                        if os.path.exists(target_file_path):
                            f.write(f"{indent}- [{header['title']}]({relative_path}#{header['id']})")
                            if header["excerpt"]:
                                f.write(f" — *{header['excerpt']}*")
                            f.write("\n")
                
                f.write("\n")

def update_content_system(docs_dir, content_json_path, description_md_path):
    """Главная функция для обновления системы Content.json и Description_for_agents.md"""
    
    content_dir = os.path.dirname(content_json_path)
    os.makedirs(content_dir, exist_ok=True)
    
    existing_file_ids = load_existing_file_ids(content_json_path)
    existing_entries = []
    if os.path.exists(content_json_path):
        try:
            with open(content_json_path, 'r', encoding='utf-8') as f:
                existing_entries = json.load(f)
            if not isinstance(existing_entries, list):
                existing_entries = []
        except (json.JSONDecodeError, FileNotFoundError):
            existing_entries = []
    
    content_entries = build_content_json(docs_dir, existing_file_ids, existing_entries)
    
    with open(content_json_path, 'w', encoding='utf-8') as f:
        json.dump(content_entries, f, indent=2, ensure_ascii=False)
    
    if description_md_path:
        write_description_for_agents(content_entries, description_md_path, docs_dir)
    
    header_map = {}
    for entry in content_entries:
        for header in entry["headers"]:
            key = (entry["path"], header["id"])
            header_map[key] = {
                "title": header["title"],
                "level": header["level"],
                "file": entry["path"]
            }
    
    include_errors = update_includes(docs_dir, header_map)
    
    clean_broken_back_links(docs_dir)
    if description_md_path:
        inject_back_to_toc_links_russian(docs_dir, description_md_path, content_entries)
    
    print(f"✅ Content.json создан: {content_json_path}")
    if description_md_path:
        print(f"✅ Description_for_agents.md создан: {description_md_path}")
        print("✅ Навигационные ссылки обновлены")
    
    if include_errors:
        print("⚠️ Обнаружены ошибки include:")
        for error in include_errors:
            print(f"  {error}")
    else:
        print("✅ Все include блоки валидны")
    
    return include_errors

def update_all_from_json(toc_json_path, toc_md_path, annotations=None):
    """Создает Markdown TOC из существующего JSON файла"""
    write_toc_from_json(toc_json_path, toc_md_path, annotations)
    print(f"✅ Markdown TOC created from {toc_json_path} and saved to: {toc_md_path}")


def clean_broken_back_links(docs_dir):
    """Удаляет существующие битые ссылки 'Back to TOC' из всех файлов документации"""
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                cleaned_lines = []
                skip_next_empty = False
                
                for line in lines:
                    if ('Back to TOC' in line and 
                        ('basic_toc.md' in line or 'comprehensive_toc.md' in line)):
                        skip_next_empty = True
                        continue
                    elif skip_next_empty and line.strip() == '':
                        skip_next_empty = False
                        continue
                    else:
                        cleaned_lines.append(line)
                        skip_next_empty = False
                
                cleaned_content = '\n'.join(cleaned_lines)
                if cleaned_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)


def inject_back_to_toc_links_russian(docs_dir, description_md_path, content_entries, readme_path='README.md'):
    """Добавляет русские навигационные ссылки 'Домой' и 'Назад' в файлы документации"""
    abs_description = os.path.abspath(description_md_path)
    abs_readme = os.path.abspath(readme_path)
    
    for entry in content_entries:
        rel_file = entry["path"]
        file_path = os.path.join(docs_dir, rel_file)
        abs_file = os.path.abspath(file_path)
        
        if abs_file == abs_description or abs_file == abs_readme:
            continue
            
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        
        relative_to_readme = os.path.relpath(readme_path, os.path.dirname(file_path)).replace("\\", "/")
        relative_to_description = os.path.relpath(description_md_path, os.path.dirname(file_path)).replace("\\", "/")
        
        home_link = f"[Домой]({relative_to_readme})"
        back_link = f"[Назад]({relative_to_description})"
        
        if home_link in content and back_link in content:
            continue
        
        navigation = f"{home_link} | {back_link}\n\n"
        updated = f"{navigation}{content}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)


def inject_back_to_toc_links(docs_dir, toc_md_path, toc):
    abs_toc = os.path.abspath(toc_md_path)
    for entry in toc:
        rel_file = entry["file"]
        file_path = os.path.join(docs_dir, rel_file)
        if os.path.abspath(file_path) == abs_toc:
            continue
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        anchor = slugify(rel_file.replace("/", "-"))
        relative = os.path.relpath(toc_md_path, os.path.dirname(file_path)).replace("\\", "/")
        link = f"[Back to TOC]({relative}#{anchor})"
        if link in content:
            continue
        updated = f"{link}\n\n{content}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)

def update_all(docs_dir, toc_path, toc_md_path=None):
    toc, header_map = build_toc(docs_dir)
    with open(toc_path, "w", encoding="utf-8") as f:
        json.dump(toc, f, indent=2, ensure_ascii=False)
    if toc_md_path:
        write_markdown_toc(toc, toc_md_path)
    errors = update_includes(docs_dir, header_map)
    if toc_md_path:
        inject_back_to_toc_links(docs_dir, toc_md_path, toc)
    print(f"✅ TOC updated and saved to: {toc_path}")
    if errors:
        print("\n".join(errors))
    else:
        print("✅ All includes are valid.")


def update_all_comprehensive(docs_dir, toc_path, toc_md_path=None, comprehensive=False, 
                            similarity_threshold=0.8, exclude_patterns=None):
    """Обновленная функция с поддержкой комплексного сканирования без дубликатов"""
    if comprehensive:
        root_dir = find_project_root()
        toc, header_map, all_documents = build_comprehensive_toc(root_dir, exclude_patterns)
        
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "root_directory": str(root_dir),
            "total_files": len(toc)
        }
        
        extended_toc = {
            "metadata": metadata,
            "files": toc
        }
        
        with open(toc_path, "w", encoding="utf-8") as f:
            json.dump(extended_toc, f, indent=2, ensure_ascii=False)
        
        if toc_md_path:
            write_toc_from_json(toc_path, toc_md_path)
    else:
        toc, header_map = build_toc(docs_dir)
        with open(toc_path, "w", encoding="utf-8") as f:
            json.dump(toc, f, indent=2, ensure_ascii=False)
        if toc_md_path:
            write_markdown_toc(toc, toc_md_path)
    
    errors = update_includes(docs_dir, header_map)
    if toc_md_path and not comprehensive:
        inject_back_to_toc_links(docs_dir, toc_md_path, toc)
    
    print(f"✅ TOC updated and saved to: {toc_path}")
    if errors:
        print("\n".join(errors))
    else:
        print("✅ All includes are valid.")

def update_all_from_json(toc_json_path, toc_md_path, annotations=None):
    """Создает Markdown TOC из существующего JSON файла"""
    write_toc_from_json(toc_json_path, toc_md_path, annotations)
    print(f"✅ Markdown TOC created from {toc_json_path} and saved to: {toc_md_path}")
