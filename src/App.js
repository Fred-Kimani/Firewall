// src/App.js

import React, { useState } from 'react';
import './App.css';

function App() {
  const [logs, setLogs] = useState([]);
  const [input, setInput] = useState("");
  const [apiData, setApiData] = useState(null);

  const handleTestClick = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5002/api/test');
      const data = await response.json();
      setApiData(data);
    } catch (error) {
      console.error('API Error:', error);
    }
  };

  const isMalicious = (text) => {
    const patterns = [ /<script>/i, /DROP TABLE/i, /SELECT \*/i, /alert\(/i ];
    return patterns.some(pattern => pattern.test(text));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isMalicious(input)) {
      setLogs([...logs, `Dangerous input detected: "${input}"`]);
      return;
    }

    const processes = [
      () => Number(input) + 5,
      () => Number(input) * 5,
      () => Number(input) / 5,
      () => Number(input) - 5,
      () => Math.abs(input),
      () => Math.round(input),
      () => Math.floor(input),
      () => Math.ceil(input),
      () => Math.max(input, 3, 7),
      () => Math.min(input, 3, 7),
      () => Math.pow(input, 2),
      () => Math.sqrt(input),
      () => Math.cbrt(input),
      () => Math.sin(input),
      () => Math.cos(input),
      () => Math.tan(input),
    ];

    const newLogs = processes.map((fn, idx) => {
      try {
        return `Process${idx + 1} result: ${fn()}`;
      } catch (err) {
        return `Process${idx + 1} error: ${err.message}`;
      }
    });

    setLogs([...logs, ...newLogs]);
  };

  return (
    <div className="App">
      <form>
        <div className = "Div1">
         <h1 className="title1">WAF SECURITY TEST FORM</h1>
         <h1 className="title2">CAUTION: AREA OF SECURITY</h1>
        </div>
        <div className = "Div2">
         <input type="text" className="InputBox" placeholder="Write one value:" value={input} onChange={e => setInput(e.target.value)}></input>
         <table className="MainWAFScreen">
          <thead className="Thead" >
            <tr className="Tr">
              <th className='Th'>Logs</th>
            </tr>
          </thead>
          <tbody className='Tbody'>
             {logs.map((log, index) => (
               <tr key={index}>
                <td>{log}</td>
               </tr>
             ))}
          </tbody>
         </table>
         <div className="button-container">
          <button onClick={handleSubmit} type="submit" className="Button">Make a Test Button</button>
         </div> 
         {apiData && (
        <div style={{ marginTop: '20px' }}>
          <h3>{apiData.message}</h3>
          <p>Value: {apiData.value}</p>
        </div>
      )}
       </div>
      </form> 
    </div>
  );
}

export default App;
