import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const generateContent = async (prompt, outputOptions) => {
    try {
        const response = await axios.post(`${API_URL}/api/generate`, {
            prompt,
            output_options: outputOptions
        });

        if (response.status === 200) {
            return response.data.responses;
        } else {
            throw new Error(response.data.error);
        }
    } catch (error) {
        throw error;
    }
};
