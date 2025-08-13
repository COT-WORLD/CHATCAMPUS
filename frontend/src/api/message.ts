import api from "./axios";

export const createMessageInRoom = (id: string, data: { body: string }) =>
  api.post(`roomDetails/${id}/`, data);

export const deleteMessageInRoom = (id: number) =>
  api.delete(`messageDelete/${id}/`);
