import React, { forwardRef, useEffect } from 'react';
import { 
  Link, 
  NavLink, 
  useLocation, 
  useNavigate 
} from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  HomeIcon, 
  CalculatorIcon, 
  TruckIcon, 
  TagIcon, 
  ShoppingBagIcon, 
  PhoneIcon, 
  UserIcon, 
  Cog6ToothIcon,
  DocumentTextIcon,
  MapPinIcon,
  UserGroupIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

const activeStyle = {
  backgroundColor: '#374151',
  color: '#f3f4f6'
};

const Sidebar = forwardRef(({ showSidebar, setShowSidebar }, ref) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSidebarClick = (e) => {
    e.stopPropagation();
  };

  const handleNavigation = (path) => {
    navigate(path);
    setShowSidebar(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    setShowSidebar(false);
  };

  return (
    <div
      ref={ref}
      className={`sidebar fixed top-0 left-0 h-full w-64 bg-indigo-900 text-white z-40 transform transition-transform duration-300 ${
        showSidebar ? 'translate-x-0' : '-translate-x-full'
      }`}
      onClick={(e) => e.stopPropagation()}
    >
      <div className="flex flex-col h-full">
        <nav className="mt-6 px-3 space-y-1">
          <div className="space-y-1">
            <NavLink
              to="/"
              style={({ isActive }) => (isActive ? activeStyle : undefined)}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
            >
              <HomeIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Home</span>
            </NavLink>
            
            <NavLink
              to="/quote"
              style={({ isActive }) => (isActive ? activeStyle : undefined)}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
            >
              <CalculatorIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Quote</span>
            </NavLink>

            <NavLink
              to="/pickup"
              style={({ isActive }) => (isActive ? activeStyle : undefined)}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
            >
              <TruckIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Pickup Request</span>
            </NavLink>

            <NavLink
              to="/tracking"
              style={({ isActive }) => (isActive ? activeStyle : undefined)}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
            >
              <MagnifyingGlassIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Tracking</span>
            </NavLink>

            <NavLink
              to="/pricing"
              style={({ isActive }) => (isActive ? activeStyle : undefined)}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
            >
              <TagIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Pricing</span>
            </NavLink>
          </div>

          <div className="mt-6">
            <div className="space-y-1">
              <Link
                to="/cart"
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
              >
                <ShoppingBagIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Cart</span>
              </Link>

              <Link
                to="/support"
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
              >
                <PhoneIcon className="h-5 w-5" />
                <span className="text-sm font-medium">Customer Support</span>
              </Link>
            </div>

            <div className="mt-6">
              {!user?.isAuthenticated ? (
                <Link
                  to="/auth"
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                >
                  <UserIcon className="h-5 w-5" />
                  <span className="text-sm font-medium">Sign In</span>
                </Link>
              ) : (
                <>
                  <NavLink
                    to="/profile"
                    style={({ isActive }) => (isActive ? activeStyle : undefined)}
                    className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700"
                  >
                    <UserIcon className="h-5 w-5" />
                    <span className="text-sm font-medium">Profile</span>
                  </NavLink>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-700 w-full"
                  >
                    <Cog6ToothIcon className="h-5 w-5" />
                    <span className="text-sm font-medium">Logout</span>
                  </button>
                </>
              )}
            </div>
          </div>
        </nav>
      </div>
    </div>
  );
});

Sidebar.displayName = 'Sidebar';

export default Sidebar;
