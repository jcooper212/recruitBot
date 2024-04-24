// Navbar.js
import React from 'react';
import { Link } from 'react-router-dom';
import Logo from '../logo.png';


const Navbar = () => {
  return (
    <nav>
      <div className="logo">
        <img src={Logo} alt="Logo" />
      </div>
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/invoice">Invoice</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;

