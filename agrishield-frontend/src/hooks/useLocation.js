import { useState } from "react";

export default function useLocation() {
  const [location, setLocation] = useState(null);
  const [loadingLocation, setLoadingLocation] = useState(false);

  const getCurrentLocation = () => {
    setLoadingLocation(true);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });

        setLoadingLocation(false);
      },
      (error) => {
        console.error(error);
        setLoadingLocation(false);
      }
    );
  };

  return {
    location,
    loadingLocation,
    getCurrentLocation,
  };
}