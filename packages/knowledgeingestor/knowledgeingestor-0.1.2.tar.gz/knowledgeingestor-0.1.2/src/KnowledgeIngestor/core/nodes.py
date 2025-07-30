import abc
from typing import List, Dict, Any

class Node(abc.ABC):
    """
    抽象基类，代表文件系统中的一个节点 (文件或文件夹)。
    所有具体的文件和文件夹节点都应继承自此基类。
    """
    def __init__(self, name: str):
        """
        初始化 Node 实例。

        :param name: 节点的名称 (例如: 文件名或文件夹名)。
        """
        self.name = name

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        将节点及其内容转换为字典（JSON可序列化）。

        此抽象方法必须由子类实现，以定义节点如何被序列化为字典结构。

        :return: 节点的字典表示。
        """
        pass

class FileNode(Node):
    """
    代表一个文件节点（叶子节点）。
    它包含文件的名称和由解析器生成的结构化内容。
    """
    def __init__(self, name: str, content: Dict[str, Any]):
        """
        初始化 FileNode 实例。

        :param name: 文件的名称。
        :param content: 由解析器生成的文件的结构化内容，通常是一个字典。
        """
        super().__init__(name)
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        """
        将 FileNode 转换为字典（JSON可序列化）。

        :return: 包含文件名称、类型和内容的字典。
        """
        return {
            "name": self.name,
            "type": "file",
            "content": self.content,
        }

class FolderNode(Node):
    """
    代表一个文件夹节点（容器节点)。
    它可以包含其他 Node 实例作为其子节点 (文件或子文件夹)。
    """
    def __init__(self, name: str):
        """
        初始化 FolderNode 实例。

        :param name: 文件夹的名称。
        """
        super().__init__(name)
        self.children: List[Node] = []

    def add_child(self, node: Node):
        """
        向当前文件夹节点添加一个子节点。

        :param node: 要添加的子节点 (可以是 FileNode 或 FolderNode 实例)。
        """
        self.children.append(node)

    def to_dict(self) -> Dict[str, Any]:
        """
        将 FolderNode 转换为字典（JSON可序列化）。

        此方法会递归调用所有子节点的 to_dict 方法，以构建完整的目录结构。

        :return: 包含文件夹名称、类型和子节点列表的字典。
        """
        return {
            "name": self.name,
            "type": "folder",
            "children": [child.to_dict() for child in self.children],
        }