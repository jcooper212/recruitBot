// App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import Register from './components/Register';
import InvoicePage from './components/InvoicePage';


function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route exact path="/" element={<LandingPage/>} />
          <Route path="/invoice" element={<InvoicePage clientName='Sodexo'/>}/>
          <Route path="/about" render={() => <h2>About Page</h2>} />
          <Route path="/login" element={<LoginPage/>} />
          <Route path="/register" element={<Register/>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

