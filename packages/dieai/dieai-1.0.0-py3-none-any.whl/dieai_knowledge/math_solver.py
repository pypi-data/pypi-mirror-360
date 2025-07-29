"""
Math Solver Module
Advanced mathematical problem solving and computation
"""
import re
import math
from typing import Union, Dict, List, Optional, Any

class MathSolver:
    """
    Mathematical problem solver with support for various mathematical operations
    """
    
    def __init__(self):
        """Initialize math solver"""
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': (1 + math.sqrt(5)) / 2,  # Golden ratio
            'sqrt2': math.sqrt(2),
            'sqrt3': math.sqrt(3),
        }
    
    def solve_equation(self, equation: str) -> Dict[str, Any]:
        """
        Solve mathematical equations
        Supports basic arithmetic, algebra, and some calculus
        """
        try:
            # Clean the equation
            equation = equation.replace(' ', '').lower()
            
            # Check for different equation types
            if '=' in equation:
                return self._solve_with_equals(equation)
            else:
                # Just evaluate the expression
                result = self.evaluate(equation)
                return {
                    'result': result,
                    'equation': equation,
                    'type': 'evaluation'
                }
        
        except Exception as e:
            return {
                'error': str(e),
                'equation': equation,
                'type': 'error'
            }
    
    def _solve_with_equals(self, equation: str) -> Dict[str, Any]:
        """Solve equations with equals sign"""
        left, right = equation.split('=', 1)
        
        # Simple linear equation solving (ax + b = c)
        if 'x' in left and 'x' not in right:
            return self._solve_linear(left, right)
        elif 'x' in right and 'x' not in left:
            return self._solve_linear(right, left)
        else:
            # Try to evaluate both sides
            left_val = self.evaluate(left)
            right_val = self.evaluate(right)
            return {
                'left': left_val,
                'right': right_val,
                'equal': abs(left_val - right_val) < 1e-10,
                'equation': equation,
                'type': 'comparison'
            }
    
    def _solve_linear(self, var_side: str, const_side: str) -> Dict[str, Any]:
        """Solve linear equations of form ax + b = c"""
        try:
            # Parse the variable side (ax + b format)
            # This is a simplified parser for basic linear equations
            const_val = self.evaluate(const_side)
            
            # Extract coefficient and constant from variable side
            # Handle cases like: 2x+3, 3x-5, x+7, x-2, 5x, x
            var_side = var_side.replace('-', '+-')
            terms = var_side.split('+')
            
            coefficient = 0
            constant = 0
            
            for term in terms:
                term = term.strip()
                if not term:
                    continue
                
                if 'x' in term:
                    # Extract coefficient
                    coef_str = term.replace('x', '')
                    if coef_str == '' or coef_str == '+':
                        coefficient += 1
                    elif coef_str == '-':
                        coefficient -= 1
                    else:
                        coefficient += float(coef_str)
                else:
                    # Constant term
                    if term:
                        constant += float(term)
            
            # Solve: coefficient * x + constant = const_val
            # x = (const_val - constant) / coefficient
            if coefficient == 0:
                return {
                    'error': 'No variable term found or coefficient is zero',
                    'type': 'error'
                }
            
            x_value = (const_val - constant) / coefficient
            
            return {
                'variable': 'x',
                'value': x_value,
                'equation': f"{var_side} = {const_side}",
                'solution': f"x = {x_value}",
                'type': 'linear_solution'
            }
            
        except Exception as e:
            return {
                'error': f"Error solving linear equation: {str(e)}",
                'type': 'error'
            }
    
    def evaluate(self, expression: str) -> float:
        """
        Safely evaluate mathematical expressions
        """
        # Replace constants
        expr = expression.lower()
        for const_name, const_value in self.constants.items():
            expr = expr.replace(const_name, str(const_value))
        
        # Replace mathematical functions
        expr = self._replace_functions(expr)
        
        # Use eval carefully with restricted globals
        allowed_names = {
            "__builtins__": {},
            "abs": abs,
            "pow": pow,
            "round": round,
            "min": min,
            "max": max,
            "math": math,
        }
        
        try:
            result = eval(expr, allowed_names)
            return float(result)
        except:
            raise ValueError(f"Cannot evaluate expression: {expression}")
    
    def _replace_functions(self, expr: str) -> str:
        """Replace mathematical function names with Python equivalents"""
        replacements = {
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'asin': 'math.asin',
            'acos': 'math.acos',
            'atan': 'math.atan',
            'sinh': 'math.sinh',
            'cosh': 'math.cosh',
            'tanh': 'math.tanh',
            'log': 'math.log',
            'ln': 'math.log',
            'log10': 'math.log10',
            'sqrt': 'math.sqrt',
            'exp': 'math.exp',
            'floor': 'math.floor',
            'ceil': 'math.ceil',
            'factorial': 'math.factorial',
        }
        
        for func, replacement in replacements.items():
            expr = re.sub(r'\b' + func + r'\b', replacement, expr)
        
        return expr
    
    def solve_quadratic(self, a: float, b: float, c: float) -> Dict[str, Any]:
        """
        Solve quadratic equation ax² + bx + c = 0
        """
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            # Two real solutions
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            return {
                'solutions': [x1, x2],
                'discriminant': discriminant,
                'type': 'two_real_solutions',
                'equation': f"{a}x² + {b}x + {c} = 0"
            }
        elif discriminant == 0:
            # One solution
            x = -b / (2*a)
            return {
                'solutions': [x],
                'discriminant': discriminant,
                'type': 'one_solution',
                'equation': f"{a}x² + {b}x + {c} = 0"
            }
        else:
            # Complex solutions
            real_part = -b / (2*a)
            imag_part = math.sqrt(-discriminant) / (2*a)
            return {
                'solutions': [
                    complex(real_part, imag_part),
                    complex(real_part, -imag_part)
                ],
                'discriminant': discriminant,
                'type': 'complex_solutions',
                'equation': f"{a}x² + {b}x + {c} = 0"
            }
    
    def geometry_calculator(self, shape: str, **kwargs) -> Dict[str, Any]:
        """
        Calculate geometric properties for various shapes
        """
        shape = shape.lower()
        
        if shape == 'circle':
            radius = kwargs.get('radius', kwargs.get('r'))
            if radius:
                return {
                    'shape': 'circle',
                    'radius': radius,
                    'area': math.pi * radius**2,
                    'circumference': 2 * math.pi * radius,
                    'diameter': 2 * radius
                }
        
        elif shape == 'rectangle':
            length = kwargs.get('length', kwargs.get('l'))
            width = kwargs.get('width', kwargs.get('w'))
            if length and width:
                return {
                    'shape': 'rectangle',
                    'length': length,
                    'width': width,
                    'area': length * width,
                    'perimeter': 2 * (length + width)
                }
        
        elif shape == 'triangle':
            base = kwargs.get('base', kwargs.get('b'))
            height = kwargs.get('height', kwargs.get('h'))
            if base and height:
                return {
                    'shape': 'triangle',
                    'base': base,
                    'height': height,
                    'area': 0.5 * base * height
                }
        
        elif shape == 'sphere':
            radius = kwargs.get('radius', kwargs.get('r'))
            if radius:
                return {
                    'shape': 'sphere',
                    'radius': radius,
                    'volume': (4/3) * math.pi * radius**3,
                    'surface_area': 4 * math.pi * radius**2
                }
        
        return {'error': f"Unsupported shape '{shape}' or missing parameters"}
    
    def statistics(self, data: List[float]) -> Dict[str, float]:
        """
        Calculate statistical measures for a dataset
        """
        if not data:
            return {'error': 'Empty dataset'}
        
        n = len(data)
        sorted_data = sorted(data)
        
        # Mean
        mean = sum(data) / n
        
        # Median
        if n % 2 == 0:
            median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            median = sorted_data[n//2]
        
        # Mode (most frequent value)
        from collections import Counter
        counts = Counter(data)
        mode_count = max(counts.values())
        modes = [k for k, v in counts.items() if v == mode_count]
        mode = modes[0] if len(modes) == 1 else modes
        
        # Variance and standard deviation
        variance = sum((x - mean)**2 for x in data) / n
        std_dev = math.sqrt(variance)
        
        # Range
        data_range = max(data) - min(data)
        
        return {
            'count': n,
            'mean': mean,
            'median': median,
            'mode': mode,
            'variance': variance,
            'standard_deviation': std_dev,
            'range': data_range,
            'min': min(data),
            'max': max(data)
        }
    
    def factorial(self, n: int) -> int:
        """Calculate factorial of n"""
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        return math.factorial(n)
    
    def fibonacci(self, n: int) -> List[int]:
        """Generate Fibonacci sequence up to n terms"""
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        
        return fib
    
    def prime_factors(self, n: int) -> List[int]:
        """Find prime factors of a number"""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    def gcd(self, a: int, b: int) -> int:
        """Greatest Common Divisor using Euclidean algorithm"""
        while b:
            a, b = b, a % b
        return a
    
    def lcm(self, a: int, b: int) -> int:
        """Least Common Multiple"""
        return abs(a * b) // self.gcd(a, b)