import math
import re
import json


def calculate(formula: str, variables: dict[str, float | int] | None = None) -> float | int | str:
    """
    Evaluate a mathematical formula with given variables.
    
    Args:
        formula: Mathematical expression string (e.g., "2*x + 3*y - 1", "sin(2 * PI / 3) / sqrt(2)"...).
            Constants are: PI, E, TAU, INF, NAN.
            Floating-point is expressed with dots `.`.
        variables: Dictionary mapping variable names to their numeric values; must be a JSON object
    
    Returns:
        The calculated result as float or int in case of success
        An error message as string in case of failure
    """
    
    # Variables validation
    if not variables:
        variables = {}
    if isinstance(variables, str):
        variables = json.loads(variables)

    # Validate that all variables are numeric
    for var_name, var_value in variables.items():
        if not isinstance(var_value, (int, float)):
            return f"Variable '{var_name}' must be numeric, got {type(var_value).__name__}"
    
    # Create a safe namespace for evaluation
    safe_dict = {
        # Math constants
        'PI': math.pi,
        'E': math.e,
        'TAU': math.tau,
        'INF': math.inf,
        'NAN': math.nan,
        
        # Basic math functions
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,
        
        # Math module functions
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'asinh': math.asinh,
        'acosh': math.acosh,
        'atanh': math.atanh,
        'sqrt': math.sqrt,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'exp': math.exp,
        'floor': math.floor,
        'ceil': math.ceil,
        'trunc': math.trunc,
        'degrees': math.degrees,
        'radians': math.radians,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'lcm': math.lcm,
        'fmod': math.fmod,
        'remainder': math.remainder,
        'copysign': math.copysign,
        'fabs': math.fabs,
        'isfinite': math.isfinite,
        'isinf': math.isinf,
        'isnan': math.isnan,
        
        # Add user variables
        **variables
    }
    
    # Powers substitution
    formula = formula.replace("^", "**")
    formula = formula.replace("²", "**2")

    # Security check: ensure the formula only contains allowed characters
    # Allow letters, numbers, operators, parentheses, dots, and underscores
    allowed_pattern = re.compile(r'^[a-zA-Z0-9+\-*/().,_\s]+$')
    if not allowed_pattern.match(formula):
        return "Formula contains invalid characters. Only alphanumeric characters, operators (+, -, *, /), parentheses, dots, and underscores are allowed."
    
    # Check for potentially dangerous operations
    dangerous_patterns = [
        '__', 'import', 'exec', 'eval', 'open', 'file', 'input', 'raw_input',
        'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr', 'delattr',
        'hasattr', 'callable', 'compile', 'execfile', 'reload'
    ]
    
    formula_lower = formula.lower()
    for pattern in dangerous_patterns:
        if pattern in formula_lower:
            return f"Formula contains potentially dangerous operation: {pattern}"
    
    try:
        # Evaluate the expression
        result = eval(formula, {"__builtins__": {}}, safe_dict)
        
        # Ensure result is numeric
        if not isinstance(result, (int, float)):
            return f"Formula evaluation resulted in non-numeric type: {type(result).__name__}"
        
        # Return int if the result is a whole number, otherwise float
        if isinstance(result, float) and result.is_integer():
            return int(result)
        else:
            return result
            
    except NameError as e:
        # Extract variable name from error message for better error reporting
        error_msg = str(e)
        if "name" in error_msg and "is not defined" in error_msg:
            var_name = error_msg.split("'")[1] if "'" in error_msg else "unknown"
            return f"Variable '{var_name}' is not defined in the variables dictionary"
        else:
            return f"Undefined variable in formula: {error_msg}"
    
    except ZeroDivisionError:
        return "Division by zero occurred in the formula"
    
    except SyntaxError as e:
        return f"Invalid formula syntax: {e}"
    
    except (TypeError, ValueError) as e:
        return f"Error evaluating formula: {e}"


# Example usage and tests
if __name__ == "__main__":
    # Test cases
    test_cases = [
        # Basic arithmetic
        ("2*x + 3*y - 1", {"x": 5, "y": 2}, 15),
        
        # Trigonometric functions
        ("sin(pi/2)", {}, 1.0),
        ("cos(0)", {}, 1),
        
        # Complex expression
        ("sqrt(x**2 + y**2)", {"x": 3, "y": 4}, 5.0),
        
        # Using math constants
        ("2 * pi * r", {"r": 5}, 2 * math.pi * 5),
        
        # Mixed operations
        ("log(e**x) + sqrt(y)", {"x": 2, "y": 9}, 5.0),
        
        # Expression that should return int
        ("x + y", {"x": 3, "y": 7}, 10),
        
        # Expression that should return float
        ("x / y", {"x": 7, "y": 2}, 3.5),
    ]
    
    print("Running test cases...")
    for i, (formula, variables, expected) in enumerate(test_cases, 1):
        try:
            result = calculate.func(formula, variables)
            success = abs(result - expected) < 1e-10 if isinstance(expected, float) else result == expected
            status = "✓" if success else "✗"
            print(f"Test {i}: {status} calculate('{formula}', {variables}) = {result}")
            if not success:
                print(f"   Expected: {expected}")
        except Exception as e:
            print(f"Test {i}: ✗ calculate('{formula}', {variables}) raised {type(e).__name__}: {e}")
    
    print("\nTesting error cases...")
    error_cases = [
        # Missing variable
        ("x + y", {"x": 1}, NameError),
        
        # Invalid syntax
        ("2 +", {}, SyntaxError),
        
        # Division by zero
        ("1/z", {"z": 0}, ZeroDivisionError),
        
        # Invalid characters
        ("import os", {}, SyntaxError),
        
        # Non-numeric variable
        ("x + 1", {"x": "hello"}, TypeError),
    ]
    
    for i, (formula, variables, expected_error) in enumerate(error_cases, 1):
        try:
            result = calculate.func(formula, variables)
            print(f"Error test {i}: ✗ Expected {expected_error.__name__} but got result: {result}")
        except expected_error:
            print(f"Error test {i}: ✓ Correctly raised {expected_error.__name__}")
        except Exception as e:
            print(f"Error test {i}: ✗ Expected {expected_error.__name__} but got {type(e).__name__}: {e}")
