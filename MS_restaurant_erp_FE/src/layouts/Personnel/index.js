import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Icon from "@mui/material/Icon";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

// Services
import { getStaff, createStaff, updateStaff, deleteStaff } from "services/StaffService";

// Hooks
import { useTheme } from "@mui/material/styles";
import { useMaterialUIController } from "context";

import PropTypes from "prop-types";

// Component hiển thị thông tin nhân viên
const Employee = ({ name, phone }) => (
  <MDBox display="flex" flexDirection="column">
    <MDTypography variant="caption" fontWeight="medium">
      {name}
    </MDTypography>
    <MDTypography variant="caption" color="text">
      {phone}
    </MDTypography>
  </MDBox>
);

Employee.propTypes = {
  name: PropTypes.string.isRequired,
  phone: PropTypes.string.isRequired,
};

// Component hiển thị thông tin vai trò và lương
const Info = ({ role, salary }) => (
  <MDBox display="flex" flexDirection="column">
    <MDTypography variant="caption" fontWeight="medium">
      {role}
    </MDTypography>
    <MDTypography variant="caption" color="text">
      {new Intl.NumberFormat("vi-VN").format(salary)} VNĐ
    </MDTypography>
  </MDBox>
);

Info.propTypes = {
  role: PropTypes.string.isRequired,
  salary: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
};

const ActionCell = ({ row, onEdit, onDelete }) => (
  <MDBox display="flex" gap={1} justifyContent="center">
    <MDButton variant="outlined" color="info" size="small" onClick={() => onEdit(row)}>
      <Icon sx={{ mr: 0.5, fontSize: "1rem" }}>edit</Icon>
      Sửa
    </MDButton>
    <MDButton variant="outlined" color="error" size="small" onClick={() => onDelete(row.id)}>
      <Icon sx={{ mr: 0.5, fontSize: "1rem" }}>delete</Icon>
      Xóa
    </MDButton>
  </MDBox>
);

ActionCell.propTypes = {
  row: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    phone: PropTypes.string.isRequired,
    role: PropTypes.string.isRequired,
    salary: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    hire_date: PropTypes.string.isRequired,
  }).isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

function Personnel() {
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;
  const theme = useTheme();
  const [validationErrors, setValidationErrors] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [staffList, setStaffList] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [openDialog, setOpenDialog] = useState(false);
  const [editRow, setEditRow] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    role: "waiter",
    salary: "",
    hire_date: "",
  });

  // Lấy dữ liệu nhân viên từ API
  const fetchStaffList = async (page = 1) => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await getStaff({ page: page });

      if (!data || !data.results) {
        throw new Error("Dữ liệu API không hợp lệ");
      }

      const transformedData = data.results.map((item) => ({
        id: item.id,
        employee: <Employee name={item.name} phone={item.phone} />,
        info: <Info role={item.role_display || item.role} salary={item.salary} />,
        hire_date: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            {item.hire_date}
          </MDTypography>
        ),
        action: (
          <ActionCell
            row={{
              id: item.id,
              name: item.name,
              phone: item.phone,
              role: item.role,
              salary: item.salary,
              hire_date: item.hire_date,
            }}
            onEdit={handleOpenDialog}
            onDelete={handleDelete}
          />
        ),
        // Lưu trữ dữ liệu gốc để chỉnh sửa
        name: item.name,
        phone: item.phone,
        role: item.role,
        salary: item.salary,
        hire_date: item.hire_date,
      }));

      setStaffList(transformedData);
      setTotalPages(Math.ceil(data.count / 20)); // PAGE_SIZE from backend is 20
      setCurrentPage(page);
    } catch (error) {
      console.error("Error fetching staff:", error);
      setError("Không thể tải dữ liệu nhân viên. Vui lòng thử lại sau.");
      setStaffList(getSampleStaffData());
    } finally {
      setIsLoading(false);
    }
  };

  // Load dữ liệu khi component mount
  useEffect(() => {
    fetchStaffList();
  }, []);

  const handleOpenDialog = (row = null) => {
    setEditRow(row);
    setValidationErrors({});
    setFormData(
      row
        ? {
            name: row.name,
            phone: row.phone,
            role: row.role,
            salary: row.salary.toString(),
            hire_date: row.hire_date,
          }
        : {
            name: "",
            phone: "",
            role: "waiter",
            salary: "",
            hire_date: new Date().toISOString().split("T")[0],
          }
    );
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditRow(null);
    setValidationErrors({});
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.name.trim()) {
      errors.name = "Tên nhân viên không được để trống";
    }

    if (!formData.phone.trim()) {
      errors.phone = "Số điện thoại không được để trống";
    } else if (!/^[0-9+\-\s()]+$/.test(formData.phone)) {
      errors.phone = "Số điện thoại không hợp lệ";
    }

    if (!formData.salary) {
      errors.salary = "Lương không được để trống";
    } else {
      const salaryValue = parseInt(formData.salary.replace(/\./g, ""));
      if (salaryValue < 1000000) {
        errors.salary = "Lương phải ít nhất 1,000,000 VNĐ";
      }
    }

    if (!formData.hire_date) {
      errors.hire_date = "Ngày vào làm không được để trống";
    }

    return errors;
  };

  const getSampleStaffData = () => {
    return [
      {
        id: 1,
        employee: <Employee name="Nguyễn Văn A" phone="0901234567" />,
        info: <Info role="Quản lý" salary={25000000} />,
        hire_date: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            2023-01-15
          </MDTypography>
        ),
        action: (
          <ActionCell
            row={{
              id: 1,
              name: "Nguyễn Văn A",
              phone: "0901234567",
              role: "manager",
              salary: 25000000,
              hire_date: "2023-01-15",
            }}
            onEdit={handleOpenDialog}
            onDelete={handleDelete}
          />
        ),
        name: "Nguyễn Văn A",
        phone: "0901234567",
        role: "manager",
        salary: 25000000,
        hire_date: "2023-01-15",
      },
      {
        id: 2,
        employee: <Employee name="Trần Thị B" phone="0987654321" />,
        info: <Info role="Đầu bếp" salary={18000000} />,
        hire_date: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            2023-02-20
          </MDTypography>
        ),
        action: (
          <ActionCell
            row={{
              id: 2,
              name: "Trần Thị B",
              phone: "0987654321",
              role: "chef",
              salary: 18000000,
              hire_date: "2023-02-20",
            }}
            onEdit={handleOpenDialog}
            onDelete={handleDelete}
          />
        ),
        name: "Trần Thị B",
        phone: "0987654321",
        role: "chef",
        salary: 18000000,
        hire_date: "2023-02-20",
      },
      {
        id: 3,
        employee: <Employee name="Lê Văn C" phone="0912345678" />,
        info: <Info role="Phục vụ" salary={12000000} />,
        hire_date: (
          <MDTypography variant="caption" color="text" fontWeight="medium">
            2023-03-10
          </MDTypography>
        ),
        action: (
          <ActionCell
            row={{
              id: 3,
              name: "Lê Văn C",
              phone: "0912345678",
              role: "waiter",
              salary: 12000000,
              hire_date: "2023-03-10",
            }}
            onEdit={handleOpenDialog}
            onDelete={handleDelete}
          />
        ),
        name: "Lê Văn C",
        phone: "0912345678",
        role: "waiter",
        salary: 12000000,
        hire_date: "2023-03-10",
      },
    ];
  };

  // Xử lý lưu dữ liệu
  const handleSave = async () => {
    setValidationErrors({});

    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    try {
      setIsLoading(true);

      const staffData = {
        name: formData.name.trim(),
        phone: formData.phone.trim(),
        role: formData.role,
        salary: formData.salary.toString().replace(/\./g, ""),
        hire_date: formData.hire_date,
      };

      let response;
      if (editRow) {
        response = await updateStaff(editRow.id, staffData);
        console.log("Staff updated successfully:", response);
      } else {
        response = await createStaff(staffData);
        console.log("Staff created successfully:", response);
      }

      await fetchStaffList(currentPage);
      handleCloseDialog();

      alert(`${editRow ? "Cập nhật" : "Thêm"} nhân viên thành công!`);
    } catch (error) {
      console.error("Error saving staff data:", error);

      if (error.response) {
        const errorMessage =
          error.response.data?.detail || error.response.data?.message || "Lỗi từ server";
        alert(`Không thể lưu dữ liệu: ${errorMessage}`);
      } else if (error.request) {
        alert("Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.");
      } else {
        alert("Có lỗi xảy ra. Vui lòng thử lại sau.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Xử lý xóa nhân viên
  const handleDelete = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa nhân viên này không?")) {
      try {
        setIsLoading(true);
        await deleteStaff(id);
        fetchStaffList(currentPage);
        alert("Xóa nhân viên thành công!");
      } catch (error) {
        console.error("Error deleting staff:", error);
        alert("Không thể xóa nhân viên. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Xử lý thay đổi giá trị form
  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    if (validationErrors[field]) {
      setValidationErrors((prev) => ({
        ...prev,
        [field]: "",
      }));
    }
  };

  // Định dạng số lương khi nhập
  const formatSalary = (value) => {
    const numericValue = value.toString().replace(/\D/g, "");
    return numericValue.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  };

  // Xử lý nhập lương với định dạng số
  const handleSalaryChange = (e) => {
    const rawValue = e.target.value;
    const numericValue = rawValue.replace(/\D/g, "");
    handleInputChange("salary", formatSalary(numericValue));
  };

  const columns = [
    { Header: "Nhân viên", accessor: "employee", width: "30%", align: "left" },
    { Header: "Vai trò & Lương", accessor: "info", align: "left" },
    { Header: "Ngày vào làm", accessor: "hire_date", align: "center" },
    { Header: "Hành động", accessor: "action", align: "center" },
  ];

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              {/* Thanh tiêu đề */}
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
                  Danh sách nhân viên
                </MDTypography>
                <MDButton variant="contained" color="dark" onClick={() => handleOpenDialog()}>
                  <Icon sx={{ mr: 1 }}>add</Icon>
                  Thêm nhân viên
                </MDButton>
              </MDBox>

              {/* Hiển thị thông báo lỗi nếu có */}
              {error && (
                <MDBox p={2}>
                  <Alert severity="error">{error}</Alert>
                </MDBox>
              )}

              {/* Hiển thị loading hoặc bảng dữ liệu */}
              {isLoading ? (
                <MDBox display="flex" justifyContent="center" p={5}>
                  <CircularProgress color="info" />
                </MDBox>
              ) : (
                <MDBox pt={3}>
                  <DataTable
                    table={{ columns, rows: staffList }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                  />
                </MDBox>
              )}

              {/* Phân trang */}
              {totalPages > 1 && (
                <MDBox display="flex" justifyContent="center" p={3}>
                  {Array.from({ length: totalPages }).map((_, index) => (
                    <MDButton
                      key={index}
                      variant={currentPage === index + 1 ? "contained" : "outlined"}
                      color="info"
                      size="small"
                      onClick={() => fetchStaffList(index + 1)}
                      sx={{ mx: 0.5 }}
                    >
                      {index + 1}
                    </MDButton>
                  ))}
                </MDBox>
              )}
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      {/* Dialog thêm/sửa nhân viên */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        fullWidth
        maxWidth="md"
        PaperProps={{
          sx: {
            bgcolor: darkMode ? theme.palette.background.card : theme.palette.background.paper,
            color: darkMode ? theme.palette.white.main : theme.palette.text.main,
            boxShadow: darkMode ? theme.boxShadows.xxl : theme.boxShadows.lg,
            borderRadius: "12px",
            minHeight: "500px",
          },
        }}
      >
        <DialogTitle
          sx={{
            color: darkMode ? theme.palette.white.main : theme.palette.text.main,
            borderBottom: "1px solid",
            borderColor: "divider",
            pb: 2,
            px: 4,
            pt: 3,
          }}
        >
          <MDBox display="flex" alignItems="center" justifyContent="center">
            <Icon sx={{ mr: 2, fontSize: "2rem", color: "info.main" }}>
              {editRow ? "edit" : "person_add"}
            </Icon>
            <MDTypography variant="h4" fontWeight="bold">
              {" "}
              {editRow ? "Sửa thông tin nhân viên" : "Thêm nhân viên mới"}
            </MDTypography>
          </MDBox>
        </DialogTitle>

        <DialogContent sx={{ p: 4, pt: 2 }}>
          {" "}
          <Grid container spacing={3}>
            {/* Tên nhân viên */}
            <Grid item xs={12} md={6}>
              <MDInput
                label="Tên nhân viên"
                fullWidth
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                required
                error={!!validationErrors.name}
                helperText={validationErrors.name}
                InputLabelProps={{ shrink: true }}
                sx={{
                  mt: 1,
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: darkMode ? "rgba(255, 255, 255, 0.05)" : undefined,
                    color: darkMode ? theme.palette.white.main : undefined,
                    height: "56px",
                  },
                  "& .MuiInputLabel-root": {
                    color: darkMode ? theme.palette.grey[400] : undefined,
                  },
                }}
              />
            </Grid>

            {/* Số điện thoại */}
            <Grid item xs={12} md={6}>
              <MDInput
                label="Số điện thoại"
                fullWidth
                value={formData.phone}
                onChange={(e) => handleInputChange("phone", e.target.value)}
                required
                error={!!validationErrors.phone}
                helperText={validationErrors.phone}
                InputLabelProps={{ shrink: true }}
                sx={{
                  mt: 1,
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: darkMode ? "rgba(255, 255, 255, 0.05)" : undefined,
                    color: darkMode ? theme.palette.white.main : undefined,
                    height: "56px",
                  },
                  "& .MuiInputLabel-root": {
                    color: darkMode ? theme.palette.grey[400] : undefined,
                  },
                }}
              />
            </Grid>

            {/* Chức vụ */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth error={!!validationErrors.role} sx={{ mt: 1 }}>
                <InputLabel
                  sx={{
                    color: darkMode ? theme.palette.grey[400] : undefined,
                  }}
                >
                  Chức vụ
                </InputLabel>
                <Select
                  value={formData.role}
                  label="Chức vụ"
                  onChange={(e) => handleInputChange("role", e.target.value)}
                  sx={{
                    backgroundColor: darkMode ? "rgba(255, 255, 255, 0.05)" : undefined,
                    color: darkMode ? theme.palette.white.main : undefined,
                    height: "56px",
                  }}
                >
                  <MenuItem value="manager">
                    <MDBox display="flex" alignItems="center">
                      <Icon sx={{ mr: 1, color: "warning.main" }}>manage_accounts</Icon>
                      Quản lý
                    </MDBox>
                  </MenuItem>
                  <MenuItem value="chef">
                    <MDBox display="flex" alignItems="center">
                      <Icon sx={{ mr: 1, color: "error.main" }}>restaurant</Icon>
                      Đầu bếp
                    </MDBox>
                  </MenuItem>
                  <MenuItem value="cashier">
                    <MDBox display="flex" alignItems="center">
                      <Icon sx={{ mr: 1, color: "success.main" }}>payments</Icon>
                      Thu ngân
                    </MDBox>
                  </MenuItem>
                  <MenuItem value="waiter">
                    <MDBox display="flex" alignItems="center">
                      <Icon sx={{ mr: 1, color: "info.main" }}>room_service</Icon>
                      Phục vụ
                    </MDBox>
                  </MenuItem>
                  <MenuItem value="janitor">
                    <MDBox display="flex" alignItems="center">
                      <Icon sx={{ mr: 1, color: "secondary.main" }}>cleaning_services</Icon>
                      Vệ sinh
                    </MDBox>
                  </MenuItem>
                </Select>
                {validationErrors.role && (
                  <MDTypography variant="caption" color="error" sx={{ mt: 1 }}>
                    {validationErrors.role}
                  </MDTypography>
                )}
              </FormControl>
            </Grid>

            {/* Lương */}
            <Grid item xs={12} md={6}>
              <MDInput
                label="Lương (VNĐ)"
                fullWidth
                value={formData.salary}
                onChange={handleSalaryChange}
                required
                error={!!validationErrors.salary}
                helperText={validationErrors.salary}
                InputLabelProps={{ shrink: true }}
                sx={{
                  mt: 1,
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: darkMode ? "rgba(255, 255, 255, 0.05)" : undefined,
                    color: darkMode ? theme.palette.white.main : undefined,
                    height: "56px",
                  },
                  "& .MuiInputLabel-root": {
                    color: darkMode ? theme.palette.grey[400] : undefined,
                  },
                }}
              />
            </Grid>

            {/* Ngày vào làm */}
            <Grid item xs={12}>
              <MDBox display="flex" justifyContent="center" mt={1}>
                {" "}
                <MDInput
                  label="Ngày vào làm"
                  fullWidth
                  type="date"
                  value={formData.hire_date}
                  onChange={(e) => handleInputChange("hire_date", e.target.value)}
                  required
                  error={!!validationErrors.hire_date}
                  helperText={validationErrors.hire_date}
                  InputLabelProps={{ shrink: true }}
                  sx={{
                    maxWidth: "300px",
                    "& .MuiOutlinedInput-root": {
                      backgroundColor: darkMode ? "rgba(255, 255, 255, 0.05)" : undefined,
                      color: darkMode ? theme.palette.white.main : undefined,
                      height: "56px",
                    },
                    "& .MuiInputLabel-root": {
                      color: darkMode ? theme.palette.grey[400] : undefined,
                    },
                    "& input::-webkit-calendar-picker-indicator": {
                      filter: darkMode ? "invert(1)" : "none",
                    },
                  }}
                />
              </MDBox>
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions
          sx={{
            px: 4,
            pb: 3,
            pt: 2,
            borderTop: "1px solid",
            borderColor: "divider",
            justifyContent: "center",
            gap: 2,
          }}
        >
          <MDButton
            variant="outlined"
            color="secondary"
            onClick={handleCloseDialog}
            size="large"
            sx={{ minWidth: "120px" }}
          >
            <Icon sx={{ mr: 1 }}>close</Icon>
            Hủy
          </MDButton>
          <MDButton
            variant="gradient"
            color="info"
            onClick={handleSave}
            disabled={!formData.name || !formData.phone || !formData.salary || !formData.hire_date}
            size="large"
            sx={{ minWidth: "140px" }}
          >
            <Icon sx={{ mr: 1 }}>{editRow ? "save" : "add"}</Icon>
            {editRow ? "Cập nhật" : "Thêm mới"}
          </MDButton>
        </DialogActions>
      </Dialog>

      <Footer />
    </DashboardLayout>
  );
}

export default Personnel;
