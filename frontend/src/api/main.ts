import api from "./axios";

export const dashboardDeatils = (url: string) => api.get(url);
