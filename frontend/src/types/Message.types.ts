import type { Room } from "./Room.types";
import type { UserType } from "./User.types";

export interface Message {
  id: number;
  body: string;
  created_at: Date;
  owner: UserType;
  room: Room;
}
