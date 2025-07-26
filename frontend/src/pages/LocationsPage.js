import { useEffect, useState } from "react";
import GoogleMapComponent from "../components/GoogleMapComponent";
import {LOCATIONS} from "../data/locations.js";

export default function LocationsPage() {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    setLocations(LOCATIONS);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Our Locations</h1>
      {locations?.length > 0 ? (
        <GoogleMapComponent locations={locations} />
      ) : (
        <p className="text-gray-500">Loading map...</p>
      )}
    </div>
  );
}
