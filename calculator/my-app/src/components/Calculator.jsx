// This tells Next.js this component runs on the client side (browser)
'use client';

import { useState } from 'react';

export default function Calculator() {
  // STATE MANAGEMENT: These track what's displayed and what's being calculated
  const [display, setDisplay] = useState('0');        // What user sees on screen
  const [expression, setExpression] = useState('');   // The actual math expression being built
  const [isResult, setIsResult] = useState(false);    // Whether we just showed a result (affects next input behavior)

  // HANDLER FUNCTIONS: These handle different types of button presses

  // Handles number button presses (0-9)
  const handleNumber = (num) => {
    if (display === '0' || isResult) {
      // If display shows 0 or we just calculated a result, replace it
      setDisplay(num);
      setExpression(num);
      setIsResult(false);
    } else {
      // Otherwise, append the number to what's already there
      setDisplay(display + num);
      setExpression(expression + num);
    }
  };

  // Handles operator button presses (+, -, *, /, etc.)
  const handleOperator = (op) => {
    if (isResult) {
      // If we just showed a result, start new expression with that result
      setExpression(display + op);
      setDisplay(display + op);
      setIsResult(false);
    } else if (display === '0') {
      // If display shows 0, replace it with the operator
      setDisplay(op);
      setExpression(op);
    } else {
      // Otherwise, add operator to current expression
      setExpression(expression + op);
      setDisplay(display + op);
    }
  };

  // Handles function button presses (sin, cos, sqrt, etc.)
  const handleFunction = (func) => {
    if (isResult) {
      // If we just showed a result, apply function to that result
      setExpression(`${func}(${display})`);
      setDisplay(`${func}(${display})`);
      setIsResult(false);
    } else if (display === '0') {
      // If display shows 0, replace it with the function
      setDisplay(func + '(');
      setExpression(func + '(');
    } else {
      // Otherwise, add function to current expression
      setExpression(expression + func + '(');
      setDisplay(display + func + '(');
    }
  };

  // Clears everything back to starting state
  const handleClear = () => {
    setDisplay('0');
    setExpression('');
    setIsResult(false);
  };

  // Deletes the last character entered
  const handleDelete = () => {
    if (display.length > 1) {
      setDisplay(display.slice(0, -1));
      setExpression(expression.slice(0, -1));
    } else {
      setDisplay('0');
      setExpression('');
    }
  };

  // Sends the expression to our Python backend for calculation
  const handleCalculate = async () => {
    try {
      // Convert display symbols to math symbols the backend understands
      let calcExpression = (expression || display)
        .replace(/×/g, '*')    // × becomes *
        .replace(/÷/g, '/')    // ÷ becomes /
        .replace(/π/g, 'pi');  // π becomes pi

      // Send HTTP POST request to our FastAPI backend
      const response = await fetch('http://localhost:8000/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ expression: calcExpression }),
      });

      const data = await response.json();

      // Handle the response
      if (response.ok) {
        if (typeof data.result === 'number') {
          setDisplay(data.result.toString());
          setIsResult(true);  // Mark that we're showing a result
        } else {
          setDisplay(data.result);  // This would be an error message
          setIsResult(true);
        }
      } else {
        setDisplay('Error');
        setIsResult(true);
      }
    } catch (error) {
      // If we can't connect to the backend
      setDisplay('Connection Error');
      setIsResult(true);
    }
  };

  // REUSABLE UI COMPONENTS: These create the visual elements

  // Creates a grid container for buttons
  const ButtonGrid = ({ children, className = "" }) => (
    <div className={`grid gap-2 ${className}`}>{children}</div>
  );

  // Creates individual calculator buttons with different styles
  const CalcButton = ({ onClick, children, className = "", variant = "default" }) => {
    const baseClasses = "h-12 rounded-lg font-medium transition-colors duration-200 active:scale-95";

    // Different color schemes for different button types
    const variants = {
      default: "bg-gray-200 hover:bg-gray-300 text-gray-800",    // Number buttons
      operator: "bg-blue-500 hover:bg-blue-600 text-white",      // +, -, *, / buttons
      function: "bg-green-500 hover:bg-green-600 text-white text-sm", // sin, cos, etc.
      equals: "bg-orange-500 hover:bg-orange-600 text-white",    // = button
      clear: "bg-red-500 hover:bg-red-600 text-white",           // Clear/Delete buttons
    };

    return (
      <button
        onClick={onClick}
        className={`${baseClasses} ${variants[variant]} ${className}`}
      >
        {children}
      </button>
    );
  };

  // THE USER INTERFACE: This creates all the visual elements
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      {/* Center the calculator on screen */}
      <div className="max-w-md mx-auto">
        {/* Calculator main body - white rounded card */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          {/* Calculator title */}
          <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Scientific Calculator
          </h1>

          {/* DISPLAY SCREEN: Shows current expression and result */}
          <div className="bg-gray-900 rounded-lg p-4 mb-6">
            <div className="text-right">
              {/* Top line: shows the expression being built (smaller, gray) */}
              <div className="text-sm text-gray-400 h-6 overflow-hidden">
                {expression || '\u00A0'}  {/* \u00A0 is a non-breaking space to maintain height */}
              </div>
              {/* Bottom line: shows current display (larger, white) */}
              <div className="text-2xl font-mono text-white break-all">
                {display}
              </div>
            </div>
          </div>

          {/* SCIENTIFIC FUNCTION BUTTONS: First row - trig and log functions */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleFunction('sin')} variant="function">sin</CalcButton>
            <CalcButton onClick={() => handleFunction('cos')} variant="function">cos</CalcButton>
            <CalcButton onClick={() => handleFunction('tan')} variant="function">tan</CalcButton>
            <CalcButton onClick={() => handleFunction('log')} variant="function">log</CalcButton>
          </ButtonGrid>

          {/* SCIENTIFIC FUNCTION BUTTONS: Second row - sqrt, power, exp, ln */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleFunction('sqrt')} variant="function">√</CalcButton>
            <CalcButton onClick={() => handleOperator('**')} variant="function">x^y</CalcButton>
            <CalcButton onClick={() => handleFunction('exp')} variant="function">exp</CalcButton>
            <CalcButton onClick={() => handleFunction('ln')} variant="function">ln</CalcButton>
          </ButtonGrid>

          {/* CONTROL BUTTONS: Clear, delete, parentheses */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={handleClear} variant="clear">AC</CalcButton>        {/* All Clear */}
            <CalcButton onClick={handleDelete} variant="clear">DEL</CalcButton>      {/* Delete last character */}
            <CalcButton onClick={() => handleOperator('(')} variant="operator">(</CalcButton>  {/* Open parenthesis */}
            <CalcButton onClick={() => handleOperator(')')} variant="operator">)</CalcButton>  {/* Close parenthesis */}
          </ButtonGrid>

          {/* NUMBER PAD: Row 7-8-9 and division */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('7')}>7</CalcButton>
            <CalcButton onClick={() => handleNumber('8')}>8</CalcButton>
            <CalcButton onClick={() => handleNumber('9')}>9</CalcButton>
            <CalcButton onClick={() => handleOperator('/')} variant="operator">÷</CalcButton>
          </ButtonGrid>

          {/* NUMBER PAD: Row 4-5-6 and multiplication */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('4')}>4</CalcButton>
            <CalcButton onClick={() => handleNumber('5')}>5</CalcButton>
            <CalcButton onClick={() => handleNumber('6')}>6</CalcButton>
            <CalcButton onClick={() => handleOperator('*')} variant="operator">×</CalcButton>
          </ButtonGrid>

          {/* NUMBER PAD: Row 1-2-3 and subtraction */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('1')}>1</CalcButton>
            <CalcButton onClick={() => handleNumber('2')}>2</CalcButton>
            <CalcButton onClick={() => handleNumber('3')}>3</CalcButton>
            <CalcButton onClick={() => handleOperator('-')} variant="operator">-</CalcButton>
          </ButtonGrid>

          {/* NUMBER PAD: Row 0 (spans 2 columns), decimal point, addition */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('0')} className="col-span-2">0</CalcButton>  {/* 0 button takes up 2 spaces */}
            <CalcButton onClick={() => handleOperator('.')}>.</CalcButton>
            <CalcButton onClick={() => handleOperator('+')} variant="operator">+</CalcButton>
          </ButtonGrid>

          {/* FINAL ROW: Pi constant and equals button */}
          <ButtonGrid className="grid-cols-2 gap-4">
            <CalcButton onClick={() => handleOperator('*pi')} variant="function">π</CalcButton>  {/* Multiplies by pi */}
            <CalcButton onClick={handleCalculate} variant="equals">=</CalcButton>                {/* Calculate result */}
          </ButtonGrid>
        </div>
      </div>
    </div>
  );
}