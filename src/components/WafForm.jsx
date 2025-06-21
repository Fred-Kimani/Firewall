import React, { useState } from 'react';

function WafForm() {
  const [apiData, setApiData] = useState(null);

  const handleTestClick = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/test');
      const data = await response.json();
      setApiData(data);
    } catch (error) {
      console.error('API Hatası:', error);
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <button onClick={handleTestClick}>Make a Test Button</button>
      {apiData && (
        <div style={{ marginTop: '20px', color: 'white' }}>
          <h3>{apiData.message}</h3>
          <p>Value: {apiData.value}</p>
        </div>
      )}
    </div>
  );
}

export default WafForm;
