import TopicsSideBarSkeleton from "../components/TopicsSideBarSkeleton";
import RoomDetailsCardSkeleton from "../components/RoomDetailsCardSkeleton";
import ActivityCardSkeleton from "../components/ActivityCardSkeleton";

const UserProfileDetailsSkeleton: React.FC = () => (
  <div className="w-full min-h-screen bg-[#2d2d39] text-[#adb5bd] font-sans">
    <div className="flex flex-wrap w-full px-3 py-4 main-container">
      {/* left sidebar skeleton */}
      <TopicsSideBarSkeleton />

      {/* centre skeleton */}
      <div className="w-full md:w-7/12 px-4 chat-room-main">
        {/* avatar + name skeleton */}
        <div className="flex flex-col items-center p-5 rounded-md">
          <div className="w-[150px] h-[150px] rounded-full bg-gray-600 animate-pulse mb-4" />
          <div className="h-6 w-48 bg-gray-600 rounded mb-2 animate-pulse" />
          <div className="h-4 w-32 bg-gray-600 rounded animate-pulse" />
          <div className="h-8 w-24 bg-gray-600 rounded mt-4 animate-pulse" />
        </div>

        {/* section title skeleton */}
        <div className="mt-6">
          <div className="h-4 w-64 bg-gray-600 rounded mb-2 animate-pulse" />
        </div>

        {/* rooms skeleton */}
        <RoomDetailsCardSkeleton />
      </div>

      {/* right sidebar skeleton */}
      <div className="hidden md:block w-full md:w-3/12 px-4 recent-activities-sidebar">
        <ActivityCardSkeleton />
      </div>
    </div>
  </div>
);

export default UserProfileDetailsSkeleton;
