import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import {SERVICES} from "../data/services.js";

export default function ServicesPage() {
  const { locationId } = useParams();
  const [services, setServices] = useState([]);

  useEffect(() => {
    setServices(SERVICES[locationId]);
  }, [locationId]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">
        Services at Location #{locationId}
      </h1>

      {services?.length > 0 ? (
        <ul className="space-y-4">
          {services.map((service, idx) => (
            <li key={idx} className="border p-4 rounded-lg">
              <h3 className="text-lg font-semibold">{service.name}</h3>
              <p className="text-gray-600 mt-1">{service.description}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500">No services listed for this location.</p>
      )}
    </div>
  );
}