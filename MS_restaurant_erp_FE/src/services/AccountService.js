import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8001";

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");

        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/authentication/sign-in";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const handleApiError = (error, context = "") => {
  console.error(`API Error in ${context}:`, error);

  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    console.error("Response data:", data);
    console.error("Response status:", status);

    if (data?.errors) {
      const errorMessages = Object.values(data.errors).flat();
      throw new Error(errorMessages.join(", "));
    } else if (data?.detail) {
      throw new Error(data.detail);
    } else if (data?.message) {
      throw new Error(data.message);
    } else {
      throw new Error(`Server error: ${status}`);
    }
  } else if (error.request) {
    console.error("Request made but no response received");
    throw new Error("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.");
  } else {
    console.error("Error setting up request:", error.message);
    throw new Error(error.message || "Có lỗi không xác định xảy ra");
  }
};

export const getCurrentUser = async () => {
  try {
    console.log("=== GET CURRENT USER ===");

    const response = await apiClient.get("/auth/me/");
    console.log("Current user response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "getCurrentUser");
  }
};

export const updateUserProfile = async (profileData) => {
  try {
    console.log("=== UPDATE USER PROFILE ===");
    console.log("Profile data:", profileData);

    if (!profileData || typeof profileData !== "object") {
      throw new Error("Invalid profile data");
    }

    const dataToSend = {};

    // Xử lý name
    if (profileData.name && profileData.name.trim()) {
      const nameParts = profileData.name.trim().split(/\s+/);
      dataToSend.first_name = nameParts[0] || "";
      dataToSend.last_name = nameParts.slice(1).join(" ") || "";
    }

    // Xử lý email
    if (profileData.email && profileData.email.trim()) {
      dataToSend.email = profileData.email.trim();
    }

    // Xử lý phone
    if (profileData.phone && profileData.phone.trim()) {
      dataToSend.phone_number = profileData.phone.trim();
    }

    if (profileData.address !== undefined) {
      dataToSend.address = profileData.address;
    }

    if (profileData.date_of_birth !== undefined) {
      dataToSend.date_of_birth = profileData.date_of_birth;
    }

    console.log("Sending data:", dataToSend);

    if (Object.keys(dataToSend).length === 0) {
      throw new Error("No data to update");
    }

    const response = await apiClient.patch("/auth/user/", dataToSend);

    console.log("Update response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "updateUserProfile");
  }
};

export const changeUserPassword = async (passwordData) => {
  try {
    console.log("=== CHANGE USER PASSWORD ===");

    if (!passwordData || typeof passwordData !== "object") {
      throw new Error("Invalid password data");
    }

    // Validate input
    if (!passwordData.currentPassword) {
      throw new Error("Current password is required");
    }

    if (!passwordData.newPassword) {
      throw new Error("New password is required");
    }

    if (passwordData.newPassword.length < 6) {
      throw new Error("New password must be at least 6 characters");
    }

    const dataToSend = {
      current_password: passwordData.currentPassword,
      new_password: passwordData.newPassword,
    };

    console.log("Sending password change request...");

    const response = await apiClient.put("/auth/change-password/", dataToSend);

    console.log("Password change response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "changeUserPassword");
  }
};

export const uploadAvatar = async (file) => {
  try {
    console.log("=== UPLOAD AVATAR ===");

    if (!file) {
      throw new Error("No file provided");
    }

    let formData;
    if (file instanceof FormData) {
      formData = file;
    } else {
      formData = new FormData();
      formData.append("avatar", file);
    }

    const response = await apiClient.post("/auth/upload-avatar/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Avatar upload response:", response.data);
    return response.data;
  } catch (error) {
    handleApiError(error, "uploadAvatar");
  }
};

export const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return null;

  // If already full URL, return as is
  if (avatarPath.startsWith("http")) {
    return avatarPath;
  }

  // If relative path, prepend API base URL
  const baseUrl = API_URL.replace("/api", ""); // Remove /api from base URL
  return `${baseUrl}${avatarPath}`;
};

export default apiClient;
