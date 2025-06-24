<template>
  <div class="container py-5 bg-light min-vh-100">
    <!-- Enhanced Title Section -->
    <div class="bg-secondary-subtle text-danger p-4 rounded shadow-sm mb-5">
      <h1 class="text-center fw-bold display-6 mb-0" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        Ready to plan your perfect trip for your time?
      </h1>
    </div>

    <!-- Start Time Picker -->
    <div class="mb-4 text-center d-flex justify-content-center flex-column" >
      <label class="form-label fw-semibold text-danger d-block">Select Start Time</label>
      <input
          type="time"
          class="form-control w-50 mx-auto text-center"
          v-model="startTime"
      />
    </div>

    <hr class="my-4" />

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

    <hr class="my-4" />

    <!-- Activities Section -->
    <div class="pb-5">
      <h2 class="h5 text-center mb-3 text-danger">Select an Activity</h2>

      <div class="d-flex flex-row flex-nowrap overflow-auto gap-3 px-3 pb-2" >
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
import { ref, computed } from 'vue'

const snapPoints = [30, 60, 120, 240, 360, 480, 720, 960]
const sliderIndex = ref(0)
const startTime = ref<string>('08:00')

const selectedTime = computed(() => snapPoints[sliderIndex.value])

const formattedTime = computed(() =>
    selectedTime.value < 60
        ? `${selectedTime.value} min`
        : `${selectedTime.value / 60}h`
)

const activities = ['Hiking', 'Swimming', 'Cycling', 'Museum', 'Picnic', 'Shopping']
const selectedActivity = ref<string | null>(null)

function selectActivity(activity: string) {
  selectedActivity.value = activity
}
import { useRouter } from 'vue-router'

const router = useRouter()

function goToNextPage() {
  const tripData = {
    startTime: startTime.value,
    durationMinutes: selectedTime.value,
    activity: selectedActivity.value,
    generatedPlan: `Do ${selectedActivity.value ?? 'something fun'} for ${formattedTime.value} starting at ${startTime.value}`,
  }

  router.push({
    name: 'results',
    state: tripData
  })
}
</script>

