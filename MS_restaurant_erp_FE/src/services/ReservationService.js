import axios from "axios";
import { API_BASE_URL } from "./config";

const API_URL = API_BASE_URL.reservation; // Reservations service

// Hàm lấy header xác thực
const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Lấy danh sách đặt bàn với phân trang
export const getReservations = async (page = 1, limit = 6) => {
  try {
    const response = await axios.get(`${API_URL}/api/reservations/`, {
      params: { page, limit },
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching reservations:", error);
    throw error;
  }
};

// Tạo đặt bàn mới
export const createReservation = async (data) => {
  try {
    const response = await axios.post(`${API_URL}/api/reservations/`, data, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error("Error creating reservation:", error);
    throw error;
  }
};

// Cập nhật đặt bàn
export const updateReservation = async (id, data) => {
  try {
    const response = await axios.put(`${API_URL}/api/reservations/${id}/`, data, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error("Error updating reservation:", error);
    throw error;
  }
};

// Xóa đặt bàn
export const deleteReservation = async (id) => {
  try {
    await axios.delete(`${API_URL}/api/reservations/${id}/`, {
      headers: getAuthHeader(),
    });
    return true;
  } catch (error) {
    console.error("Error deleting reservation:", error);
    throw error;
  }
};
