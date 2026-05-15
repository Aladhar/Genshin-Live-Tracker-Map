import * as L from "leaflet";
import { map } from "./map_obj";

const trackerUrl = "/tracker/latest.json";

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
    const position = payload?.map_position;
    if (!payload?.accepted || position?.lat == null || position?.lng == null) {
      removeMarker();
      return;
    }

    ensureMarker()?.setLatLng([position.lat, position.lng]);
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
