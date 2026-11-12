
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const detectImage = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await API.post(
    "/detect/image",
    formData
  );

  return response.data;
};

export default API;
