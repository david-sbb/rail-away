<template>
  <div class="container py-5 bg-light min-vh-100">
    <!-- Enhanced Title Section -->
    <div class="bg-secondary-subtle text-danger p-4 rounded shadow-sm mb-5">
      <h1 class="text-center fw-bold display-6 mb-0" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        Ready to plan the perfect trip ?
      </h1>
    </div>



    <hr class="my-4"/>

    <!-- Time Spent Slider -->
    <div class="mb-4 text-center">
      <label class="form-label fw-semibold text-danger d-block">Time to spend</label>
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
    <div class="pb-5">
      <h2 class="h5 text-center mb-3 text-danger">Select an Activity</h2>

      <div class="d-flex flex-row flex-nowrap justify-content-center overflow-auto gap-3 px-3 pb-2">
        <div
            v-for="activity in activities"
            :key="activity.value"
            @click="selectActivity(activity.value)"
            class="activity-card position-relative text-white rounded overflow-hidden"
            :class="{'selected': selectedActivity === activity.value}"
        >
          <img
              :src="activity.image"
              alt="activity image"
              class="w-100 h-100 object-fit-cover"
          />
          <div class="overlay position-absolute top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center">
            <span class="fs-5 fw-semibold text-center px-2">{{ activity.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bottom-right Fixed Action Button -->
  <button
      class="btn btn-danger position-fixed bottom-0 end-0 m-4 fw-bold rounded-pill px-5 py-3 shadow fs-5"
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

const activities = [
  { value: 'museum', label: 'Museum', image: 'https://images.unsplash.com/photo-1514905552197-0610a4d8fd73?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
  { value: 'hiking', label: 'Hiking', image: 'https://images.unsplash.com/photo-1465188162913-8fb5709d6d57?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
  { value: 'swimming', label: 'Swimming', image: 'https://images.unsplash.com/photo-1438029071396-1e831a7fa6d8?q=80&w=1450&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D' },
];
const selectedActivity = ref<string | null>(null);


function selectActivity(activityValue: string) {
  selectedActivity.value = activityValue;
}

const router = useRouter();
let city = ref<string | null>(null);

let location;

onMounted(() => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async position => {
      location = position.coords;

      // Use OpenStreetMap Nominatim for reverse geocoding
      const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${location.latitude}&lon=${location.longitude}&format=json`);
      const data = await response.json();

      city.value = data.address.suburb;
      console.log(city)
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

    // Prepare real trip data to pass to the results page
    const tripData = {
      startTime: startTime.value,
      durationMinutes: selectedTime.value,
      activity:activities.filter(activity => activity.value == selectedActivity.value)[0].label,
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
<style>
.activity-card {
  width: 180px;
  height: 120px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  flex: 0 0 auto;
  border: 2px solid transparent;
}

.activity-card:hover {
  transform: scale(1.03);
}

.activity-card.selected {
  border-color: #dc3545; /* Bootstrap danger color */
  box-shadow: 0 0 10px rgba(220, 53, 69, 0.5);
}

.object-fit-cover {
  object-fit: cover;
}

</style>

