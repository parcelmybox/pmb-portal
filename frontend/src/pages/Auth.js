import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext'; // use the custom hook
import axios from 'axios';

const images = ['/images/1.png', '/images/2.png', '/images/3.png'];

export default function Auth() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isSignUp, setIsSignUp] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const { login, signup } = useAuth(); // ✅ get auth functions

  const redirectTo = new URLSearchParams(location.search).get('redirect') || '/';

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    const { first_name, last_name, email, password } = form;

    const success = await signup(first_name, last_name, email, password);
    if (success) {
      alert('Signup successful! You are now logged in.');
      navigate(redirectTo);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const { email, password } = form;

    const success = await login(email, password); // ✅ using AuthContext login
    if (success) {
      alert('Login successful!');
      navigate(redirectTo); // ✅ go back to /feedback or home
    }
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % images.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <style>
        {`
          @keyframes fill {
            from { width: 0%; }
            to { width: 100%; }
          }
          .animate-fill {
            animation: fill 4s linear forwards;
          }
          @font-face {
            font-family: 'SequelSans';
            src: url('/fonts/SequelSans-Medium.ttf') format('truetype');
            font-weight: 400;
            font-style: normal;
          }
          .sequel-font {
            font-family: 'SequelSans', sans-serif;
          }
        `}
      </style>

      <div
        className="fixed top-0 left-0 w-screen h-screen flex p-0 m-0 overflow-hidden z-50"
        style={{ backgroundColor: '#2C2638' }}
      >
        {/* Left Slideshow */}
        <div className="w-1/2 flex items-center justify-center p-[0.5cm]">
          <div className="w-full h-full rounded-lg overflow-hidden relative">
            <img
              src={images[currentIndex]}
              alt="Slideshow"
              className="object-cover w-full h-full transition-all duration-1000 rounded-lg"
            />
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2 w-[40%]">
              {images.map((_, idx) => {
                const isActive = idx === currentIndex;
                const isCompleted = idx < currentIndex;
                return (
                  <div
                    key={idx}
                    className="h-1 w-full rounded-md bg-white bg-opacity-30 overflow-hidden"
                  >
                    <div
                      className={`h-full ${
                        isActive
                          ? 'bg-white animate-fill'
                          : isCompleted
                          ? 'bg-white bg-opacity-50 w-full'
                          : 'w-0'
                      }`}
                    ></div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Auth Form */}
        <div className="w-1/2 flex flex-col justify-center items-center px-12 text-white sequel-font">
          {isSignUp ? (
            <>
              <div className="w-full max-w-lg text-left mb-8">
                <h2 className="text-5xl font-normal">Create an Account</h2>
                <p className="text-sm mt-2 mb-8">
                  Already have an account?{' '}
                  <span
                    className="underline cursor-pointer"
                    onClick={() => setIsSignUp(false)}
                  >
                    Login.
                  </span>
                </p>
              </div>

              <form className="w-full max-w-lg space-y-6" onSubmit={handleSignup}>
                <div className="flex space-x-4">
                  <input
                    type="text"
                    name="first_name"
                    placeholder="First Name"
                    value={form.first_name}
                    onChange={handleChange}
                    className="w-1/2 px-5 py-4 rounded-md focus:outline-none"
                    style={{ backgroundColor: '#3C364C', color: 'white' }}
                    required
                  />
                  <input
                    type="text"
                    name="last_name"
                    placeholder="Last Name"
                    value={form.last_name}
                    onChange={handleChange}
                    className="w-1/2 px-5 py-4 rounded-md focus:outline-none"
                    style={{ backgroundColor: '#3C364C', color: 'white' }}
                    required
                  />
                </div>
                <input
                  type="email"
                  name="email"
                  placeholder="Email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full px-5 py-4 rounded-md focus:outline-none"
                  style={{ backgroundColor: '#3C364C', color: 'white' }}
                  required
                />
                <input
                  type="password"
                  name="password"
                  placeholder="Password"
                  value={form.password}
                  onChange={handleChange}
                  className="w-full px-5 py-4 rounded-md focus:outline-none"
                  style={{ backgroundColor: '#3C364C', color: 'white' }}
                  required
                />
                <div className="flex items-center space-x-2 text-sm mt-2">
                  <input type="checkbox" className="accent-[#6D54B5]" required />
                  <label>I accept the Terms & Conditions</label>
                </div>
                <div className="mt-10">
                  <button
                    type="submit"
                    className="w-full py-4 font-semibold rounded-md hover:opacity-90 transition"
                    style={{ backgroundColor: '#6D54B5', color: 'white' }}
                  >
                    Create Account
                  </button>
                </div>
              </form>
            </>
          ) : (
            <>
              <h2 className="text-4xl font-bold mb-6">Welcome Back</h2>
              <form className="w-full max-w-lg space-y-5" onSubmit={handleLogin}>
                <input
                  type="email"
                  name="email"
                  placeholder="Email"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full px-5 py-4 rounded-md focus:outline-none"
                  style={{ backgroundColor: '#3C364C', color: 'white' }}
                  required
                />
                <input
                  type="password"
                  name="password"
                  placeholder="Password"
                  value={form.password}
                  onChange={handleChange}
                  className="w-full px-5 py-4 rounded-md focus:outline-none"
                  style={{ backgroundColor: '#3C364C', color: 'white' }}
                  required
                />
                <button
                  type="submit"
                  className="w-full py-4 font-semibold rounded-md hover:opacity-90 transition"
                  style={{ backgroundColor: '#6D54B5', color: 'white' }}
                >
                  LogIn
                </button>
              </form>
              <p className="text-sm text-center mt-4">
                Don’t have an account?{' '}
                <span
                  className="underline cursor-pointer"
                  onClick={() => setIsSignUp(true)}
                >
                  Sign Up
                </span>
              </p>
            </>
          )}
        </div>
      </div>
    </>
  );
}
