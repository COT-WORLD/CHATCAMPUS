import { Link, useLocation } from "react-router-dom";
import TopicsSideBar from "../components/TopicsSideBar";
import RoomDetailsCard from "../components/RoomDetailsCard";
import ActivityCard from "../components/ActivityCard";
import { useEffect, useState } from "react";
import type { Topic } from "../types/Topic.types";
import type { Room } from "../types/Room.types";
import type { Message } from "../types/Message.types";
import { dashboardDeatils } from "../api/main";
import Loader from "../components/Loader";

const Dashboard = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [topicsCount, setTopicsCount] = useState<number>(0);
  const [roomsDetails, setRoomsDetails] = useState<Room[]>([]);
  const [roomMessages, setRoomMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const location = useLocation();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams(location.search);
        const q = params.get("q") || "";
        const url = q ? `?q=${encodeURIComponent(q)}` : "";
        const response = await dashboardDeatils(url);
        setTopics(response.data?.topics);
        setTopicsCount(response.data?.topics_count);
        setRoomsDetails(response.data?.rooms);
        setRoomMessages(response.data?.room_messages);
      } catch (error) {
        console.error(`Dashboard details retrive error${error}`);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [location.search]);

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="w-full px-3 py-6 bg-[#2d2d39] text-[#adb5bd] min-h-screen">
      <div className="flex flex-col md:flex-row gap-5">
        <TopicsSideBar topics={topics} topicsCount={topicsCount} />

        <div className="md:w-7/12">
          <div className="flex justify-between mb-4">
            <div>
              <h5 className="text-lg font-semibold">Chat Room</h5>
              <small className="text-sm text-gray-400">
                {2} Rooms available
              </small>
            </div>
            <Link
              to="/createRoom"
              className="inline-flex items-center text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
            >
              <i className="fas fa-plus mr-1"></i> Create Room
            </Link>
          </div>
          <RoomDetailsCard roomsDetails={roomsDetails} />
        </div>

        <div className="md:w-1/4">
          <ActivityCard roomMessages={roomMessages} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
