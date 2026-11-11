import React from 'react';

function Offline() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      textAlign: 'center',
      padding: '20px'
    }}>
      <h1>🔌 Offline Mode</h1>
      <p>Please check your internet connection.</p>
      <p>Some features are still available offline.</p>
      <button 
        onClick={() => window.location.reload()}
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          fontSize: '16px',
          cursor: 'pointer'
        }}
      >
        Try Again
      </button>
    </div>
  );
}

export default Offline;