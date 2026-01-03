/* eslint-disable react/prop-types */
import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import IconButton from "@mui/material/IconButton";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import TextField from "@mui/material/TextField";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import Chip from "@mui/material/Chip";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

import UserService from "services/UserService";

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState("create");
  const [selectedUser, setSelectedUser] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [menuUser, setMenuUser] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "staff",
    custom_role: "",
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usersRes, rolesRes] = await Promise.all([
        UserService.getUsers(),
        UserService.getRoles(),
      ]);
      // Handle paginated response {count, results} or direct array
      const usersData = usersRes.results || usersRes.data || usersRes || [];
      const rolesData = rolesRes.results || rolesRes.data || rolesRes || [];
      setUsers(Array.isArray(usersData) ? usersData : []);
      setRoles(Array.isArray(rolesData) ? rolesData : []);
    } catch (error) {
      showSnackbar("Lỗi tải dữ liệu: " + error.message, "error");
      setUsers([]);
      setRoles([]);
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = "success") => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleOpenMenu = (event, user) => {
    setAnchorEl(event.currentTarget);
    setMenuUser(user);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
    setMenuUser(null);
  };

  const handleOpenDialog = (mode, user = null) => {
    setDialogMode(mode);
    setSelectedUser(user);
    if (mode === "edit" && user) {
      setFormData({
        username: user.username,
        email: user.email,
        password: "",
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        role: user.role || "staff",
        custom_role: user.custom_role ? String(user.custom_role) : "",
      });
    } else {
      setFormData({
        username: "",
        email: "",
        password: "",
        first_name: "",
        last_name: "",
        role: "staff",
        custom_role: "",
      });
    }
    setOpenDialog(true);
    handleCloseMenu();
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
    try {
      const submitData = { ...formData };
      if (submitData.custom_role) {
        submitData.custom_role = parseInt(submitData.custom_role, 10);
      } else {
        delete submitData.custom_role;
      }

      if (dialogMode === "create") {
        await UserService.createUser(submitData);
        showSnackbar("Tạo tài khoản thành công!");
      } else {
        if (!submitData.password) {
          delete submitData.password;
        }
        await UserService.updateUser(selectedUser.id, submitData);
        showSnackbar("Cập nhật tài khoản thành công!");
      }
      handleCloseDialog();
      loadData();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      showSnackbar("Lỗi: " + errorMsg, "error");
    }
  };

  const handleLockUnlock = async (user) => {
    try {
      if (user.is_locked) {
        await UserService.unlockUser(user.id);
        showSnackbar("Đã mở khóa tài khoản!");
      } else {
        await UserService.deactivateUser(user.id);
        showSnackbar("Đã khóa tài khoản!");
      }
      loadData();
    } catch (error) {
      showSnackbar("Lỗi: " + error.message, "error");
    }
    handleCloseMenu();
  };

  const handleResetPassword = async (user) => {
    try {
      const result = await UserService.resetUserPassword(user.id);
      const newPassword = result.data?.new_password || result.new_password || "123456";
      showSnackbar(`Mật khẩu mới: ${newPassword}`);
    } catch (error) {
      showSnackbar("Lỗi reset mật khẩu: " + error.message, "error");
    }
    handleCloseMenu();
  };

  const handleDelete = async (user) => {
    if (window.confirm(`Bạn có chắc muốn xóa tài khoản "${user.username}"?`)) {
      try {
        await UserService.deleteUser(user.id);
        showSnackbar("Đã xóa tài khoản!");
        loadData();
      } catch (error) {
        showSnackbar("Lỗi xóa tài khoản: " + error.message, "error");
      }
    }
    handleCloseMenu();
  };

  const getRoleLabel = (role) => {
    const roleLabels = {
      admin: "Quản trị viên",
      manager: "Quản lý",
      staff: "Nhân viên",
      chef: "Đầu bếp",
      waiter: "Phục vụ",
      cashier: "Thu ngân",
    };
    return roleLabels[role] || role;
  };

  const columns = [
    { Header: "Username", accessor: "username", width: "15%" },
    { Header: "Email", accessor: "email", width: "20%" },
    { Header: "Họ tên", accessor: "fullname", width: "20%" },
    { Header: "Vai trò", accessor: "role_display", width: "15%" },
    { Header: "Trạng thái", accessor: "status", width: "15%" },
    { Header: "Thao tác", accessor: "action", width: "15%", align: "center" },
  ];

  const rows = users.map((user) => ({
    username: user.username,
    email: user.email,
    fullname: `${user.first_name || ""} ${user.last_name || ""}`.trim() || "-",
    role_display: (
      <Chip
        label={user.custom_role_name || getRoleLabel(user.role)}
        color={user.role === "admin" ? "error" : user.role === "manager" ? "warning" : "info"}
        size="small"
      />
    ),
    status: (
      <Chip
        label={user.is_locked ? "Đã khóa" : user.is_active ? "Hoạt động" : "Không hoạt động"}
        color={user.is_locked ? "error" : user.is_active ? "success" : "default"}
        size="small"
      />
    ),
    action: (
      <IconButton size="small" onClick={(e) => handleOpenMenu(e, user)}>
        <Icon>more_vert</Icon>
      </IconButton>
    ),
  }));

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
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
                <MDTypography variant="h6" color="white">
                  Quản lý tài khoản
                </MDTypography>
                <MDButton
                  variant="gradient"
                  color="dark"
                  size="small"
                  onClick={() => handleOpenDialog("create")}
                >
                  <Icon sx={{ fontWeight: "bold" }}>add</Icon>
                  &nbsp;Thêm tài khoản
                </MDButton>
              </MDBox>
              <MDBox pt={3}>
                {loading ? (
                  <MDBox p={3} textAlign="center">
                    <MDTypography variant="body2">Đang tải...</MDTypography>
                  </MDBox>
                ) : (
                  <DataTable
                    table={{ columns, rows }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                  />
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleCloseMenu}>
        <MenuItem onClick={() => handleOpenDialog("edit", menuUser)}>
          <Icon sx={{ mr: 1 }}>edit</Icon> Chỉnh sửa
        </MenuItem>
        <MenuItem onClick={() => handleLockUnlock(menuUser)}>
          <Icon sx={{ mr: 1 }}>{menuUser?.is_locked ? "lock_open" : "lock"}</Icon>
          {menuUser?.is_locked ? "Mở khóa" : "Khóa tài khoản"}
        </MenuItem>
        <MenuItem onClick={() => handleResetPassword(menuUser)}>
          <Icon sx={{ mr: 1 }}>vpn_key</Icon> Reset mật khẩu
        </MenuItem>
        <MenuItem onClick={() => handleDelete(menuUser)} sx={{ color: "error.main" }}>
          <Icon sx={{ mr: 1 }}>delete</Icon> Xóa
        </MenuItem>
      </Menu>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogMode === "create" ? "Thêm tài khoản mới" : "Chỉnh sửa tài khoản"}
        </DialogTitle>
        <DialogContent>
          <MDBox pt={2} display="flex" flexDirection="column" gap={2}>
            <MDInput
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleFormChange}
              fullWidth
              disabled={dialogMode === "edit"}
            />
            <MDInput
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleFormChange}
              fullWidth
            />
            <MDInput
              label={dialogMode === "create" ? "Mật khẩu" : "Mật khẩu mới (để trống nếu không đổi)"}
              name="password"
              type="password"
              value={formData.password}
              onChange={handleFormChange}
              fullWidth
            />
            <MDInput
              label="Họ"
              name="first_name"
              value={formData.first_name}
              onChange={handleFormChange}
              fullWidth
            />
            <MDInput
              label="Tên"
              name="last_name"
              value={formData.last_name}
              onChange={handleFormChange}
              fullWidth
            />
            <FormControl fullWidth>
              <InputLabel>Vai trò cơ bản</InputLabel>
              <Select
                name="role"
                value={formData.role}
                onChange={handleFormChange}
                label="Vai trò cơ bản"
                sx={{ height: 45 }}
              >
                <MenuItem value="admin">Quản trị viên</MenuItem>
                <MenuItem value="manager">Quản lý</MenuItem>
                <MenuItem value="staff">Nhân viên</MenuItem>
                <MenuItem value="chef">Đầu bếp</MenuItem>
                <MenuItem value="waiter">Phục vụ</MenuItem>
                <MenuItem value="cashier">Thu ngân</MenuItem>
              </Select>
            </FormControl>
            {roles.length > 0 && (
              <FormControl fullWidth>
                <InputLabel>Vai trò tùy chỉnh</InputLabel>
                <Select
                  name="custom_role"
                  value={formData.custom_role}
                  onChange={handleFormChange}
                  label="Vai trò tùy chỉnh"
                  sx={{ height: 45 }}
                >
                  <MenuItem value="">Không</MenuItem>
                  {roles.map((role) => (
                    <MenuItem key={role.id} value={String(role.id)}>
                      {role.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
          </MDBox>
        </DialogContent>
        <DialogActions>
          <MDButton onClick={handleCloseDialog} color="secondary">
            Hủy
          </MDButton>
          <MDButton onClick={handleSubmit} color="info">
            {dialogMode === "create" ? "Tạo" : "Lưu"}
          </MDButton>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "top", horizontal: "right" }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Footer />
    </DashboardLayout>
  );
}

export default UserManagement;
