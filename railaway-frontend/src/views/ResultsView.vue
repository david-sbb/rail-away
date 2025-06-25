<template>
  <div class="app-container">
    <!-- Map (Top 50%) -->
    <div id="map" class="map-container"></div>

    <!-- Results View (Bottom 50%) -->
    <div class="results-view">
      <hr class="my-4 border border-success mt-0 border-3 w-75 mx-auto">

      <div v-if="!userLocation">Fetching your location...</div>

      <div v-else class="scroll-content">
        <div
            v-for="(segment, index) in poiSegments"
            :key="index"
            class="border rounded p-3 mb-4 shadow-sm bg-light"
        >
          <div class="row align-items-center">
            <div class="col-md-3 text-center">
              <div><strong>Start Station</strong></div>
              <div>{{ segment.start }}</div>
            </div>

            <div class="col-md-6 text-center position-relative">
              <div class="border-top border-dark" style="height: 2px; position: relative; top: 50%;"></div>
              <div class="position-absolute top-50 start-50 translate-middle bg-white px-2">
                Traveltime: {{ segment.duration }}
              </div>
            </div>

            <div class="col-md-3 text-center">
              <div><strong>End Station</strong></div>
              <div>{{ segment.end }}</div>
            </div>
          </div>

          <div class="text-center mt-3">
            <span class="badge bg-secondary fs-6">
              {{ segment.activity }} at {{ segment.place }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
});

const tripData = window.history.state as {
  startTime: string
  durationMinutes: number
  activity: string
  recommendations: any
};


// 🧠 Reactive wrapper for display
const poiSegments = computed(() =>
    tripData.recommendations.map((segment) => ({
      start: segment.start_station_name,
      end: segment.end_station_name,
      duration: `${segment.travel_time} min`,
      activity: tripData.activity,
      place: segment.end_station_name
    }))
);


const userLocation = ref<{ latitude: number; longitude: number } | null>(null);

onMounted(() => {
  const firstSegment = tripData.recommendations[0];
  const lastSegment = tripData.recommendations[tripData.recommendations.length - 1];

  const initialLat = firstSegment.start_station_lat;
  const initialLng = firstSegment.start_station_lon;

  const map = L.map('map');

  // Tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Custom icons
  const startIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/5193/5193769.png', // green flag
    iconSize: [40, 40],
    iconAnchor: [16, 40],
    popupAnchor: [0, -40]
  });

  const endIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/2107/2107961.png', // red flag
    iconSize: [40, 40],
    iconAnchor: [0, 40],
    popupAnchor: [0, -40]
  });

  const bounds = L.latLngBounds([]);
  const polylinePoints: [number, number][] = [];

  tripData.recommendations.forEach((segment, index) => {
    const startLatLng = [segment.start_station_lat, segment.start_station_lon] as [number, number];
    const endLatLng = [segment.end_station_lat, segment.end_station_lon] as [number, number];

    // Add markers with conditional icons
// Start marker
    if (index === 0) {
      L.marker(startLatLng, {icon: startIcon})
          .addTo(map)
          .bindPopup(segment.start_station_name);
    }

// End marker

    L.marker(endLatLng, {icon: endIcon})
        .addTo(map)
        .bindPopup(segment.end_station_name);

    bounds.extend(startLatLng);
    bounds.extend(endLatLng);

    polylinePoints.push(startLatLng, endLatLng); // Add both to the polyline path
  });

  // Draw red polyline through all points
  L.polyline(polylinePoints, {
    color: 'red',
    weight: 4,
    opacity: 0.8,
    smoothFactor: 1
  }).addTo(map);

  // Fit the map
  map.fitBounds(bounds, {
    padding: [60, 60],
    maxZoom: 14,
    animate: true
  });

  userLocation.value = {latitude: initialLat, longitude: initialLng};
});

</script>

<style>
/* Full app fills viewport */
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Top half: map */
.map-container {
  height: 50vh;
  width: 100%;
}

/* Bottom half: scrollable results */
.results-view {
  height: 50vh;
  overflow-y: auto;
  padding: 20px;
  background-color: white;
}

.scroll-content {
  max-width: 800px;
  margin: auto;
}

.leaflet-container {
  z-index: 1;
}

</style>
