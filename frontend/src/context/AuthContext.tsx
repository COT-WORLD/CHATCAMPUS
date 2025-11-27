import React, {
  createContext,
  useContext,
  useMemo,
  useEffect,
  useState,
} from "react";
import type { UserType } from "../types/User.types";
import { login as apiLogin, logout as apiLogout } from "../api/auth";
import api from "../api/axios";
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  clearTokens,
} from "../utils/tokenStorage";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { AuthPhase } from "../types/AuthPhase";
import { dashboardDetails } from "../api/main";

type AuthContextType = {
  user: UserType | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  phase: AuthPhase;
  loginInProgress: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const queryClient = useQueryClient();
  const [loginInProgress, setLoginInProgress] = useState(false);

  const {
    data: user,
    error,
    refetch,
    isLoading,
  } = useQuery<UserType | null, Error>({
    queryKey: ["userProfile"],
    queryFn: async () => {
      const response = await api.get<{ user: UserType }>("user/me/");
      return response.data.user;
    },
    enabled: Boolean(getAccessToken() && getRefreshToken()),
    staleTime: 60 * 1000,
    retry: false,
  });

  useEffect(() => {
    if (error) {
      clearTokens();
      queryClient.removeQueries({ queryKey: ["userProfile"] });
    }
  }, [error, queryClient]);

  const phase = useMemo<AuthPhase>(() => {
    if (loginInProgress) return "logging_in";
    if (!getAccessToken()) return "idle";
    if (error) return "idle";
    if (isLoading) return "refetching_user";
    return "ready";
  }, [isLoading, error, loginInProgress]);

  const login = async (email: string, password: string) => {
    setLoginInProgress(true);
    try {
      const { data } = await apiLogin({ email, password });
      setAccessToken(data.access);
      setRefreshToken(data.refresh);
      api.defaults.headers.common["Authorization"] = `Bearer ${data.access}`;

      await Promise.all([
        refetch(),
        queryClient.fetchQuery({
          queryKey: ["dashboardDetails", ""],
          queryFn: () => dashboardDetails("").then((r) => r.data),
        }),
      ]);
    } catch (e) {
      throw e;
    } finally {
      setLoginInProgress(false);
    }
  };

  const logout = async () => {
    const refresh = getRefreshToken();
    if (refresh) apiLogout(refresh).catch(() => {});
    clearTokens();
    delete api.defaults.headers.common["Authorization"];
    queryClient.clear();
    window.location.href = "/login";
  };

  const value = useMemo<AuthContextType>(
    () => ({ user: user ?? null, login, logout, phase, loginInProgress }),
    [user, login, logout, phase, loginInProgress]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
