import axios from "axios";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
} from "../utils/tokenStorage";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers = config.headers ?? {};
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      getRefreshToken()
    ) {
      originalRequest._retry = true;
      try {
        const refresh = getRefreshToken();
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}auth/token/refresh/`,
          { refresh }
        );

        const newAccess = response.data.access;
        setAccessToken(newAccess);

        api.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;
        originalRequest.headers["Authorization"] = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch (error) {
        clearTokens();
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
