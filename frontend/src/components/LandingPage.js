// LandingPage.js
import React from 'react';

const LandingPage = () => {
  return (
    <div>
      <h1>Welcome to My React App</h1>
      <button onClick={() => console.log('Register clicked')}>Register</button>
      <button onClick={() => console.log('Login clicked')}>Login</button>
    </div>
  );
};

export default LandingPage;

