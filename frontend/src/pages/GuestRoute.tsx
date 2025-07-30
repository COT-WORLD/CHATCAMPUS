import { Navigate, Outlet } from "react-router-dom";
import { getAccessToken } from "../utils/tokenStorage";

const GuestRoute = () => {
  const token = getAccessToken();
  return token ? <Navigate to="/" replace /> : <Outlet />;
};

export default GuestRoute;
