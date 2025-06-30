import defaultQuestions from './questions/questions.json';
import questions1 from './questions/questions1.json';
import linear_reg_part1 from './questions/linear_reg_part1.json';
import linear_reg_part2 from './questions/linear_reg_part2.json';
import logis_reg_part1 from './questions/logis_reg_part1.json';
import logis_reg_part2 from './questions/logis_reg_part2.json';
import navie_bayes_part1 from './questions/navie_bayes_part1.json';
import navie_bayes_part2 from './questions/navie_bayes_part2.json';
import decision_tree_part1 from './questions/decision_tree_part1.json';
import decision_tree_part2 from './questions/decision_tree_part2.json';
import unsupervised_learning from './questions/unsupervised_learning1.json';
import unsupervised_learning2 from './questions/unsupervised_learning2.json';
import svm_advanced from './questions/svm_advanced.json';
import svm_exam_a from './questions/svm_exam_a.json';
import svm_exam_b from './questions/svm_exam_b.json';
import { getExamDuration } from '../constants/examConstants';

// Helper function to get exam duration info
const calculateExamInfo = (questions) => {
  const count = questions?.length || 0;
  const duration = getExamDuration(count);
  return {
    questionCount: count,
    duration: duration,
    durationText: `${duration} phút`
  };
};


// Map of exam types to question data
export const examData = {
  1: {
    title: "MongoDB Exam",
    questions: questions1,
    ...calculateExamInfo(questions1)
  },
  2: {
    title: "Linear Regression - Part 1", 
    questions: linear_reg_part1,
    ...calculateExamInfo(linear_reg_part1)
  },
  3: {
    title: "Linear Regression - Part 2",
    questions: linear_reg_part2,
    ...calculateExamInfo(linear_reg_part2)
  },
  4: {
    title: "Logistic Regression - Part 1",
    questions: logis_reg_part1,
    ...calculateExamInfo(logis_reg_part1)
  },
  5: {
    title: "Logistic Regression - Part 2",
    questions: logis_reg_part2,
    ...calculateExamInfo(logis_reg_part2)
  },
  6: {
    title: "Naive Bayes - Part 1",
    questions: navie_bayes_part1,
    ...calculateExamInfo(navie_bayes_part1)
  },
  7: {
    title: "Naive Bayes - Part 2",
    questions: navie_bayes_part2,
    ...calculateExamInfo(navie_bayes_part2)
  },
  8: {
    title: "Decision Tree - Part 1",
    questions: decision_tree_part1,
    ...calculateExamInfo(decision_tree_part1)
  },
  9: {
    title: "Decision Tree - Part 2",
    questions: decision_tree_part2,
    ...calculateExamInfo(decision_tree_part2)
  },
  10: {
    title: "Unsupervised Learning - K-means & Hierarchical - Part 1",
    questions: unsupervised_learning.questions,
    ...calculateExamInfo(unsupervised_learning.questions)
  },
  11: {
    title: "Unsupervised Learning - K-means & Hierarchical - Part 2",
    questions: unsupervised_learning2,
    ...calculateExamInfo(unsupervised_learning2)
  },
  12: {
    title: "Support Vector Machine - Exam A",
    questions: svm_exam_a.questions,
    ...calculateExamInfo(svm_exam_a.questions)
  },
  13: {
    title: "Support Vector Machine - Exam B",
    questions: svm_exam_b.questions,
    ...calculateExamInfo(svm_exam_b.questions)
  },
  14: {
    title: "Support Vector Machine - Advanced",
    questions: svm_advanced.questions,
    ...calculateExamInfo(svm_advanced.questions)
  }
};

// Get available exam types
export const getExamTypes = () => {
  const types = Object.keys(examData).map(key => ({
    value: key === 'default' ? 'default' : key,
    label: examData[key].title,
    questionCount: examData[key].questionCount,
    duration: examData[key].duration,
    durationText: examData[key].durationText
  }));
  
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

// Get exam info
export const getExamInfo = (examType) => {
  return {
    title: examData[examType]?.title || "Default Exam",
    questionCount: examData[examType]?.questionCount || 0,
    duration: examData[examType]?.duration || 120,
    durationText: examData[examType]?.durationText || "120 phút"
  };
};
