import React, { createContext, useState, useContext } from 'react';

const TestDataContext = createContext();

export const useTestData = () => useContext(TestDataContext);

export const TestDataProvider = ({ children }) => {
  const [testData, setTestData] = useState([]);

  // Function to add test name to JSON data
  const addTestNameToJson = (testName, jsonData) => {
    const jsonWithName = {
      testName: testName,
      ...jsonData
    };
    return jsonWithName;
  };

  // Function to save test with its name
  const saveTestWithName = (testName, testData) => {
    const namedTest = addTestNameToJson(testName, testData);
    // Here you would typically save to localStorage or send to server
    return namedTest;
  };

  // Function to identify test from JSON
  const identifyTestFromJson = (jsonData) => {
    return jsonData.testName || 'Unknown Test';
  };

  const value = {
    testData,
    setTestData,
    addTestNameToJson,
    saveTestWithName,
    identifyTestFromJson
  };

  return (
    <TestDataContext.Provider value={value}>
      {children}
    </TestDataContext.Provider>
  );
};
