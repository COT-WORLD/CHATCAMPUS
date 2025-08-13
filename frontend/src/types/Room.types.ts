import type { Topic } from "./Topic.types";
import type { UserType } from "./User.types";

export interface Room {
  id: number;
  room_name: string;
  room_description: string;
  owner: UserType;
  created_at: Date;
  participants_count: number;
  topic_details: Topic;
}
