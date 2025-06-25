// services/RecommendationService.ts
import axios from 'axios'

const API_URL = 'http://localhost:5000' // Or your deployed API base URL

class RecommendationService {
    // Send user input to get recommendations
    async getRecommendations(data: {
        longitude: number
        latitude: number
        time_to_spend: number
        activity: string
    }) {
        try {
            const response = await axios.post(`${API_URL}/recommend`, data)
            return response.data
        } catch (error: any) {
            throw new Error(error.response?.data?.error || 'Failed to fetch recommendations')
        }
    }

    // Reload the CSV data on the server
    async reloadData() {
        try {
            const response = await axios.post(`${API_URL}/reload_data`)
            return response.data
        } catch (error: any) {
            throw new Error(error.response?.data?.error || 'Failed to reload data')
        }
    }
}

export default new RecommendationService()
