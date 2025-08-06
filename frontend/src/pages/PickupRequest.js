import axios from 'axios';
import React, { useState, useEffect, useRef, useCallback } from 'react';

// Constants
const PACKAGE_OPTIONS = [
  {
    id: 'doc',
    icon: 'fa-file-lines',
    title: 'Documents',
    description: (weightUnit) => 'Paperwork etc'
  },
  {
    id: 'Medicine',
    icon: 'fa-file-lines',
    title: 'Medicine',
    description: (weightUnit) => 'Pharmacy etc'
  },
  {
    id: 'small',
    icon: 'fa-box-open',
    title: 'Small',
    description: (weightUnit) => weightUnit === 'kg' ? 'Package (<1kg)' : 'Package (<2.2lb)'
  },
  {
    id: 'medium',
    icon: 'fa-box',
    title: 'Medium',
    description: (weightUnit) => weightUnit === 'kg' ? 'Package (1-5kg)' : 'Package (2.2-11lb)'
  },
  {
    id: 'large',
    icon: 'fa-boxes',
    title: 'Large',
    description: (weightUnit) => weightUnit === 'kg' ? 'Package (5-10kg)' : 'Package (11-22lb)'
  },
  {
    id: 'xl',
    icon: 'fa-pallet',
    title: 'Extra Large',
    description: (weightUnit) => weightUnit === 'kg' ? 'Package (>10kg)' : 'Package (>22lb)'
  }
];

const USA_CITIES = [
  'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix',
  'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'
];

const INDIA_CITIES = [
  'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
  'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat','Visakhapatnam',
  'Vijayawada','Guntur','Nellore','Kurnool','Rajahmundry','Tirupati','Kakinada','Anantapur',
  'Kadapa','Eluru','Ongole','Srikakulam','Chittoor','Nandyal','Machilipatnam','Tenali','Proddatur',
  'Hindupur','Bhimavaram'
];

const TIME_SLOTS = [
  { value: '09:00:00', label: 'Morning (9AM-12PM)' },
  { value: '12:00:00', label: 'Afternoon (12PM-3PM)' },
  { value: '15:00:00', label: 'Late Afternoon (3PM-6PM)' },
  { value: '18:00:00', label: 'Evening (6PM-9PM)' }
];

const COUNTRY_CODES = [
  { value: '+91', label: '+91 (IN)' },
  { value: '+1', label: '+1 (US)' }
];

const getDefaultDate = () => {
  const date = new Date();
  date.setDate(date.getDate() + 3); // Add 3 days to current date
  return date.toISOString().split('T')[0];
};

const INITIAL_FORM_STATE = {
  name: '',
  phone: '',
  countryCode: '+91',
  email: '',
  pickupAddress: '',
  postalCode: '',  
  city: '',
  date: getDefaultDate(),
  time: '12:00:00',
  notes: '',
  terms: false,
  weightUnit: 'kg',
  packageWeight: '',
  packageType: 'medium',
  shippingDirection: 'india_to_usa'
};

// Reusable Components
const InputWithIcon = React.memo(({ 
  icon, 
  type = 'text', 
  name, 
  value, 
  onChange, 
  placeholder, 
  required = false, 
  inputRef,
  min,
  step,
  maxLength
}) => (
  <div className="relative">
    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
      <i className={`fas ${icon} text-blue-400 text-lg`}></i>
    </div>
    <input
      ref={inputRef}
      type={type}
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
      placeholder={placeholder}
      required={required}
      min={min}
      step={step}
      maxLength={maxLength}
    />
  </div>
));

const SelectWithIcon = React.memo(({ 
  icon, 
  name, 
  value, 
  onChange, 
  options, 
  placeholder, 
  required = false,
  selectRef 
}) => (
  <div className="relative">
    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
      <i className={`fas ${icon} text-blue-400 text-lg`}></i>
    </div>
    <select
      ref={selectRef}
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200 appearance-none"
      required={required}
    >
      <option value="" disabled>{placeholder}</option>
      {options.map((option) => (
        <option key={option.value || option} value={option.value || option}>
          {option.label || option}
        </option>
      ))}
    </select>
    <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
      <i className="fas fa-chevron-down text-gray-400"></i>
    </div>
  </div>
));

const CityInput = ({ 
  icon, 
  name, 
  value, 
  onChange, 
  options, 
  placeholder, 
  required,
  selectRef,
  isLookingUpCity
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [customCity, setCustomCity] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  const filteredOptions = options.filter(option =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelect = (value) => {
    onChange({ target: { name, value } });
    setIsOpen(false);
    setSearchTerm('');
    setShowCustomInput(false);
  };

  const handleCustomCitySubmit = () => {
    if (customCity.trim()) {
      onChange({ target: { name, value: customCity } });
      setShowCustomInput(false);
    }
  };

  return (
    <div className="relative">
      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
        <i className={`fas ${icon} text-blue-400 text-lg`}></i>
      </div>
      
      {showCustomInput ? (
        <div className="flex">
          <input
            type="text"
            value={customCity}
            onChange={(e) => setCustomCity(e.target.value)}
            className="flex-1 pl-10 pr-4 py-3 border-2 border-gray-200 rounded-l-xl transition-all focus:border-blue-500 focus:ring-blue-200"
            placeholder="Enter city name"
            autoFocus
          />
          <button
            onClick={handleCustomCitySubmit}
            className="px-4 bg-blue-500 text-white rounded-r-xl hover:bg-blue-600 transition-all"
          >
            <i className="fas fa-check"></i>
          </button>
        </div>
      ) : (
        <div 
          onClick={() => setIsOpen(!isOpen)}
          className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200 cursor-pointer"
        >
          {value || placeholder}
        </div>
      )}
      
      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        {isLookingUpCity ? (
          <i className="fas fa-spinner fa-spin text-blue-500"></i>
        ) : (
          <i className={`fas ${isOpen ? 'fa-chevron-up' : 'fa-chevron-down'} text-gray-400`}></i>
        )}
      </div>
      
      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-xl border border-gray-200 max-h-60 overflow-auto">
          <div className="p-2 sticky top-0 bg-white border-b">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3">
                <i className="fas fa-search text-gray-400"></i>
              </div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                placeholder="Search city..."
                autoFocus
              />
            </div>
          </div>
          
          <div className="py-1">
            {filteredOptions.length > 0 ? (
              <>
                {filteredOptions.map((option) => (
                  <div
                    key={option}
                    onClick={() => handleSelect(option)}
                    className={`px-4 py-2 cursor-pointer hover:bg-blue-50 ${value === option ? 'bg-blue-100 text-blue-700' : 'text-gray-700'}`}
                  >
                    {option}
                  </div>
                ))}
                <div
                  onClick={() => {
                    setShowCustomInput(true);
                    setIsOpen(false);
                  }}
                  className="px-4 py-2 cursor-pointer bg-gray-100 text-blue-600 hover:bg-blue-50"
                >
                  <i className="fas fa-plus mr-2"></i> Add custom city
                </div>
              </>
            ) : (
              <>
                <div className="px-4 py-2 text-gray-500">No matching cities found</div>
                <div
                  onClick={() => {
                    setShowCustomInput(true);
                    setIsOpen(false);
                  }}
                  className="px-4 py-2 cursor-pointer bg-gray-100 text-blue-600 hover:bg-blue-50"
                >
                  <i className="fas fa-plus mr-2"></i> Add custom city
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const WeightInput = React.memo(({ 
  weightUnit, 
  packageWeight, 
  onWeightChange, 
  onUnitChange,
  weightRef
}) => {
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="block font-medium text-gray-700">Package Weight</label>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Unit:</span>
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              type="button"
              onClick={() => onUnitChange('kg')}
              className={`px-3 py-1 text-sm rounded-md transition-all ${weightUnit === 'kg' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-200'}`}
            >
              kg
            </button>
            <button
              type="button"
              onClick={() => onUnitChange('lb')}
              className={`px-3 py-1 text-sm rounded-md transition-all ${weightUnit === 'lb' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-200'}`}
            >
              lb
            </button>
          </div>
        </div>
      </div>
      <InputWithIcon 
        inputRef={weightRef}
        icon="fa-weight-hanging" 
        type="number" 
        name="packageWeight" 
        value={packageWeight} 
        onChange={onWeightChange} 
        placeholder={`Enter weight in ${weightUnit}`} 
        required 
        min="0"
        step="0.1"
      />
    </div>
  );
});

const TermsCheckbox = React.memo(({ checked, onChange }) => {
  return (
    <div className="flex items-center">
      <input
        type="checkbox"
        id="terms"
        name="terms"
        checked={checked}
        onChange={onChange}
        className="absolute opacity-0 h-0 w-0"
        required
      />
      <label 
        htmlFor="terms" 
        className={`relative h-5 w-5 rounded-md mr-3 transition-all ${checked ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'} border-2`}
      >
        {checked && (
          <span className="absolute left-1.5 top-0.5 w-1.5 h-2.5 border-white border-r-2 border-b-2 transform rotate-45"></span>
        )}
      </label>
      <span className="text-gray-700">
        I agree to the <button className="text-blue-600 hover:underline" onClick={(e) => { e.preventDefault(); alert('Terms of service would be displayed here.'); }}>terms of service</button>
      </span>
    </div>
  );
});

const SuccessMessage = ({ pickupAddress, city, onNewRequest, trackingNumber }) => {
  return (
    <div className="text-center p-8">
      <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 bg-blue-100/20 text-blue-600 text-4xl animate-bounce">
        <i className="fas fa-check"></i>
      </div>
      <h2 className="text-2xl font-bold mb-2 text-gray-800">Pickup Scheduled!</h2>
      
      {trackingNumber && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg inline-block">
          <div className="flex items-center justify-center">
            <span className="font-semibold mr-2">Tracking Number:</span>
            <span className="bg-white px-3 py-1 rounded-md font-mono text-blue-600 border border-blue-200">
              {trackingNumber}
            </span>
          </div>
        </div>
      )}
      
      <p className="mb-6 text-gray-600">
        Thank you for choosing us! Your pickup is set we will contact you soon
      </p>
      
      <button
        onClick={onNewRequest}
        className="inline-flex items-center justify-center px-8 py-3 rounded-xl font-semibold text-center whitespace-nowrap transition-all bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-lg hover:shadow-xl mb-8"
      >
        <i className="fas fa-plus mr-2"></i> New Request
      </button>
      
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-700">Need help? Contact our support</h3>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <a 
            href="https://wa.me/15107146946" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center justify-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-all"
          >
            <i className="fab fa-whatsapp mr-2 text-lg"></i> WhatsApp
          </a>
          <a 
            href="https://mail.google.com/mail/?view=cm&fs=1&to=parcelmybox3@gmail.com" 
            target="_blank"
            rel="noopener noreferrer"
            className="flex flex-col items-center justify-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all"
          >
            <i className="fas fa-envelope text-lg mb-1"></i>
            <span className="text-xs">parcelmybox3@gmail.com</span>
          </a>
          <a 
            href="tel:+15107146946" 
            className="flex flex-col items-center justify-center px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-all"
          >
            <i className="fas fa-phone text-lg mb-1"></i>
            <span className="text-xs">+1 (510) 714-6946</span>
          </a>
        </div>
      </div>
    </div>
  );
};

const PickupForm = () => {
  const [formData, setFormData] = useState(INITIAL_FORM_STATE);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trackingNumber, setTrackingNumber] = useState('');
  const [isLookingUpCity, setIsLookingUpCity] = useState(false);

  // Refs
  const nameRef = useRef();
  const emailRef = useRef();
  const phoneRef = useRef();
  const pickupAddressRef = useRef();
  const postalCodeRef = useRef();
  const dateRef = useRef();
  const timeRef = useRef();
  const packageTypeRef = useRef();
  const packageWeightRef = useRef();
  const notesRef = useRef();
  const cityRef = useRef();

  // Get cities based on shipping direction
  const getCities = () => {
    return formData.shippingDirection === 'usa_to_india' ? USA_CITIES : INDIA_CITIES;
  };

  // Postal code lookup function
  const lookupCityFromPostalCode = async (postalCode, country) => {
    setIsLookingUpCity(true);
    try {
      // For India - using PostalPin API
      if (country === 'india_to_usa') {
        const response = await axios.get(`https://api.postalpincode.in/pincode/${postalCode}`);
        if (response.data && response.data[0]?.Status === 'Success' && response.data[0]?.PostOffice?.length > 0) {
          return response.data[0].PostOffice[0].District;
        }
      }
      // For USA - using Zippopotam API
      else {
        const response = await axios.get(`https://api.zippopotam.us/us/${postalCode}`);
        if (response.data?.places?.length > 0) {
          return response.data.places[0]['place name'];
        }
      }
    } catch (error) {
      console.error('Postal code lookup failed:', error);
      return null;
    } finally {
      setIsLookingUpCity(false);
    }
  };

  // Handlers
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  }, []);

  const handlePostalCodeChange = async (e) => {
    const { value } = e.target;
    setFormData(prev => ({ ...prev, postalCode: value }));
    
    // Only lookup if postal code is complete
    const expectedLength = formData.shippingDirection === 'india_to_usa' ? 6 : 5;
    if (value.length === expectedLength) {
      const city = await lookupCityFromPostalCode(value, formData.shippingDirection);
      if (city) {
        setFormData(prev => ({ ...prev, city }));
      }
    }
  };

  const handleUnitChange = useCallback((unit) => {
    setFormData(prev => ({ ...prev, weightUnit: unit }));
  }, []);

  const handleWhatsAppClick = useCallback(() => {
    window.open('https://wa.me/15107146946', '_blank');
  }, []);

  const toggleShippingDirection = useCallback(() => {
    setFormData(prev => ({
      ...prev,
      shippingDirection: prev.shippingDirection === 'usa_to_india' ? 'india_to_usa' : 'usa_to_india',
      city: '',
      postalCode: ''
    }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.terms) {
      setError('You must accept the terms of service');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData = {
        name: formData.name,
        phone_number: `${formData.countryCode}${formData.phone}`,
        email: formData.email,
        address: formData.pickupAddress,
        city: formData.city,
        postal_code: formData.postalCode,
        date: formData.date,
        time: formData.time.value || formData.time,
        package_type: formData.packageType || 'small',
        weight: parseFloat(formData.packageWeight),
        instructions: formData.notes,
        shipping_direction: formData.shippingDirection,
      };

      const response = await axios.post(
        'http://localhost:8000/api/pickup-requests/',
        requestData,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 10000
        }
      );

      if (response.status === 201) {
        setIsSubmitted(true);
        setTrackingNumber(response.data.tracking_number);
        setFormData(INITIAL_FORM_STATE);
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error.response?.data?.detail || 'Failed to submit. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewRequest = useCallback(() => {
    setIsSubmitted(false);
    setFormData(INITIAL_FORM_STATE);
    setTrackingNumber('');
    setError(null);
    nameRef.current?.focus();
  }, []);

  // Load external resources
  useEffect(() => {
    const fontAwesome = document.createElement('link');
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(fontAwesome);

    return () => {
      document.head.removeChild(fontAwesome);
    };
  }, []);

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="relative bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(255,255,255,0.15)_0%,rgba(255,255,255,0)_70%)]"></div>
          <div className="relative flex flex-col items-center text-center">
            <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-6 animate-float">
              <i className="fas fa-truck-fast text-3xl text-white glow-icon"></i>
            </div>
            <h1 className="text-4xl font-bold mb-3">Pickup Request</h1>
            <p className="text-white/90 max-w-md">Schedule your pickup with our lightning-fast delivery network</p>
          </div>
        </div> 
        
        <div className="p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}
          
          {!isSubmitted ? (
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputWithIcon 
                  inputRef={nameRef}
                  icon="fa-user" 
                  type="text" 
                  name="name" 
                  value={formData.name} 
                  onChange={handleChange} 
                  placeholder="Full Name" 
                  required 
                />
                
                <div className="flex gap-3">
                  <div className="relative flex items-center flex-grow border-2 border-gray-200 rounded-xl focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-300 transition-all">
                    <div className="pl-3 pr-2 text-blue-400 pointer-events-none">
                      <i className="fas fa-phone text-lg"></i>
                    </div>
                    <select
                      name="countryCode"
                      value={formData.countryCode}
                      onChange={handleChange}
                      className="bg-transparent border-none outline-none text-gray-700 cursor-pointer appearance-none pr-1"
                      required
                    >
                      {COUNTRY_CODES.map(code => (
                        <option key={code.value} value={code.value}>{code.value}</option>
                      ))}
                    </select>
                    <div className="h-6 w-px bg-gray-300 mx-1"></div>
                    <input
                      ref={phoneRef}
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="Phone Number"
                      className="flex-grow py-3 pr-4 text-gray-900 placeholder-gray-400 bg-transparent outline-none"
                      required
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleWhatsAppClick}
                    className="flex items-center justify-center w-12 bg-green-500 hover:bg-green-600 text-white rounded-xl transition-all shadow-md hover:shadow-lg"
                    title="Contact via WhatsApp"
                  >
                    <i className="fab fa-whatsapp text-xl"></i>
                  </button>
                </div>
              </div>

              <div className="mt-6">
                <InputWithIcon 
                  inputRef={emailRef}
                  icon="fa-envelope" 
                  type="email" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleChange} 
                  placeholder="Email Address" 
                  required 
                />
              </div>

              <div className="mt-6">
                <div className="flex justify-start mb-2">
                  <div className="bg-gray-100 rounded-lg p-1 flex">
                    <button
                      type="button"
                      onClick={toggleShippingDirection}
                      className={`px-4 py-2 rounded-md transition-all ${formData.shippingDirection === 'india_to_usa' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                    >
                      India 
                    </button>
                    <button
                      type="button"
                      onClick={toggleShippingDirection}
                      className={`px-4 py-2 rounded-md transition-all ${formData.shippingDirection === 'usa_to_india' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                    >
                      USA
                    </button>
                  </div>
                </div>
                <InputWithIcon 
                  inputRef={pickupAddressRef}
                  icon="fa-map-marker-alt" 
                  name="pickupAddress" 
                  value={formData.pickupAddress} 
                  onChange={handleChange} 
                  placeholder="Pickup Address" 
                  required 
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <InputWithIcon 
                  inputRef={postalCodeRef}
                  icon="fa-mail-bulk" 
                  name="postalCode" 
                  value={formData.postalCode} 
                  onChange={handlePostalCodeChange}
                  placeholder="Postal Code" 
                  required 
                  maxLength={formData.shippingDirection === 'india_to_usa' ? 6 : 5}
                />
                
                <CityInput
                  icon="fa-city"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  options={getCities()}
                  placeholder={`Select ${formData.shippingDirection === 'india_to_usa' ? 'India' : 'USA'} City`}
                  required
                  selectRef={cityRef}
                  isLookingUpCity={isLookingUpCity}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <InputWithIcon 
                  inputRef={dateRef}
                  icon="fa-calendar-day" 
                  type="date" 
                  name="date" 
                  value={formData.date} 
                  onChange={handleChange} 
                  required 
                  min={new Date().toISOString().split('T')[0]}
                />
                
                <SelectWithIcon
                  selectRef={timeRef}
                  icon="fa-clock"
                  name="time"
                  value={formData.time}
                  onChange={handleChange}
                  options={TIME_SLOTS}
                  placeholder="Time Window"
                  required
                />
              </div>
              
              <div className="mt-6 space-y-6">
                <SelectWithIcon
                  selectRef={packageTypeRef}
                  icon="fa-box"
                  name="packageType"
                  value={formData.packageType}
                  onChange={handleChange}
                  options={PACKAGE_OPTIONS.map(pkg => ({
                    value: pkg.id,
                    label: `${pkg.title} - ${pkg.description(formData.weightUnit)}`
                  }))}
                  placeholder="Select Package Type"
                  required
                />

                <WeightInput
                  weightUnit={formData.weightUnit}
                  packageWeight={formData.packageWeight}
                  onWeightChange={handleChange}
                  onUnitChange={handleUnitChange}
                  weightRef={packageWeightRef}
                />
              </div>
              
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute top-3 left-3 text-blue-400">
                    <i className="fas fa-comment-dots text-lg"></i>
                  </div>
                  <textarea
                    ref={notesRef}
                    id="notes"
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    rows="3"
                    className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
                    placeholder="Special Instructions"
                  ></textarea>
                </div>
              </div>
              
              <div className="mt-6">
                <TermsCheckbox 
                  checked={formData.terms} 
                  onChange={handleChange} 
                />
              </div>
              
              <div className="mt-8">
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`w-full inline-flex items-center justify-center px-6 py-3 rounded-xl font-semibold text-center whitespace-nowrap transition-all bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 ${isLoading ? 'opacity-75 cursor-not-allowed' : ''}`}
                >
                  {isLoading ? (
                    <>
                      <i className="fas fa-spinner fa-spin mr-2"></i> Processing...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-paper-plane mr-2 glow-icon"></i> Schedule Pickup
                    </>
                  )}
                </button>
              </div>
            </form>
          ) : (
            <SuccessMessage 
              pickupAddress={formData.pickupAddress}
              city={formData.city}
              onNewRequest={handleNewRequest}
              trackingNumber={trackingNumber}
            />
          )}
        </div>
      </div>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {
          font-family: 'Inter', sans-serif;
          margin: 0;
        }
        
        .glow-icon {
          animation: glow 2s ease-in-out infinite alternate;
        }
        
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        
        @keyframes glow {
          0% { filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.5)); }
          100% { filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.8)); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
};

export default PickupForm;