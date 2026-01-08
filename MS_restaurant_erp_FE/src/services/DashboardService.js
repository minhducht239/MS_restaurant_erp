import axios from "axios";
import { API_BASE_URL } from "./config";

const API_URL = API_BASE_URL.dashboard;

// Hàm lấy header xác thực
const getAuthHeader = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Thêm hàm theo dõi request/response để debug
const logApiCall = async (name, promise) => {
  try {
    console.log(`Calling API: ${name}...`);
    const result = await promise;
    console.log(`API ${name} success:`, result);
    return result;
  } catch (error) {
    console.error(`API ${name} failed:`, error);
    throw error;
  }
};

// Lấy thống kê tổng quan cho dashboard
export const getDashboardStatistics = async () => {
  const headers = getAuthHeader();
  console.log("Auth headers:", headers);

  return logApiCall(
    "getDashboardStatistics",
    axios.get(`${API_URL}/statistics/`, { headers }).then((response) => response.data)
  );
};

// Lấy dữ liệu doanh thu theo tuần
export const getWeeklyRevenue = async () => {
  try {
    const response = await axios.get(`${API_URL}/weekly-revenue/`, {
      headers: getAuthHeader(),
    });

    // Đảm bảo dữ liệu trả về là mảng đúng định dạng
    const data = response.data;
    if (Array.isArray(data) && data.length === 7) {
      return data;
    }

    console.warn("Weekly revenue API returned unexpected format:", data);
    // Fallback nếu dữ liệu không đúng định dạng
    return [0, 0, 0, 0, 0, 0, 0];
  } catch (error) {
    console.error("Error fetching weekly revenue:", error);
    return [0, 0, 0, 0, 0, 0, 0]; // Fallback
  }
};

// Thêm hàm doanh thu theo tháng
export const getMonthlyRevenue = async () => {
  try {
    const response = await axios.get(`${API_URL}/monthly-revenue/`, {
      headers: getAuthHeader(),
    });

    // Log dữ liệu để kiểm tra
    console.log("Monthly revenue API response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching monthly revenue:", error);
    // Trả về mảng rỗng khi có lỗi
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  }
};

// Lấy top món ăn bán chạy
export const getTopSellingItems = async () => {
  try {
    console.log("Calling top-items API...");
    const response = await axios.get(`${API_URL}/top-items/`, {
      headers: getAuthHeader(),
    });

    console.log("Top selling items raw data:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching top selling items:", error);
    // Trả về dữ liệu rỗng khi có lỗi
    return {
      food: [],
      drinks: [],
    };
  }
};
