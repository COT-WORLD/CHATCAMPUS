import type React from "react";

const TopicsSideBarSkeleton: React.FC = () => (
  <div className="w-full md:w-1/6 px-4 py-[15px] max-md:hidden">
    <div className="h-4 w-32 bg-gray-600 rounded mb-4 animate-pulse" />
    <ul className="space-y-2">
      {/* "All" row */}
      <li className="flex justify-between items-center py-3 px-4">
        <div className="h-4 w-12 bg-gray-600 rounded animate-pulse" />
        <div className="h-5 w-8 bg-gray-600 rounded-full animate-pulse" />
      </li>
      {/* 6 fake topics */}
      {Array.from({ length: 6 }).map((_, i) => (
        <li key={i} className="flex justify-between items-center py-3 px-4">
          <div className="h-4 w-20 bg-gray-600 rounded animate-pulse" />
          <div className="h-5 w-7 bg-gray-600 rounded-full animate-pulse" />
        </li>
      ))}
    </ul>
    <div className="mt-2 h-4 w-16 bg-gray-600 rounded animate-pulse" />
  </div>
);

export default TopicsSideBarSkeleton;
