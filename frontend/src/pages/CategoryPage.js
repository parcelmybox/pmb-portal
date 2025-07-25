import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const shippingItems = [
    {
        id: 1,
        title: 'FedEx Document Shipping',
        price: 65,
        originalPrice: 125,
        tag: 'USA2INDIA',
        image: 'https://cdn.store.link/products/deliveryhub/vhw4tp-whatsapp%20image%202025-02-11%20at%2013.40.25.jpeg?versionId=mSOKdS8hZ7KuLmh_GLmQ3PRDGRI50Zqw',
        buttonText: 'Add to cart',
    },
    {
        id: 2,
        title: 'FedEx Shipping',
        price: 87,
        originalPrice: 93,
        tag: 'India2USA',
        image: 'https://cdn.store.link/products/deliveryhub/8-zoia-pmb-shipping.jpeg?versionId=4W5HLH9osaEbCTs_pig_eyCAEHaEcjyK',
        buttonText: 'See options',
    },
    {
        id: 3,
        title: 'UPS Package',
        price: 10,
        originalPrice: 11,
        tag: 'USA2INDIA',
        image: 'https://cdn.store.link/products/deliveryhub/gfk-6n-dh-usa-to-india-flyer.png?versionId=2mpPVfldVCjbsnPuZsEqi3D.0epij9Vo',
        buttonText: 'Add to cart',
    },
];

const CategoryPage = () => {
    const { categoryName } = useParams();

    const [filters, setFilters] = useState({
        tags: [],
        priceRange: [10, 180],
    });
    const [products, setProducts] = useState([]);
    const [tagList, setTagList] = useState([]);
    const [filteredItems, setFilteredItems] = useState([]);

    const toggleTag = (tag) => {
        setFilters((prev) => ({
            ...prev,
            tags: prev.tags.includes(tag)
                ? prev.tags.filter((t) => t !== tag)
                : [...prev.tags, tag],
        }));
    };

    useEffect(() => {
        const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        fetch(`${API_URL}/api/products/fetch-category/${categoryName}/`)
            .then((response) => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then((data) => {
                console.log(data);
                const uniqueTags = [...new Set(data.map(product => product.tag))];
                setTagList(uniqueTags);
                setProducts(data);
                const filtered = data.filter((item) => {
                    const inTag = filters.tags.length === 0 || filters.tags.includes(item.tag);
                    const inPrice =
                        item.price >= filters.priceRange[0] &&
                        item.price <= filters.priceRange[1];
                    return inTag && inPrice;
                });
                console.log(filtered);
                setFilteredItems(filtered);
            });
    }, []);

    return (
        <>
            {/* Top Heading Bar */}
            <div className="border-b border-gray-200 mb-6 pb-2 pt-6 max-w">
                <div className="max-w-5xl mx-auto px-6 py-4 text-left">
                    <h2 className="text-xl font-bold">Shipping <span className='text-gray-600 font-normal'> - {filteredItems.length > 0 && (filteredItems.length)} items</span></h2>
                </div>
            </div>
            <div className="max-w-5xl mx-auto min-h-screen px-6 py-4">
                {/* Sidebar + Main content */}
                <div className="flex gap-10">
                    {/* Sidebar */}
                    <aside className="w-1/4">
                        <h3 className="text-lg font-semibold mb-3">Tag</h3>
                        <div className="space-y-2 mb-6">
                            {tagList.length > 0 && (tagList.map((tag) => (
                                <label key={tag} className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        checked={filters.tags.includes(tag)}
                                        onChange={() => toggleTag(tag)}
                                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                    />
                                    <span>{tag}</span>
                                </label>
                            )))}
                        </div>

                        <h3 className="text-lg font-semibold mb-2">Price</h3>
                        <div>
                            <input
                                type="range"
                                min="10"
                                max="180"
                                value={filters.priceRange[1]}
                                onChange={(e) =>
                                    setFilters((prev) => ({
                                        ...prev,
                                        priceRange: [prev.priceRange[0], +e.target.value],
                                    }))
                                }
                                className="w-full accent-indigo-600"
                            />

                            <div className="flex justify-between items-center mt-2 space-x-4">
                                <div className="flex flex-col">
                                    <label htmlFor="minPrice" className="text-sm text-gray-600">Min</label>
                                    <input
                                        id="minPrice"
                                        type="number"
                                        min="10"
                                        max={filters.priceRange[1]}
                                        value={filters.priceRange[0]}
                                        onChange={(e) =>
                                            setFilters((prev) => ({
                                                ...prev,
                                                priceRange: [+e.target.value, prev.priceRange[1]],
                                            }))
                                        }
                                        className="border rounded px-2 py-1 w-24"
                                    />
                                </div>

                                <div className="flex flex-col">
                                    <label htmlFor="maxPrice" className="text-sm text-gray-600">Max</label>
                                    <input
                                        id="maxPrice"
                                        type="number"
                                        min={filters.priceRange[0]}
                                        max="180"
                                        value={filters.priceRange[1]}
                                        onChange={(e) =>
                                            setFilters((prev) => ({
                                                ...prev,
                                                priceRange: [prev.priceRange[0], +e.target.value],
                                            }))
                                        }
                                        className="border rounded px-2 py-1 w-24"
                                    />
                                </div>
                            </div>
                        </div>

                    </aside>

                    {/* Main Product Content */}
                    <main className="w-full">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredItems.length > 0 && (filteredItems.map((item) => (
                                <div
                                    key={item.id}
                                    className="border rounded-lg overflow-hidden shadow hover:shadow-md transition"
                                >
                                    <div className="relative">
                                        <img
                                            src={item.images[0].image_url}
                                            alt={item.name}
                                            className="w-full h-48 object-cover"
                                        />
                                        <span className="absolute top-2 right-2 bg-indigo-100 text-indigo-600 text-sm font-semibold px-3 py-1 rounded-full">
                                            {item.tag}
                                        </span>
                                    </div>
                                    <div className="p-4">
                                        <h3 className="font-semibold truncate">{item.name}</h3>
                                        <div className="text-indigo-600 font-bold">
                                            ${item.discounted_price.toFixed(2)}
                                            <span className="text-gray-400 line-through text-sm ml-2">
                                                ${item.price.toFixed(2)}
                                            </span>
                                        </div>
                                        <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-md transition mt-5">
                                            {item.weights ? "See Options" : "Add to Cart"}
                                        </button>
                                    </div>
                                </div>
                            )))}
                        </div>
                    </main>
                </div>
            </div>
        </>
    );
};

export default CategoryPage;
