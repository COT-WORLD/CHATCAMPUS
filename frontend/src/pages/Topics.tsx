import { memo, useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { topicsList } from "../api/main";
import type { Topic } from "../types/Topic.types";
import TopicsSkeleton from "../components/TopicsSkeleton";

const Topics = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const q = new URLSearchParams(location.search).get("q") ?? "";

  const [search, setSearch] = useState(q);

  useEffect(() => {
    const id = setTimeout(() => {
      const term = search.trim();
      navigate(term ? `?q=${encodeURIComponent(term)}` : "/topics", {
        replace: true,
      });
    }, 600); // <- 600 ms debounce

    return () => clearTimeout(id);
  }, [search, navigate]);

  const { data, isLoading } = useQuery({
    queryKey: ["topicList", q],
    queryFn: () => topicsList(q).then((r) => r.data),
    staleTime: 2 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 1,
  });

  const topics = data?.topics ?? [];
  const totalTopicsCount = topics.length;

  if (isLoading) return <TopicsSkeleton />;

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#2d2d39] text-[#adb5bd] font-sans">
      <div className="bg-[#3f4156] shadow-lg rounded-lg w-full max-w-2xl p-8 flex flex-col gap-6">
        {/* Header */}
        <h2 className="relative text-2xl font-semibold flex items-center justify-center text-[#adb5bd] mb-2">
          <Link
            to="/"
            className="absolute left-0 top-1/2 -translate-y-1/2 text-[#adb5bd] hover:text-[#4e54c8] transition"
            aria-label="Back to home"
          >
            <i className="fas fa-arrow-left" />
          </Link>
          Browse Topics
        </h2>

        <input
          name="q"
          type="search"
          className="w-full p-2 rounded border border-gray-400 text-[#adb5bd] bg-transparent placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#4e54c8]"
          placeholder="Search for topics..."
          aria-label="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <ul className="mt-2 flex flex-col gap-1">
          <li>
            <Link
              to="/"
              className="flex items-center justify-between px-4 py-2 rounded transition text-[#adb5bd] font-bold hover:bg-[#edeaf6] hover:text-[#4e54c8]"
            >
              <span className="text-base">All</span>
              <span className="ml-2 text-xs opacity-80">
                {totalTopicsCount}
              </span>
            </Link>
          </li>

          <TopicsListMemo topics={topics} current={q} />
        </ul>
      </div>
    </div>
  );
};

const TopicsList = ({
  topics,
  current,
}: {
  topics: Topic[];
  current: string;
}) => (
  <>
    {topics.map((topic) => (
      <li key={topic.id}>
        <Link
          to={`/?q=${encodeURIComponent(topic.topic_name)}`}
          className={`flex items-center justify-between px-4 py-2 rounded transition text-[#adb5bd] ${
            current === topic.topic_name
              ? "bg-gradient-to-r from-[#4e54c8] to-[#8f94fb] text-white font-bold"
              : "hover:bg-[#edeaf6] hover:text-[#4e54c8]"
          }`}
        >
          <span>{topic.topic_name}</span>
          <span className="ml-2 text-xs opacity-80">{topic.room_count}</span>
        </Link>
      </li>
    ))}
  </>
);
const TopicsListMemo = memo(TopicsList);

export default Topics;
