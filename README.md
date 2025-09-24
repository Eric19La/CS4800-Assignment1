# Scientific Calculator

A full-stack calculator application with a Next.js frontend and FastAPI backend using SymPy for mathematical operations.

## Features

- Basic arithmetic operations (+, -, ×, ÷)
- Advanced mathematical functions:
  - Trigonometric functions (sin, cos, tan)
  - Logarithmic functions (log, ln)
  - Power operations (x^y)
  - Square root (√)
  - Exponential function (exp)
  - Constants (π, e)
  - Parentheses for grouping

## Setup Instructions

### Backend (Python FastAPI)

1. Navigate to the backend directory:

   ```bash
   cd math-backend
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend (Next.js)

1. Navigate to the frontend directory:

   ```bash
   cd my-app
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /calculate` - Calculate mathematical expressions
  - Body: `{"expression": "2+2*sin(pi/2)"}`
  - Response: `{"result": 4.0, "original_expression": "2+2*sin(pi/2)"}`

## Usage Examples

- Basic: `2 + 3 * 4`
- Trigonometry: `sin(pi/2) + cos(0)`
- Logarithms: `log(100) + ln(e)`
- Power: `2**3 + sqrt(16)`
- Complex: `sin(pi/4) * cos(pi/4) + log10(1000)`

## Architecture

- **Frontend**: Next.js with React, Tailwind CSS for styling
- **Backend**: FastAPI with SymPy for mathematical computation
- **Communication**: REST API with JSON payloads
