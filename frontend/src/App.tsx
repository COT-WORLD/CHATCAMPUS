import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import { AuthProvider } from "./context/AuthContext";
import Layout from "./pages/Layout";
import GuestRoute from "./pages/GuestRoute";
import ProtectedRoute from "./pages/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Register from "./pages/Register";
import { GoogleOAuthProvider } from "@react-oauth/google";
import Topics from "./pages/Topics";
const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

function App() {
  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route element={<GuestRoute />}>
                <Route path="login" element={<Login />} />
                <Route path="signup" element={<Register />} />
              </Route>
              <Route element={<ProtectedRoute />}>
                <Route path="/" element={<Dashboard />} />
                <Route path="/topics" element={<Topics />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
