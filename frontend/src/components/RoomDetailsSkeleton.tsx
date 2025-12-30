const RoomDetailsSkeleton = () => {
  return (
    <div className="flex flex-col lg:flex-row gap-4 p-5 min-h-screen bg-[#2d2d39] text-[#adb5bd] font-sans overflow-hidden">
      {/* Chat Room Card */}
      <div className="flex flex-col w-full lg:w-[70%] bg-[#3f4156] rounded-lg overflow-hidden shadow-md max-h-screen min-h-0">
        {/* Header skeleton */}
        <div className="flex justify-between items-center px-4 py-3 border-b border-[#e0e0e0] bg-[#696d97]">
          <div className="flex items-center text-white gap-2">
            <i className="fas fa-arrow-left" />
            <span className="h-5 w-32 bg-gray-500 rounded animate-pulse" />
          </div>
          <div className="flex gap-3">
            <span className="h-6 w-6 bg-gray-400 rounded animate-pulse" />
            <span className="h-6 w-6 bg-gray-400 rounded animate-pulse" />
          </div>
        </div>

        {/* Room Title skeleton */}
        <div className="p-4 flex flex-col gap-4">
          <div className="flex justify-between items-center flex-wrap gap-2">
            <span className="h-7 w-48 bg-gray-500 rounded animate-pulse" />
            <span className="h-4 w-24 bg-gray-500 rounded animate-pulse" />
          </div>
          <span className="h-5 w-40 bg-gray-500 rounded animate-pulse" />
          <span className="h-4 w-full bg-gray-500 rounded animate-pulse" />
          <span className="h-4 w-3/4 bg-gray-500 rounded animate-pulse" />
          <div className="flex gap-2 mt-2">
            <span className="h-6 w-16 bg-gray-400 rounded animate-pulse" />
          </div>
        </div>

        {/* Messages skeleton */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="mb-4 bg-[#696d97] rounded-lg p-3 shadow animate-pulse"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="h-10 w-10 bg-gray-400 rounded-full" />
                  <span className="h-4 w-28 bg-gray-400 rounded" />
                </div>
                <span className="h-3 w-20 bg-gray-400 rounded" />
              </div>
              <span className="h-4 w-full bg-gray-300 rounded" />
              <span className="h-4 w-5/6 bg-gray-300 rounded mt-1" />
            </div>
          ))}
        </div>

        {/* Input skeleton */}
        <div className="bg-[#3f4156] p-2 border-t border-gray-700">
          <span className="block h-12 w-full bg-gray-500 rounded animate-pulse" />
        </div>
      </div>

      {/* Participants skeleton */}
      <div className="w-full lg:w-[30%] bg-[#3f4156] rounded-lg shadow flex flex-col max-h-screen overflow-hidden">
        <div className="px-4 py-3 bg-[#696d97] border-b border-[#e0e0e0]">
          <span className="h-5 w-40 bg-gray-400 rounded animate-pulse" />
        </div>
        <div className="px-4 py-2 space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-start gap-3 animate-pulse">
              <span className="h-12 w-12 bg-gray-400 rounded-full" />
              <div className="flex flex-col gap-1">
                <span className="h-4 w-24 bg-gray-400 rounded" />
                <span className="h-3 w-20 bg-gray-300 rounded" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RoomDetailsSkeleton;
