import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

const MathRenderer = ({ children, block = false }) => {
  if (!children) return null;
  
  // Process LaTeX syntax in text
  const processText = (text) => {
    if (typeof text !== 'string') return text;
    
    // Split text by LaTeX delimiters and process each part
    const parts = [];
    let currentIndex = 0;
    
    // Find all LaTeX expressions - Updated regex to match double-escaped LaTeX
    const latexRegex = /\\\\?\((.*?)\\\\?\)/g;
    let match;
    
    while ((match = latexRegex.exec(text)) !== null) {
      // Add text before the math
      if (match.index > currentIndex) {
        parts.push(text.slice(currentIndex, match.index));
      }
      
      // Clean up the math expression by removing extra backslashes
      let mathExpression = match[1];
      // Replace double backslashes with single backslashes for KaTeX
      mathExpression = mathExpression.replace(/\\\\/g, '\\');
      
      // Add the math expression
      parts.push(
        <InlineMath key={match.index} math={mathExpression} />
      );
      
      currentIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (currentIndex < text.length) {
      parts.push(text.slice(currentIndex));
    }
    
    return parts.length > 0 ? parts : text;
  };
  
  if (block) {
    // Clean up block math as well
    const cleanMath = typeof children === 'string' ? children.replace(/\\\\/g, '\\') : children;
    return <BlockMath math={cleanMath} />;
  }
  
  return <>{processText(children)}</>;
};

export default MathRenderer; 