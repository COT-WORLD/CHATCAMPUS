import { useEffect, useState } from "react";
import type { Topic } from "../types/Topic.types";
import { topicsList } from "../api/main";
import { Link, useLocation, useNavigate } from "react-router-dom";

const Topics = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [totalTopicsCount, setTotalTopicsCount] = useState<number>(0);
  const [search, setSearch] = useState("");
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get("q") ?? "";
    if (location.search && q !== search) {
      setSearch(q);
    }
    if (search === "" && q) {
      navigate("/topics", { replace: true });
      return;
    }
    const fetchData = async () => {
      try {
        const response = await topicsList(q);
        setTopics(response.data?.topics || []);
        setTotalTopicsCount(response.data?.topics?.length || 0);
      } catch (error) {
        console.error(`Topics retriving error ${error}`);
      }
    };
    fetchData();
  }, [location.search, navigate]);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (search.trim()) {
      navigate(`?q=${encodeURIComponent(search.trim())}`);
    } else {
      navigate(`/topics`);
    }
  };

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
        {/* Search */}
        <form className="w-full" method="get" action="" onSubmit={handleSearch}>
          <input
            name="q"
            type="search"
            className="w-full p-2 rounded border border-gray-400 text-[#adb5bd] bg-transparent focus:outline-none"
            placeholder="Search for topics..."
            aria-label="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>
        <ul className="mt-2 flex flex-col gap-1">
          <li>
            <a
              href="/"
              className={`flex items-center justify-between px-4 py-2 rounded transition text-[#adb5bd] font-bold hover:bg-[#edeaf6] hover:text-[#4e54c8] `}
            >
              <span className="text-base">All</span>
              <span className="ml-2 text-xs opacity-80">
                {totalTopicsCount}
              </span>
            </a>
          </li>
          {topics?.map((topic) => (
            <li key={topic.id}>
              <Link
                to={`/?q=${encodeURIComponent(topic.topic_name)}`}
                className={`flex items-center justify-between px-4 py-2 rounded transition text-[#adb5bd] ${
                  search === topic.topic_name
                    ? "bg-gradient-to-r from-[#4e54c8] to-[#8f94fb] text-white font-bold"
                    : "hover:bg-[#edeaf6] hover:text-[#4e54c8]"
                }`}
              >
                <span>{topic.topic_name}</span>
                <span className="ml-2 text-xs opacity-80">
                  {topic.room_count}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Topics;
