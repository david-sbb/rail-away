<template>
  <div class="app-container">
    <!-- Map (Top 50%) -->
    <div id="map" class="map-container"></div>

    <!-- Results View (Bottom 50%) -->
    <div class="results-view">
      <h2 class="mb-4">Event Summary</h2>
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
  const initialLat = firstSegment.start_station_lat;
  const initialLng = firstSegment.start_station_lon;

  const map = L.map('map');

// Tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

// Add all points and collect bounds
  const bounds = L.latLngBounds([]);

  tripData.recommendations.forEach(segment => {
    const startLatLng = [segment.start_station_lat, segment.start_station_lon] as [number, number];
    const endLatLng = [segment.end_station_lat, segment.end_station_lon] as [number, number];

    L.marker(startLatLng).addTo(map).bindPopup(segment.start_station_name);
    L.marker(endLatLng).addTo(map).bindPopup(segment.end_station_name);

    bounds.extend(startLatLng);
    bounds.extend(endLatLng);
  });

// Fit the map to show all markers
  map.fitBounds(bounds, {
    padding: [60, 60],
    maxZoom: 14,       // Optional: don’t zoom in too far
    animate: true      // Optional: smooth transition
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  userLocation.value = {latitude: initialLat, longitude: initialLng};

  // Add start/end markers
  tripData.recommendations.forEach(segment => {
    L.marker([segment.start_station_lat, segment.start_station_lon])
        .addTo(map)
        .bindPopup(segment.start_station_name);

    L.marker([segment.end_station_lat, segment.end_station_lon])
        .addTo(map)
        .bindPopup(segment.end_station_name);


  });
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
