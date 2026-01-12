import Dashboard from "layouts/dashboard";
import Personnel from "layouts/Personnel";
import Billing from "layouts/billing";
import Payment from "layouts/Payment";
import AccountSettings from "layouts/account-settings";
import SignIn from "layouts/authentication/sign-in";
import SignUp from "layouts/authentication/sign-up";
import Menu from "layouts/menu";
import MenuItemDetail from "layouts/menu/components/MenuItemDetail";
import Customer from "layouts/customerTable";
import TableManagement from "layouts/table-management";
import UserManagement from "layouts/user-management";
import ActivityLogs from "layouts/activity-logs";
import RoleManagement from "layouts/role-management";
// @mui icons
import Icon from "@mui/material/Icon";

// Tạo mảng routes cơ bản không phụ thuộc vào trạng thái đăng nhập
const routes = [
  {
    type: "collapse",
    name: "Trang chủ",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <Dashboard />,
    protected: true,
    // Dashboard luôn hiển thị cho tất cả user đã đăng nhập
  },
  {
    type: "collapse",
    name: "Thực đơn",
    key: "menu",
    icon: <Icon fontSize="small">restaurant_menu</Icon>,
    route: "/menu",
    component: <Menu />,
    protected: true,
    requiredPermission: "menu.access",
  },
  {
    type: "route",
    key: "menu-item-detail",
    route: "/menu/:id",
    component: <MenuItemDetail />,
    protected: true,
    requiredPermission: "menu.access",
  },
  {
    type: "collapse",
    name: "Danh sách nhân viên",
    key: "personnel",
    icon: <Icon fontSize="small">manageaccounts</Icon>,
    route: "/personnel",
    component: <Personnel />,
    protected: true,
    requiredPermission: "staff.access",
  },
  {
    type: "collapse",
    name: "Khách hàng thân thiết",
    key: "customer",
    icon: <Icon fontSize="small">group</Icon>,
    route: "/customer",
    component: <Customer />,
    protected: true,
    requiredPermission: "customer.access",
  },
  {
    type: "collapse",
    name: "Quản lý bàn",
    key: "table-management",
    icon: <Icon fontSize="small">table_restaurant</Icon>,
    route: "/table-management",
    component: <TableManagement />,
    protected: true,
    requiredPermission: "table.access",
  },
  {
    type: "collapse",
    name: "Quản lý hóa đơn",
    key: "billing",
    icon: <Icon fontSize="small">receipt</Icon>,
    route: "/billing",
    component: <Billing />,
    protected: true,
    requiredPermission: "billing.access",
  },
  {
    type: "route",
    name: "Tạo hóa đơn thanh toán",
    key: "create-payment-bill",
    route: "/create-payment-bill",
    component: <Payment />,
    protected: true,
    requiredPermission: "billing.access",
  },
  {
    type: "collapse",
    name: "Tài khoản",
    key: "account-settings",
    icon: <Icon fontSize="small">person</Icon>,
    route: "/account-settings",
    component: <AccountSettings />,
    protected: true,
    // Account settings luôn hiển thị cho tất cả user đã đăng nhập
  },
  {
    type: "divider",
    key: "divider-admin",
  },
  {
    type: "title",
    title: "Quản trị",
    key: "admin-title",
  },
  {
    type: "collapse",
    name: "Quản lý người dùng",
    key: "user-management",
    icon: <Icon fontSize="small">manage_accounts</Icon>,
    route: "/user-management",
    component: <UserManagement />,
    protected: true,
    adminOnly: true,
  },
  {
    type: "collapse",
    name: "Vai trò & Quyền",
    key: "role-management",
    icon: <Icon fontSize="small">security</Icon>,
    route: "/role-management",
    component: <RoleManagement />,
    protected: true,
    adminOnly: true,
  },
  {
    type: "collapse",
    name: "Lịch sử hoạt động",
    key: "activity-logs",
    icon: <Icon fontSize="small">history</Icon>,
    route: "/activity-logs",
    component: <ActivityLogs />,
    protected: true,
    adminOnly: true,
  },
  // Thêm các routes đăng nhập/đăng ký vào mảng cơ bản
  {
    type: "collapse",
    name: "Sign In",
    key: "sign-in",
    icon: <Icon fontSize="small">login</Icon>,
    route: "/authentication/sign-in",
    component: <SignIn />,
    authRoute: true, // Đánh dấu là route xác thực
  },
  {
    type: "collapse",
    name: "Sign Up",
    key: "sign-up",
    icon: <Icon fontSize="small">assignment</Icon>,
    route: "/authentication/sign-up",
    component: <SignUp />,
    authRoute: true, // Đánh dấu là route xác thực
  },
  // Google OAuth Callback - redirect to sign-in with code param
  {
    type: "route",
    key: "google-callback",
    route: "/auth/google/callback",
    component: <SignIn />,
    authRoute: true,
  },
];

export default routes;
