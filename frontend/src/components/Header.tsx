import { Link, useNavigate, useLocation } from "react-router-dom";
import Logo from "../assets/logo.svg";
import avatarLogo from "../assets/avatar.svg";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

const Header = () => {
  const { user, logout } = useAuth();

  const location = useLocation();
  const currentPath = location.pathname;
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: any) => {
    e.preventDefault();
    const q = search.trim();
    navigate(`/${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  };
  return (
    <header>
      <nav className="flex items-center justify-between bg-[#3f4156] p-4">
        <Link to="/" className="flex items-center space-x-2 flex-shrink-0">
          <img src={Logo} alt="Logo" className="h-9" />
          <span className="text-white text-xl font-semibold">Chat Room</span>
        </Link>
        {currentPath == "/" && (
          <form className="flex-1 flex mx-6" onSubmit={handleSubmit}>
            <input
              name="q"
              id="q"
              type="search"
              placeholder="Search here..."
              aria-label="Search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="form-input w-full px-3 py-2 rounded-md border border-gray-400 text-white bg-transparent focus:outline-none"
            />
          </form>
        )}
        <div className="relative user-info text-white flex items-center space-x-2 flex-shrink-0">
          {user?.id ? (
            <>
              <Link
                to={`/editProfile/${user.id}`}
                className="flex items-center space-x-3 avatar avatar--medium active"
              >
                <img
                  className="rounded-full w-10 h-10 object-cover"
                  src={user.avatar || avatarLogo}
                  alt="User avatar"
                />
                <p>
                  {user.email}{" "}
                  <span className="text-gray-400">@{user.first_name}</span>
                </p>
              </Link>
              <button
                className="dropdown-button text-white"
                onClick={() => setIsOpen(!isOpen)}
              >
                <i className="fas fa-chevron-down"></i>
              </button>
              {isOpen && (
                <div className="dropdown-menu absolute right-0 mt-35 w-40 bg-gray-700 rounded-md shadow-lg z-10">
                  <Link
                    to={`/editProfile/${user.id}`}
                    className="dropdown-link flex items-center px-3 py-2 hover:bg-gray-600"
                  >
                    <i className="fas fa-tools mr-2"></i>Settings
                  </Link>
                  <button
                    type="button"
                    className="dropdown-link flex items-center px-3 py-2 hover:bg-gray-600 w-full text-left"
                    onClick={logout}
                  >
                    <i className="fas fa-sign-out-alt mr-2"></i>Logout
                  </button>
                </div>
              )}
            </>
          ) : (
            <>
              <Link className="flex items-center" to="/login">
                <i className="fas fa-sign-in-alt me-1 mr-2"></i>Login
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;
