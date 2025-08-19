import { Outlet } from "react-router-dom";
import Header from "../components/Header";
import { useAuth } from "../context/AuthContext";
import Loader from "../components/Loader";

const Layout = () => {
  const { isLoading } = useAuth();
  if (isLoading) {
    return <Loader />;
  }
  return (
    <>
      <Header />
      <main>
        <Outlet />
      </main>
    </>
  );
};

export default Layout;
