import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function GoogleMapComponent({ locations }) {
  const mapRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!window.google || !locations.length) return;

    const map = new window.google.maps.Map(mapRef.current, {
      zoom: 5,
      center: {
        lat: locations[0].lat,
        lng: locations[0].lng,
      },
    });

    locations.forEach((loc) => {
      const marker = new window.google.maps.Marker({
        position: { lat: loc.lat, lng: loc.lng },
        map,
        title: loc.name,
      });

      marker.addListener("click", () => {
        navigate(`/services/${loc.id}`);
      });
    });
  }, [locations, navigate]);

  return <div className="w-full h-[80vh]" ref={mapRef}></div>;
}
