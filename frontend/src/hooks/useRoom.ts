import { useQuery } from "@tanstack/react-query";
import { getRoomDetail } from "../api/room";

const useRoom = (roomId: string | undefined) => {
  return useQuery({
    queryKey: ["roomMessages", roomId],
    queryFn: () => getRoomDetail(roomId!).then((response) => response.data),
    enabled: !!roomId,
    staleTime: 2 * 60 * 1000,
  });
};

export default useRoom;
