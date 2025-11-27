import { Link, useLocation } from "react-router-dom";
import TopicsSideBar from "../components/TopicsSideBar";
import RoomDetailsCard from "../components/RoomDetailsCard";
import ActivityCard from "../components/ActivityCard";
import type { Topic } from "../types/Topic.types";
import type { Room } from "../types/Room.types";
import type { Message } from "../types/Message.types";
import { dashboardDetails } from "../api/main";
import { useQuery } from "@tanstack/react-query";
import TopicsSideBarSkeleton from "../components/TopicsSideBarSkeleton";
import RoomDetailsCardSkeleton from "../components/RoomDetailsCardSkeleton";
import ActivityCardSkeleton from "../components/ActivityCardSkeleton";

import { memo } from "react";

const TopicsSideBarMemo = memo(TopicsSideBar);
const RoomDetailsCardMemo = memo(RoomDetailsCard);
const ActivityCardMemo = memo(ActivityCard);

const Dashboard = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const q = params.get("q") || "";
  const urlQuery = q ? `?q=${encodeURIComponent(q)}` : "";
  const { data, isLoading } = useQuery({
    queryKey: ["dashboardDetails", q],
    queryFn: () => dashboardDetails(urlQuery).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const topics: Topic[] = data?.topics ?? [];
  const topicsCount: number = data?.topics_count ?? 0;
  const roomsDetails: Room[] = data?.rooms ?? [];
  const roomMessages: Message[] = data?.room_messages ?? [];

  return (
    <div className="w-full px-3 py-6 bg-[#2d2d39] text-[#adb5bd] min-h-screen">
      <div className="flex flex-col md:flex-row gap-5">
        {isLoading ? (
          <TopicsSideBarSkeleton />
        ) : (
          <TopicsSideBarMemo topics={topics} topicsCount={topicsCount} />
        )}

        <div className="md:w-7/12">
          <div className="flex justify-between mb-4">
            <div>
              <h5 className="text-lg font-semibold">Chat Room</h5>
              <small className="text-sm text-gray-400">
                {roomsDetails.length} Rooms available
              </small>
            </div>
            <Link
              to="/createRoom"
              className="inline-flex items-center text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
            >
              <i className="fas fa-plus mr-1"></i> Create Room
            </Link>
          </div>
          {isLoading ? (
            <RoomDetailsCardSkeleton />
          ) : (
            <RoomDetailsCardMemo roomsDetails={roomsDetails} />
          )}
        </div>

        <div className="md:w-1/4">
          {isLoading ? (
            <ActivityCardSkeleton />
          ) : (
            <ActivityCardMemo roomMessages={roomMessages} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
