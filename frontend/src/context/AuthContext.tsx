import React, { createContext, useContext, useEffect, useState } from "react";
import type { UserType } from "../types/user.types";
import { login as apiLogin, logout as apiLogout } from "../api/auth";
import api from "../api/axios";
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  clearTokens,
} from "../utils/tokenStorage";

type AuthContextType = {
  user: UserType | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<UserType | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  //Helper: fetch user profile
  const fetchUserProfile = async () => {
    try {
      const response = await api.get<{ user: UserType }>("user/me/");
      setUser(response.data.user);
    } catch (error) {
      setUser(null);
      clearTokens();
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await apiLogin({ email, password });
      const tokens = response.data;

      setAccessToken(tokens.access);
      setRefreshToken(tokens.refresh);

      api.defaults.headers.common["Authorization"] = `Bearer ${tokens.access}`;

      fetchUserProfile().finally(() => setIsLoading(false));
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      const refresh = getRefreshToken();
      if (refresh) {
        await apiLogout(refresh);
      }
    } catch (error) {
      console.warn("Logout API call failed", error);
    } finally {
      clearTokens();
      setUser(null);
      delete api.defaults.headers.common["Authorization"];
      setIsLoading(false);
      window.location.href = "/login";
    }
  };

  useEffect(() => {
    const access = getAccessToken();
    const refresh = getRefreshToken();
    if (access && refresh) {
      setAccessToken(access);
      setRefreshToken(refresh);
      api.defaults.headers.common["Authorization"] = `Bearer ${access}`;
      fetchUserProfile().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
