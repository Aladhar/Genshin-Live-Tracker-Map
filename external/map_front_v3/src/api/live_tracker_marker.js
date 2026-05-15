import * as L from "leaflet";
import { map } from "./map_obj";

const trackerUrl = "/tracker/latest.json";
const defaultTileUnit = 1024;

let marker = null;
let pollTimer = null;
let styleInstalled = false;

const trackerIcon = L.divIcon({
  className: "live-tracker-marker",
  html: `<span class="live-tracker-marker__dot"></span><span class="live-tracker-marker__ring"></span>`,
  iconSize: [30, 30],
  iconAnchor: [15, 15],
});

function ensureMarker() {
  if (marker || !map.value) {
    return marker;
  }
  installTrackerStyle();
  marker = L.marker([0, 0], {
    icon: trackerIcon,
    interactive: false,
    zIndexOffset: 1000000,
  }).addTo(map.value);
  return marker;
}

function installTrackerStyle() {
  if (styleInstalled) {
    return;
  }
  const style = document.createElement("style");
  style.textContent = `
    .live-tracker-marker {
      pointer-events: none;
    }
    .live-tracker-marker__dot,
    .live-tracker-marker__ring {
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
      border-radius: 50%;
    }
    .live-tracker-marker__dot {
      width: 12px;
      height: 12px;
      background: #28d8ff;
      border: 2px solid #ffffff;
      box-shadow: 0 0 12px rgba(40, 216, 255, 0.9);
    }
    .live-tracker-marker__ring {
      width: 26px;
      height: 26px;
      border: 2px solid rgba(40, 216, 255, 0.7);
    }
    .live-tracker-marker--candidate .live-tracker-marker__dot {
      background: #ffb020;
      box-shadow: 0 0 12px rgba(255, 176, 32, 0.9);
    }
    .live-tracker-marker--candidate .live-tracker-marker__ring {
      border-color: rgba(255, 176, 32, 0.75);
    }
  `;
  document.head.appendChild(style);
  styleInstalled = true;
}

function removeMarker() {
  if (marker && map.value) {
    map.value.removeLayer(marker);
  }
  marker = null;
}

function numericValue(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : null;
}

function firstNumeric(...values) {
  for (const value of values) {
    const numberValue = numericValue(value);
    if (numberValue !== null) {
      return numberValue;
    }
  }
  return null;
}

function deriveMapPosition(payload) {
  const payloadPosition = payload?.map_position;
  const payloadLat = numericValue(payloadPosition?.lat);
  const payloadLng = numericValue(payloadPosition?.lng);
  if (payloadLat !== null && payloadLng !== null) {
    return { lat: payloadLat, lng: payloadLng, accepted: true };
  }

  const candidatePosition = payload?.candidate_position;
  const candidateLat = numericValue(candidatePosition?.lat);
  const candidateLng = numericValue(candidatePosition?.lng);
  if (candidateLat !== null && candidateLng !== null) {
    return { lat: candidateLat, lng: candidateLng, accepted: false };
  }

  const result = payload?.result || {};
  const topCandidates = Array.isArray(result.top_candidates)
    ? result.top_candidates
    : [];
  const candidate = topCandidates[0] || {};
  const tileX = firstNumeric(result.tile_x, candidate.tile_x);
  const tileY = firstNumeric(result.tile_y, candidate.tile_y);
  const localX = firstNumeric(
    result.local_x,
    candidate.local_x,
    result.candidate_local_x,
  );
  const localY = firstNumeric(
    result.local_y,
    candidate.local_y,
    result.candidate_local_y,
  );
  const mapWidth = firstNumeric(result.map_width, candidate.map_width);
  const mapHeight = firstNumeric(result.map_height, candidate.map_height);

  if (
    tileX !== null &&
    tileY !== null &&
    localX !== null &&
    localY !== null &&
    mapWidth !== null &&
    mapHeight !== null
  ) {
    const tileUnit = firstNumeric(payload.frontend_tile_unit, defaultTileUnit);
    return {
      lat: tileX * tileUnit + (localX * tileUnit) / mapWidth,
      lng: tileY * tileUnit + (localY * tileUnit) / mapHeight,
      accepted: !!payload?.accepted,
    };
  }

  const x = firstNumeric(result.x, result.candidate_x);
  const y = firstNumeric(result.y, result.candidate_y);
  return x !== null && y !== null
    ? { lat: x, lng: y, accepted: !!payload?.accepted }
    : null;
}

async function updateLiveTrackerMarker() {
  if (!map.value) {
    return;
  }

  try {
    const response = await fetch(`${trackerUrl}?t=${Date.now()}`, {
      cache: "no-store",
    });
    if (!response.ok) {
      removeMarker();
      return;
    }

    const payload = await response.json();
    const position = deriveMapPosition(payload);
    if (!position) {
      removeMarker();
      return;
    }

    const nextMarker = ensureMarker();
    nextMarker?.setLatLng([position.lat, position.lng]);
    nextMarker
      ?.getElement()
      ?.classList.toggle("live-tracker-marker--candidate", !position.accepted);
  } catch {
    removeMarker();
  }
}

export function startLiveTrackerMarker(intervalMs = 750) {
  stopLiveTrackerMarker();
  updateLiveTrackerMarker();
  pollTimer = window.setInterval(updateLiveTrackerMarker, intervalMs);
}

export function stopLiveTrackerMarker() {
  if (pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
  removeMarker();
}
