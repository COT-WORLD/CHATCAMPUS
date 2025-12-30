export type WSAction =
  | { action: "Auth_check"; token: string }
  | { action: "send_message"; body: string }
  | { action: "delete_message"; message_id: number };
