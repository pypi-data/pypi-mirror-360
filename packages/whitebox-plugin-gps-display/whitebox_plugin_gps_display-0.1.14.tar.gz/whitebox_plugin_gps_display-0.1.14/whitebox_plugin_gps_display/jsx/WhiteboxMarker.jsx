import { useEffect, useRef } from "react";
import { Marker, useMap } from "react-leaflet";
import useMapStore from "./stores/map";

import './utils/leaflet_patch.js';

const WhiteboxMarker = () => {
  const map = useMap();

  const whiteboxMarkerRef = useMapStore((state) => state.whiteboxMarkerRef);
  const whiteboxCoordinates = useMapStore((state) => state.whiteboxCoordinates);
  const setWhiteboxMarkerRef = useMapStore((state) => state.setWhiteboxMarkerRef);

  const defaultFollowZoom = useMapStore((state) => state.defaultFollowZoom);
  const follow = useMapStore((state) => state.follow);
  const setFollow = useMapStore((state) => state.setFollow);

  const markerRef = useRef(whiteboxMarkerRef);

  // When the component mounts, we set the marker reference in the store and
  // update it every time the marker reference changes.
  useEffect(() => {
    setWhiteboxMarkerRef(markerRef);
  }, [setWhiteboxMarkerRef, markerRef.current]);

  useEffect(() => {
    if (!whiteboxCoordinates) return;

    // Animate the map
    if (follow) {
      map.flyTo(whiteboxCoordinates);
    }

    // Move the marker without the full re-render
    if (markerRef.current) {
      markerRef.current.setLatLng(whiteboxCoordinates);
    }
  }, [map, whiteboxCoordinates]);

  // If the marker location does not exist, do not render anything
  if (!whiteboxCoordinates) return null;

  return (
      <Marker
        position={whiteboxCoordinates}
        ref={markerRef}
        eventHandlers={{
          click: () => {
            map.setView(whiteboxCoordinates, defaultFollowZoom);
            setFollow(true);
          },
        }}
      />
  );
};

export { WhiteboxMarker };
export default WhiteboxMarker;
