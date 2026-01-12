import { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import PropTypes from "prop-types";
// Material Dashboard 2 React components
import Sidenav from "examples/Sidenav";
import Configurator from "examples/Configurator";

// Material Dashboard 2 React themes
import theme from "assets/theme";
import themeDark from "assets/theme-dark";

// Material Dashboard 2 React routes - import the basic routes
import routes from "routes";

// Material Dashboard 2 React contexts
import { useMaterialUIController, setMiniSidenav, setOpenConfigurator } from "context";

// Images
import brandWhite from "assets/images/logo-ct.png";
import brandDark from "assets/images/logo-ct-dark.png";

// Auth Context
import { AuthProvider, useAuth } from "context/AuthContext";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <div>Loading...</div>
      </MDBox>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/authentication/sign-in" state={{ from: location }} />;
  }

  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

// Admin Route Component - chỉ cho phép admin truy cập
const AdminRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <div>Loading...</div>
      </MDBox>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/authentication/sign-in" state={{ from: location }} />;
  }

  // Kiểm tra quyền admin
  const isAdmin = user?.role === "admin" || user?.is_superuser || user?.is_staff;
  if (!isAdmin) {
    return <Navigate to="/dashboard" />;
  }

  return children;
};

AdminRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

// Permission Route Component - kiểm tra permission cụ thể
const PermissionRoute = ({ children, requiredPermission }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <div>Loading...</div>
      </MDBox>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/authentication/sign-in" state={{ from: location }} />;
  }

  // Admin có tất cả quyền
  const isAdmin = user?.role === "admin" || user?.is_superuser || user?.is_staff;
  if (isAdmin) {
    return children;
  }

  // Kiểm tra permission
  const userPermissions = user?.permissions || [];
  if (requiredPermission && !userPermissions.includes(requiredPermission)) {
    return <Navigate to="/dashboard" />;
  }

  return children;
};

PermissionRoute.propTypes = {
  children: PropTypes.node.isRequired,
  requiredPermission: PropTypes.string,
};

PermissionRoute.defaultProps = {
  requiredPermission: null,
};

// Nội dung chính của ứng dụng - sử dụng useAuth bên trong AuthProvider
function AppContent() {
  const [controller, dispatch] = useMaterialUIController();
  const {
    miniSidenav,
    direction,
    layout,
    openConfigurator,
    sidenavColor,
    transparentSidenav,
    whiteSidenav,
    darkMode,
  } = controller;
  const { pathname } = useLocation();
  const { isAuthenticated, logout, user } = useAuth();

  // Kiểm tra user có phải admin không
  const isAdmin = user?.role === "admin" || user?.is_superuser || user?.is_staff;

  // Kiểm tra user có permission cụ thể không
  const hasPermission = (permissionCode) => {
    if (!permissionCode) return true; // Không yêu cầu permission
    if (isAdmin) return true; // Admin có tất cả quyền

    // Check trong mảng permissions của user
    const userPermissions = user?.permissions || [];
    return userPermissions.includes(permissionCode);
  };

  // Lọc và điều chỉnh routes dựa trên trạng thái đăng nhập và quyền
  const displayRoutes = [...routes].filter((route) => {
    // Ẩn các route đăng nhập/đăng ký nếu đã xác thực
    if (route.authRoute && isAuthenticated) return false;

    // Ẩn các route admin nếu user không phải admin
    if (route.adminOnly && !isAdmin) return false;

    // Ẩn divider và title của admin nếu không phải admin
    if ((route.key === "divider-admin" || route.key === "admin-title") && !isAdmin) return false;

    // Kiểm tra permission cho route
    if (route.requiredPermission && !hasPermission(route.requiredPermission)) return false;

    return true;
  });

  // Thêm nút Sign Out nếu đã đăng nhập
  if (isAuthenticated) {
    displayRoutes.push({
      type: "collapse",
      name: "Sign Out",
      key: "sign-out",
      icon: <Icon fontSize="small">logout</Icon>,
      route: "#",
      onClick: logout,
    });
  }

  // Change the openConfigurator state
  const handleConfiguratorOpen = () => setOpenConfigurator(dispatch, !openConfigurator);

  // Open sidenav when mouse enter on mini sidenav
  const handleOnMouseEnter = () => {
    if (miniSidenav && !openConfigurator) {
      setMiniSidenav(dispatch, false);
    }
  };

  // Close sidenav when mouse leave mini sidenav
  const handleOnMouseLeave = () => {
    if (!openConfigurator) {
      setMiniSidenav(dispatch, true);
    }
  };

  // Setting the dir attribute for the body element
  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  // Setting page scroll to 0 when changing the route
  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  const routeComponents = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) {
        return routeComponents(route.collapse);
      }

      if (route.route && route.route !== "#") {
        // Route chỉ dành cho admin
        if (route.adminOnly) {
          return (
            <Route
              exact
              path={route.route}
              element={<AdminRoute>{route.component}</AdminRoute>}
              key={route.key}
            />
          );
        }
        // Route yêu cầu permission cụ thể
        if (route.requiredPermission) {
          return (
            <Route
              exact
              path={route.route}
              element={
                <PermissionRoute requiredPermission={route.requiredPermission}>
                  {route.component}
                </PermissionRoute>
              }
              key={route.key}
            />
          );
        }
        // Route yêu cầu đăng nhập
        if (route.protected) {
          return (
            <Route
              exact
              path={route.route}
              element={<ProtectedRoute>{route.component}</ProtectedRoute>}
              key={route.key}
            />
          );
        }
        return <Route exact path={route.route} element={route.component} key={route.key} />;
      }

      return null;
    });

  const configsButton = (
    <MDBox
      display="flex"
      justifyContent="center"
      alignItems="center"
      width="3.25rem"
      height="3.25rem"
      bgColor="white"
      shadow="sm"
      borderRadius="50%"
      position="fixed"
      right="2rem"
      bottom="2rem"
      zIndex={99}
      color="dark"
      sx={{ cursor: "pointer" }}
      onClick={handleConfiguratorOpen}
    >
      <Icon fontSize="small" color="inherit">
        settings
      </Icon>
    </MDBox>
  );

  return (
    <ThemeProvider theme={darkMode ? themeDark : theme}>
      <CssBaseline />
      {layout === "dashboard" && (
        <>
          <Sidenav
            color={sidenavColor}
            brand={(transparentSidenav && !darkMode) || whiteSidenav ? brandDark : brandWhite}
            brandName="Restaurant ERP"
            routes={displayRoutes}
            onMouseEnter={handleOnMouseEnter}
            onMouseLeave={handleOnMouseLeave}
          />
          <Configurator />
          {configsButton}
        </>
      )}
      {!layout.includes("authentication") && (
        <>
          <Configurator />
          {configsButton}
        </>
      )}
      {layout === "vr" && <Configurator />}
      <Routes>
        {routeComponents(routes)}
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </ThemeProvider>
  );
}

// Component App chính - bao quanh AppContent bằng AuthProvider
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
