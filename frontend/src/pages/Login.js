import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const images = [
  'http://localhost:8000/static/images/1.png',
  'http://localhost:8000/static/images/2.png',
  'http://localhost:8000/static/images/3.png',
];

export default function Login() {
  const [currentImage, setCurrentImage] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % images.length);
    }, 4000); // Change every 4 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const userData = {
      email,
      isAdmin: email === 'admin@example.com',
      name: email.split('@')[0],
    };
    login(userData);
    navigate('/');
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side: Slideshow */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-tr from-blue-800 to-purple-900 items-center justify-center relative p-6">
        <img
          src={images[currentImage]}
          alt="Slideshow"
          className="rounded-2xl shadow-lg object-cover w-full h-full"
        />
        <div className="absolute bottom-10 left-10 text-white text-xl font-semibold">
          Capturing Moments, <br /> Creating Memories
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-[#1f1d2b] text-white px-6 py-12">
        <div className="max-w-md w-full">
          <h2 className="text-3xl font-bold mb-2">Sign in to your account</h2>
          <p className="text-sm mb-6">
            Don’t have an account?{' '}
            <Link to="/create-account" className="text-purple-400 hover:underline">
              Create one
            </Link>
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              className="w-full px-4 py-2 bg-[#2a2838] border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full px-4 py-2 bg-[#2a2838] border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                Remember me
              </label>
              <a href="#" className="text-purple-400 hover:underline">
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              className="w-full py-2 bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 rounded-md font-semibold"
            >
              Sign In
            </button>
          </form>

          <div className="my-6 text-center text-sm text-gray-400">or sign in with</div>

          <div className="flex space-x-4 justify-center">
            <button className="bg-[#2a2838] px-4 py-2 rounded-md border border-gray-700 hover:bg-[#3a3748]">
              <img src="https://img.icons8.com/color/24/000000/google-logo.png" alt="Google" />
            </button>
            <button className="bg-[#2a2838] px-4 py-2 rounded-md border border-gray-700 hover:bg-[#3a3748]">
              <img src="https://img.icons8.com/ios-filled/24/ffffff/mac-os.png" alt="Apple" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
