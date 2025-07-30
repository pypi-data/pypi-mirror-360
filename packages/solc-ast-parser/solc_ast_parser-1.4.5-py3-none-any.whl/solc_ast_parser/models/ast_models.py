import re
import typing
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from solc_ast_parser.models.yul_models import YulBlock
from .base_ast_models import (
    ExpressionBase,
    Comment,
    MultilineComment,
    Node,
    NodeBase,
    NodeType,
    TypeBase,
    TypeDescriptions,
)

ASTNode = Union[
    "PragmaDirective",
    "SourceUnit",
    "StructuredDocumentation",
    "IdentifierPath",
    "InheritanceSpecifier",
    "UsingForDirective",
    "ParameterList",
    "OverrideSpecifier",
    "FunctionDefinition",
    "ModifierDefinition",
    "ModifierInvocation",
    "EventDefinition",
    "ErrorDefinition",
    "TypeName",
    "TryCatchClause",
    "Expression",
    "Declaration",
    "Statement",
]

Statement = Union[
    "Block",
    "PlaceholderStatement",
    "IfStatement",
    "TryStatement",
    "ForStatement",
    "WhileStatement",
    "Continue",
    "Break",
    "Return",
    "Throw",
    "RevertStatement",
    "EmitStatement",
    "VariableDeclarationStatement",
    "ExpressionStatement",
    "InlineAssembly",
    "Comment",
    "MultilineComment",
]

Declaration = Union[
    "ImportDirective",
    "ContractDefinition",
    "StructDefinition",
    "EnumDefinition",
    "EnumValue",
    "UserDefinedValueTypeDefinition",
    "VariableDeclaration",
]

Expression = Union[
    "Conditional",
    "Assignment",
    "TupleExpression",
    "UnaryOperation",
    "BinaryOperation",
    "FunctionCall",
    "FunctionCallOptions",
    "NewExpression",
    "MemberAccess",
    "IndexAccess",
    "IndexRangeAccess",
    "PrimaryExpression",
]

PrimaryExpression = Union[
    "Literal",
    "Identifier",
    "ElementaryTypeNameExpression",
]

TypeName = Union[
    "ElementaryTypeName",
    "UserDefinedTypeName",
    "FunctionTypeName",
    "Mapping",
    "ArrayTypeName",
]


def build_function_header(node: ASTNode, spaces_count=0):
    name = f" {node.name}" if node.name else ""
    visibility = f" {node.visibility}" if node.kind != "constructor" else ""
    mutability = (
        f" {node.state_mutability}" if node.state_mutability != "nonpayable" else ""
    )

    overrides = " override" if node.overrides else ""
    virtual = " virtual" if node.virtual else ""
    return_params = node.return_parameters.to_solidity()
    modifiers = (
        f" {' '.join([mod.to_solidity() for mod in node.modifiers])}"
        if node.modifiers
        else ""
    )

    if return_params:
        return_params = f" returns ({return_params})"

    if node.kind == "constructor":
        return f"{' ' * spaces_count}constructor({node.parameters.to_solidity()})"
    else:
        return f"{' ' * spaces_count}{node.kind}{name}({node.parameters.to_solidity()}){visibility}{virtual}{mutability}{overrides}{modifiers}{return_params}"


class SourceUnit(NodeBase):
    license: Optional[str] = Field(default=None)
    nodes: List[ASTNode]
    experimental_solidity: Optional[bool] = Field(
        default=None, alias="experimentalSolidity"
    )
    exported_symbols: Optional[Dict[str, List[int]]] = Field(
        default=None, alias="exportedSymbols"
    )
    absolute_path: Optional[str] = Field(default=None, alias="absolutePath")
    node_type: typing.Literal[NodeType.SOURCE_UNIT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count: int = 0):
        result = super().to_solidity(spaces_count)
        for node in self.nodes:
            result += node.to_solidity(spaces_count)

        return result


class PragmaDirective(NodeBase):
    literals: List[str]
    node_type: typing.Literal[NodeType.PRAGMA_DIRECTIVE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count)
        return (
            result
            + f"{' ' * spaces_count}pragma {self.literals[0]} {''.join(self.literals[1:])};\n\n"
        )


class ImportDirective(NodeBase):
    file: str
    source_unit: Optional[SourceUnit] = Field(default=None, alias="sourceUnit")
    scope: Optional[int] = Field(default=None)
    absolute_path: Optional[str] = Field(default=None, alias="absolutePath")
    unit_alias: Optional[str] = Field(default=None, alias="unitAlias")
    symbol_aliases: dict | list | None = Field(
        default=None, alias="symbolAliases"
    )  # TODO Check this type
    name_locaton: str | None = Field(default=None, alias="nameLocation")

    node_type: typing.Literal[NodeType.IMPORT_DIRECTIVE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}import \"{self.absolute_path}\";\n"
        )


class ContractDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    contract_kind: str = Field(alias="contractKind")
    abstract: bool
    base_contracts: List["InheritanceSpecifier"] = Field(alias="baseContracts")
    contract_dependencies: List[int] = Field(alias="contractDependencies")
    used_events: List[int] = Field(alias="usedEvents")
    used_errors: List = Field(alias="usedErrors")
    nodes: List[ASTNode]
    scope: Optional[int] = Field(default=None)
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")
    fully_implemented: Optional[bool] = Field(default=None, alias="fullyImplemented")
    linearized_base_contracts: Optional[List] = Field(
        default=None, alias="linearizedBaseContracts"
    )  # TODO: Check this type
    internal_function_ids: Optional[List] = Field(
        default=None, alias="internalFunctionIDs"
    )  # TODO: Check this type

    node_type: typing.Literal[NodeType.CONTRACT_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        base_contracts = ""
        if len(self.base_contracts):
            base_contracts = [base.to_solidity() for base in self.base_contracts]
            base_contracts = f" is {', '.join(base_contracts)}"
        code = (
            super().to_solidity(spaces_count)
            + f"{self.contract_kind} {self.name}{base_contracts} {{{f' // {self.comment.text}' if self.comment else ''}\n"
        )
        spaces_count = 4
        for contract_node in self.nodes:
            if contract_node.node_type == NodeType.VARIABLE_DECLARATION:
                code += f"{contract_node.to_solidity(spaces_count)};{f' // {contract_node.comment.text}' if contract_node.comment else ''}\n"
                continue
            code += contract_node.to_solidity(spaces_count)
        code += "}\n\n"

        return code


class IdentifierPath(NodeBase):
    name: str
    name_locations: List[str] = Field(alias="nameLocations")
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )

    node_type: typing.Literal[NodeType.IDENTIFIER_PATH] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}{self.name}"


class InheritanceSpecifier(NodeBase):
    base_name: Union[IdentifierPath] = Field(alias="baseName")
    arguments: List[Expression] = Field(default_factory=list)

    node_type: typing.Literal[NodeType.INHERITANCE_SPECIFIER] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count) + self.base_name.to_solidity()
        if self.arguments:
            args = [arg.to_solidity() for arg in self.arguments]
            result += f"({', '.join(args)})"
        return result


class FunctionNode(BaseModel, Node):
    function: Optional[IdentifierPath] = Field(default=None)
    definition: Optional[IdentifierPath] = Field(default=None)
    operator: Optional[str] = Field(default=None)

    node_type: typing.Literal[NodeType.FUNCTION_NODE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return self.function.to_solidity() if self.function else self.operator or ""


class UsingForDirective(NodeBase):
    type_name: Optional[TypeName] = Field(default=None, alias="typeName")
    library_name: Optional[IdentifierPath] = Field(default=None, alias="libraryName")
    global_: bool = Field(default=False, alias="global")
    function_list: Optional[List[FunctionNode]] = Field(
        default=None, alias="functionList"
    )

    node_type: typing.Literal[NodeType.USING_FOR_DIRECTIVE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count) + f"{' ' * spaces_count}using "

        if self.library_name:
            result += self.library_name.to_solidity()

        if self.function_list:
            funcs = [f.to_solidity() for f in self.function_list]
            result += f"{{{', '.join(funcs)}}}"

        result += " for "

        if self.type_name:
            result += self.type_name.to_solidity()
        else:
            result += "*"

        if self.global_:
            result += " global"

        return result + ";\n"


class StructDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    visibility: str
    members: List["VariableDeclaration"]
    scope: Optional[int] = Field(default=None)
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")

    node_type: typing.Literal[NodeType.STRUCT_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        code = (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}struct {self.name} {{\n"
        )
        spaces_count += 4
        for member in self.members:
            code += f"{' ' * spaces_count}{member.type_name.to_solidity(is_parameter=True) if member.type_name.node_type == NodeType.ELEMENTARY_TYPE_NAME else member.type_name.to_solidity()} {member.name};\n"
        spaces_count -= 4

        code += f"{' ' * spaces_count}}}\n"
        return code


class EnumDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    members: List["EnumValue"]
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")

    node_type: typing.Literal[NodeType.ENUM_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}enum {self.name} {{\n"
        )
        spaces_count += 4
        members = [f"{' ' * spaces_count}{member.name}" for member in self.members]
        result += ",\n".join(members)
        spaces_count -= 4
        result += f"\n{' ' * spaces_count}}}\n"
        return result


class EnumValue(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")

    node_type: typing.Literal[NodeType.ENUM_VALUE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}{self.name}"


class UserDefinedValueTypeDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    underlying_type: TypeName = Field(alias="underlyingType")
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")

    node_type: typing.Literal[NodeType.USER_DEFINED_VALUE_TYPE_DEFINITION] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}struct {self.name} {{\n{' ' * spaces_count}}}\n"
        )


class ParameterList(NodeBase):
    parameters: List["VariableDeclaration"] = Field(default_factory=list)

    node_type: typing.Literal[NodeType.PARAMETER_LIST] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        parsed = []
        for parameter in self.parameters:
            storage_location = (
                f" {parameter.storage_location}"
                if parameter.storage_location != "default"
                else ""
            )
            if parameter.type_name.node_type == NodeType.ELEMENTARY_TYPE_NAME:
                var_type = parameter.type_name.to_solidity(is_parameter=True)
            else:
                var_type = parameter.type_name.to_solidity()
            name = f" {parameter.name}" if parameter.name else ""
            if parameter.node_type == NodeType.VARIABLE_DECLARATION:
                indexed = " indexed" if parameter.indexed else ""
            parsed.append(f"{var_type}{indexed}{storage_location}{name}")
        return super().to_solidity() + ", ".join(parsed)


class OverrideSpecifier(NodeBase):
    overrides: List[IdentifierPath]

    node_type: typing.Literal[NodeType.OVERRIDE_SPECIFIER] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        if self.overrides:
            overrides = [f.name for f in self.overrides]
        return f"{' ' * spaces_count}override({', '.join(overrides)}) "


class FunctionDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    kind: Optional[str] = Field(default=None)
    state_mutability: str = Field(alias="stateMutability")
    virtual: bool = Field(default=False)
    overrides: Optional[OverrideSpecifier] = Field(default=None)
    parameters: ParameterList
    return_parameters: ParameterList = Field(alias="returnParameters")
    modifiers: List["ModifierInvocation"] = Field(default_factory=list)
    body: Optional["Block"] = Field(default=None)
    implemented: bool
    scope: Optional[int] = Field(default=None)
    visibility: Optional[str] = Field(default=None)
    function_selector: Optional[str] = Field(default=None, alias="functionSelector")
    base_functions: Optional[List[int]] = Field(default=None, alias="baseFunctions")

    node_type: typing.Literal[NodeType.FUNCTION_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count) + build_function_header(
            self, spaces_count
        )
        if not self.body:
            return result + ";\n\n"
        body = self.body.to_solidity(spaces_count + 4)
        if body:
            result += f" {{\n{body}{' ' * spaces_count}}}\n\n"
        else:
            result += " {}\n\n"
        return result


class VariableDeclaration(TypeBase):
    name: str
    name_location: Optional[str] = Field(alias="nameLocation")
    type_name: TypeName = Field(alias="typeName")
    constant: bool
    mutability: str
    state_variable: bool = Field(alias="stateVariable")
    storage_location: str = Field(alias="storageLocation")
    overrides: Optional[OverrideSpecifier] = Field(default=None)
    visibility: str
    value: Optional[Expression] = Field(default=None)
    scope: Optional[int] = Field(default=None)
    function_selector: Optional[str] = Field(default=None, alias="functionSelector")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    indexed: Optional[bool] = Field(default=None)
    base_functions: Optional[Dict] = Field(
        default=None, alias="baseFunctions"
    )  # TODO: Check this type

    node_type: typing.Literal[NodeType.VARIABLE_DECLARATION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        storage_location = (
            f" {self.storage_location}" if self.storage_location != "default" else ""
        )
        visibility = f" {self.visibility}" if self.visibility != "internal" else ""
        constant = " constant" if self.constant else ""
        value = ""
        if self.value:
            value = f" = {self.value.to_solidity()}"
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.type_name.to_solidity()}{visibility}{constant}{storage_location} {self.name}{value}"
        )


class ModifierDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    visibility: str
    parameters: ParameterList
    virtual: bool
    overrides: Optional[OverrideSpecifier] = Field(default=None)
    body: Optional["Block"] = Field(default=None)
    base_modifiers: Optional[Dict] = Field(
        default=None, alias="baseModifiers"
    )  # TODO: Check this type

    node_type: typing.Literal[NodeType.MODIFIER_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}modifier {self.name}({self.parameters.to_solidity()}) {{\n"
        )
        spaces_count += 4
        result += self.body.to_solidity(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class ModifierInvocation(NodeBase):
    modifier_name: IdentifierPath = Field(alias="modifierName")
    arguments: List[Expression] = Field(default_factory=list)
    kind: Optional[str] = Field(default=None)
    node_type: typing.Literal[NodeType.MODIFIER_INVOCATION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        arguments = (
            f"({', '.join([arg.to_solidity() for arg in self.arguments])})"
            if self.arguments
            else ""
        )
        return f"{' ' * spaces_count}{self.modifier_name.to_solidity()}{arguments}"


class EventDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    parameters: ParameterList
    anonymous: bool
    event_selector: Optional[str] = Field(default=None, alias="eventSelector")
    node_type: typing.Literal[NodeType.EVENT_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}event {self.name}({self.parameters.to_solidity()});\n"
        )


class ErrorDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    parameters: ParameterList
    error_selector: Optional[str] = Field(default=None, alias="errorSelector")
    node_type: typing.Literal[NodeType.ERROR_DEFINITION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}error {self.name}({self.parameters.to_solidity()});\n"
        )


class ElementaryTypeName(TypeBase):
    name: str
    state_mutability: Optional[str] = Field(default=None, alias="stateMutability")
    node_type: typing.Literal[NodeType.ELEMENTARY_TYPE_NAME] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, is_parameter=False):
        if self.name == "address" and self.state_mutability == "payable":
            return (
                super().to_solidity(spaces_count)
                + f"{' ' * spaces_count}{f'{self.name} ' if is_parameter else ''}{self.state_mutability}"
            )
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}{self.name}"


class UserDefinedTypeName(TypeBase):
    path_node: IdentifierPath = Field(alias="pathNode")
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )
    node_type: typing.Literal[NodeType.USER_DEFINED_TYPE_NAME] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.path_node.name}"
        )


class FunctionTypeName(TypeBase):
    visibility: str
    state_mutability: str = Field(alias="stateMutability")
    parameter_types: List[ParameterList] = Field(alias="parameterTypes")
    return_parameter_types: List[ParameterList] = Field(alias="returnParameterTypes")
    node_type: typing.Literal[NodeType.FUNCTION_TYPE_NAME] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{build_function_header(self)};\n"


class Mapping(TypeBase):
    key_type: TypeName = Field(alias="keyType")
    key_name: str = Field(alias="keyName")
    key_name_location: str = Field(alias="keyNameLocation")
    value_type: TypeName = Field(alias="valueType")
    value_name: str = Field(alias="valueName")
    value_name_location: str = Field(alias="valueNameLocation")
    node_type: typing.Literal[NodeType.MAPPING] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        key_type = self.key_type.to_solidity()
        value_type = self.value_type.to_solidity()
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}mapping({key_type} => {value_type})"
        )


class ArrayTypeName(TypeBase):
    base_type: TypeName = Field(alias="baseType")
    length: Optional[Expression] = Field(default=None)
    node_type: typing.Literal[NodeType.ARRAY_TYPE_NAME] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.base_type.to_solidity()}[{self.length.to_solidity() if self.length else ''}]"
        )


class InlineAssembly(NodeBase):
    AST: YulBlock
    external_references: Optional[List[Dict]] = Field(
        default=None, alias="externalReferences"
    )
    evm_version: Optional[str] = Field(default=None, alias="evmVersion")
    eof_version: Optional[int] = Field(default=None, alias="eofVersion")
    flags: Optional[List[str]] = Field(default=None)
    node_type: typing.Literal[NodeType.INLINE_ASSEMBLY] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}assembly {self.AST.to_solidity(spaces_count)}"
        )


class Block(NodeBase):
    statements: List[Statement]
    node_type: typing.Literal[NodeType.BLOCK, NodeType.UNCHECKED_BLOCK] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count)
        for statement in self.statements:
            if not statement.node_type in (
                NodeType.COMMENT,
                NodeType.MULTILINE_COMMENT,
            ):
                st = statement.to_solidity(spaces_count)
                if (
                    statement.node_type != NodeType.INLINE_ASSEMBLY
                    and not st.endswith(";\n")
                    and not st.endswith("}\n")
                    and not re.search(r"\/\/ .+", st)
                ):
                    st += f";{f' // {statement.comment.text}' if statement.comment else ''}\n"
                result += st

            else:
                result += statement.to_solidity(spaces_count)
        return result


class PlaceholderStatement(NodeBase):
    node_type: typing.Literal[NodeType.PLACEHOLDER_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}_;\n"


class IfStatement(NodeBase):
    condition: Expression
    true_body: Statement = Field(alias="trueBody")
    false_body: Optional[Statement] = Field(default=None, alias="falseBody")
    node_type: typing.Literal[NodeType.IF_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}if ({self.condition.to_solidity()}) {{\n"
        )
        spaces_count += 4
        result += self.true_body.to_solidity(spaces_count)
        spaces_count -= 4

        if self.false_body:
            result += f"{' ' * spaces_count}}} else {{\n"
            spaces_count += 4
            result += self.false_body.to_solidity(spaces_count)
            spaces_count -= 4

        if not result.endswith(";\n") and not result.endswith("}\n"):
            result += f";\n"

        result += f"{' ' * spaces_count}}}\n"
        return result


class TryCatchClause(NodeBase):
    error_name: str = Field(alias="errorName")
    parameters: Optional[ParameterList] = Field(default=None)
    block: Block
    node_type: typing.Literal[NodeType.TRY_CATCH_CLAUSE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count) + f"{' ' * spaces_count}catch "
        if self.parameters:
            result += f"({self.parameters.to_solidity()}) "
        result += "{\n"
        spaces_count += 4
        result += self.block.to_solidity(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class TryStatement(NodeBase):
    external_call: Optional[Expression] = Field(default=None, alias="externalCall")
    clauses: List[TryCatchClause]
    node_type: typing.Literal[NodeType.TRY_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count) + f"{' ' * spaces_count}try "
        if self.external_call:
            result += self.external_call.to_solidity()
        if self.clauses:
            result += (
                f" returns ({self.clauses[0].parameters.to_solidity()})"
                if self.clauses[0].parameters
                else ""
            )
            result += " {\n"

            result += self.clauses[0].block.to_solidity(spaces_count + 4)

            result += f"{' ' * spaces_count}}}"

        for clause in self.clauses[1:]:
            result += clause.to_solidity(spaces_count)

        return result


class WhileStatement(NodeBase):  # DoWhileStatement
    condition: Expression
    body: Statement
    node_type: typing.Literal[NodeType.WHILE_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}while ({self.condition.to_solidity()}) {{\n"
        )
        spaces_count += 4
        result += self.body.to_solidity(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class ForStatement(NodeBase):
    intialization_expression: Optional[Statement] = Field(
        default=None, alias="initializationExpression"
    )
    condition: Optional[Expression] = Field(default=None)
    loop_expression: Optional["ExpressionStatement"] = Field(
        default=None, alias="loopExpression"
    )
    body: Statement
    is_simple_counter_loop: Optional[bool] = Field(
        default=None, alias="isSimpleCounterLoop"
    )
    node_type: typing.Literal[NodeType.FOR_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        result = super().to_solidity(spaces_count) + f"{' ' * spaces_count}for ("
        if self.intialization_expression:
            result += f"{self.intialization_expression.to_solidity()}; "
        if self.condition:
            result += f"{self.condition.to_solidity()}; "
        if self.loop_expression:
            result += f"{self.loop_expression.to_solidity()}"
        result += f") {{\n"
        spaces_count += 4
        result += self.body.to_solidity(spaces_count)
        if not result.endswith(";\n") and not result.endswith("}\n"):
            result += f";\n"
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class Continue(NodeBase):
    node_type: typing.Literal[NodeType.CONTINUE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}continue"


class Break(NodeBase):
    node_type: typing.Literal[NodeType.BREAK] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}break"


class Return(NodeBase):
    expression: Optional[Expression] = Field(default=None)
    function_return_parameters: Optional[int] = Field(
        default=None, alias="functionReturnParameters"
    )
    node_type: typing.Literal[NodeType.RETURN] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        if self.expression:
            return (
                super().to_solidity(spaces_count)
                + f"{' ' * spaces_count}return {self.expression.to_solidity()};\n"
            )
        else:
            return super().to_solidity(spaces_count) + f"{' ' * spaces_count}return"


class Throw(NodeBase):
    node_type: typing.Literal[NodeType.THROW] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}throw;\n"


class EmitStatement(NodeBase):
    event_call: "FunctionCall" = Field(alias="eventCall")
    node_type: typing.Literal[NodeType.EMIT_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * (spaces_count)}emit {self.event_call.to_solidity()};\n"
        )


class RevertStatement(NodeBase):
    error_call: Optional["FunctionCall"] = Field(default=None, alias="errorCall")
    node_type: typing.Literal[NodeType.REVERT_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}revert {self.error_call.to_solidity()};\n"
        )


class VariableDeclarationStatement(NodeBase):
    assignments: List[Union[int, None]] = Field(default_factory=list)
    declarations: List[Union[VariableDeclaration, None]]
    initial_value: Optional[Expression] = Field(default=None, alias="initialValue")
    node_type: typing.Literal[NodeType.VARIABLE_DECLARATION_STATEMENT] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0):
        declarations = []
        comment = ""
        for declaration in self.declarations:
            if declaration is None:
                declarations.append("")
            else:
                declarations.append(declaration.to_solidity())
                if declaration.comment:
                    comment = f"; // {declaration.comment.text}\n"
        if len(declarations) > 1:
            declarations_str = f"({', '.join(declarations)})"
        else:
            declarations_str = declarations[0]
        left = declarations_str
        right = f" = {self.initial_value.to_solidity()}" if self.initial_value else ""
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * (spaces_count)}{left}{right}"
            + comment
        )


class ExpressionStatement(NodeBase):
    expression: Expression
    node_type: typing.Literal[NodeType.EXPRESSION_STATEMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * (spaces_count)}{self.expression.to_solidity()}"
        )


class Conditional(ExpressionBase):  # TODO maybe errors
    condition: Expression
    true_expression: Expression = Field(alias="trueExpression")
    false_expression: Expression = Field(alias="falseExpression")
    node_type: typing.Literal[NodeType.CONDITIONAL] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.condition.to_solidity()} ? {self.true_expression.to_solidity()} : {self.false_expression.to_solidity()}"
        )


class Assignment(ExpressionBase):
    operator: str
    left_hand_side: Expression = Field(default=None, alias="leftHandSide")
    right_hand_side: Expression = Field(default=None, alias="rightHandSide")
    node_type: typing.Literal[NodeType.ASSIGNMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.left_hand_side.to_solidity()} {self.operator} {self.right_hand_side.to_solidity()}"
        )


class TupleExpression(ExpressionBase):
    is_inline_array: bool = Field(alias="isInlineArray")
    components: List[Expression | None]
    node_type: typing.Literal[NodeType.TUPLE_EXPRESSION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        res_tuple = [
            component.to_solidity() if component else ""
            for component in self.components
        ]
        if self.is_inline_array:
            res_tuple = f"[{', '.join(res_tuple)}]"
        else:
            res_tuple = f"({', '.join(res_tuple)})"

        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{res_tuple}"
        )


class UnaryOperation(ExpressionBase):
    prefix: bool
    operator: str
    sub_expression: Expression = Field(alias="subExpression")
    function: Optional[int] = Field(default=None)
    node_type: typing.Literal[NodeType.UNARY_OPERATION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        if self.prefix:
            return (
                super().to_solidity(spaces_count)
                + f"{' ' * spaces_count}{self.operator}{' ' if self.operator == 'delete' else ''}{self.sub_expression.to_solidity()}"
            )
        else:
            return (
                super().to_solidity(spaces_count)
                + f"{' ' * spaces_count}{self.sub_expression.to_solidity()}{self.operator}"
            )


class BinaryOperation(ExpressionBase):
    operator: str
    left_expression: Expression = Field(alias="leftExpression")
    right_expression: Expression = Field(alias="rightExpression")
    common_type: TypeDescriptions = Field(alias="commonType")
    function: Optional[int] = Field(default=None)
    node_type: typing.Literal[NodeType.BINARY_OPERATION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.left_expression.to_solidity()} {self.operator} {self.right_expression.to_solidity()}"
        )


class FunctionCall(ExpressionBase):
    expression: Expression
    names: List[str]
    name_locations: List[str] = Field(alias="nameLocations")
    arguments: List[Expression]
    try_call: bool = Field(alias="tryCall")
    kind: Optional[str] = Field(default=None)
    node_type: typing.Literal[NodeType.FUNCTION_CALL] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        arguments = [arg.to_solidity() for arg in self.arguments]
        if len(self.names) > 0:
            arguments = [f"{name}: {arg}" for name, arg in zip(self.names, arguments)]
            arguments_str = f"{{{', '.join(arguments)}}}"
        else:
            arguments_str = ", ".join(arguments)
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.expression.to_solidity()}({arguments_str})"
        )


class FunctionCallOptions(ExpressionBase):
    expression: Expression
    names: List[str]
    options: List[Expression]
    node_type: typing.Literal[NodeType.FUNCTION_CALL_OPTIONS] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        options = [
            f"{name}: {option.to_solidity()}"
            for name, option in zip(self.names, self.options)
        ]
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.expression.to_solidity()}{{{' ,'.join(options)}}}"
        )


class NewExpression(ExpressionBase):
    type_name: TypeName = Field(alias="typeName")
    node_type: typing.Literal[NodeType.NEW_EXPRESSION] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}new {self.type_name.to_solidity()}"
        )


class MemberAccess(ExpressionBase):
    member_name: str = Field(alias="memberName")
    member_location: str = Field(alias="memberLocation")
    expression: Expression
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )
    node_type: typing.Literal[NodeType.MEMBER_ACCESS] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.expression.to_solidity()}.{self.member_name}"
        )


class IndexAccess(ExpressionBase):
    base_expression: Expression = Field(alias="baseExpression")
    index_expression: Optional[Expression] = Field(
        default=None, alias="indexExpression"
    )
    node_type: typing.Literal[NodeType.INDEX_ACCESS] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.base_expression.to_solidity()}"
            + f"[{self.index_expression.to_solidity() if self.index_expression else ''}]"
        )


class IndexRangeAccess(ExpressionBase):
    base_expression: Expression = Field(alias="baseExpression")
    start_expression: Optional[Expression] = Field(
        default=None, alias="startExpression"
    )
    end_expression: Optional[Expression] = Field(default=None, alias="endExpression")
    node_type: typing.Literal[NodeType.INDEX_RANGE_ACCESS] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.base_expression.to_solidity()}"
            + f"[{self.start_expression.to_solidity()}:{self.end_expression.to_solidity()}]"
        )


class Identifier(TypeBase):
    name: str
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )
    overloaded_declarations: Optional[List[int]] = Field(
        default=None, alias="overloadedDeclarations"
    )
    node_type: typing.Literal[NodeType.IDENTIFIER] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        return super().to_solidity(spaces_count) + f"{' ' * spaces_count}{self.name}"


class ElementaryTypeNameExpression(ExpressionBase):
    type_name: ElementaryTypeName = Field(alias="typeName")
    node_type: typing.Literal[NodeType.ELEMENTARY_TYPE_NAME_EXPRESSION] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0):
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.type_name.to_solidity()}"
        )


class Literal(ExpressionBase):
    kind: Optional[str] = Field(default=None)
    value: str
    hex_value: str = Field(alias="hexValue")
    subdenomination: Optional[str] = Field(default=None)
    node_type: typing.Literal[NodeType.LITERAL] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0):
        subdenomination = f" {self.subdenomination}" if self.subdenomination else ""
        if self.kind == "string":
            return f"{' ' * spaces_count}{repr(self.value)}{subdenomination}"
        return (
            super().to_solidity(spaces_count)
            + f"{' ' * spaces_count}{self.value}{subdenomination}"
        )


class StructuredDocumentation(NodeBase):
    text: str  ## TODO CHECK THIS
