import pytest
import os
import shutil
from KnowledgeIngestor.ingestor import KnowledgeIngestor
from KnowledgeIngestor.core.parsers import IParser
from typing import Dict, Any

@pytest.fixture
def knowledge_ingestor():
    return KnowledgeIngestor()

@pytest.fixture
def temp_docs_structure(tmp_path):
    # Create a complex temporary directory structure
    # root_dir/
    # ├── folder1/
    # │   ├── file1.md
    # │   └── subfolder1/
    # │       └── file2.md
    # ├── folder2/
    # │   ├── file3.txt (ignored)
    # │   └── file4.md
    # └── file5.md
    # └── .hidden_file.md (ignored by os.listdir by default)

    root_dir = tmp_path / "root_dir"
    root_dir.mkdir()

    folder1 = root_dir / "folder1"
    folder1.mkdir()
    (folder1 / "file1.md").write_text("# File1 Title\nContent of file1.")

    subfolder1 = folder1 / "subfolder1"
    subfolder1.mkdir()
    (subfolder1 / "file2.md").write_text("## File2 Title\nContent of file2.")

    folder2 = root_dir / "folder2"
    folder2.mkdir()
    (folder2 / "file3.txt").write_text("This is a text file.") # Should be ignored
    (folder2 / "file4.md").write_text("# File4 Title\nContent of file4.")

    (root_dir / "file5.md").write_text("# File5 Title\nContent of file5.")
    (root_dir / ".hidden_file.md").write_text("# Hidden File Title\nContent of hidden file.")

    return root_dir

class CustomParser(IParser):
    def parse(self, file_path: str) -> Dict[str, Any]:
        return {"custom_content": f"Parsed by CustomParser: {os.path.basename(file_path)}"}

def test_ingest_basic_structure(knowledge_ingestor, temp_docs_structure):
    result = knowledge_ingestor.ingest(str(temp_docs_structure))
    
    assert result["name"] == "root_dir"
    assert result["type"] == "folder"
    assert len(result["children"]) == 3 # folder1, folder2, file5.md (hidden file is ignored)

    # Check folder1
    folder1_node = next(n for n in result["children"] if n["name"] == "folder1")
    assert folder1_node["type"] == "folder"
    assert len(folder1_node["children"]) == 2 # file1.md, subfolder1

    file1_node = next(n for n in folder1_node["children"] if n["name"] == "file1.md")
    assert file1_node["type"] == "file"
    assert file1_node["content"]["title"] == "File1 Title"

    subfolder1_node = next(n for n in folder1_node["children"] if n["name"] == "subfolder1")
    assert subfolder1_node["type"] == "folder"
    assert len(subfolder1_node["children"]) == 1

    file2_node = next(n for n in subfolder1_node["children"] if n["name"] == "file2.md")
    assert file2_node["type"] == "file"
    assert file2_node["content"]["title"] == "File2 Title"

    # Check folder2
    folder2_node = next(n for n in result["children"] if n["name"] == "folder2")
    assert folder2_node["type"] == "folder"
    assert len(folder2_node["children"]) == 1 # file4.md (file3.txt is ignored)

    file4_node = next(n for n in folder2_node["children"] if n["name"] == "file4.md")
    assert file4_node["type"] == "file"
    assert file4_node["content"]["title"] == "File4 Title"

    # Check file5.md
    file5_node = next(n for n in result["children"] if n["name"] == "file5.md")
    assert file5_node["type"] == "file"
    assert file5_node["content"]["title"] == "File5 Title"

def test_ingest_non_existent_path(knowledge_ingestor):
    with pytest.raises(ValueError, match="Path 'non_existent_path' is not a valid directory."):
        knowledge_ingestor.ingest("non_existent_path")

def test_register_custom_parser(knowledge_ingestor, temp_docs_structure):
    # Create a file with a custom extension
    custom_file_path = temp_docs_structure / "custom_file.xyz"
    custom_file_path.write_text("This is a custom file content.")

    # Register the custom parser
    knowledge_ingestor.register_parser(".xyz", CustomParser())

    result = knowledge_ingestor.ingest(str(temp_docs_structure))

    # Find the custom file in the result
    custom_file_node = None
    for child in result["children"]:
        if child["name"] == "custom_file.xyz":
            custom_file_node = child
            break
    
    assert custom_file_node is not None
    assert custom_file_node["type"] == "file"
    assert custom_file_node["content"] == {"custom_content": "Parsed by CustomParser: custom_file.xyz"}

def test_ingest_empty_directory(knowledge_ingestor, tmp_path):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    result = knowledge_ingestor.ingest(str(empty_dir))
    assert result["name"] == "empty_dir"
    assert result["type"] == "folder"
    assert result["children"] == []
