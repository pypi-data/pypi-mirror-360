import os
from typing import Dict, Any

from .core.nodes import FolderNode, FileNode
from .core.parsers import IParser, MarkdownParser

class KnowledgeIngestor:
    """
    KnowledgeIngestor 类用于摄取指定目录中的知识，并将其组织成一个可查询的结构。
    它支持通过注册不同的解析器来处理不同类型的文件。
    """
    def __init__(self):
        """
        初始化 KnowledgeIngestor 实例。
        默认注册 Markdown (.md, .markdown) 文件的解析器。
        """
        self._parser_registry: Dict[str, IParser] = {}
        self.register_parser(".md", MarkdownParser())
        self.register_parser(".markdown", MarkdownParser())

    def register_parser(self, extension: str, parser: IParser):
        """
        注册一个文件扩展名对应的解析器。

        :param extension: 文件扩展名 (例如: ".md", ".txt")。
        :param parser: 实现了 IParser 接口的解析器实例。
        """
        self._parser_registry[extension.lower()] = parser

    def _get_parser(self, file_path: str) -> IParser | None:
        """
        根据文件路径获取对应的解析器。

        :param file_path: 文件的完整路径。
        :return: 对应的解析器实例，如果没有注册则返回 None。
        """
        extension = os.path.splitext(file_path)[1].lower()
        return self._parser_registry.get(extension)

    def _walk_directory(self, dir_path: str) -> FolderNode:
        """
        递归遍历目录并构建节点树。

        此方法会忽略隐藏文件和目录 (以 '.' 开头的文件/目录)。
        对于识别的文件类型，它会使用注册的解析器解析文件内容。

        :param dir_path: 要遍历的目录路径。
        :return: 表示目录结构的 FolderNode 实例。
        """
        dir_name = os.path.basename(dir_path)
        folder_node = FolderNode(dir_name)

        for item_name in sorted(os.listdir(dir_path)):
            if item_name.startswith('.'):
                continue
            item_path = os.path.join(dir_path, item_name)
            
            if os.path.isdir(item_path):
                sub_folder_node = self._walk_directory(item_path)
                folder_node.add_child(sub_folder_node)
            else:
                parser = self._get_parser(item_path)
                if parser:
                    content = parser.parse(item_path)
                    file_node = FileNode(item_name, content)
                    folder_node.add_child(file_node)
        
        return folder_node

    def ingest(self, root_path: str) -> Dict[str, Any]:
        """
        SDK 的主入口方法。

        接收一个根目录路径，递归遍历该目录及其子目录中的文件，
        并根据注册的解析器解析文件内容，最终返回一个表示整个知识结构的 JSON 字典。

        :param root_path: 要摄取的根目录路径。
        :raises ValueError: 如果 root_path 不是一个有效的目录。
        :return: 包含目录和文件节点结构的 JSON 字典。
        """
        if not os.path.isdir(root_path):
            raise ValueError(f"Path '{root_path}' is not a valid directory.")

        root_node = self._walk_directory(root_path)
        return root_node.to_dict()