import { Link, Navigate, useParams } from "react-router-dom";
import TopicsSideBar from "../components/TopicsSideBar";
import ActivityCard from "../components/ActivityCard";
import RoomDetailsCard from "../components/RoomDetailsCard";
import defaultAvatar from "../assets/avatar.svg";
import { useAuth } from "../context/AuthContext";
import type { UserType } from "../types/User.types";
import type { Topic } from "../types/Topic.types";
import type { Room } from "../types/Room.types";
import type { Message } from "../types/Message.types";
import { getUserProfileDetail } from "../api/user";
import { useQuery } from "@tanstack/react-query";
import UserProfileDetailsSkeleton from "../components/UserProfileDetailsSkeleton";
import { memo } from "react";

const TopicsSideBarMemo = memo(TopicsSideBar);
const RoomDetailsCardMemo = memo(RoomDetailsCard);
const ActivityCardMemo = memo(ActivityCard);

const UserProfile = () => {
  const { id } = useParams<{ id?: string }>();
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;

  if (!id) return <Navigate to="/" replace />;
  const { data, isLoading, error } = useQuery({
    queryKey: ["userProfileDetails", id],
    queryFn: () => getUserProfileDetail(id).then((res) => res.data),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 14 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  if (isLoading) return <UserProfileDetailsSkeleton />;

  if (error) {
    return <div>Error loading Userprofile data.</div>;
  }

  const users: UserType = data?.user ?? [];
  const topics: Topic[] = data?.topics ?? [];
  const topicsCount: number = data?.topics_count ?? 0;
  const roomsDetails: Room[] = data?.rooms ?? [];
  const roomMessages: Message[] = data?.room_messages ?? [];
  const avatarUrl = users?.avatar ? users.avatar : defaultAvatar;
  const name = users?.first_name || users?.last_name;
  const userTag = `@${users?.first_name || users?.last_name}`;
  const isOwner = users?.id == user?.id;
  const editPath = `/editProfile/${user.id}`;

  return (
    <div className="w-full min-h-screen bg-[#2d2d39] text-[#adb5bd] font-sans">
      <div className="flex flex-wrap w-full px-3 py-4 main-container">
        <TopicsSideBarMemo topics={topics} topicsCount={topicsCount} />

        <div className="w-full md:w-7/12 px-4 chat-room-main">
          <div className="flex flex-col items-center p-5 rounded-md">
            <div className="w-[150px] h-[150px] rounded-full overflow-hidden flex justify-center items-center mb-4">
              <img
                src={avatarUrl}
                alt="User Avatar"
                className="w-full h-full object-cover"
              />
            </div>

            <div className="text-center mb-4">
              <div className="text-xl font-bold text-white">{name}</div>
              <div className="text-base text-[#b2bdbd]">{userTag}</div>
            </div>

            {isOwner && (
              <Link
                to={editPath}
                className="text-[#71c6dd] border border-[#71c6dd] py-2 px-6 rounded-[10%] text-base hover:bg-[#e5e5e526] transition duration-200"
              >
                Edit Profile
              </Link>
            )}
          </div>

          <div className="mt-6">
            <p className="text-sm mb-2 text-[#b2bdbd] uppercase tracking-[0.05em]">
              Chat Rooms Hosted by {users?.first_name?.toUpperCase()}
            </p>
          </div>
          <RoomDetailsCardMemo roomsDetails={roomsDetails} />
        </div>

        <div className="hidden md:block w-full md:w-3/12 px-4 recent-activities-sidebar">
          <ActivityCardMemo roomMessages={roomMessages} />
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
