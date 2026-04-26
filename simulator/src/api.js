import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const updateVehicleState = async (stateData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/update-state`, stateData);
        return response.data;
    } catch (error) {
        console.error("Error sending data to Python backend. Is the Python server running?", error);
        return null;
    }
};