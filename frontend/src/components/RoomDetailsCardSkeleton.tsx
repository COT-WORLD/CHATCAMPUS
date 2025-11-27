import type React from "react";

const RoomDetailsCardSkeleton: React.FC = () => (
  <div className="w-full space-y-4">
    {Array.from({ length: 10 }).map((_, i) => (
      <div
        key={i}
        className="bg-[#3f4156] border border-[#495057] rounded-lg p-4"
      >
        {/* header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-600 animate-pulse" />
            <div className="h-4 w-24 bg-gray-600 rounded animate-pulse" />
          </div>
          <div className="h-3 w-20 bg-gray-600 rounded animate-pulse" />
        </div>

        {/* title */}
        <div className="mt-3 h-5 w-3/4 bg-gray-600 rounded animate-pulse" />

        {/* divider */}
        <hr className="border-[#495057] my-3" />

        {/* footer */}
        <div className="flex justify-between items-center">
          <div className="h-4 w-28 bg-gray-600 rounded animate-pulse" />
          <div className="h-4 w-16 bg-gray-600 rounded animate-pulse" />
        </div>
      </div>
    ))}
  </div>
);

export default RoomDetailsCardSkeleton;
