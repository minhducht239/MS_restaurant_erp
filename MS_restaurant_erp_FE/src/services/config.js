// Cấu hình API URL cho từng service từ environment variables
export const API_BASE_URL = {
  auth: process.env.REACT_APP_AUTH_API_URL || "http://localhost:8001",
  user: process.env.REACT_APP_USER_API_URL || "http://localhost:8002",
  billing: process.env.REACT_APP_BILLING_API_URL || "http://localhost:8003",
  customer: process.env.REACT_APP_CUSTOMER_API_URL || "http://localhost:8004",
  dashboard: process.env.REACT_APP_DASHBOARD_API_URL || "http://localhost:8005",
  menu: process.env.REACT_APP_MENU_API_URL || "http://localhost:8006",
  staff: process.env.REACT_APP_STAFF_API_URL || "http://localhost:8007",
  tables: process.env.REACT_APP_TABLES_API_URL || "http://localhost:8008"
};

// Export riêng cho các service cần dùng
export const AUTH_API_URL = API_BASE_URL.auth;
export const USER_API_URL = API_BASE_URL.user;
export const BILLING_API_URL = API_BASE_URL.billing;
export const CUSTOMER_API_URL = API_BASE_URL.customer;
export const DASHBOARD_API_URL = API_BASE_URL.dashboard;
export const MENU_API_URL = API_BASE_URL.menu;
export const STAFF_API_URL = API_BASE_URL.staff;
export const TABLES_API_URL = API_BASE_URL.tables;

// Hàm helper để log tất cả API URLs (dùng cho debug)
export const logApiUrls = () => {
  console.log("=== API Configuration ===");
  Object.entries(API_BASE_URL).forEach(([service, url]) => {
    console.log(`${service.toUpperCase()}: ${url}`);
  });
  console.log("========================");
};