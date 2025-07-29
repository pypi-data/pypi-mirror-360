from update_docs.core import (
    slugify,
    extract_headers,
    build_toc,
    extract_section,
    update_includes,
    write_markdown_toc,
    inject_back_to_toc_links,
    generate_persistent_file_id,
    detect_author_type_enhanced,
    classify_author_from_git,
    match_file_by_content,
    build_content_json,
)


def test_slugify():
    assert slugify("Hello World!") == "hello-world-"


def test_extract_headers(tmp_path):
    md = tmp_path / "sample.md"
    md.write_text("# Title <!-- id:main-title -->\n## Subsection\n")
    headers = extract_headers(md)
    assert len(headers) == 2
    assert headers[0]["level"] == 1
    assert headers[0]["title"] == "Title"
    assert headers[0]["id"] == "main-title"
    assert headers[0]["parent_id"] is None
    assert headers[1]["level"] == 2
    assert headers[1]["title"] == "Subsection"
    assert headers[1]["id"] == "subsection"
    assert headers[1]["parent_id"] == "main-title"


def test_build_toc(tmp_path):
    docs = tmp_path
    (docs / "a.md").write_text("# A\n")
    sub = docs / "sub"
    sub.mkdir()
    (sub / "b.md").write_text("# B\n")

    toc, header_map = build_toc(docs)

    assert len(toc) == 2
    assert toc[0]["file"] == "a.md"
    assert len(toc[0]["headers"]) == 1
    assert toc[0]["headers"][0]["title"] == "A"
    assert toc[0]["headers"][0]["level"] == 1
    assert toc[1]["file"] == "sub/b.md"
    assert len(toc[1]["headers"]) == 1
    assert toc[1]["headers"][0]["title"] == "B"
    assert toc[1]["headers"][0]["level"] == 1
    assert header_map[("a.md", "a")] == {"title": "A", "level": 1, "file": "a.md"}


def test_extract_section(tmp_path):
    md = tmp_path / "section.md"
    md.write_text(
        "# Top\ntext\n## Section\nline1\nline2\n## End\n"
    )
    result = extract_section(md, "section", 2)
    assert result == "line1\nline2"


def test_update_includes(tmp_path):
    docs = tmp_path
    (docs / "src.md").write_text("# Source\n## part\ncontent\n")
    target = docs / "dest.md"
    target.write_text("# Dest\n<!-- include:src.md#part -->\n")

    toc, header_map = build_toc(docs)
    errors = update_includes(docs, header_map)

    assert errors == []
    content = target.read_text()
    assert "<!-- BEGIN include:src.md#part -->" in content
    assert "content" in content


def test_write_markdown_toc(tmp_path):
    toc = [{"file": "index.md", "headers": []}]
    path = tmp_path / "toc.md"
    write_markdown_toc(toc, path)
    content = path.read_text()
    assert "[index.md](docs/index.md)" in content
    assert '<a id="index-md"></a>' in content




def test_generate_persistent_file_id(tmp_path):
    """Тест генерации persistent file_id"""
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test Content\nSome content here")
    
    file_id = generate_persistent_file_id(str(test_file))
    assert file_id.startswith("test-")
    assert len(file_id.split("-")[1]) == 8


def test_detect_author_type_enhanced():
    """Тест расширенного определения типа автора"""
    author, source = detect_author_type_enhanced("", "<!-- AUTO-GENERATED -->")
    assert author == "generator" and source in ["comment_marker", "registry_lookup"]
    
    author, source = detect_author_type_enhanced("", "<!-- AI-GENERATED -->")
    assert author == "generator" and source in ["comment_marker", "registry_lookup"]
    
    author, source = detect_author_type_enhanced("regular_file.md", "Regular content without special markers")
    assert author == "human" and source == "default"


def test_classify_author_from_git():
    """Тест классификации автора по git данным"""
    git_info = {'last_author_email': 'devin@example.com', 'last_author_name': 'Devin'}
    assert classify_author_from_git(git_info) == "ai"
    
    git_info = {'last_author_email': 'auto@example.com', 'last_author_name': 'Auto'}
    assert classify_author_from_git(git_info) == "generator"
    
    git_info = {'last_author_email': 'user@example.com', 'last_author_name': 'John Doe'}
    assert classify_author_from_git(git_info) == "human"


def test_extract_headers_with_parent_id(tmp_path):
    """Тест извлечения заголовков с parent_id и excerpt"""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Main Title\nSome content for main title.\n## Subsection\nContent for subsection.\n### Deep Section\nDeep content here.\n## Another Subsection")
    
    headers = extract_headers(str(md_file))
    assert len(headers) == 4
    assert headers[0]["parent_id"] is None
    assert headers[1]["parent_id"] == headers[0]["id"]
    assert headers[2]["parent_id"] == headers[1]["id"]
    assert headers[3]["parent_id"] == headers[0]["id"]
    assert "Some content" in headers[0]["excerpt"]


def test_build_content_json(tmp_path):
    """Тест создания Content.json с git интеграцией"""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    test_file = docs_dir / "test.md"
    test_file.write_text("# Test Document\nContent here")
    
    entries = build_content_json(str(docs_dir))
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Document"
    assert entries[0]["author"] in ["human", "ai", "generator", "mixed"]
    assert "editable" in entries[0]
    assert "file_id" in entries[0]


def test_match_file_by_content(tmp_path):
    """Тест поиска файла по содержимому при переименовании"""
    test_file = tmp_path / "test.md"
    content = "# Test Content\nSome content here"
    test_file.write_text(content)
    
    file_id = generate_persistent_file_id(str(test_file), content)
    existing_entries = [{"file_id": file_id, "path": "old_name.md"}]
    
    matched_id = match_file_by_content(str(test_file), content, existing_entries)
    assert matched_id == file_id

def test_inject_back_to_toc_links(tmp_path):
    docs = tmp_path
    md = docs / "index.md"
    md.write_text("# Title\n")
    toc_md = tmp_path / "toc.md"
    toc_md.write_text("toc")
    toc = [{"file": "index.md", "headers": []}]
    inject_back_to_toc_links(docs, toc_md, toc)
    content = md.read_text().splitlines()[0]
    assert "[Back to TOC]" in content

