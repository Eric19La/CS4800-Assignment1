'use client';

import { useState } from 'react';

export default function Calculator() {
  const [display, setDisplay] = useState('0');
  const [expression, setExpression] = useState('');
  const [isResult, setIsResult] = useState(false);

  const handleNumber = (num) => {
    if (display === '0' || isResult) {
      setDisplay(num);
      setExpression(num);
      setIsResult(false);
    } else {
      setDisplay(display + num);
      setExpression(expression + num);
    }
  };

  const handleOperator = (op) => {
    if (isResult) {
      setExpression(display + op);
      setIsResult(false);
    } else {
      setExpression(expression + op);
    }
    setDisplay(display + op);
  };

  const handleFunction = (func) => {
    if (isResult) {
      setExpression(`${func}(${display})`);
      setDisplay(`${func}(${display})`);
      setIsResult(false);
    } else {
      setExpression(expression + func + '(');
      setDisplay(display + func + '(');
    }
  };

  const handleClear = () => {
    setDisplay('0');
    setExpression('');
    setIsResult(false);
  };

  const handleDelete = () => {
    if (display.length > 1) {
      setDisplay(display.slice(0, -1));
      setExpression(expression.slice(0, -1));
    } else {
      setDisplay('0');
      setExpression('');
    }
  };

  const handleCalculate = async () => {
    try {
      const response = await fetch('http://localhost:8000/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ expression: expression || display }),
      });

      const data = await response.json();

      if (response.ok) {
        if (typeof data.result === 'number') {
          setDisplay(data.result.toString());
          setIsResult(true);
        } else {
          setDisplay(data.result);
          setIsResult(true);
        }
      } else {
        setDisplay('Error');
        setIsResult(true);
      }
    } catch (error) {
      setDisplay('Connection Error');
      setIsResult(true);
    }
  };

  const ButtonGrid = ({ children, className = "" }) => (
    <div className={`grid gap-2 ${className}`}>{children}</div>
  );

  const CalcButton = ({ onClick, children, className = "", variant = "default" }) => {
    const baseClasses = "h-12 rounded-lg font-medium transition-colors duration-200 active:scale-95";
    const variants = {
      default: "bg-gray-200 hover:bg-gray-300 text-gray-800",
      operator: "bg-blue-500 hover:bg-blue-600 text-white",
      function: "bg-green-500 hover:bg-green-600 text-white text-sm",
      equals: "bg-orange-500 hover:bg-orange-600 text-white",
      clear: "bg-red-500 hover:bg-red-600 text-white",
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-6">
          <h1 className="text-2xl font-bold text-center text-gray-800 mb-6">
            Scientific Calculator
          </h1>

          {/* Display */}
          <div className="bg-gray-900 rounded-lg p-4 mb-6">
            <div className="text-right">
              <div className="text-sm text-gray-400 h-6 overflow-hidden">
                {expression || '\u00A0'}
              </div>
              <div className="text-2xl font-mono text-white break-all">
                {display}
              </div>
            </div>
          </div>

          {/* Function Buttons */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleFunction('sin')} variant="function">sin</CalcButton>
            <CalcButton onClick={() => handleFunction('cos')} variant="function">cos</CalcButton>
            <CalcButton onClick={() => handleFunction('tan')} variant="function">tan</CalcButton>
            <CalcButton onClick={() => handleFunction('log')} variant="function">log</CalcButton>
          </ButtonGrid>

          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleFunction('sqrt')} variant="function">√</CalcButton>
            <CalcButton onClick={() => handleOperator('**')} variant="function">x^y</CalcButton>
            <CalcButton onClick={() => handleFunction('exp')} variant="function">exp</CalcButton>
            <CalcButton onClick={() => handleFunction('ln')} variant="function">ln</CalcButton>
          </ButtonGrid>

          {/* Main Calculator */}
          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={handleClear} variant="clear">AC</CalcButton>
            <CalcButton onClick={handleDelete} variant="clear">DEL</CalcButton>
            <CalcButton onClick={() => handleOperator('(')} variant="operator">(</CalcButton>
            <CalcButton onClick={() => handleOperator(')')} variant="operator">)</CalcButton>
          </ButtonGrid>

          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('7')}>7</CalcButton>
            <CalcButton onClick={() => handleNumber('8')}>8</CalcButton>
            <CalcButton onClick={() => handleNumber('9')}>9</CalcButton>
            <CalcButton onClick={() => handleOperator('/')} variant="operator">÷</CalcButton>
          </ButtonGrid>

          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('4')}>4</CalcButton>
            <CalcButton onClick={() => handleNumber('5')}>5</CalcButton>
            <CalcButton onClick={() => handleNumber('6')}>6</CalcButton>
            <CalcButton onClick={() => handleOperator('*')} variant="operator">×</CalcButton>
          </ButtonGrid>

          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('1')}>1</CalcButton>
            <CalcButton onClick={() => handleNumber('2')}>2</CalcButton>
            <CalcButton onClick={() => handleNumber('3')}>3</CalcButton>
            <CalcButton onClick={() => handleOperator('-')} variant="operator">-</CalcButton>
          </ButtonGrid>

          <ButtonGrid className="grid-cols-4 mb-4">
            <CalcButton onClick={() => handleNumber('0')} className="col-span-2">0</CalcButton>
            <CalcButton onClick={() => handleOperator('.')}>.</CalcButton>
            <CalcButton onClick={() => handleOperator('+')} variant="operator">+</CalcButton>
          </ButtonGrid>

          <ButtonGrid className="grid-cols-2 gap-4">
            <CalcButton onClick={() => handleOperator('*3.14159')} variant="function">π</CalcButton>
            <CalcButton onClick={handleCalculate} variant="equals">=</CalcButton>
          </ButtonGrid>
        </div>
      </div>
    </div>
  );
}