
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 0
});

export const detectImage = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
        "/detect/image",
        formData
    );

    return response.data;
};


export const detectVideo = async (file) => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
        "/detect/video",
        formData
    );

    return response.data;
};


export const getOutputUrl = (path) => {

    if (!path) return "";

    if (path.startsWith("http")) {
        return path;
    }

    return `${API_BASE_URL}${path}`;
};

export default api;
