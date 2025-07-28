import React, { useState } from "react";

const SortDropdown = ({ sortMethod, setSortMethod }) => {
    const [isOpen, setIsOpen] = useState(false);

    const options = ["Default", "Price: Low to High", "Price: High to Low", "Letter: A to Z", "Letter: Z to A"];

    const toggleDropdown = () => setIsOpen(!isOpen);

    const handleSelect = (option) => {
        setSortMethod(option);
        setIsOpen(false);
    };

    return (
        <div className="relative inline-block text-left">
            <button
                onClick={toggleDropdown}
                className="flex items-center gap-1 text-gray-700 hover:text-black"
            >
                <span className="font-medium">Sort</span>
            </button>

            {isOpen && (
                <div className="absolute mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                    <div className="py-1">
                        {options.map((option, idx) => (
                            <button
                                key={idx}
                                onClick={() => handleSelect(option)}
                                className={`block w-full text-left px-4 py-2 text-sm ${sortMethod === option
                                        ? "font-semibold text-gray-900"
                                        : "text-gray-700"
                                    } hover:bg-gray-100`}
                            >
                                {option}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SortDropdown;
