import { Link, useNavigate } from "react-router-dom";
import Logo from "../assets/logo.svg";
import avatarLogo from "../assets/avatar.svg";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

const Header = () => {
  const { user, phase, logout } = useAuth();
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = search.trim();
    navigate(`/${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  };

  return (
    <header className="bg-[#3f4156] text-white">
      <nav className="flex items-center justify-between p-4">
        {/* Logo */}
        <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
          <img src={Logo} alt="Logo" className="h-8" />
          <span className="text-xl font-semibold">Chat Room</span>
        </Link>

        {phase !== "idle" && (
          <form className="flex-1 flex mx-6" onSubmit={handleSubmit}>
            <input
              name="q"
              id="q"
              type="search"
              placeholder="Search here..."
              aria-label="Search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-gray-400 bg-transparent placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#71c6dd]"
            />
          </form>
        )}

        <div className="relative flex items-center space-x-3 group">
          {user?.id ? (
            <>
              <button className="peer flex items-center space-x-2 rounded-md hover:bg-gray-700 px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#71c6dd]">
                <img
                  className="w-10 h-10 rounded-full object-cover"
                  src={user.avatar || avatarLogo}
                  alt="User avatar"
                />
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium">{user.email}</p>
                  <p className="text-xs text-gray-400">@{user.first_name}</p>
                </div>
                <i className="fas fa-chevron-down text-xs transition-transform group-hover:rotate-180 peer-focus:rotate-180"></i>
              </button>

              <div
                className="absolute right-0 top-full w-48 bg-gray-800 border border-gray-700 rounded-md shadow-lg z-20 py-1
                opacity-0 pointer-events-none
                -mt-1
                group-hover:opacity-100 group-hover:pointer-events-auto
                peer-focus:opacity-100 peer-focus:pointer-events-auto
                transition-opacity"
              >
                <Link
                  to={`/editProfile/${user.id}`}
                  className="flex items-center px-4 py-2 text-sm hover:bg-gray-700"
                  onClick={() => document.body.click()}
                >
                  <i className="fas fa-tools mr-3"></i>Settings
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    logout();
                    document.body.click();
                  }}
                  className="flex items-center w-full px-4 py-2 text-sm hover:bg-gray-700 text-left"
                >
                  <i className="fas fa-sign-out-alt mr-3"></i>Logout
                </button>
              </div>
            </>
          ) : (
            <Link
              to="/login"
              className="flex items-center space-x-2 rounded-md hover:bg-gray-700 px-3 py-2"
            >
              <i className="fas fa-sign-in-alt"></i>
              <span>Login</span>
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;
