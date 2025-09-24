from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp
import math
import re
from typing import Union

app = FastAPI(title="Calculator API", description="A calculator with basic and advanced mathematical operations")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalculationRequest(BaseModel):
    expression: str

class CalculationResponse(BaseModel):
    result: Union[float, str]
    original_expression: str

def safe_eval_expression(expression: str) -> Union[float, str]:
    """
    Safely evaluate mathematical expressions using SymPy
    Supports: +, -, *, /, **, sqrt, sin, cos, tan, log, ln, exp, abs
    """
    try:
        # Clean the expression
        expression = expression.strip()

        # Replace common mathematical notation
        expression = re.sub(r'\blog\(([^)]+)\)', r'log(\1, 10)', expression)  # log(x) -> log(x, 10)
        expression = re.sub(r'\bln\(([^)]+)\)', r'log(\1)', expression)       # ln(x) -> log(x)
        expression = expression.replace('^', '**')            # ^ -> **

        # Create sympy symbols for common constants
        x, y, z = sp.symbols('x y z')

        # Define allowed functions and constants
        allowed_functions = {
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'sqrt': sp.sqrt,
            'log': sp.log,        # can take base as second argument
            'exp': sp.exp,
            'abs': sp.Abs,
            'pi': sp.pi,
            'e': sp.E,
            'factorial': sp.factorial,
            'asin': sp.asin,
            'acos': sp.acos,
            'atan': sp.atan,
        }

        # Parse and evaluate the expression
        try:
            # Use sympify to parse the expression safely
            parsed_expr = sp.sympify(expression, locals=allowed_functions)

            # Evaluate the expression
            result = float(parsed_expr.evalf())

            return result

        except (ValueError, TypeError, sp.SympifyError) as e:
            return f"Error: Invalid mathematical expression - {str(e)}"

    except Exception as e:
        return f"Error: Could not evaluate expression - {str(e)}"

@app.get("/")
async def root():
    return {"message": "Calculator API is running"}

@app.post("/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    """
    Calculate mathematical expressions
    Supports basic operations: +, -, *, /, **
    Advanced functions: sin, cos, tan, sqrt, log, ln, exp, abs
    Constants: pi, e
    """
    try:
        result = safe_eval_expression(request.expression)

        return CalculationResponse(
            result=result,
            original_expression=request.expression
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Calculator API is operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)