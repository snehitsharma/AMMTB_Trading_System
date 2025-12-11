import axios from "axios";

const api = axios.create({
    timeout: 5000,
});

// Retry Logic
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const config = error.config;
        if (!config || !config.retry) {
            config.retry = 0;
        }

        // Max Retries = 3
        if (config.retry >= 3) {
            return Promise.reject(error);
        }

        config.retry += 1;
        const delay = Math.pow(2, config.retry) * 1000; // 2s, 4s, 8s

        console.log(`⚠️ API Error. Retrying in ${delay}ms... (${config.url})`);

        await new Promise((resolve) => setTimeout(resolve, delay));
        return api(config);
    }
);

export default api;
