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
        model_id = "gemini-1.5-flash"  # Using stable model
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
        Please evaluate the following mathematical expression and return ONLY the numerical result:

        Expression: {expression}

        Rules:
        - If the expression contains trigonometric functions, use radians
        - Return only the final numerical answer as a decimal number
        - If invalid, respond with "Error: [brief description]"

        Calculate: {expression}
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

            # Try to parse as float
            try:
                # Remove any extra text and extract number
                import re
                number_match = re.search(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)', result_text)
                if number_match:
                    return float(number_match.group())
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

            # Evaluate the expression
            result = float(parsed_expr.evalf())

            return result

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

            # Check if AI result is valid (not an error message)
            if isinstance(ai_result, (int, float)) or (isinstance(ai_result, str) and not ai_result.startswith("AI Error:")):
                result = ai_result
                method_used = "ai"
                logger.info(f"AI evaluation successful: {result}")
            else:
                logger.warning(f"AI evaluation failed: {ai_result}")

        # Fallback to SymPy if AI failed or unavailable
        if result is None or (isinstance(result, str) and result.startswith("AI Error:")):
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