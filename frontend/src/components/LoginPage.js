// LoginPage.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Import useHistory to redirect after successful login
import '../loginPage.css'; // Import the shared CSS file for styling

//axios.defaults.headers.post['Content-Type'] ='application/json;charset=utf-8';
//axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
//axios.defaults.headers.post["Access-Control-Request-Headers"] = 'Content-Type, Authorization';



const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate(); // Get history object for redirection

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Call the authenticate API
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      console.log(formData);
      const response = await axios.post('http://localhost:8000/authenticate', formData);
      console.log('Response:', response.data);

      // Handle successful authentication
      const token = response.data.access_token;

      // Store the token in sessionStorage
      sessionStorage.setItem('token', token);

      // Redirect to the homepage
      navigate('/'); // Redirect to the homepage or any other page
    } catch (error) {
      // Handle login error
      console.error('Login error:', error);
      setError('Login failed. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <h2>Login Page</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit">Login</button>
      </form>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default LoginPage;

