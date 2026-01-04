import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  useMemo,
  useCallback,
  useRef,
} from "react";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import axios from "axios";

// Tạo context cho authentication
const AuthContext = createContext(null);

// ==================================================================
// CẤU HÌNH URL API
// ==================================================================
const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || "http://localhost:8001";
// ==================================================================

// AuthProvider để bao quanh toàn bộ ứng dụng
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const navigate = useNavigate();

  const isCheckingRef = useRef(false);
  const mounted = useRef(true);

  useEffect(() => {
    return () => {
      mounted.current = false;
    };
  }, []);

  const getCurrentUser = useCallback(async () => {
    // Tránh multiple calls đồng thời
    if (isCheckingRef.current) {
      console.log("getCurrentUser already in progress, skipping");
      return user;
    }

    try {
      isCheckingRef.current = true;
      if (mounted.current) setIsChecking(true);

      const token = localStorage.getItem("access_token");
      if (!token) {
        throw new Error("No access token found");
      }

      console.log("Fetching current user...");

      // Gọi Auth Service để lấy profile
      const response = await axios.get(`${AUTH_API_URL}/api/auth/profile/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        timeout: 10000,
      });

      console.log("Current user response:", response.data);
      // Xử lý dữ liệu trả về - backend trả về {success: true, user: {...}}
      const userData = response.data.user || response.data.body?.user || response.data;

      if (mounted.current) {
        setUser(userData);
        setError(null);
      }

      return userData;
    } catch (error) {
      console.error("Error fetching current user:", error);

      if (error.response?.status === 401) {
        try {
          const isRefreshed = await refreshToken();
          if (isRefreshed && mounted.current) {
            // Thử lại với token mới
            const newToken = localStorage.getItem("access_token");
            const retryResponse = await axios.get(`${AUTH_API_URL}/api/auth/profile/`, {
              headers: {
                Authorization: `Bearer ${newToken}`,
              },
              timeout: 10000,
            });

            const userData =
              retryResponse.data.user || retryResponse.data.body?.user || retryResponse.data;
            if (mounted.current) {
              setUser(userData);
              setError(null);
            }
            return userData;
          }
        } catch (retryError) {
          console.error("Token refresh failed:", retryError);
        }
      }

      if (mounted.current) {
        setUser(null);
        setError(error.response?.data?.detail || "Authentication failed");

        // Clear invalid tokens
        if (error.response?.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      }

      throw error;
    } finally {
      isCheckingRef.current = false;
      if (mounted.current) setIsChecking(false);
    }
  }, [user]);

  const updateUser = useCallback((updatedUserData) => {
    console.log("Updating user data:", updatedUserData);
    if (mounted.current) {
      setUser((prev) => {
        if (!prev) return updatedUserData;
        return { ...prev, ...updatedUserData };
      });
    }
  }, []);

  const refreshToken = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        console.log("No refresh token available");
        return false;
      }

      console.log("Attempting to refresh token...");
      const response = await axios.post(
        `${AUTH_API_URL}/api/auth/token/refresh/`,
        {
          refresh: refreshToken,
        },
        {
          timeout: 10000,
        }
      );

      if (response.status === 200) {
        const data = response.data.body || response.data;

        const newAccessToken = data.access || data.access_token;

        if (newAccessToken) {
          localStorage.setItem("access_token", newAccessToken);
        }

        if (data.refresh || data.refresh_token) {
          localStorage.setItem("refresh_token", data.refresh || data.refresh_token);
        }

        console.log("Token refreshed successfully");
        return true;
      }

      return false;
    } catch (error) {
      console.error("Token refresh error:", error);

      if (error.response?.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }

      return false;
    }
  }, []);

  const login = useCallback(
    async (emailOrCredentials, password) => {
      try {
        if (mounted.current) setError(null);

        let credentials;
        if (typeof emailOrCredentials === "object") {
          credentials = emailOrCredentials;
        } else {
          credentials = {
            username: emailOrCredentials,
            password: password,
          };
        }

        console.log("Attempting login with:", { username: credentials.username });

        const response = await axios.post(`${AUTH_API_URL}/api/auth/login/`, credentials, {
          timeout: 15000,
        });

        const data = response.data.body || response.data;
        console.log("Login response data:", data);

        // Backend trả về tokens trong object khác
        const accessToken = data.access_token || data.tokens?.access;
        const refreshToken = data.refresh_token || data.tokens?.refresh;

        if (!accessToken || !refreshToken) {
          console.error("Invalid token format in response:", data);
          throw new Error("Invalid response: missing tokens");
        }

        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);

        try {
          await getCurrentUser();
          console.log("Login successful, user data fetched");
        } catch (userError) {
          console.warn(
            "Could not fetch user data immediately after login (Check User Service URL)",
            userError
          );
        }

        return typeof emailOrCredentials === "object" ? { success: true } : true;
      } catch (error) {
        console.error("Login error:", error);

        const errorMessage =
          error.response?.data?.body?.detail ||
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          "Login failed";

        if (mounted.current) setError(errorMessage);

        return typeof emailOrCredentials === "object"
          ? { success: false, error: errorMessage }
          : false;
      }
    },
    [getCurrentUser]
  );

  const register = useCallback(async (userData) => {
    try {
      if (mounted.current) setError(null);

      if (!userData.username || !userData.password || !userData.email) {
        throw new Error("Missing required fields");
      }

      // Chuẩn bị data cho API
      const registerData = {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        confirm_password: userData.password,
      };

      const response = await axios.post(`${AUTH_API_URL}/api/auth/register/`, registerData, {
        timeout: 15000,
      });

      if (response.status === 201 || response.status === 200) {
        console.log("Registration successful");
        return { success: true };
      }

      return { success: false, error: "Registration failed" };
    } catch (error) {
      console.error("Register error:", error);

      const errorMessage =
        error.response?.data?.body?.detail ||
        error.response?.data?.detail ||
        error.response?.data?.message ||
        Object.values(error.response?.data || {})
          .flat()
          .join(", ") ||
        error.message ||
        "Registration failed";

      if (mounted.current) setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  }, []);

  const logout = useCallback(() => {
    console.log("Logging out user");

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    if (mounted.current) {
      setUser(null);
      setError(null);
      setIsChecking(false);
    }

    isCheckingRef.current = false;
    navigate("/authentication/sign-in");
  }, [navigate]);

  // ============= GOOGLE OAUTH =============
  const getGoogleLoginUrl = useCallback(async () => {
    try {
      const response = await axios.get(`${AUTH_API_URL}/api/auth/google/login/`, {
        timeout: 10000,
      });
      return response.data.url;
    } catch (error) {
      console.error("Error getting Google login URL:", error);
      throw error;
    }
  }, []);

  const loginWithGoogle = useCallback(
    async (code) => {
      try {
        if (mounted.current) setError(null);

        console.log("Processing Google login with code...");

        const response = await axios.post(
          `${AUTH_API_URL}/api/auth/google/callback/`,
          { code },
          { timeout: 15000 }
        );

        const data = response.data;
        console.log("Google login response:", data);

        if (!data.success) {
          throw new Error(data.message || "Google login failed");
        }

        const accessToken = data.tokens?.access;
        const refreshToken = data.tokens?.refresh;

        if (!accessToken || !refreshToken) {
          throw new Error("Invalid response: missing tokens");
        }

        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);

        if (mounted.current) {
          setUser(data.user);
        }

        console.log("Google login successful");
        return { success: true, isNewUser: data.is_new_user };
      } catch (error) {
        console.error("Google login error:", error);

        const errorMessage =
          error.response?.data?.message || error.message || "Google login failed";

        if (mounted.current) setError(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [getCurrentUser]
  );
  // ============= END GOOGLE OAUTH =============

  useEffect(() => {
    const checkLoggedIn = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          console.log("No token found, user not authenticated");
          if (mounted.current) setLoading(false);
          return;
        }

        console.log("Checking authentication...");
        await getCurrentUser();
      } catch (error) {
        console.error("Auth check error:", error);

        // Không tự động logout nếu chỉ là lỗi mạng, chỉ logout khi 401 thật sự
        if (error.response?.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          if (mounted.current) {
            setUser(null);
            setError("Session expired. Please login again.");
          }
        }
      } finally {
        if (mounted.current) setLoading(false);
      }
    };

    if (!user && !isCheckingRef.current) {
      checkLoggedIn();
    } else if (user && mounted.current) {
      setLoading(false);
    }
  }, [getCurrentUser, user]);

  const value = useMemo(
    () => ({
      user,
      loading,
      error,
      isChecking,
      login,
      register,
      logout,
      refreshToken,
      getCurrentUser,
      updateUser,
      isAuthenticated: !!user,
      // Google OAuth
      getGoogleLoginUrl,
      loginWithGoogle,
    }),
    [
      user,
      loading,
      error,
      isChecking,
      login,
      register,
      logout,
      refreshToken,
      getCurrentUser,
      updateUser,
      getGoogleLoginUrl,
      loginWithGoogle,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
