import type { Topic } from "./topic.types";
import type { UserType } from "./user.types";

export interface Room {
  id: number;
  room_name: string;
  owner: UserType;
  created_at: Date;
  participants_count: number;
  topic_details: Topic;
}
