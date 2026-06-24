# LLM Output

=== FILE: src/App.jsx ===
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { HashRouter, Route, Routes, Navigate } from 'react-router-dom';
import axios from 'axios';
import { ToastContainer } from 'react-toastify';
import { FiLogIn, FiLogOut } from 'react-icons/fi';
import { RiAddLine } from 'react-icons/ri';
import { format } from 'date-fns';
import { useForm } from 'react-hook-form';
import { clsx } from 'clsx';
import 'react-toastify/dist/ReactToastify.css';
import 'tailwindcss/tailwind.css';

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const App = () => {
  const [user, setUser] = useState(null);
  const [properties, setProperties] = useState([]);
  const [summary, setSummary] = useState({});
  const [period, setPeriod] = useState('week');
  const [isOpen, setIsOpen] = useState(false);
  const [newProperty, setNewProperty] = useState({});

  const { register, handleSubmit, reset } = useForm();

  const handleLogin = useCallback(async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/login`, data);
      setUser(response.data);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleRegistration = useCallback(async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/register`, data);
      setUser(response.data);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleLogout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('token');
  }, []);

  const handleAddProperty = useCallback(async (data) => {
    try {
      const response = await axios.post(`${BASE_URL}/properties`, data, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setProperties((prevProperties) => [...prevProperties, response.data]);
      setIsOpen(false);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleGetProperty = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/properties`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const safeList = Array.isArray(response.data) ? response.data : (response.data?.items || []);
      setProperties(safeList);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const handleGetSummary = useCallback(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/summary`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setSummary(response.data);
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    handleGetProperty();
    handleGetSummary();
  }, [handleGetProperty, handleGetSummary]);

  const handleFilter = useCallback((period) => {
    setPeriod(period);
  }, []);

  const Header = () => (
    <header className="bg-gray-900 py-4">
      <nav className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Real Estate Property Management Portal</h1>
        {user ? (
          <button
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
            onClick={handleLogout}
          >
            <FiLogOut size={20} className="mr-2" />
            Logout
          </button>
        ) : (
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={() => navigate('/login')}
          >
            <FiLogIn size={20} className="mr-2" />
            Login
          </button>
        )}
      </nav>
    </header>
  );

  const Footer = () => (
    <footer className="bg-gray-900 py-4 mt-10">
      <p className="container mx-auto text-white text-center">
        &copy; 2023 Real Estate Property Management Portal
      </p>
    </footer>
  );

  const Login = () => (
    <div className="container mx-auto p-4 pt-6 mt-10 flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-4">Login</h2>
      <form onSubmit={handleSubmit(handleLogin)}>
        <input
          type="email"
          placeholder="Email"
          className="w-full p-2 mb-4 border border-gray-400 rounded"
          {...register('email')}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-2 mb-4 border border-gray-400 rounded"
          {...register('password')}
        />
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Login
        </button>
      </form>
    </div>
  );

  const Register = () => (
    <div className="container mx-auto p-4 pt-6 mt-10 flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-4">Register</h2>
      <form onSubmit={handleSubmit(handleRegistration)}>
        <input
          type="email"
          placeholder="Email"
          className="w-full p-2 mb-4 border border-gray-400 rounded"
          {...register('email')}
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-2 mb-4 border border-gray-400 rounded"
          {...register('password')}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          className="w-full p-2 mb-4 border border-gray-400 rounded"
          {...register('confirmPassword')}
        />
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Register
        </button>
      </form>
    </div>
  );

  const Dashboard = () => (
    <div className="container mx-auto p-4 pt-6 mt-10 flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-4">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-gray-800 p-4 rounded">
          <h3 className="text-2xl font-bold mb-2">Total Properties</h3>
          <p className="text-4xl font-bold">{summary.totalProperties}</p>
        </div>
        <div className="bg-gray-800 p-4 rounded">
          <h3 className="text-2xl font-bold mb-2">Active Listings</h3>
          <p className="text-4xl font-bold">{summary.activeListings}</p>
        </div>
        <div className="bg-gray-800 p-4 rounded">
          <h3 className="text-2xl font-bold mb-2">Total Revenue</h3>
          <p className="text-4xl font-bold">{summary.totalRevenue}</p>
        </div>
      </div>
      <table className="w-full mb-4">
        <thead>
          <tr>
            <th className="px-4 py-2">Property Name</th>
            <th className="px-4 py-2">Location</th>
            <th className="px-4 py-2">Price</th>
            <th className="px-4 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {properties.map((property) => (
            <tr key={property.id}>
              <td className="px-4 py-2">{property.name}</td>
              <td className="px-4 py-2">{property.location}</td>
              <td className="px-4 py-2">{property.price}</td>
              <td className="px-4 py-2">
                {property.status === 'available' ? (
                  <span className="bg-green-200 text-green-600 py-1 px-2 rounded">
                    Available
                  </span>
                ) : property.status === 'rented' ? (
                  <span className="bg-yellow-200 text-yellow-600 py-1 px-2 rounded">
                    Rented
                  </span>
                ) : (
                  <span className="bg-red-200 text-red-600 py-1 px-2 rounded">
                    Sold
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        onClick={() => setIsOpen(true)}
      >
        <RiAddLine size={20} className="mr-2" />
        Add Property
      </button>
      {isOpen && (
        <div className="fixed top-0 left-0 w-full h-full bg-gray-800 bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-4 rounded">
            <h2 className="text-2xl font-bold mb-4">Add Property</h2>
            <form onSubmit={handleSubmit(handleAddProperty)}>
              <input
                type="text"
                placeholder="Property Name"
                className="w-full p-2 mb-4 border border-gray-400 rounded"
                {...register('name')}
              />
              <input
                type="text"
                placeholder="Location"
                className="w-full p-2 mb-4 border border-gray-400 rounded"
                {...register('location')}
              />
              <input
                type="number"
                placeholder="Price"
                className="w-full p-2 mb-4 border border-gray-400 rounded"
                {...register('price')}
              />
              <select
                className="w-full p-2 mb-4 border border-gray-400 rounded"
                {...register('status')}
              >
                <option value="available">Available</option>
                <option value="rented">Rented</option>
                <option value="sold">Sold</option>
              </select>
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Add Property
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <HashRouter>
      <Header />
      <ToastContainer />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/dashboard"
          element={user ? <Dashboard /> : <Navigate to="/login" replace />}
        />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
      <Footer />
    </HashRouter>
  );
};

export default App;

=== END ===