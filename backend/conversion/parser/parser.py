"""Pine Script parser using Lark grammar."""

from lark import Lark, Transformer, Tree, Token
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import re


class PineASTNode:
    """Base class for Pine AST nodes."""
    pass


class VersionStatement(PineASTNode):
    def __init__(self, version: str):
        self.version = version


class IndicatorStatement(PineASTNode):
    def __init__(self, title: str, args: Dict[str, Any]):
        self.title = title
        self.args = args


class StrategyStatement(PineASTNode):
    def __init__(self, title: str, args: Dict[str, Any]):
        self.title = title
        self.args = args


class InputStatement(PineASTNode):
    def __init__(self, name: str, input_type: str, args: Dict[str, Any]):
        self.name = name
        self.input_type = input_type
        self.args = args


class VariableDeclaration(PineASTNode):
    def __init__(self, name: str, value: Any, var_type: str = "normal"):
        self.name = name
        self.value = value
        self.var_type = var_type  # "var", "varip", or "normal"


class Assignment(PineASTNode):
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value


class StrategyCall(PineASTNode):
    def __init__(self, method: str, args: Dict[str, Any]):
        self.method = method
        self.args = args


class FunctionCall(PineASTNode):
    def __init__(self, namespace: Optional[str], name: str, args: List[Any]):
        self.namespace = namespace
        self.name = name
        self.args = args


class BinaryOp(PineASTNode):
    def __init__(self, left: Any, operator: str, right: Any):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOp(PineASTNode):
    def __init__(self, operator: str, operand: Any):
        self.operator = operator
        self.operand = operand


class TernaryOp(PineASTNode):
    def __init__(self, condition: Any, true_value: Any, false_value: Any):
        self.condition = condition
        self.true_value = true_value
        self.false_value = false_value


class IndexAccess(PineASTNode):
    def __init__(self, series: Any, index: Any):
        self.series = series
        self.index = index


class PineTransformer(Transformer):
    """Transform Lark parse tree to Pine AST nodes."""
    
    def start(self, items):
        return items
    
    def version_statement(self, items):
        return VersionStatement(str(items[0]))
    
    def indicator_statement(self, items):
        title = items[0]
        args = dict(items[1:]) if len(items) > 1 else {}
        return IndicatorStatement(title, args)
    
    def strategy_statement(self, items):
        title = items[0]
        args = dict(items[1:]) if len(items) > 1 else {}
        return StrategyStatement(title, args)
    
    def input_statement(self, items):
        name, input_type = items[0], items[1]
        args = dict(items[2:]) if len(items) > 2 else {}
        return InputStatement(name, input_type, args)
    
    def variable_declaration(self, items):
        if len(items) == 3 and items[0] in ['var', 'varip']:
            return VariableDeclaration(items[1], items[2], items[0])
        else:
            return VariableDeclaration(items[0], items[1])
    
    def assignment(self, items):
        return Assignment(items[0], items[1])
    
    def strategy_call(self, items):
        method = items[0]
        args = dict(items[1:]) if len(items) > 1 else {}
        return StrategyCall(method, args)
    
    def function_call(self, items):
        if len(items) == 3:  # namespace.name(args)
            return FunctionCall(items[0], items[1], items[2])
        else:  # name(args)
            return FunctionCall(None, items[0], items[1])
    
    def ternary(self, items):
        if len(items) == 3:
            return TernaryOp(items[0], items[1], items[2])
        return items[0]
    
    def factor(self, items):
        if len(items) == 2:  # array access
            return IndexAccess(items[0], items[1])
        return items[0]
    
    def argument_list(self, items):
        return items or []
    
    def argument(self, items):
        if len(items) == 2:  # named argument
            return (items[0], items[1])
        return items[0]
    
    # Binary operations
    def logical_or(self, items):
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items)):
            result = BinaryOp(result, 'or', items[i])
        return result
    
    def logical_and(self, items):
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items)):
            result = BinaryOp(result, 'and', items[i])
        return result
    
    def equality(self, items):
        if len(items) == 1:
            return items[0]
        return BinaryOp(items[0], items[1], items[2])
    
    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        return BinaryOp(items[0], items[1], items[2])
    
    def addition(self, items):
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items), 2):
            result = BinaryOp(result, items[i], items[i+1])
        return result
    
    def multiplication(self, items):
        if len(items) == 1:
            return items[0]
        result = items[0]
        for i in range(1, len(items), 2):
            result = BinaryOp(result, items[i], items[i+1])
        return result
    
    def unary(self, items):
        if len(items) == 1:
            return items[0]
        return UnaryOp(items[0], items[1])
    
    # Literals
    def string(self, items):
        return str(items[0])[1:-1]  # Remove quotes
    
    def boolean(self, items):
        return str(items[0]) == "true"
    
    def NUMBER(self, token):
        value = float(token.value)
        return int(value) if value.is_integer() else value
    
    def NAME(self, token):
        return str(token.value)


class PineParser:
    """Pine Script parser."""
    
    def __init__(self):
        grammar_path = Path(__file__).parent / "pine_grammar.lark"
        with open(grammar_path, 'r') as f:
            grammar = f.read()
        
        self.parser = Lark(grammar, parser='lalr')
        self.transformer = PineTransformer()
    
    def parse(self, pine_code: str) -> List[PineASTNode]:
        """Parse Pine Script code into AST nodes."""
        # Preprocess to handle some Pine-specific syntax
        preprocessed = self._preprocess(pine_code)
        
        try:
            tree = self.parser.parse(preprocessed)
            ast_nodes = self.transformer.transform(tree)
            return ast_nodes
        except Exception as e:
            raise ValueError(f"Failed to parse Pine script: {e}")
    
    def _preprocess(self, code: str) -> str:
        """Preprocess Pine code for easier parsing."""
        # Remove Pine-specific decorators and handle some syntax quirks
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Handle some Pine syntax normalization
            line = re.sub(r'\btrue\b', 'true', line)
            line = re.sub(r'\bfalse\b', 'false', line)
            
            lines.append(line)
        
        return '\n'.join(lines)
    
    def parse_file(self, file_path: str) -> List[PineASTNode]:
        """Parse Pine Script file."""
        with open(file_path, 'r') as f:
            code = f.read()
        return self.parse(code)