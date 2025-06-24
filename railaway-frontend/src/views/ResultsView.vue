<template>
  <div id="map" class="map-container"></div>

  <div class="results-view">
    <h2 class="mb-4">Event Summary</h2>
    <div v-if="!userLocation">Fetching your location...</div>

    <div v-else>
      <div
          v-for="(segment, index) in poiSegments"
          :key="index"
          class="border rounded p-3 mb-4 shadow-sm bg-light"
      >
        <div class="row align-items-center">
          <!-- Start -->
          <div class="col-md-3 text-center">
            <div><strong>Start Station</strong></div>
            <div>{{ segment.start }}</div>
          </div>

          <!-- Travel line with duration -->
          <div class="col-md-6 text-center position-relative">
            <div class="border-top border-dark" style="height: 2px; position: relative; top: 50%;"></div>
            <div class="position-absolute top-50 start-50 translate-middle bg-white px-2">
              Traveltime: {{ segment.duration }}
            </div>
          </div>

          <!-- End -->
          <div class="col-md-3 text-center">
            <div><strong>End Station</strong></div>
            <div>{{ segment.end }}</div>
          </div>
        </div>

        <!-- Activity label -->
        <div class="text-center mt-3">
          <span class="badge bg-secondary fs-6">
            {{ segment.activity }} at {{ segment.place }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// ✅ Segment data (normally fetched from API)
const rawSegments = [
  {
    end_station_id: 8506206,
    end_station_lat: 47.46241308,
    end_station_lon: 9.04099536,
    end_station_name: 'Wil SG',
    start_station_id: 8506210,
    start_station_lat: 47.41183485,
    start_station_lon: 9.25305167,
    start_station_name: 'Gossau SG',
    stop_features: `{
      "type": "Feature",
      "properties": {
        "route": "hiking",
        "from": "Gossau Bhf Süd",
        "to": "Buech"
      },
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [9.2534063, 47.4109195],
          [9.2534209, 47.41058],
          [9.2533347, 47.4104397],
          [9.2549828, 47.406723],
          [9.2577747, 47.4046376]
        ]
      }
    }`,
    travel_time: 17
  }
]

// 🧠 Reactive wrapper for display
const poiSegments = computed(() =>
    rawSegments.map((segment) => ({
      start: segment.start_station_name,
      end: segment.end_station_name,
      duration: `${segment.travel_time} min`,
      activity: 'Hiking',
      place: segment.end_station_name,
      route: JSON.parse(segment.stop_features)
    }))
)

const userLocation = ref<{ latitude: number; longitude: number } | null>(null)

onMounted(() => {
  const firstSegment = rawSegments[0]
  const initialLat = firstSegment.start_station_lat
  const initialLng = firstSegment.start_station_lon

  const map = L.map('map').setView([initialLat, initialLng], 13)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map)

  userLocation.value = { latitude: initialLat, longitude: initialLng }

  // Add start/end markers
  rawSegments.forEach(segment => {
    L.marker([segment.start_station_lat, segment.start_station_lon])
        .addTo(map)
        .bindPopup(segment.start_station_name)

    L.marker([segment.end_station_lat, segment.end_station_lon])
        .addTo(map)
        .bindPopup(segment.end_station_name)

    // Optional: Add hiking route as polyline
    const geo = JSON.parse(segment.stop_features)
    if (geo.geometry?.coordinates) {
      const latlngs = geo.geometry.coordinates.map(([lon, lat]) => [lat, lon])
      L.polyline(latlngs, {
        color: 'green',
        weight: 3,
        opacity: 0.7
      }).addTo(map)
    }
  })
})

</script>

<style>
.map-container {
  height: 400px;
  width: 100%;
}

.results-view {
  max-width: 800px;
  margin: auto;
  padding: 20px;
}

.leaflet-container {
  z-index: 1;
}
</style>
