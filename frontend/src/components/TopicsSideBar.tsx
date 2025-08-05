import { Link } from "react-router-dom";
import type { Topic } from "../types/topic.types";
import type React from "react";
interface TopicsSideBarProps {
  topics: Topic[];
  topicsCount: number;
}

const TopicsSideBar: React.FC<TopicsSideBarProps> = ({
  topics,
  topicsCount,
}) => {
  return (
    <div className="w-full md:w-1/6 px-4 py-[15px] text-[#adb5bd]  max-md:hidden">
      <h5 className="text-[#b2bdbd] mb-4 text-sm uppercase tracking-wide">
        Browse Topics
      </h5>
      <ul className="list-none p-0 m-0 max-h-[500px] overflow-y-auto scrollbar-thin scrollbar-thumb-[#6c757d] scrollbar-track-[#3f4156]">
        <li className="flex justify-between items-center bg-transparent border-none text-[#adb5bd] py-3 px-4 text-sm rounded mb-1">
          <Link
            to="/topics"
            className="text-[#b2bdbd] no-underline hover:text-[#71c6dd]"
          >
            All
          </Link>
          <span className="bg-[#51546e] text-[#b2bdbd] text-xs px-2 py-[0.3em] rounded-full">
            {topicsCount}
          </span>
        </li>
        {topics.map((topic) => (
          <li
            key={topic.id}
            className="flex justify-between items-center bg-transparent border-none text-[#0e2945] py-3 px-4 text-sm rounded mb-1"
          >
            <Link
              to={`/?q=${encodeURIComponent(topic.topic_name)}`}
              className="text-[#e5e5e5] no-underline hover:text-[#71c6dd]"
            >
              {topic.topic_name}
            </Link>
            <span className="bg-[#51546e] text-[#b2bdbd] text-xs px-2 py-[0.3em] rounded-full">
              {topic.room_count}
            </span>
          </li>
        ))}
      </ul>
      <Link
        to="/topics"
        className="mt-2 block text-[#78c2ad] no-underline text-sm hover:underline"
      >
        More <i className="fas fa-chevron-down fa-xs" />
      </Link>
    </div>
  );
};

export default TopicsSideBar;
