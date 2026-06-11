import ast
import operator
import math
import re

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
    "factorial": math.factorial,
}

CONSTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
}

WORD_TO_OP = {
    " plus ": "+",
    " minus ": "-",
    " times ": "*",
    " multiplied by ": "*",
    " divided by ": "/",
    " over ": "/",
    " to the power of ": "**",
    " squared": "**2",
    " cubed": "**3",
    " mod ": "%",
}

def normalize(expr):
    expr = expr.strip()

    # Strip natural language prefixes
    for prefix in ("calculate ", "compute ", "evaluate "):
        if expr.lower().startswith(prefix):
            expr = expr[len(prefix):]

    # Replace unicode operators
    expr = expr.replace("×", "*")
    expr = expr.replace("÷", "/")
    expr = expr.replace("−", "-")
    expr = expr.replace("²", "**2")
    expr = expr.replace("³", "**3")

    # Replace word operators
    lower = expr.lower()
    for word, op in WORD_TO_OP.items():
        lower = lower.replace(word, op)
    expr = lower

    # Replace ^ with ** for power
    expr = expr.replace("^", "**")

    # Remove commas in numbers like 1,000
    expr = expr.replace(",", "")

    return expr.strip()

def looks_like_math(expr):
    expr = expr.strip().lower()

    # Strip "what is" prefix and check remainder
    if expr.startswith("what is "):
        remainder = expr[8:].strip()
        # Only math if remainder has digits or operators but no letters
        if any(c.isdigit() for c in remainder) and not any(c.isalpha() for c in remainder):
            expr = remainder
        else:
            return False

    non_math = ("why is ", "why does ", "why do ", "what does ", "how does ")
    if any(expr.startswith(p) for p in non_math):
        return False

    # Natural language math
    if any(expr.startswith(p) for p in ("calculate ", "compute ", "evaluate ")):
        return True

    # Unicode operators
    if any(c in expr for c in "×÷²³"):
        return True

    # Has digits
    if any(c.isdigit() for c in expr):
        return True

    # Has operators
    if any(op in expr for op in "+-*/^%"):
        return True

    # Math functions
    math_funcs = ("sin(", "cos(", "tan(", "sqrt(", "log(", "exp(",
                  "abs(", "floor(", "ceil(", "round(", "factorial(")
    if any(f in expr for f in math_funcs):
        return True

    # Standalone constants
    if re.fullmatch(r'\s*(pi|tau|inf)\s*', expr):
        return True

    # Constants with operators
    if re.search(r'\b(pi|e|tau)\b', expr):
        if any(op in expr for op in "+-*/^%()") or any(c.isdigit() for c in expr):
            return True

    # Word math
    if any(w in expr for w in (" plus ", " minus ", " times ", " divided by ", " multiplied by ")):
        return True

    return False

def evaluate_math(expr):
    expr = normalize(expr)
    try:
        node = ast.parse(expr, mode="eval")
        result = _eval(node.body)
        # Clean up float display
        if isinstance(result, float) and result.is_integer():
            return int(result)
        if isinstance(result, float):
            return round(result, 10)
        return result
    except ZeroDivisionError:
        return "Error: division by zero"
    except ValueError as e:
        return f"Error: {e}"
    except Exception:
        return "Error: invalid expression"

def _eval(node):
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        if node.id in CONSTS:
            return CONSTS[node.id]
        raise ValueError(f"unknown constant '{node.id}'")

    if isinstance(node, ast.BinOp):
        left = _eval(node.left)
        right = _eval(node.right)
        op = type(node.op)
        if op not in OPS:
            raise ValueError("unsupported operator")
        return OPS[op](left, right)

    if isinstance(node, ast.UnaryOp):
        return OPS[type(node.op)](_eval(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("invalid function call")
        fname = node.func.id
        if fname not in FUNCS:
            raise ValueError(f"unknown function '{fname}'")
        args = [_eval(a) for a in node.args]
        return FUNCS[fname](*args)

    raise ValueError("invalid expression")