// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginForm from './LoginForm';
import Home from './Home';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* <Route exact path="/" component={Home} /> */}
          <Route path="/" element={<Home />}></Route>
          <Route path="/login" element={<LoginForm />}></Route>
          {/* <Route exact path="/login" component={LoginForm} /> */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;