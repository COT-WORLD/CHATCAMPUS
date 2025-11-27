import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = () => {
  const { phase, loginInProgress } = useAuth();
  const location = useLocation();

  if (phase === "idle" || loginInProgress) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
};
export default ProtectedRoute;
