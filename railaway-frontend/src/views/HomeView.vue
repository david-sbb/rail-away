<template>
  <div class="container py-5 bg-light min-vh-100">
    <!-- Enhanced Title Section -->
    <div class="bg-secondary-subtle text-danger p-4 rounded shadow-sm mb-5">
      <h1 class="text-center fw-bold display-6 mb-0" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        Ready to plan your perfect trip for your time?
      </h1>
    </div>

    <!-- Start Time Picker -->
    <div class="mb-4 text-center d-flex justify-content-center flex-column">
      <label class="form-label fw-semibold text-danger d-block">Select Start Time</label>
      <input
          type="time"
          class="form-control w-50 mx-auto text-center"
          v-model="startTime"
      />
    </div>

    <hr class="my-4"/>

    <!-- Time Spent Slider -->
    <div class="mb-4 text-center">
      <label class="form-label fw-semibold text-danger d-block">Time Spent</label>
      <input
          type="range"
          class="form-range w-75 mx-auto"
          :min="0"
          :max="snapPoints.length - 1"
          v-model="sliderIndex"
      />
      <div class="mt-2 fw-bold fs-5 text-secondary">
        {{ formattedTime }}
      </div>
    </div>

    <hr class="my-4"/>

    <!-- Activities Section -->
    <div class="pb-5">
      <h2 class="h5 text-center mb-3 text-danger">Select an Activity</h2>

      <div class="d-flex flex-row flex-nowrap overflow-auto gap-3 px-3 pb-2">
        <button
            v-for="activity in activities"
            :key="activity"
            @click="selectActivity(activity)"
            :class="[
            'btn',
            'btn-outline-danger',
            'rounded-pill',
            'px-4',
            'py-2',
            'fw-semibold',
            selectedActivity === activity ? 'btn-danger text-white' : ''
          ]"
        >
          {{ activity }}
        </button>
      </div>
    </div>
  </div>

  <!-- Bottom-right Fixed Action Button -->
  <button
      class="btn btn-danger position-fixed bottom-0 end-0 m-4 rounded-pill px-4 py-2 shadow"
      @click="goToNextPage"
  >
    Plan Trip →
  </button>
</template>


<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue';
import {useRouter} from 'vue-router';
import RecommendationService from '@/services/RecommendationService';

const snapPoints = [30, 60, 120, 240, 360, 480, 720, 960];
const sliderIndex = ref(0);
const startTime = ref<string>('08:00');

const selectedTime = computed(() => snapPoints[sliderIndex.value]);

const formattedTime = computed(() =>
    selectedTime.value < 60
        ? `${selectedTime.value} min`
        : `${selectedTime.value / 60}h`
);

const activities = ['Hiking', 'Swimming', 'Cycling', 'Museum', 'Picnic', 'Shopping'];
const selectedActivity = ref<string | null>(null);


function selectActivity(activity: string) {
  selectedActivity.value = activity;
}

const router = useRouter();
let city;

let location;

onMounted(() => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async position => {
      location = position.coords;

      // Use OpenStreetMap Nominatim for reverse geocoding
      const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${location.latitude}&lon=${location.longitude}&format=json`);
      const data = await response.json();

      city = data.address.city || data.address.town || data.address.village || 'Unknown location';
    }, error => {
      console.error('Geolocation error:', error);
      city.value = 'Permission denied or unavailable';
    });
  } else {
    city.value = 'Geolocation not supported';
  }
});


async function goToNextPage() {
  try {
    // Send request to backend for recommendations
    const recommendations = await RecommendationService.getRecommendations({
      longitude: location.longitude,     // Replace with actual longitude source
      latitude: location.latitude,       // Replace with actual latitude source
      time_to_spend: selectedTime.value,  // Assumes selectedTime is in minutes
      activity: selectedActivity.value == null ? 'park' : selectedActivity.value
    });

    const rawSegments =
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
        };
    recommendations.push(rawSegments);
    console.log(recommendations);

    // Prepare real trip data to pass to the results page
    const tripData = {
      startTime: startTime.value,
      durationMinutes: selectedTime.value,
      activity: selectedActivity.value,
      recommendations // actual results from the backend
    };

    // Navigate to results page with real data
    await router.push({
      name: 'results',
      state: tripData
    });

  } catch (error) {
    console.error('Failed to fetch recommendations:', error.message);
    // Optionally show an error message to the user
  }
}
</script>

