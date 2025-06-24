import { useState, useEffect } from 'react';

export default function PickupForm() {
  const [formData, setFormData] = useState({
  name: '',
  phone: '',
  countrycode: '',
  email: '',
  pickupAddress: '',
  postalCode: '',  
  City: '',
  date: '',
  time: '',
  notes: '',
  terms: false,
  weightUnit: 'kg',
  packageWeight: '',
  isWhatsapp: false 
});


  const [selectedPackage, setSelectedPackage] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  useEffect(() => {
    const tailwindScript = document.createElement('script');
    tailwindScript.src = 'https://cdn.tailwindcss.com';
    document.head.appendChild(tailwindScript);

    const fontAwesome = document.createElement('link');
    fontAwesome.rel = 'stylesheet';
    fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(fontAwesome);

    return () => {
      document.head.removeChild(tailwindScript);
      document.head.removeChild(fontAwesome);
    };
  }, [])
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
      createConfetti();
    }, 1500);
  };
  const handleNewRequest = () => {
    setIsSubmitted(false);
    setFormData({
  name: '',
  phone: '',
  email: '',
  pickupAddress: '',
  City: '',
  date: '',
  time: '',
  notes: '',
  terms: false,
  weightUnit: 'kg',
  packageWeight: '',
  isWhatsapp: false 
});

    setSelectedPackage('');
  };
  const createConfetti = () => {
    const container = document.createElement('div');
    container.className = 'fixed inset-0 pointer-events-none z-50';
    document.body.appendChild(container);

    for (let i = 0; i < 50; i++) {
      const dot = document.createElement('div');
      dot.className = 'absolute w-2 h-2 rounded-full bg-blue-500';
      dot.style.left = `${Math.random() * 100}vw`;
      dot.style.top = `${Math.random() * 100}vh`;
      dot.style.opacity = '0.8';
      dot.style.transform = `scale(${Math.random() * 0.5 + 0.5})`;
      container.appendChild(dot);

      setTimeout(() => {
        dot.style.transition = 'all 1s ease-out';
        dot.style.transform += ' translateY(-20px)';
        dot.style.opacity = '0';
      }, 100);
    }

    setTimeout(() => {
      container.remove();
    }, 1000);
  };
const packageOptions = [
  {
    id: 'small',
    icon: 'fa-box-open',
    title: 'Small',
    description: formData.weightUnit === 'kg' ? 'Up to 5kg' : 'Up to 11lb'
  },
  {
    id: 'medium',
    icon: 'fa-box',
    title: 'Medium',
    description: formData.weightUnit === 'kg' ? '5-15kg' : '11-33lb'
  },
  {
    id: 'large',
    icon: 'fa-boxes',
    title: 'Large',
    description: formData.weightUnit === 'kg' ? '15-30kg' : '33-66lb'
  },
  {
    id: 'oversized',
    icon: 'fa-pallet',
    title: 'Oversized',
    description: formData.weightUnit === 'kg' ? '30kg+' : '66lb+'
  },
    {
    id: 'document',
    icon: 'fa-file-lines',
    title: 'Document',
    description: 'Paperwork etc.'
  },
  {
  id: 'medicine',
  icon: 'fa-kit-medical',
  title: 'Medicine',
  description: 'Pharmacy items'
}


];

  const cityOptions = [
    'New York',
    'Los Angeles',
    'Chicago',
    'Houston',
    'Phoenix',
    'Philadelphia',
    'San Antonio',
    'San Diego',
    'Dallas',
    'San Jose'
  ];

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="relative bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 overflow-hidden">
  {/* Background Glow */}
  <div className="absolute inset-0 bg-[radial-gradient(circle,rgba(255,255,255,0.15)_0%,rgba(255,255,255,0)_70%)]"></div>
<div className="relative flex flex-col items-center text-center">
  <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mb-6 animate-float">
    <i className="fas fa-truck-fast text-3xl text-white glow-icon"></i>
  </div>
  <h1 className="text-4xl font-bold mb-3">Pickup Request</h1>
  <p className="text-white/90 max-w-md">
    Schedule your pickup with our lightning-fast delivery network
  </p>
</div>
</div> 
        <div className="p-8">
          {!isSubmitted ? (
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                <div className="form-group">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <i className="fas fa-user text-blue-400 text-lg animate-pulse-slow"></i>
                    </div>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
                      placeholder="Full Name"
                      required
                    />
                  </div>
                </div>
                
                
 <div className="form-group">
  <div className="flex gap-3">
    {/* Combined phone input */}
    <div className="relative flex items-center flex-grow border-2 border-gray-200 rounded-xl focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-300 transition-all">
      {/* Phone icon */}
      <div className="pl-3 pr-2 text-blue-400 pointer-events-none">
        <i className="fas fa-phone text-lg"></i>
      </div>

      {/* Country code select */}
      <select
        name="countryCode"
        value={formData.countryCode}
        onChange={handleChange}
        className="bg-transparent border-none outline-none text-gray-700 cursor-pointer appearance-none pr-2"
      >
        <option value="+1">+1</option>
        <option value="+91">+91</option>
      </select>

      {/* Divider */}
      <div className="h-6 w-px bg-gray-300 mx-2"></div>

      {/* Phone number input */}
      <input
        type="tel"
        name="phone"
        value={formData.phone}
        onChange={handleChange}
        placeholder="Phone Number"
        className="flex-grow py-3 pr-4 text-gray-900 placeholder-gray-400 bg-transparent outline-none"
        required
      />
    </div>

    {/* WhatsApp Icon Button */}
    <a
      href={`https://wa.me/${(formData.countryCode || '+1').replace('+', '')}${formData.phone}`}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center justify-center w-12 h-12 bg-green-500 hover:bg-green-600 text-white rounded-xl shadow-md transition-all"
      title="Chat on WhatsApp"
    >
      <i className="fab fa-whatsapp text-2xl"></i>
    </a>
  </div>
</div>
</div>

              {/* Email */}
              <div className="form-group mt-6">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <i className="fas fa-envelope text-blue-400 text-lg animate-float"></i>
                  </div>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
                    placeholder="Email Address"
                    required
                  />
                </div>
              </div>
              
              {/* Address Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                {/* Pickup Address */}
                <div className="form-group">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <i className="fas fa-map-marker-alt text-blue-400 text-lg glow-icon"></i>
                    </div>
                    <input
                      type="text"
                      id="pickupAddress"
                      name="pickupAddress"
                      value={formData.pickupAddress}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
                      placeholder="Pickup Address"
                      required
                    />
                  </div>
                </div>
                {/* Postal Code */}
<div className="form-group">
  <div className="relative">
    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
      <i className="fas fa-mail-bulk text-blue-400 text-lg"></i>
    </div>
    <input
      type="text"
      id="postalCode"
      name="postalCode"
      value={formData.postalCode || ''}
      onChange={handleChange}
      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
      placeholder="Postal Code"
      required
    />
  </div>
</div>

                
                {/* Destination City */}
                <div className="form-group">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <i className="fas fa-city text-blue-400 text-lg"></i>
                    </div>
                    <select
                      id="City"
                      name="City"
                      value={formData.City}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200 appearance-none"
                      required
                    >
                      <option value="" disabled> City</option>
                      {cityOptions.map((city) => (
                        <option key={city} value={city}>{city}</option>
                      ))}
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                      <i className="fas fa-chevron-down text-gray-400"></i>
                    </div>
                  </div>
                </div>
              </div>
              
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                {/* Date */}
                <div className="form-group">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <i className="fas fa-calendar-day text-blue-400 text-lg"></i>
                    </div>
                    <input
                      type="date"
                      id="date"
                      name="date"
                      value={formData.date}
                      onChange={handleChange}
                      min={new Date().toISOString().split('T')[0]}
                      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
                      required
                    />
                  </div>
                </div>
                
                {/* Time */}
                <div className="form-group">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <i className="fas fa-clock text-blue-400 text-lg animate-pulse-slow"></i>
                    </div>
                    <select
                      id="time"
                      name="time"
                      value={formData.time}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200 appearance-none"
                      required
                    >
                      <option value="" disabled>Time Window</option>
                      <option value="9am-12pm">Morning (9AM-12PM)</option>
                      <option value="12pm-3pm">Afternoon (12PM-3PM)</option>
                      <option value="3pm-6pm">Late Afternoon (3PM-6PM)</option>
                      <option value="6pm-9pm">Evening (6PM-9PM)</option>
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                      <i className="fas fa-chevron-down text-gray-400"></i>
                    </div>
                  </div>
                </div>
              </div>
              
              
              <div className="form-group mt-6">
                <div className="flex justify-between items-center mb-2">
                  <label className="block font-medium text-gray-700">
                  </label>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">Weight Unit:</span>
                    <div className="flex bg-gray-100 rounded-lg p-1">
                      <button
                        type="button"
                        onClick={() => setFormData({...formData, weightUnit: 'kg'})}
                        className={`px-3 py-1 text-sm rounded-md transition-all ${formData.weightUnit === 'kg' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-200'}`}
                      >
                        kg
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormData({...formData, weightUnit: 'lb'})}
                        className={`px-3 py-1 text-sm rounded-md transition-all ${formData.weightUnit === 'lb' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-200'}`}
                      >
                        lb
                      </button>
                    </div>
                  </div>
                </div>
                
                <div className="relative mt-2">
  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
    <i className="fas fa-box text-blue-400 text-lg"></i>
  </div>
  <select
    id="packageType"
    name="packageType"
    value={selectedPackage}
    onChange={(e) => setSelectedPackage(e.target.value)}
    className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200 appearance-none"
    required
  >
    <option value="" disabled>Select Package Type</option>
    {packageOptions.map((pkg) => (
      <option key={pkg.id} value={pkg.id}>
        {pkg.title} - {pkg.description}
      </option>
    ))}
  </select>
  <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
    <i className="fas fa-chevron-down text-gray-400"></i>
  </div>
</div>

<div className="form-group mt-6">
  <div className="relative">
    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
      <i className="fas fa-weight-hanging text-blue-400 text-lg"></i>
    </div>
    <input
      type="number"
      id="packageWeight"
      name="packageWeight"
      min="0"
      step="0.1"
      value={formData.packageWeight}
      onChange={handleChange}
      className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl transition-all focus:border-blue-500 focus:ring-blue-200"
      placeholder={`Enter weight in ${formData.weightUnit}`}
      required
    />
  </div>
</div>

              </div>
              
              {/* Notes */}
              <div className="form-group mt-6">
                <div className="relative">
                  <div className="absolute top-3 left-3 text-blue-400">
                    <i className="fas fa-comment-dots text-lg"></i>
                  </div>
                  <textarea
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
              
              {/* Terms */}
              <div className="form-group mt-6 flex items-center">
                <input
                  type="checkbox"
                  id="terms"
                  name="terms"
                  checked={formData.terms}
                  onChange={handleChange}
                  className="absolute opacity-0 h-0 w-0"
                  required
                />
                <label 
                  htmlFor="terms" 
                  className={`relative h-5 w-5 rounded-md mr-3 transition-all ${formData.terms ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'} border-2`}
                >
                  {formData.terms && (
                    <span className="absolute left-1.5 top-0.5 w-1.5 h-2.5 border-white border-r-2 border-b-2 transform rotate-45"></span>
                  )}
                </label>
                <span className="text-gray-700">
                  I agree to the <button className="text-blue-600 hover:underline" onClick={(e) => { e.preventDefault(); alert('Terms of service would be displayed here.'); }}>terms of service</button>
                </span>
              </div>
              
              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full mt-6 inline-flex items-center justify-center px-6 py-3 rounded-xl font-semibold text-center whitespace-nowrap transition-all bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 ${isLoading ? 'opacity-75 cursor-not-allowed' : ''}`}
              >
                {isLoading ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i> Processing...
                  </>
                ) : (
                  <>
                    <i className="fas fa-paper-plane mr-2 glow-icon"></i> Schedule  Pickup
                  </>
                )}
              </button>
            </form>
          ) : (
            
            <div className="text-center p-8">
              <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 bg-blue-100/20 text-blue-600 text-4xl animate-bounce">
                <i className="fas fa-check"></i>
              </div>
              <h2 className="text-2xl font-bold mb-2 text-gray-800">Pickup Scheduled!</h2>
              <p className="mb-6 text-gray-600">
                Your pickup from {formData.pickupAddress} to {formData.City} has been confirmed.
              </p>
              <button
                onClick={handleNewRequest}
                className="inline-flex items-center justify-center px-8 py-3 rounded-xl font-semibold text-center whitespace-nowrap transition-all bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-lg hover:shadow-xl"
              >
                <i className="fas fa-plus mr-2"></i> New Request
              </button>
            </div>
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
        
        .animate-pulse-slow {
          animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        .animate-bounce-slow {
          animation: bounce 1.5s infinite;
        }
        
        @keyframes glow {
          0% { filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.5)); }
          100% { filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.8)); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  );
}
