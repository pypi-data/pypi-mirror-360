import pytest
from KnowledgeIngestor.core.nodes import Node, FileNode, FolderNode

def test_file_node_to_dict():
    content = {"title": "Test Title", "content": "Some content"}
    file_node = FileNode("test_file.md", content)
    expected_dict = {
        "name": "test_file.md",
        "type": "file",
        "content": content,
    }
    assert file_node.to_dict() == expected_dict

def test_folder_node_to_dict_empty():
    folder_node = FolderNode("test_folder")
    expected_dict = {
        "name": "test_folder",
        "type": "folder",
        "children": [],
    }
    assert folder_node.to_dict() == expected_dict

def test_folder_node_to_dict_with_children():
    folder_node = FolderNode("parent_folder")
    
    file_content = {"title": "Child File", "content": "File content"}
    file_node = FileNode("child_file.txt", file_content)
    
    sub_folder_node = FolderNode("sub_folder")
    sub_file_content = {"title": "Sub Child File", "content": "Sub file content"}
    sub_file_node = FileNode("sub_child_file.txt", sub_file_content)
    sub_folder_node.add_child(sub_file_node)

    folder_node.add_child(file_node)
    folder_node.add_child(sub_folder_node)

    expected_dict = {
        "name": "parent_folder",
        "type": "folder",
        "children": [
            {
                "name": "child_file.txt",
                "type": "file",
                "content": file_content,
            },
            {
                "name": "sub_folder",
                "type": "folder",
                "children": [
                    {
                        "name": "sub_child_file.txt",
                        "type": "file",
                        "content": sub_file_content,
                    }
                ],
            },
        ],
    }
    assert folder_node.to_dict() == expected_dict

def test_node_abstract_method():
    with pytest.raises(TypeError):
        Node("abstract_node")