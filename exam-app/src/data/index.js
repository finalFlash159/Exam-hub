import defaultQuestions from './questions/questions.json';
import questions1 from './questions/questions1.json';
import linear_reg from './questions/linear_reg.json';
import logis_reg from './questions/logis_reg.json';
import navie_bayes from './questions/navie_bayes.json';
import test_exam from './questions/test_exam.json';

// Map of exam types to question data
export const examData = {
  1: {
    title: "MongoDB Exam",
    questions: questions1
  },
  2: {
    title: "Linear Regression", 
    questions: linear_reg
  },
  3: {
    title: "Logistic Regression",
    questions: logis_reg
  },
  4: {
    title: "Naive Bayes",
    questions: navie_bayes
  },
  5: {
    title: "Quick Test (5 Questions)",
    questions: test_exam
  },
  // 3: {
  //   title: "MongoDB Aggregation Exam",
  //   questions: questions3
  // }
};

// Cache for performance
const examTypesCache = new Map();

// Get available exam types
export const getExamTypes = () => {
  const cacheKey = 'all_types';
  if (examTypesCache.has(cacheKey)) {
    return examTypesCache.get(cacheKey);
  }
  
  const types = Object.keys(examData).map(key => ({
    value: key === 'default' ? 'default' : key,
    label: examData[key].title
  }));
  
  examTypesCache.set(cacheKey, types);
  return types;
};

// Get questions by exam type
export const getQuestions = (examType = 'default') => {
  const questions = examData[examType]?.questions || defaultQuestions;
  
  // Add unique IDs if not present
  return questions.map((q, index) => ({
    ...q,
    id: q.id || `q_${examType}_${index}`
  }));
};
