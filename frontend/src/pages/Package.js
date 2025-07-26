import React, { useState, useEffect } from 'react';

export default function PackageForm() {
  const [packages, setPackages] = useState([
    {
      pickupId: '',
      weight: '',
      length: '',
      width: '',
      height: '',
      dimensionUnit: 'cm',
      contentsDescription: '',
      packagingStatus: '',
    },
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Load Tailwind & FontAwesome…
  useEffect(() => {
    const t = document.createElement('script');
    t.src = 'https://cdn.tailwindcss.com';
    document.head.appendChild(t);
    const f = document.createElement('link');
    f.rel = 'stylesheet';
    f.href =
      'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(f);
    return () => {
      document.head.removeChild(t);
      document.head.removeChild(f);
    };
  }, []);

  const handleChange = (idx, e) => {
    const { name, value } = e.target;
    setPackages((pkgs) => {
      const copy = [...pkgs];
      copy[idx] = { ...copy[idx], [name]: value };
      return copy;
    });
  };

  const addPackage = () => {
    setPackages((pkgs) => [
      ...pkgs,
      {
        pickupId: '',
        weight: '',
        length: '',
        width: '',
        height: '',
        dimensionUnit: 'cm',
        contentsDescription: '',
        packagingStatus: '',
      },
    ]);
  };

  const removePackage = (idx) => {
    setPackages((pkgs) => pkgs.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage('');

    try {
      await Promise.all(
        packages.map((pkg) => {
          const dims = `${pkg.length}x${pkg.width}x${pkg.height}${pkg.dimensionUnit}`;
          return fetch('http://localhost:8000/api/package-details/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              // now posting raw pickup_id
              pickup_id: parseInt(pkg.pickupId, 10),
              weight: parseFloat(pkg.weight),
              dimensions: dims,
              contents_description: pkg.contentsDescription,
              packaging_status: pkg.packagingStatus,
            }),
          }).then(async (res) => {
            if (!res.ok) {
              let errText = `HTTP ${res.status}`;
              try {
                const body = await res.json();
                errText = body.detail || JSON.stringify(body);
              } catch {}
              throw new Error(errText);
            }
          });
        })
      );
      setSubmitted(true);
    } catch (err) {
      console.error('Submit error:', err);
      setErrorMessage(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-green-50 p-4">
        <div className="bg-white p-8 rounded-xl shadow-lg text-center">
          <i className="fas fa-check-circle text-4xl text-green-500 mb-4"></i>
          <h2 className="text-2xl font-semibold mb-2">All Packages Created!</h2>
          <button
            onClick={() => {
              setSubmitted(false);
              setPackages([
                {
                  pickupId: '',
                  weight: '',
                  length: '',
                  width: '',
                  height: '',
                  dimensionUnit: 'cm',
                  contentsDescription: '',
                  packagingStatus: '',
                },
              ]);
            }}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Create More
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-3xl bg-white rounded-2xl shadow-xl p-8 space-y-8"
      >
        <h1 className="text-3xl font-bold text-center">New Package Details</h1>

        {packages.map((pkg, idx) => (
          <div key={idx} className="border p-4 rounded-lg space-y-4 relative">
            {packages.length > 1 && (
              <button
                type="button"
                onClick={() => removePackage(idx)}
                className="absolute top-2 right-2 text-red-500 hover:text-red-700"
                title="Remove this package"
              >
                <i className="fas fa-trash-alt"></i>
              </button>
            )}

            {/* Pickup ID */}
            <div>
              <label
                htmlFor={`pickupId-${idx}`}
                className="block font-medium mb-1"
              >
                Pickup Request ID
              </label>
              <input
                type="number"
                id={`pickupId-${idx}`}
                name="pickupId"
                value={pkg.pickupId}
                onChange={(e) => handleChange(idx, e)}
                required
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
                placeholder="e.g. 42"
              />
            </div>

            {/* Weight */}
            <div>
              <label
                htmlFor={`weight-${idx}`}
                className="block font-medium mb-1"
              >
                Weight (kg)
              </label>
              <input
                type="number"
                step="0.01"
                id={`weight-${idx}`}
                name="weight"
                value={pkg.weight}
                onChange={(e) => handleChange(idx, e)}
                required
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
                placeholder="e.g. 2.50"
              />
            </div>

            {/* Dimensions */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {['length', 'width', 'height'].map((dim) => (
                <div key={dim}>
                  <label
                    htmlFor={`${dim}-${idx}`}
                    className="block text-sm mb-1 capitalize"
                  >
                    {dim}
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    id={`${dim}-${idx}`}
                    name={dim}
                    value={pkg[dim]}
                    onChange={(e) => handleChange(idx, e)}
                    required
                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
                    placeholder={`e.g. ${
                      dim === 'length' ? '30' : dim === 'width' ? '20' : '10'
                    }`}
                  />
                </div>
              ))}

              <div className="flex items-center space-x-6 mt-6">
                {['cm', 'in'].map((unit) => (
                  <label key={unit} className="inline-flex items-center">
                    <input
                      type="radio"
                      name="dimensionUnit"
                      value={unit}
                      checked={pkg.dimensionUnit === unit}
                      onChange={(e) => handleChange(idx, e)}
                      className="form-radio"
                    />
                    <span className="ml-2">
                      {unit === 'cm' ? 'cm' : 'inches'}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Contents */}
            <div>
              <label
                htmlFor={`contents-${idx}`}
                className="block font-medium mb-1"
              >
                Contents Description
              </label>
              <textarea
                id={`contents-${idx}`}
                name="contentsDescription"
                value={pkg.contentsDescription}
                onChange={(e) => handleChange(idx, e)}
                rows={3}
                required
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
                placeholder="Describe what’s inside…"
              />
            </div>

            {/* Packaging Status */}
            <div>
              <label htmlFor={`status-${idx}`} className="block font-medium mb-1">
                Packaging Status
              </label>
              <select
                id={`status-${idx}`}
                name="packagingStatus"
                value={pkg.packagingStatus}
                onChange={(e) => handleChange(idx, e)}
                required
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
              >
                <option value="" disabled>
                  Select status…
                </option>
                <option value="boxed">Boxed</option>
                <option value="loose">Loose</option>
                <option value="fragile">Fragile</option>
              </select>
            </div>
          </div>
        ))}

        {errorMessage && (
          <p className="text-red-600 font-medium">{errorMessage}</p>
        )}

        <div className="flex justify-between items-center">
          <button
            type="button"
            onClick={addPackage}
            className="flex items-center space-x-2 text-blue-600 hover:underline"
          >
            <i className="fas fa-plus"></i>
            <span>Add Another Package</span>
          </button>

          <button
            type="submit"
            disabled={isSubmitting}
            className={`px-6 py-3 rounded-lg text-white font-semibold transition ${
              isSubmitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSubmitting ? (
              <i className="fas fa-spinner fa-spin mr-2"></i>
            ) : (
              <i className="fas fa-box-open mr-2"></i>
            )}
            {isSubmitting ? 'Submitting…' : 'Create Packages'}
          </button>
        </div>
      </form>
    </div>
  );
}
