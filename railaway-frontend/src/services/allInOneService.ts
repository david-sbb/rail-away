// services/UserService.js
import axios from 'axios'

const API_URL = 'https://your-api-url.com/api'

class UserService {
    // Get all users
    async getUsers() {
        const response = await axios.get(`${API_URL}/users`)
        return response.data
    }

    // Get a single user
    async getUser(id) {
        const response = await axios.get(`${API_URL}/users/${id}`)
        return response.data
    }

    // Create a user
    async createUser(data) {
        const response = await axios.post(`${API_URL}/users`, data)
        return response.data
    }

    // Update a user
    async updateUser(id, data) {
        const response = await axios.put(`${API_URL}/users/${id}`, data)
        return response.data
    }

    // Delete a user
    async deleteUser(id) {
        const response = await axios.delete(`${API_URL}/users/${id}`)
        return response.data
    }
}

export default new UserService()
