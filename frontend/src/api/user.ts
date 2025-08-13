import api from "./axios";

export const getUserProfileDetail = (id: string) =>
  api.get(`user/profile/${id}/`);
