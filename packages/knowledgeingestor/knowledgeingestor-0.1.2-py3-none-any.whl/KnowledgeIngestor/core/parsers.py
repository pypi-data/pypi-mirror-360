import abc
from typing import Dict, Any, List
from markdown_it import MarkdownIt

class IParser(abc.ABC):
    """
    所有文件解析器的抽象基类。
    定义了文件解析器必须实现的接口。
    """
    @abc.abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析指定路径的文件内容，并返回一个结构化的字典。

        :param file_path: 要解析的文件的完整路径。
        :return: 包含文件内容的结构化字典。
        """
        pass

class MarkdownParser(IParser):
    """
    负责解析Markdown文件，核心任务是构建标题的嵌套结构。
    它将Markdown文件解析为一系列的token，然后根据这些token构建一个层级化的字典结构，
    其中包含标题、内容和子标题。
    """
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析Markdown文件并返回其结构化内容。

        该方法读取Markdown文件，使用 markdown-it 库将其解析为token，
        然后根据标题层级构建一个嵌套的字典结构。

        :param file_path: Markdown文件的路径。
        :return: 包含Markdown文件标题和内容的嵌套字典结构。
                 如果文件没有标题，则返回一个默认的 "Untitled" 根节点。
        """
        md = MarkdownIt()
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        tokens = md.parse(text)
        
        # Debugging: Write tokens to a file
        import json
        debug_output = []
        for token in tokens:
            debug_output.append({
                "type": token.type,
                "tag": token.tag,
                "level": token.level,
                "content": token.content,
                "markup": token.markup,
                "info": token.info,
                "map": token.map,
                "children_count": len(token.children) if token.children else 0
            })
        with open(file_path + ".debug_tokens.json", "w", encoding="utf-8") as f:
            json.dump(debug_output, f, indent=2, ensure_ascii=False)

        # 这是实现标题嵌套的关键算法
        # root是最终返回的字典
        # path用于追踪当前的标题层级
        root = {"title": "root", "level": 0, "content": [], "children": []}
        path = [root]

        for token in tokens:
            if token.type == 'heading_open':
                level = int(token.tag[1]) # h1 -> 1, h2 -> 2
                # 寻找正确的父节点
                while path[-1]['level'] >= level:
                    path.pop()
                
                new_node = {
                    "title": "", # 标题在下一个inline token中
                    "level": level,
                    "content": [],
                    "children": []
                }
                path[-1]['children'].append(new_node)
                path.append(new_node)

            elif token.type == 'inline' and path[-1]['title'] == "":
                # 捕获标题文本
                path[-1]['title'] = token.content

            elif token.type not in ['heading_open', 'heading_close']:
                # 捕获所有非标题内容块
                if token.content:
                    path[-1]['content'].append(token.content)

        # 清理content中的空字符串并合并
        def clean_node(node):
            node['content'] = "\n".join(node['content'])
            for child in node['children']:
                clean_node(child)
            return node

        # 返回第一个标题节点，或者如果文件没有标题则返回根节点的内容
        if root['children']:
             return clean_node(root['children'][0])
        else:
             return {"title": "Untitled", "level": 0, "content": "\n".join(root['content']), "children":[]}