import React, { useState } from 'react';
import './App.css';

function App() {
  const [logs, setLogs] = useState([]);
  const [input, setInput] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const textToSend = input;
    // This will be displayed in the logs on the screen
    let logToShow = `> Sending input: "${textToSend}"\n`;

    try {
      // Send the input to the python server
      const response = await fetch('http://localhost:5002/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: textToSend }),
      });

      const data = await response.json();

      // Check if the server blocked it or allowed it
      if (response.ok) {
        // This is for a success message
        logToShow += `Server Response: ${data.message}`;
      } else {
        // This is for an error or a blocked message
        logToShow += `Server Error (${response.status}): ${data.message || data.error}`;
      }

    } catch (error) {
      // This is for if the server is not running
      logToShow += `Network Error: Could not connect to the API.`;
    }

    setLogs(prevLogs => [...prevLogs, logToShow]);
    setInput(""); // Clear the input box
  };

  return (
    // I DID NOT CHANGE ANY HTML OR CSS HERE
    <div className="App">
      <form onSubmit={handleSubmit}>
        <div className="Div1">
          <h1 className="title1">WAF SECURITY TEST FORM</h1>
          <h1 className="title2">CAUTION: AREA OF SECURITY</h1>
        </div>
        <div className="Div2">
          <input
            type="text"
            className="InputBox"
            placeholder="Enter payload to test..."
            value={input}
            onChange={e => setInput(e.target.value)}
          />
          <div className="button-container">
            <button type="submit" className="Button">Make a Test Button</button>
          </div>
          <table className="MainWAFScreen">
            <thead className="Thead">
              <tr className="Tr">
                <th className='Th'>Logs</th>
              </tr>
            </thead>
            <tbody className='Tbody'>
              {logs.map((log, index) => (
                <tr key={index}>
                  <td style={{ whiteSpace: 'pre-wrap' }}>{log}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </form>
    </div>
  );
}

export default App