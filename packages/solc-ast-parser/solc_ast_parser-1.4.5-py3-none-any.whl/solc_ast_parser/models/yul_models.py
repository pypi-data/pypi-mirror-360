from typing import List, Optional, Union
import typing

from pydantic import Field
from solc_ast_parser.models.base_ast_models import YulBase, YulNodeType

YulExpression = Union[
    "YulFunctionCall", "YulLiteral", "YulIdentifier", "YulBuiltinName"
]

YulStatement = Union[
    "YulExpressionStatement",
    "YulAssignment",
    "YulVariableDeclaration",
    "YulFunctionDefinition",
    "YulIf",
    "YulSwitch",
    "YulForLoop",
    "YulBreak",
    "YulContinue",
    "YulLeave",
    "YulBlock",
]

YulNode = Union["YulBlock", YulStatement, YulExpression]


class YulBlock(YulBase):
    statements: List[YulStatement]
    node_type: typing.Literal[YulNodeType.YUL_BLOCK] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line: bool = False):
        if (
            len(self.statements) == 1
            and not new_line
            and self.statements[0].node_type
            not in [YulNodeType.YUL_BLOCK, YulNodeType.YUL_SWITCH]
        ):
            return f"{{ {self.statements[0].to_solidity()} }}"

        if not self.statements:
            return "{ }"

        statements = "\n".join(
            [statement.to_solidity(spaces_count + 4) for statement in self.statements]
        )
        return f"{{\n{statements}\n{' ' * spaces_count}}}"


class YulTypedName(YulBase):
    name: str
    type: str
    node_type: typing.Literal[YulNodeType.YUL_TYPED_NAME] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.name}"
        )


class YulLiteral(YulBase):
    kind: str
    hex_value: Optional[str] = Field(default=None, alias="hexValue")
    type: str
    value: str
    node_type: typing.Literal[YulNodeType.YUL_LITERAL] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.value}"
        )


class YulIdentifier(YulBase):
    name: str
    node_type: typing.Literal[YulNodeType.YUL_IDENTIFIER] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.name}"
        )


class YulBuiltinName(YulBase):
    name: str
    node_type: typing.Literal[YulNodeType.YUL_BUILTIN_NAME] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.name}"
        )


class YulAssignment(YulBase):
    variable_names: List[YulIdentifier] = Field(alias="variableNames")
    value: Optional[YulExpression] = Field(default=None)
    node_type: typing.Literal[YulNodeType.YUL_ASSIGNMENT] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{', '.join([var.to_solidity() for var in self.variable_names])} := {self.value.to_solidity()}"
        )


class YulFunctionCall(YulBase):
    function_name: YulIdentifier = Field(alias="functionName")
    arguments: List[YulExpression]
    node_type: typing.Literal[YulNodeType.YUL_FUNCTION_CALL] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{self.function_name.to_solidity()}"
            + f"({', '.join([arg.to_solidity() for arg in self.arguments])})"
        )


class YulExpressionStatement(YulBase):
    expression: YulExpression
    node_type: typing.Literal[YulNodeType.YUL_EXPRESSION_STATEMENT] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.expression.to_solidity( spaces_count)}"
        )


class YulVariableDeclaration(YulBase):
    variables: List[YulTypedName]
    value: Optional[YulExpression] = Field(default=None)
    node_type: typing.Literal[YulNodeType.YUL_VARIABLE_DECLARATION] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0, new_line=False):
        value = f" := {self.value.to_solidity()}" if self.value else ""
        variables = ",".join([var.to_solidity() for var in self.variables])
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{variables}{value}"
        )


class YulFunctionDefinition(YulBase):
    name: str
    parameters: List[YulTypedName] = Field(default=None)
    return_variables: List[YulTypedName] = Field(default=None)
    body: YulBlock
    node_type: typing.Literal[YulNodeType.YUL_FUNCTION_DEFINITION] = Field(
        alias="nodeType"
    )

    def to_solidity(self, spaces_count=0, new_line=False):
        parameters = ", ".join([param.to_solidity() for param in self.parameters])
        return_variables = ", ".join(
            [return_variable.to_solidity() for return_variable in self.return_variables]
        )
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}function {self.name}({parameters}) -> {return_variables} {self.body.to_solidity()}"
        )


class YulIf(YulBase):
    condition: YulExpression
    body: YulBlock
    node_type: typing.Literal[YulNodeType.YUL_IF] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}if {self.condition.to_solidity()} {self.body.to_solidity( spaces_count, True)}"
        )


class YulCase(YulBase):
    value: YulExpression | str
    body: YulBlock
    node_type: typing.Literal[YulNodeType.YUL_CASE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}{f'case {self.value.to_solidity() if type(self.value) != str else self.value}' if self.value != 'default' else 'default'} {self.body.to_solidity(spaces_count, new_line=True)}"
        )


class YulSwitch(YulBase):
    expression: YulExpression
    cases: List[YulCase]
    node_type: typing.Literal[YulNodeType.YUL_SWITCH] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        cases = "\n".join([case.to_solidity(spaces_count) for case in self.cases])
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}switch {self.expression.to_solidity()}\n{cases}"
        )


class YulForLoop(YulBase):
    pre: YulBlock
    condition: YulExpression
    post: YulBlock
    body: YulBlock
    node_type: typing.Literal[YulNodeType.YUL_FOR_LOOP] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        pre_arr = []
        for statement in self.pre.statements:
            if statement.node_type == YulNodeType.YUL_VARIABLE_DECLARATION:
                pre_arr.append(f"let {statement.to_solidity()}")
            else:
                pre_arr.append(statement.to_solidity())
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}for {{ {', '.join(pre_arr)} }} {self.condition.to_solidity()} {self.post.to_solidity()} {self.body.to_solidity(spaces_count, True)}"
        )


class YulBreak(YulBase):
    node_type: typing.Literal[YulNodeType.YUL_BREAK] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line) + f"{' ' * spaces_count}break"
        )


class YulContinue(YulBase):
    node_type: typing.Literal[YulNodeType.YUL_CONTINUE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line)
            + f"{' ' * spaces_count}continue"
        )


class YulLeave(YulBase):
    node_type: typing.Literal[YulNodeType.YUL_LEAVE] = Field(alias="nodeType")

    def to_solidity(self, spaces_count=0, new_line=False):
        return (
            super().to_solidity(spaces_count, new_line) + f"{' ' * spaces_count}leave"
        )
