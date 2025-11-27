import type React from "react";

const ActivityCardSkeleton: React.FC = () => (
  <div className="w-full">
    <div className="h-4 w-32 bg-gray-600 rounded mb-4 animate-pulse" />
    {Array.from({ length: 10 }).map((_, i) => (
      <div
        key={i}
        className="bg-[#3f4156] border border-[#495057] rounded-md p-4 mb-4"
      >
        {/* user row */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-600 animate-pulse" />
            <div className="h-4 w-20 bg-gray-600 rounded animate-pulse" />
          </div>
          <div className="h-3 w-16 bg-gray-600 rounded animate-pulse" />
        </div>

        {/* text line */}
        <div className="h-4 w-3/4 bg-gray-600 rounded mb-2 animate-pulse" />

        {/* message block */}
        <div className="h-10 w-full bg-gray-600 rounded-xl animate-pulse" />
      </div>
    ))}
  </div>
);

export default ActivityCardSkeleton;
