from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp
import math
import re
import os
import logging
from typing import Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Calculator API", description="A calculator with AI-powered and SymPy fallback mathematical operations")

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
    method_used: str  # "ai" or "sympy"
    ai_available: bool

# Initialize Gemini AI client
try:
    from google import genai

    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        client = genai.Client(api_key=gemini_api_key)
        model_id = "gemini-1.5-flash-8b"  # Using free alternative model
        ai_available = True
        logger.info("Gemini AI initialized successfully")
    else:
        ai_available = False
        logger.warning("GEMINI_API_KEY not found in environment variables")
except ImportError:
    ai_available = False
    logger.warning("google-genai package not installed")
except Exception as e:
    ai_available = False
    logger.error(f"Failed to initialize Gemini AI: {e}")

def evaluate_with_ai(expression: str) -> Union[float, str]:
    """
    Evaluate mathematical expressions using Gemini AI
    """
    try:
        if not ai_available:
            raise Exception("AI service not available")

        # Create a prompt for mathematical evaluation
        prompt = f"""
        You are a precise mathematical calculator. Evaluate this expression exactly:

        {expression}

        CRITICAL REQUIREMENTS:
        - Use radians for all trigonometric functions (sin, cos, tan)
        - Use natural logarithm for ln() and base-10 for log()
        - Return ONLY the final numerical result as a decimal number
        - Be precise to at least 4 decimal places
        - If invalid, return "Error: [reason]"

        Calculate this step by step and return only the final number.
        """

        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config={
                "temperature": 0.1,  # Low temperature for consistent mathematical results
                "max_output_tokens": 100
            }
        )

        # Extract the result from the response
        if response.candidates and len(response.candidates) > 0:
            result_text = response.candidates[0].content.parts[0].text.strip()
            logger.info(f"AI raw response: '{result_text}'")  # Debug: see full AI response

            # Try to parse as float
            try:
                # Remove any extra text and extract number
                import re
                number_match = re.search(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)', result_text)
                if number_match:
                    parsed_result = float(number_match.group())
                    rounded_result = round(parsed_result, 4)  # Round AI results to 4 decimals too
                    logger.info(f"AI parsed result: {parsed_result}, rounded: {rounded_result}")
                    return rounded_result
                else:
                    return f"AI Error: Could not extract numerical result from: {result_text}"
            except ValueError:
                return f"AI Error: Non-numerical result: {result_text}"
        else:
            return "AI Error: No response generated"

    except Exception as e:
        logger.error(f"AI evaluation failed: {e}")
        return f"AI Error: {str(e)}"

def safe_eval_expression(expression: str) -> Union[float, str]:
    """
    Safely evaluate mathematical expressions using SymPy (fallback method)
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

            # Evaluate the expression and round to 4 decimal places
            result = float(parsed_expr.evalf())
            rounded_result = round(result, 4)

            return rounded_result

        except (ValueError, TypeError, sp.SympifyError) as e:
            return f"SymPy Error: Invalid mathematical expression - {str(e)}"

    except Exception as e:
        return f"SymPy Error: Could not evaluate expression - {str(e)}"

@app.get("/")
async def root():
    return {
        "message": "AI Calculator API is running",
        "ai_available": ai_available,
        "fallback": "SymPy mathematical engine"
    }

@app.post("/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    """
    Calculate mathematical expressions using AI first, then SymPy fallback
    Supports basic operations: +, -, *, /, **
    Advanced functions: sin, cos, tan, sqrt, log, ln, exp, abs
    Constants: pi, e
    """
    try:
        method_used = "sympy"  # Default fallback
        result = None

        # Try AI first if available
        if ai_available:
            logger.info(f"Attempting AI evaluation for: {request.expression}")
            ai_result = evaluate_with_ai(request.expression)

            # Also get SymPy result for verification
            sympy_result = safe_eval_expression(request.expression)

            # Check if AI result is valid and close to SymPy result
            if isinstance(ai_result, (int, float)) and isinstance(sympy_result, (int, float)):
                # If results are close (within 0.1% or 0.001 absolute), use AI
                diff = abs(ai_result - sympy_result)
                relative_diff = diff / max(abs(sympy_result), 1) if sympy_result != 0 else diff

                if relative_diff < 0.001 or diff < 0.001:
                    result = ai_result
                    method_used = "ai"
                    logger.info(f"AI evaluation verified: {result}")
                else:
                    result = sympy_result
                    method_used = "sympy"
                    logger.warning(f"AI result {ai_result} differs from SymPy {sympy_result}, using SymPy")
            else:
                # If AI result is invalid, use SymPy
                if isinstance(sympy_result, (int, float)):
                    result = sympy_result
                    method_used = "sympy"
                    logger.warning(f"AI evaluation failed: {ai_result}, using SymPy")
                else:
                    result = ai_result  # Return AI error if SymPy also failed
                    method_used = "ai"

        # Fallback to SymPy if AI unavailable
        if result is None:
            logger.info(f"Using SymPy fallback for: {request.expression}")
            result = safe_eval_expression(request.expression)
            method_used = "sympy"

        return CalculationResponse(
            result=result,
            original_expression=request.expression,
            method_used=method_used,
            ai_available=ai_available
        )
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI Calculator API is operational",
        "ai_available": ai_available,
        "fallback_available": True
    }

@app.get("/ai-status")
async def ai_status():
    """Check AI availability and configuration"""
    return {
        "ai_available": ai_available,
        "gemini_api_key_configured": bool(os.getenv('GEMINI_API_KEY')),
        "fallback_method": "SymPy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)