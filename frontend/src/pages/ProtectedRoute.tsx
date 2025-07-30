import { Navigate, Outlet } from "react-router-dom";
import { getAccessToken } from "../utils/tokenStorage";

const ProtectedRoute = () => {
  const token = getAccessToken();
  return token ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
