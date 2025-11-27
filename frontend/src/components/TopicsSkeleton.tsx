import type React from "react";

const TopicsSkeleton: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#2d2d39] text-[#adb5bd] font-sans">
    <div className="bg-[#3f4156] shadow-lg rounded-lg w-full max-w-2xl p-8 flex flex-col gap-6">
      {/* header bar */}
      <div className="flex items-center justify-between">
        <div className="h-8 w-32 bg-gray-600 rounded animate-pulse" />
        <div className="h-6 w-6 bg-gray-600 rounded-full animate-pulse" />
      </div>

      {/* search bar */}
      <div className="h-10 w-full bg-gray-600 rounded animate-pulse" />

      {/* list items */}
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="h-10 w-full bg-gray-600 rounded animate-pulse"
        />
      ))}
    </div>
  </div>
);

export default TopicsSkeleton;
