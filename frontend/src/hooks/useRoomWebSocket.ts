import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import type { Message } from "types/Message.types";
import type { WSAction } from "types/Websocket.types";
import { getAccessToken } from "../utils/tokenStorage";

const WS_URL = import.meta.env.VITE_WEBSOCKET_URL;

const useRoomWebSocket = (roomId: string | undefined) => {
  const queryClient = useQueryClient();
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!roomId) return;

    const socket = new WebSocket(`${WS_URL}/ws/chat/${roomId}/`);
    ws.current = socket;

    socket.onopen = () =>
      socket.send(
        JSON.stringify({ action: "Auth_Check", token: getAccessToken() })
      );
    socket.onmessage = (e) => {
      const message = JSON.parse(e.data);
      if (message.type === "chat_message") {
        queryClient.setQueryData<Message[]>(
          ["roomMessages", roomId],
          (old: any) =>
            old ? { ...old, messages: [...old.messages, message.message] } : old
        );
      } else if (message.type === "chat_message_delete") {
        queryClient.setQueryData<Message[]>(
          ["roomMessages", roomId],
          (old: any) =>
            old
              ? {
                  ...old,
                  messages: old.messages.filter(
                    (m: Message) => m.id !== message.message_id
                  ),
                }
              : old
        );
      }
    };
    socket.onerror = (error) => console.error("Websocket error: ", error);
    socket.onclose = () => ws.current == null;

    return () => socket.close();
  }, [roomId, queryClient]);

  const send = (action: WSAction) => ws.current?.send(JSON.stringify(action));

  return { send, socket: ws.current };
};

export default useRoomWebSocket;
