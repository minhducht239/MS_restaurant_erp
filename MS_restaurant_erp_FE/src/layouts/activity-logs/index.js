/* eslint-disable react/prop-types */
import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Chip from "@mui/material/Chip";
import TextField from "@mui/material/TextField";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Icon from "@mui/material/Icon";
import CircularProgress from "@mui/material/CircularProgress";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Pagination from "@mui/material/Pagination";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

import UserService from "services/UserService";

function ActivityLogs() {
  // Helper to format number with thousands separator
  const formatNumber = (num) => (typeof num === "number" ? num.toLocaleString("vi-VN") : num);
  const [tabValue, setTabValue] = useState(0);
  const [activityLogs, setActivityLogs] = useState([]);
  const [loginHistory, setLoginHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    user: "",
    action: "",
    status: "",
    startDate: "",
    endDate: "",
  });

  useEffect(() => {
    loadData();
    // eslint-disable-next-line
  }, [tabValue, page]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        ...filters,
        page,
      };

      if (tabValue === 0) {
        const response = await UserService.getActivityLogs(params);
        let data = response.results || response.data || response || [];
        if (!Array.isArray(data) && typeof data === "object") data = [];
        setActivityLogs(Array.isArray(data) ? data : []);
        setTotalPages(
          Math.ceil((response.count || (Array.isArray(data) ? data.length : 0)) / 20) || 1
        );
      } else {
        const response = await UserService.getLoginHistory(params);
        let data = response.results || response.data || response || [];
        if (!Array.isArray(data) && typeof data === "object") data = [];
        setLoginHistory(Array.isArray(data) ? data : []);
        setTotalPages(
          Math.ceil((response.count || (Array.isArray(data) ? data.length : 0)) / 20) || 1
        );
      }
    } catch (err) {
      console.error("Error loading data:", err);
      setError(err.response?.data?.detail || err.message || "Không thể tải dữ liệu");
      if (tabValue === 0) {
        setActivityLogs([]);
      } else {
        setLoginHistory([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setPage(1);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({ ...filters, [name]: value });
  };

  const handleSearch = () => {
    setPage(1);
    setTimeout(() => loadData(), 0); // ensure state update before reload
  };

  const handleClearFilters = () => {
    setFilters({
      user: "",
      action: "",
      status: "",
      startDate: "",
      endDate: "",
    });
    setPage(1);
    setTimeout(() => loadData(), 0);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getActionColor = (action) => {
    const colors = {
      login: "success",
      logout: "secondary",
      login_failed: "error",
      password_change: "warning",
      password_reset: "warning",
      profile_update: "info",
      user_create: "success",
      user_update: "info",
      user_delete: "error",
      role_change: "primary",
    };
    return colors[action] || "default";
  };

  const getStatusColor = (status) => {
    const colors = {
      success: "success",
      failed: "error",
      blocked: "warning",
    };
    return colors[status] || "default";
  };

  const getActionLabel = (action) => {
    const labels = {
      login: "Đăng nhập",
      logout: "Đăng xuất",
      login_failed: "Đăng nhập thất bại",
      password_change: "Đổi mật khẩu",
      password_reset: "Reset mật khẩu",
      profile_update: "Cập nhật profile",
      avatar_upload: "Tải lên avatar",
      account_locked: "Khóa tài khoản",
      account_unlocked: "Mở khóa tài khoản",
      role_change: "Đổi vai trò",
      user_create: "Tạo người dùng",
      user_update: "Cập nhật người dùng",
      user_delete: "Xóa người dùng",
      user_activate: "Kích hoạt người dùng",
      user_deactivate: "Vô hiệu hóa người dùng",
    };
    return labels[action] || action;
  };

  const renderEmptyState = (message) => (
    <MDBox display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={8}>
      <Icon sx={{ fontSize: 64, color: "grey.400", mb: 2 }}>inbox</Icon>
      <MDTypography variant="h6" color="text" fontWeight="medium">
        {message}
      </MDTypography>
      <MDTypography variant="body2" color="text">
        Thử thay đổi bộ lọc hoặc quay lại sau
      </MDTypography>
    </MDBox>
  );

  const renderErrorState = () => (
    <MDBox display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={8}>
      <Icon sx={{ fontSize: 64, color: "error.main", mb: 2 }}>error_outline</Icon>
      <MDTypography variant="h6" color="error" fontWeight="medium">
        Lỗi tải dữ liệu
      </MDTypography>
      <MDTypography variant="body2" color="text" mb={2}>
        {error}
      </MDTypography>
      <MDButton variant="outlined" color="info" onClick={loadData}>
        Thử lại
      </MDButton>
    </MDBox>
  );

  const renderLoadingState = () => (
    <MDBox display="flex" justifyContent="center" alignItems="center" py={8}>
      <CircularProgress color="info" />
      <MDTypography variant="body2" color="text" ml={2}>
        Đang tải dữ liệu...
      </MDTypography>
    </MDBox>
  );

  const renderActivityTable = () => {
    if (activityLogs.length === 0) {
      return renderEmptyState("Không có lịch sử hoạt động");
    }

    return (
      <>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: "bold", width: "15%" }}>Thời gian</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "12%" }}>Người dùng</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "15%" }}>Hành động</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "30%" }}>Mô tả</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "13%" }}>Đối tượng</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "15%" }}>IP</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {activityLogs.map((log, index) => (
                <TableRow key={log.id || index} hover>
                  <TableCell>
                    <MDTypography variant="caption" fontWeight="medium">
                      {formatDate(log.created_at || log.timestamp)}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">
                      {log.user_username || log.user || "-"}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getActionLabel(log.action)}
                      color={getActionColor(log.action)}
                      size="small"
                      sx={{ fontSize: "0.7rem" }}
                    />
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">
                      {log.description || log.action_display || "-"}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">{log.target_user_username || "-"}</MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption" color="text">
                      {log.ip_address || "-"}
                    </MDTypography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {totalPages > 1 && (
          <MDBox display="flex" justifyContent="center" py={2}>
            <Pagination count={totalPages} page={page} onChange={handlePageChange} color="info" />
          </MDBox>
        )}
      </>
    );
  };

  const renderLoginTable = () => {
    if (loginHistory.length === 0) {
      return renderEmptyState("Không có lịch sử đăng nhập");
    }

    return (
      <>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: "bold", width: "15%" }}>Thời gian</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "12%" }}>Người dùng</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "10%" }}>Trạng thái</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "13%" }}>IP</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "15%" }}>Trình duyệt</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "12%" }}>Thiết bị</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "10%" }}>Hệ điều hành</TableCell>
                <TableCell sx={{ fontWeight: "bold", width: "13%" }}>Lý do lỗi</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loginHistory.map((log, index) => (
                <TableRow key={log.id || index} hover>
                  <TableCell>
                    <MDTypography variant="caption" fontWeight="medium">
                      {formatDate(log.created_at || log.timestamp)}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">
                      {log.user_username || log.user || "-"}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={
                        log.status === "success"
                          ? "Thành công"
                          : log.status === "failed"
                          ? "Thất bại"
                          : "Bị chặn"
                      }
                      color={getStatusColor(log.status)}
                      size="small"
                      sx={{ fontSize: "0.7rem" }}
                    />
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption" color="text">
                      {log.ip_address || "-"}
                    </MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">{log.browser || "-"}</MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">{log.device_type || "-"}</MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption">{log.os || "-"}</MDTypography>
                  </TableCell>
                  <TableCell>
                    <MDTypography variant="caption" color="error">
                      {log.failure_reason || "-"}
                    </MDTypography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {totalPages > 1 && (
          <MDBox display="flex" justifyContent="center" py={2}>
            <Pagination count={totalPages} page={page} onChange={handlePageChange} color="info" />
          </MDBox>
        )}
      </>
    );
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
                display="flex"
                justifyContent="space-between"
                alignItems="center"
              >
                <MDBox display="flex" alignItems="center">
                  <Icon sx={{ color: "white", mr: 1 }}>history</Icon>
                  <MDTypography variant="h6" color="white">
                    Lịch sử hoạt động & Đăng nhập
                  </MDTypography>
                </MDBox>
                <MDButton variant="outlined" color="white" size="small" onClick={loadData}>
                  <Icon sx={{ mr: 0.5 }}>refresh</Icon>
                  Làm mới
                </MDButton>
              </MDBox>

              <MDBox px={3} pt={3}>
                <Tabs
                  value={tabValue}
                  onChange={handleTabChange}
                  textColor="primary"
                  indicatorColor="primary"
                >
                  <Tab
                    label={
                      <MDBox display="flex" alignItems="center">
                        <Icon sx={{ mr: 0.5 }}>assignment</Icon>
                        Lịch sử hoạt động
                      </MDBox>
                    }
                  />
                  <Tab
                    label={
                      <MDBox display="flex" alignItems="center">
                        <Icon sx={{ mr: 0.5 }}>login</Icon>
                        Lịch sử đăng nhập
                      </MDBox>
                    }
                  />
                </Tabs>
              </MDBox>

              <MDBox px={3} py={2}>
                <Card variant="outlined" sx={{ p: 2, mb: 2, backgroundColor: "grey.50" }}>
                  <MDTypography variant="caption" fontWeight="bold" mb={1} display="block">
                    Bộ lọc tìm kiếm
                  </MDTypography>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={2.5}>
                      <TextField
                        label="Người dùng"
                        name="user"
                        value={filters.user}
                        onChange={handleFilterChange}
                        fullWidth
                        size="small"
                        placeholder="Nhập tên người dùng..."
                      />
                    </Grid>
                    {tabValue === 0 ? (
                      <Grid item xs={12} md={2}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Hành động</InputLabel>
                          <Select
                            name="action"
                            value={filters.action}
                            onChange={handleFilterChange}
                            label="Hành động"
                          >
                            <MenuItem value="">Tất cả</MenuItem>
                            <MenuItem value="login">Đăng nhập</MenuItem>
                            <MenuItem value="logout">Đăng xuất</MenuItem>
                            <MenuItem value="password_change">Đổi mật khẩu</MenuItem>
                            <MenuItem value="profile_update">Cập nhật profile</MenuItem>
                            <MenuItem value="user_create">Tạo người dùng</MenuItem>
                            <MenuItem value="user_update">Cập nhật người dùng</MenuItem>
                            <MenuItem value="user_delete">Xóa người dùng</MenuItem>
                            <MenuItem value="role_change">Đổi vai trò</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                    ) : (
                      <Grid item xs={12} md={2}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Trạng thái</InputLabel>
                          <Select
                            name="status"
                            value={filters.status}
                            onChange={handleFilterChange}
                            label="Trạng thái"
                          >
                            <MenuItem value="">Tất cả</MenuItem>
                            <MenuItem value="success">Thành công</MenuItem>
                            <MenuItem value="failed">Thất bại</MenuItem>
                            <MenuItem value="blocked">Bị chặn</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                    )}
                    <Grid item xs={12} md={2}>
                      <TextField
                        label="Từ ngày"
                        name="startDate"
                        type="date"
                        value={filters.startDate}
                        onChange={handleFilterChange}
                        fullWidth
                        size="small"
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} md={2}>
                      <TextField
                        label="Đến ngày"
                        name="endDate"
                        type="date"
                        value={filters.endDate}
                        onChange={handleFilterChange}
                        fullWidth
                        size="small"
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} md={3.5}>
                      <MDBox display="flex" gap={1}>
                        <MDButton
                          variant="gradient"
                          color="info"
                          size="small"
                          onClick={handleSearch}
                        >
                          <Icon sx={{ mr: 0.5 }}>search</Icon>
                          Tìm kiếm
                        </MDButton>
                        <MDButton
                          variant="outlined"
                          color="secondary"
                          size="small"
                          onClick={handleClearFilters}
                        >
                          <Icon sx={{ mr: 0.5 }}>clear</Icon>
                          Xóa bộ lọc
                        </MDButton>
                      </MDBox>
                    </Grid>
                  </Grid>
                </Card>
              </MDBox>

              <MDBox px={3} pb={3}>
                {loading
                  ? renderLoadingState()
                  : error
                  ? renderErrorState()
                  : tabValue === 0
                  ? renderActivityTable()
                  : renderLoginTable()}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default ActivityLogs;
