import React from 'react';
import { Link } from 'react-router-dom';

const BreadCrumbs = ({ product }) => {
    return (
        <nav className="text-sm text-gray-500 my-4">
            <ol className="list-none p-0 inline-flex space-x-2">
                <li>
                    <Link to="/" className="text-gray-800 hover:text-indigo-600">
                        Home
                    </Link>
                    <span className="mx-2">/</span>
                </li>
                <li className='inline-flex items-center'>
                    <Link to={`/category/${product && product.category}`} className="text-gray-800 hover:text-indigo-600">
                        {product && product.category}
                    </Link>
                    <span className="mx-2">/</span>
                </li>
                <li className='inline-flex items-center'>
                    <span className="text-gray-700 capitalize">{product && product.name}</span>
                </li>
            </ol>
        </nav>
    )
}

export default BreadCrumbs;