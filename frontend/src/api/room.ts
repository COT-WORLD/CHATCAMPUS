import api from "./axios";

type RoomCreateData = {
  topic: string;
  room_name: string;
  room_description: string;
};

export const getRoomDetailsById = (id: string) => api.get(`rooms/${id}/`);

export const createRoom = (data: RoomCreateData) => api.post("rooms/", data);
export const updateRoomById = (id: string, data: RoomCreateData) =>
  api.patch(`rooms/${id}/`, data);
