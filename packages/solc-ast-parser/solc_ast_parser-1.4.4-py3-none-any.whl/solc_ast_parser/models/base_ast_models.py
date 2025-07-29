from abc import ABC
import enum
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class NodeType(enum.StrEnum):
    SOURCE_UNIT = "SourceUnit"
    BLOCK = "Block"
    UNCHECKED_BLOCK = "UncheckedBlock"
    PRAGMA_DIRECTIVE = "PragmaDirective"
    CONTRACT_DEFINITION = "ContractDefinition"
    FUNCTION_DEFINITION = "FunctionDefinition"
    FUNCTION_NODE = "FunctionNode"
    VARIABLE_DECLARATION = "VariableDeclaration"
    VARIABLE_DECLARATION_STATEMENT = "VariableDeclarationStatement"
    FUNCTION_CALL = "FunctionCall"
    PARAMETER_LIST = "ParameterList"
    EVENT_DEFINITION = "EventDefinition"
    EMIT_STATEMENT = "EmitStatement"
    ASSIGNMENT = "Assignment"
    BINARY_OPERATION = "BinaryOperation"
    UNARY_OPERATION = "UnaryOperation"
    LITERAL = "Literal"
    IDENTIFIER = "Identifier"
    IDENTIFIER_PATH = "IdentifierPath"
    MEMBER_ACCESS = "MemberAccess"
    INDEX_ACCESS = "IndexAccess"
    INDEX_RANGE_ACCESS = "IndexRangeAccess"
    INLINE_ASSEMBLY = "InlineAssembly"
    TUPLE_EXPRESSION = "TupleExpression"
    EXPRESSION_STATEMENT = "ExpressionStatement"
    RETURN = "Return"
    ELEMENTARY_TYPE_NAME = "ElementaryTypeName"
    USER_DEFINED_TYPE_NAME = "UserDefinedTypeName"
    STRUCT_DEFINITION = "StructDefinition"
    MAPPING = "Mapping"
    ELEMENTARY_TYPE_NAME_EXPRESSION = "ElementaryTypeNameExpression"
    INHERITANCE_SPECIFIER = "InheritanceSpecifier"
    USING_FOR_DIRECTIVE = "UsingForDirective"
    STRUCTURED_DOCUMENTATION = "StructuredDocumentation"
    MODIFIER_DEFINITION = "ModifierDefinition"
    MODIFIER_INVOCATION = "ModifierInvocation"
    ERROR_DEFINITION = "ErrorDefinition"
    PLACEHOLDER_STATEMENT = "PlaceholderStatement"
    IF_STATEMENT = "IfStatement"
    TRY_CATCH_CLAUSE = "TryCatchClause"
    TRY_STATEMENT = "TryStatement"
    FOR_STATEMENT = "ForStatement"
    WHILE_STATEMENT = "WhileStatement"
    CONTINUE = "Continue"
    BREAK = "Break"
    THROW = "Throw"
    REVERT_STATEMENT = "RevertStatement"
    FUNCTION_CALL_OPTIONS = "FunctionCallOptions"
    NEW_EXPRESSION = "NewExpression"
    CONDITIONAL = "Conditional"
    IMPORT_DIRECTIVE = "ImportDirective"
    ENUM_DEFINITION = "EnumDefinition"
    ENUM_VALUE = "EnumValue"
    USER_DEFINED_VALUE_TYPE_DEFINITION = "UserDefinedValueTypeDefinition"
    FUNCTION_TYPE_NAME = "FunctionTypeName"
    ARRAY_TYPE_NAME = "ArrayTypeName"
    OVERRIDE_SPECIFIER = "OverrideSpecifier"
    COMMENT = "Comment"
    MULTILINE_COMMENT = "MultilineComment"


class YulNodeType(enum.StrEnum):
    YUL_BLOCK = "YulBlock"
    YUL_FUNCTION_DEFINITION = "YulFunctionDefinition"
    YUL_VARIABLE_DECLARATION = "YulVariableDeclaration"
    YUL_ASSIGNMENT = "YulAssignment"
    YUL_FUNCTION_CALL = "YulFunctionCall"
    YUL_LITERAL = "YulLiteral"
    YUL_IDENTIFIER = "YulIdentifier"
    YUL_EXPRESSION_STATEMENT = "YulExpressionStatement"
    YUL_IF = "YulIf"
    YUL_FOR_LOOP = "YulForLoop"
    YUL_SWITCH = "YulSwitch"
    YUL_CASE = "YulCase"
    YUL_BREAK = "YulBreak"
    YUL_CONTINUE = "YulContinue"
    YUL_LEAVE = "YulLeave"
    YUL_BUILTIN_NAME = "YulBuiltinName"
    YUL_TYPED_NAME = "YulTypedName"


class TypeDescriptions(BaseModel):
    type_identifier: Optional[str] = Field(default=None, alias="typeIdentifier")
    type_string: Optional[str] = Field(default=None, alias="typeString")


class Comment(BaseModel):
    id: int
    src: str
    node_type: NodeType = Field(alias="nodeType")
    text: str
    is_pure: bool = Field(default=False, alias="isPure")

    def to_solidity(self, spaces_count: int = 0) -> str:
        return f"{' ' * spaces_count}// {self.text}\n"


class MultilineComment(BaseModel):
    id: int
    src: str
    node_type: NodeType = Field(alias="nodeType")
    text: str

    def to_solidity(self, spaces_count: int = 0) -> str:
        return f"{' ' * spaces_count}{self.text}\n"


class Node(ABC):
    def to_solidity(self, spaces_count: int = 0) -> str:
        raise NotImplementedError


class NodeBase(BaseModel, Node):
    model_config = ConfigDict(extra="forbid")

    id: int
    src: str
    node_type: NodeType = Field(alias="nodeType")
    comment: Optional[Comment] = Field(default=None)
    documentation: Optional[str] = Field(default=None)

    def to_solidity(self, spaces_count=0):
        return (
            f"{' ' * spaces_count}/// {self.documentation}\n"
            if self.documentation
            else ""
        )


class YulBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    src: str
    node_type: YulNodeType = Field(alias="nodeType")
    native_src: str = Field(alias="nativeSrc")
    documentation: Optional[str] = Field(default=None)

    def to_solidity(self, spaces_count=0, new_line: bool = False):
        return (
            f"{' ' * spaces_count}/// {self.documentation}\n"
            if self.documentation
            else ""
        )


class TypeBase(NodeBase):
    type_descriptions: Optional[TypeDescriptions] = Field(
        default=None, alias="typeDescriptions"
    )
    argument_types: Optional[List[TypeDescriptions]] = Field(
        default=None, alias="argumentTypes"
    )


class ExpressionBase(TypeBase):
    is_constant: Optional[bool] = Field(default=None, alias="isConstant")
    is_lvalue: Optional[bool] = Field(default=None, alias="isLValue")
    is_pure: Optional[bool] = Field(default=None, alias="isPure")
    lvalue_requested: Optional[bool] = Field(default=None, alias="lValueRequested")
