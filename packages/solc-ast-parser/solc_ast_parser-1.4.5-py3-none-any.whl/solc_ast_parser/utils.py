from collections import deque
import json
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import typing
import solcx

from solc_ast_parser.models import ast_models
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.models.base_ast_models import Comment, MultilineComment, NodeType


def compile_contract_from_source(source: str):
    suggested_version = solcx.install.select_pragma_version(
        source, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_source(source, solc_version=suggested_version)
    return json_compiled[list(json_compiled.keys())[0]]["ast"]


def compile_contract_with_standart_input(
    source: str, contract_file_name: str = "example.sol"
):
    suggested_version = solcx.install_solc_pragma(
        source, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_standard(
        create_standard_solidity_input(source, contract_file_name),
        solc_version=suggested_version,
    )["sources"]
    return json_compiled[list(json_compiled.keys())[0]]["ast"]


def create_ast_from_source(source: str) -> SourceUnit:
    ast = compile_contract_from_source(source)
    return SourceUnit(**ast)


def create_ast_with_standart_input(
    source: str, contract_file_name: str = "example.sol"
) -> SourceUnit:
    ast = compile_contract_with_standart_input(source, contract_file_name)
    return SourceUnit(**ast)


def traverse_ast(
    node: ast_models.ASTNode,
    visitor: Callable[[Any, Optional[ast_models.ASTNode]], None],
    parent: Optional[ast_models.ASTNode] = None,
) -> None:
    if node is None:
        return

    visitor(node, parent)

    for field_name, field in node.model_fields.items():
        value = getattr(node, field_name)

        if isinstance(value, list):
            for item in value:
                if hasattr(item, "model_fields") and hasattr(item, "node_type"):
                    traverse_ast(item, visitor, node)
        elif hasattr(value, "model_fields") and hasattr(value, "node_type"):
            traverse_ast(value, visitor, node)


def update_node_fields(
    ast_node: ast_models.ASTNode,
    target_fields: Dict[str, Any],
    new_values: Dict[str, Any],
) -> bool:
    stack = deque([ast_node])
    updated = False
    visited = set()

    while stack:
        current_node = stack.popleft()
        if not hasattr(current_node, "id"):
            continue
        node_id = current_node.id
        if node_id in visited:
            continue
        visited.add(node_id)

        matches = True
        for field, value in target_fields.items():
            if not hasattr(current_node, field):
                matches = False
                break

            current_value = getattr(current_node, field)
            if isinstance(value, list):
                if current_value not in value:
                    matches = False
                    break
            elif current_value != value:
                matches = False
                break

        if matches:
            for field, value in new_values.items():
                if hasattr(current_node, field):
                    setattr(current_node, field, value)
                    updated = True

        for field_name, field_value in current_node.__dict__.items():
            if isinstance(field_value, list):
                for item in field_value:
                    if hasattr(item, "model_fields"):
                        stack.append(item)
            elif hasattr(field_value, "model_fields"):
                stack.append(field_value)

    return updated


def replace_node(
    ast_node: ast_models.ASTNode, target_id: int, replacement_node: ast_models.ASTNode
) -> bool:
    if hasattr(ast_node, "id") and ast_node.id == target_id:
        return False

    stack = deque([(ast_node, None, None)])

    while stack:
        current_node, parent_field, list_index = stack.popleft()

        for field_name, field_value in current_node.__dict__.items():
            if isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if hasattr(item, "id") and item.id == target_id:
                        field_value[i] = replacement_node
                        return True
                    elif hasattr(item, "__dict__"):
                        stack.append((item, field_name, i))

            elif hasattr(field_value, "__dict__"):
                if hasattr(field_value, "id") and field_value.id == target_id:
                    setattr(current_node, field_name, replacement_node)
                    return True
                stack.append((field_value, field_name, None))

    return False


def replace_node_to_multiple(
    ast_node: ast_models.ASTNode,
    target_id: int,
    replacement_nodes: List[ast_models.ASTNode],
) -> bool:
    if hasattr(ast_node, "id") and ast_node.id == target_id:
        return False

    stack = deque([(ast_node, None, None)])

    while stack:
        current_node, parent_field, list_index = stack.popleft()

        for field_name, field_value in current_node.__dict__.items():
            if isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if hasattr(item, "id") and item.id == target_id:
                        field_value[i] = replacement_nodes
                        return True
                    elif hasattr(item, "__dict__"):
                        stack.append((item, field_name, i))

            elif hasattr(field_value, "__dict__"):
                if hasattr(field_value, "id") and field_value.id == target_id:
                    setattr(current_node, field_name, replacement_nodes)
                    return True
                stack.append((field_value, field_name, None))

    return False


def remove_node(ast_node: ast_models.ASTNode, target_id: int) -> bool:
    if hasattr(ast_node, "id") and ast_node.id == target_id:
        return False

    stack = deque([(ast_node, None, None)])

    while stack:
        current_node, parent_field, list_index = stack.popleft()

        for field_name, field_value in current_node.__dict__.items():
            if isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if hasattr(item, "id") and item.id == target_id:
                        del field_value[i]
                        return True
                    elif hasattr(item, "__dict__"):
                        stack.append((item, field_name, i))

            elif hasattr(field_value, "__dict__"):
                if hasattr(field_value, "id") and field_value.id == target_id:
                    setattr(current_node, field_name, None)
                    return True
                stack.append((field_value, field_name, None))

    return False


def create_standard_solidity_input(contract_content: str, contract_name: str) -> Dict:
    return {
        "language": "Solidity",
        "sources": {contract_name: {"content": contract_content}},
        "settings": {
            "stopAfter": "parsing",
            "outputSelection": {"*": {"": ["ast"]}},
        },
    }


def find_node_with_properties(
    ast: ast_models.ASTNode, **kwargs  # name="functionName"
) -> List[ast_models.ASTNode]:
    def check_node(node):
        for key, value in kwargs.items():
            if not hasattr(node, key) or getattr(node, key) != value:
                return False
        return True

    nodes = []
    traverse_ast(ast, lambda n, p: nodes.append(n) if check_node(n) else None)
    return nodes


def get_contract_nodes(
    ast: SourceUnit, node_type: NodeType = None
) -> List[ast_models.ASTNode]:
    nodes = []
    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            if not node_type:
                return node.nodes
            for contract_node in node.nodes:
                if contract_node.node_type == node_type:
                    if (
                        contract_node.node_type == NodeType.FUNCTION_DEFINITION
                        and contract_node.kind == "constructor"
                    ):
                        continue
                    nodes.append(contract_node)
    return nodes


def insert_node(
    ast_node: ast_models.ASTNode,
    target_id: int,
    new_node: ast_models.ASTNode,
    position: typing.Literal["after", "before", "child_first", "child_last"] = "after",
) -> bool:
    if hasattr(ast_node, "id") and ast_node.id == target_id:
        return False

    stack = deque([(ast_node, None, None, None)])

    while stack:
        current_node, parent_node, field_name, list_index = stack.popleft()

        for field_name, field_value in current_node.__dict__.items():
            if isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if hasattr(item, "id") and item.id == target_id:
                        if position == "before":
                            field_value.insert(i, new_node)
                        elif position == "after":
                            field_value.insert(i + 1, new_node)
                        elif position == "child_first":
                            if hasattr(item, "nodes"):
                                item.nodes.insert(0, new_node)
                            elif hasattr(item, "statements"):
                                item.statements.insert(0, new_node)
                            else:
                                return False
                        elif position == "child_last":
                            if hasattr(item, "nodes"):
                                item.nodes.append(new_node)
                            elif hasattr(item, "statements"):
                                item.statements.append(new_node)
                            else:
                                return False
                        return True
                    elif hasattr(item, "__dict__"):
                        stack.append((item, current_node, field_name, i))

            elif hasattr(field_value, "__dict__"):
                if hasattr(field_value, "id") and field_value.id == target_id:
                    if position == "child_first":
                        if hasattr(field_value, "nodes"):
                            field_value.nodes.insert(0, new_node)
                        elif hasattr(field_value, "statements"):
                            field_value.statements.insert(0, new_node)
                        else:
                            return False
                    elif position == "child_last":
                        if hasattr(field_value, "nodes"):
                            field_value.nodes.append(new_node)
                        elif hasattr(field_value, "statements"):
                            field_value.statements.append(new_node)
                        else:
                            return False
                    return True
                stack.append((field_value, current_node, field_name, None))

    return False
