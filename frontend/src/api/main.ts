import api from "./axios";

export const dashboardDetails = (url: string) => api.get(url);
export const topicsList = (query: string) =>
  api.get(`topics/${query ? `?q=${encodeURIComponent(query)}` : ""}`);
