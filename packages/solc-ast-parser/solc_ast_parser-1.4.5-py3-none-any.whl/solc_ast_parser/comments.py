import random
import re
from typing import List, Optional, Union
from solc_ast_parser.models import ast_models
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.models.base_ast_models import Comment, MultilineComment, NodeType, YulNodeType
from solc_ast_parser.utils import replace_node, traverse_ast


def find_comments(source: str) -> List[Union[Comment, MultilineComment]]:
    comments = []

    for match in re.finditer(r"(.*)(\/\/.*?(?=\n|$))", source):
        comments.append(
            create_comment_node(
                match.start() + len(match.group(1)) - 2,
                match.group(2).strip("/ "),
                False,
                match.group(1).strip() == "",
            )
        )

    for match in re.finditer(r"/\*.*?\*/", source, re.DOTALL):
        comments.append(create_comment_node(match.start(), match.group(), True))

    return sorted(comments, key=lambda x: x.src.split(":")[0])


def create_comment_node(
    start: int, text: str, is_multiline: bool = False, is_pure: bool = True
) -> Comment:
    if is_multiline:
        return MultilineComment(
            src=f"{start}:{len(text)}:0",
            text=text,
            id=random.randint(0, 1000000),
            nodeType=NodeType.MULTILINE_COMMENT,
        )
    return Comment(
        src=f"{start}:{len(text)}:0",
        text=text,
        id=random.randint(0, 1000000),
        nodeType=NodeType.MULTILINE_COMMENT if is_multiline else NodeType.COMMENT,
        isPure=is_pure,
    )


def insert_comments_into_ast(source_code: str, ast: SourceUnit) -> SourceUnit:
    comments = find_comments(source_code)
    return insert_nodes_into_ast(ast, comments)


def insert_node_into_node(
    node: ast_models.ASTNode,
    parent_node: ast_models.ASTNode,
    new_node: ast_models.ASTNode,
) -> ast_models.ASTNode:
    if node == new_node:
        return parent_node

    if not parent_node:
        if node.node_type == NodeType.SOURCE_UNIT:
            node.nodes.insert(0, new_node)
        return node

    if new_node.node_type == NodeType.COMMENT and not new_node.is_pure:
        if parent_node.node_type == NodeType.VARIABLE_DECLARATION:
            parent_node.comment = new_node
            return node
        node.comment = new_node
        return node

    if parent_node.node_type in (NodeType.SOURCE_UNIT, NodeType.CONTRACT_DEFINITION):
        parent_node.nodes.insert(parent_node.nodes.index(node), new_node)
    elif parent_node.node_type in [NodeType.BLOCK, NodeType.UNCHECKED_BLOCK]:
        parent_node.statements.insert(parent_node.statements.index(node), new_node)
    else:
        parent_node.comment = new_node

    return parent_node


def insert_nodes_into_ast(ast: SourceUnit, nodes: List[Comment]) -> SourceUnit:
    for node in nodes:
        min_distance = float("inf")
        closest_node = None
        parent_node = None

        def find_closest_node(
            current_node: ast_models.ASTNode, parent: Optional[ast_models.ASTNode]
        ) -> None:
            nonlocal min_distance, closest_node, parent_node
            start = int(current_node.src.split(":")[0])
            if isinstance(node, Comment) and not node.is_pure:
                start = int(current_node.src.split(":")[0]) + int(
                    current_node.src.split(":")[1]
                )
            distance = start - int(node.src.split(":")[0])
            if 0 <= distance < min_distance and current_node.node_type not in [item.value for item in YulNodeType]:
                min_distance = distance
                closest_node = current_node
                parent_node = parent

        traverse_ast(ast, find_closest_node)

        if closest_node is not None:
            parent_node = insert_node_into_node(closest_node, parent_node, node)
            replace_node(ast, parent_node.id, parent_node)
    return ast
