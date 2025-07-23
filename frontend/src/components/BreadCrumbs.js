import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const BreadCrumbs = () => {
    const location = useLocation();
    const pathNames = location.pathname.split('/').filter((x) => x);

    return (
        <nav className="text-sm text-gray-500 my-4">
            <ol className="list-none p-0 inline-flex space-x-2">
                <li>
                    <Link to="/" className="text-gray-800 hover:text-indigo-600">
						Home
					</Link>
					<span className="mx-2">/</span>
                </li>
                    {pathNames.map((path, index) => {
                        const url = `/${pathNames.slice(0, index + 1).join('/')}`;
                        const isLastElement = index === pathNames.length - 1;

                        return (
                            <li className='inline-flex items-center'>
                                {isLastElement ? (
                                    <span className="text-gray-700 capitalize">{decodeURIComponent(path)}</span>
                                ) : (
                                    <>
                                        <Link to={url} className="text-gray-800 hover:text-indigo-600">
                                            {
                                                decodeURIComponent(path).split(' ').map((item) => (item.charAt(0).toUpperCase() + item.slice(1))).join(' ')
                                            }
                                        </Link>
                                        <span className="mx-2">/</span>
                                    </>
                                )}
                            </li>
                        );
                    })}
            </ol>
        </nav>
    )
}

export default BreadCrumbs;