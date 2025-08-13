import api from "./axios";

export const getUserProfileDetail = (id: string) =>
  api.get(`user/profile/${id}/`);

export const updateUserProfileDetailById = (data: FormData) =>
  api.patch(`user/me/`, data, {
    headers: { "Content-Type": "multipart/form-data" },
  });
