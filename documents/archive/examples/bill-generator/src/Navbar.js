// Navbar.js
import React from 'react';

export default function Navbar() {
  return (
    <div className="navbar">
      <div className="logo">Parcel My Box</div>
      <div className="nav-links">
        <a href="#">Home</a>
        <a href="#">About Us</a>
        <a href="#">Contact Us</a>
      </div>
      <div className="contact-info">
        <span>
          <img src="https://flagcdn.com/in.svg" alt="India" />
          +91 92474 99247
        </span>
        <span>
          <img src="https://flagcdn.com/us.svg" alt="USA" />
          0 01-510 714 6946
        </span>
      </div>
    </div>
  );
}
