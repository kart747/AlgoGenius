"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const UserContext = createContext({
  user: null,
  isAdmin: false,
  loading: true,
  refresh: async () => {},
  setUser: () => {},
});

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const hydrate = useCallback(async () => {
    let token = null;
    try {
      if (typeof window !== "undefined") {
        token = localStorage.getItem("access_token");
      }
    } catch (err) {
      token = null;
    }

    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
      const response = await fetch(`${apiBase}/users/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(
          `Profile request failed with status ${response.status}`
        );
      }

      const data = await response.json();
      setUser(data);
      if (typeof window !== "undefined") {
        localStorage.setItem("user", JSON.stringify(data));
      }
    } catch (err) {
      setUser(null);
      if (typeof window !== "undefined") {
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      let token = null;
      try {
        if (typeof window !== "undefined") {
          token = localStorage.getItem("access_token");
        }
      } catch (err) {
        token = null;
      }

      if (!token) {
        if (!cancelled) {
          setUser(null);
          setLoading(false);
        }
        return;
      }

      try {
        if (typeof window !== "undefined") {
          const stored = localStorage.getItem("user");
          if (stored) {
            const parsed = JSON.parse(stored);
            if (!cancelled) {
              setUser(parsed);
              setLoading(false);
            }
            hydrate();
            return;
          }
        }
      } catch (err) {
        // ignore JSON parsing errors
      }

      await hydrate();
    };

    bootstrap();

    return () => {
      cancelled = true;
    };
  }, [hydrate]);

  const value = useMemo(
    () => ({
      user,
      isAdmin: Boolean(user?.is_admin),
      loading,
      refresh: hydrate,
      setUser,
    }),
    [hydrate, loading, user]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export function useUserContext() {
  return useContext(UserContext);
}
