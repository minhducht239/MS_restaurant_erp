// Cấu hình API URL cho từng service từ environment variables
// Demo local: mỗi service chạy trên port riêng theo docker-compose
export const API_BASE_URL = {
  auth: process.env.REACT_APP_AUTH_API_URL || "http://localhost:8001",
  menu: process.env.REACT_APP_MENU_API_URL || "http://localhost:8002",
  billing: process.env.REACT_APP_BILLING_API_URL || "http://localhost:8003",
  customer: process.env.REACT_APP_CUSTOMER_API_URL || "http://localhost:8004",
  tables: process.env.REACT_APP_TABLES_API_URL || "http://localhost:8005",
  staff: process.env.REACT_APP_STAFF_API_URL || "http://localhost:8006",
  reservation: process.env.REACT_APP_RESERVATION_API_URL || "http://localhost:8007",
  dashboard: process.env.REACT_APP_DASHBOARD_API_URL || "http://localhost:8008",
};

// Export riêng cho các service cần dùng
export const AUTH_API_URL = API_BASE_URL.auth;
export const MENU_API_URL = API_BASE_URL.menu;
export const BILLING_API_URL = API_BASE_URL.billing;
export const CUSTOMER_API_URL = API_BASE_URL.customer;
export const TABLES_API_URL = API_BASE_URL.tables;
export const STAFF_API_URL = API_BASE_URL.staff;
export const RESERVATION_API_URL = API_BASE_URL.reservation;
export const DASHBOARD_API_URL = API_BASE_URL.dashboard;

// Hàm helper để log tất cả API URLs (dùng cho debug)
export const logApiUrls = () => {
  console.log("=== API Configuration ===");
  Object.entries(API_BASE_URL).forEach(([service, url]) => {
    console.log(`${service.toUpperCase()}: ${url}`);
  });
  console.log("========================");
};
