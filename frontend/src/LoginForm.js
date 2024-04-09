// src/LoginForm.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Message } from 'semantic-ui-react';

const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail);
      }

      // Store authentication token in session storage
      sessionStorage.setItem('authToken', data.access_token);

      // Redirect user to homepage
      navigate('/');
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <div style={{ width: '400px', margin: 'auto', marginTop: '100px' }}>
      <h2>Login</h2>
      <Form onSubmit={handleLogin} error={error !== ''}>
        <Form.Input
          icon="user"
          iconPosition="left"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <Form.Input
          icon="lock"
          iconPosition="left"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit" color="blue">Login</Button>
        {error && <Message error content={error} />}
      </Form>
    </div>
  );
};

export default LoginForm;

