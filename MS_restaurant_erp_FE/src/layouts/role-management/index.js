/* eslint-disable react/prop-types */
import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import IconButton from "@mui/material/IconButton";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Chip from "@mui/material/Chip";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

import UserService from "services/UserService";

function RoleManagement() {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState("create");
  const [selectedRole, setSelectedRole] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    permissions: [],
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rolesRes, permsRes] = await Promise.all([
        UserService.getRoles(),
        UserService.getPermissions(),
      ]);
      // Handle paginated response {count, results} or direct array
      const rolesData = rolesRes.results || rolesRes.data || rolesRes || [];
      const permsData = permsRes.results || permsRes.data || permsRes || [];
      setRoles(Array.isArray(rolesData) ? rolesData : []);
      setPermissions(Array.isArray(permsData) ? permsData : []);
    } catch (error) {
      showSnackbar("Lỗi tải dữ liệu: " + error.message, "error");
      setRoles([]);
      setPermissions([]);
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

  const handleOpenDialog = (mode, role = null) => {
    setDialogMode(mode);
    setSelectedRole(role);
    if (mode === "edit" && role) {
      setFormData({
        name: role.name,
        description: role.description || "",
        permissions: role.permissions ? role.permissions.map((p) => p.id || p) : [],
      });
    } else {
      setFormData({
        name: "",
        description: "",
        permissions: [],
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedRole(null);
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handlePermissionChange = (permissionId) => {
    const newPermissions = formData.permissions.includes(permissionId)
      ? formData.permissions.filter((id) => id !== permissionId)
      : [...formData.permissions, permissionId];
    setFormData({ ...formData, permissions: newPermissions });
  };

  const handleSubmit = async () => {
    try {
      if (dialogMode === "create") {
        await UserService.createRole(formData);
        showSnackbar("Tạo vai trò thành công!");
      } else {
        await UserService.updateRole(selectedRole.id, formData);
        showSnackbar("Cập nhật vai trò thành công!");
      }
      handleCloseDialog();
      loadData();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      showSnackbar("Lỗi: " + errorMsg, "error");
    }
  };

  const handleDelete = async (role) => {
    if (window.confirm("Bạn có chắc muốn xóa vai trò " + role.name + "?")) {
      try {
        await UserService.deleteRole(role.id);
        showSnackbar("Đã xóa vai trò!");
        loadData();
      } catch (error) {
        showSnackbar("Lỗi xóa vai trò: " + error.message, "error");
      }
    }
  };

  const groupPermissionsByCategory = () => {
    const grouped = {};
    permissions.forEach((perm) => {
      const cat = perm.category || "Other";
      if (!grouped[cat]) {
        grouped[cat] = [];
      }
      grouped[cat].push(perm);
    });
    return grouped;
  };

  const columns = [
    { Header: "Tên vai trò", accessor: "name", width: "20%" },
    { Header: "Mô tả", accessor: "description", width: "30%" },
    { Header: "Số quyền", accessor: "permission_count", width: "15%" },
    { Header: "Số người dùng", accessor: "user_count", width: "15%" },
    { Header: "Thao tác", accessor: "action", width: "20%", align: "center" },
  ];

  // Helper to format number with thousands separator
  const formatNumber = (num) => (typeof num === "number" ? num.toLocaleString("vi-VN") : num);

  const rows = roles.map((role) => ({
    name: <Chip label={role.name} color="primary" size="small" />,
    description: role.description || "-",
    permission_count: formatNumber(role.permissions ? role.permissions.length : 0),
    user_count: formatNumber(role.user_count || 0),
    action: (
      <MDBox display="flex" justifyContent="center" gap={1}>
        <IconButton size="small" onClick={() => handleOpenDialog("edit", role)} color="info">
          <Icon>edit</Icon>
        </IconButton>
        <IconButton size="small" onClick={() => handleDelete(role)} color="error">
          <Icon>delete</Icon>
        </IconButton>
      </MDBox>
    ),
  }));

  const groupedPermissions = groupPermissionsByCategory();

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
                  Quản lý vai trò và Phân quyền
                </MDTypography>
                <MDButton
                  variant="gradient"
                  color="dark"
                  size="small"
                  onClick={() => handleOpenDialog("create")}
                >
                  <Icon sx={{ fontWeight: "bold" }}>add</Icon>
                  &nbsp;Thêm vai trò
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

          <Grid item xs={12}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h6" mb={2}>
                  Danh sách quyền hệ thống
                </MDTypography>
                {Object.entries(groupedPermissions).map(([category, perms]) => (
                  <Accordion key={category}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <MDTypography variant="button" fontWeight="medium">
                        {category} ({perms.length} quyền)
                      </MDTypography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={1}>
                        {perms.map((perm) => (
                          <Grid item xs={12} md={4} key={perm.id}>
                            <Chip
                              label={perm.code + ": " + perm.name}
                              size="small"
                              variant="outlined"
                              sx={{ m: 0.5 }}
                            />
                          </Grid>
                        ))}
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === "create" ? "Thêm vai trò mới" : "Chỉnh sửa vai trò"}
        </DialogTitle>
        <DialogContent>
          <MDBox pt={2} display="flex" flexDirection="column" gap={2}>
            <MDInput
              label="Tên vai trò"
              name="name"
              value={formData.name}
              onChange={handleFormChange}
              fullWidth
            />
            <MDInput
              label="Mô tả"
              name="description"
              value={formData.description}
              onChange={handleFormChange}
              fullWidth
              multiline
              rows={2}
            />

            <MDTypography variant="h6" mt={2}>
              Phân quyền
            </MDTypography>

            {Object.entries(groupedPermissions).map(([category, perms]) => (
              <Accordion key={category} defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <MDTypography variant="button" fontWeight="medium">
                    {category}
                  </MDTypography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container>
                    {perms.map((perm) => (
                      <Grid item xs={12} md={4} key={perm.id}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={formData.permissions.includes(perm.id)}
                              onChange={() => handlePermissionChange(perm.id)}
                            />
                          }
                          label={perm.name}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
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

export default RoleManagement;
