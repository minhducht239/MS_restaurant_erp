import { useEffect, useState, useCallback, useMemo } from "react";
import {
  Card,
  Grid,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Collapse,
  IconButton,
  InputAdornment,
  Divider,
} from "@mui/material";
import Alert from "@mui/material/Alert";
import { Icon } from "@mui/material";
import PropTypes from "prop-types";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

// Services
import {
  getCustomers,
  getCustomerDetail,
  getCustomerLoyaltyHistory,
  refreshCustomers, // THÊM import
} from "services/CustomerService";

// Data functions
import { buildCustomerTableData } from "./data/customerTableData";

// Hooks
import { useTheme } from "@mui/material/styles";
import { useMaterialUIController } from "context";

// Client-side filtering fallback function
const applyClientSideFilters = (customers, filters) => {
  return customers.filter((customer) => {
    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const matchesSearch =
        customer.name?.toLowerCase().includes(searchLower) ||
        customer.phone?.toLowerCase().includes(searchLower) ||
        customer.email?.toLowerCase().includes(searchLower);

      if (!matchesSearch) return false;
    }

    // Loyalty points filter
    if (filters.loyaltyRange && filters.loyaltyRange !== "all") {
      const points = customer.loyalty_points || 0;

      switch (filters.loyaltyRange) {
        case "0-50":
          if (points < 0 || points > 50) return false;
          break;
        case "51-100":
          if (points < 51 || points > 100) return false;
          break;
        case "101-200":
          if (points < 101 || points > 200) return false;
          break;
        case "200+":
          if (points < 200) return false;
          break;
      }
    }

    // Total spent filter
    if (filters.spentRange && filters.spentRange !== "all") {
      const spent = customer.total_spent || 0;

      switch (filters.spentRange) {
        case "0-5000000":
          if (spent < 0 || spent > 5000000) return false;
          break;
        case "5000000-10000000":
          if (spent < 5000000 || spent > 10000000) return false;
          break;
        case "10000000-20000000":
          if (spent < 10000000 || spent > 20000000) return false;
          break;
        case "20000000+":
          if (spent < 20000000) return false;
          break;
      }
    }

    return true;
  });
};

// CustomerFilters Component
const CustomerFilters = ({ onFilterChange, totalCount }) => {
  const [filters, setFilters] = useState({
    search: "",
    loyaltyRange: "all",
    spentRange: "all",
    sortBy: "total_spent",
    sortOrder: "desc",
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleFilterChange = useCallback(
    (key, value) => {
      const newFilters = { ...filters, [key]: value };
      setFilters(newFilters);

      if (key !== "search") {
        onFilterChange(newFilters);
      }
    },
    [filters, onFilterChange]
  );

  const [searchTimeout, setSearchTimeout] = useState(null);

  useEffect(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    const timeout = setTimeout(
      () => {
        onFilterChange(filters);
      },
      filters.search ? 500 : 0
    );

    setSearchTimeout(timeout);

    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [filters.search, onFilterChange]);

  const clearAllFilters = useCallback(() => {
    const defaultFilters = {
      search: "",
      loyaltyRange: "all",
      spentRange: "all",
      sortBy: "total_spent",
      sortOrder: "desc",
    };
    setFilters(defaultFilters);
    onFilterChange(defaultFilters);
  }, [onFilterChange]);

  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (filters.search && filters.search.trim()) count++;
    if (filters.loyaltyRange !== "all") count++;
    if (filters.spentRange !== "all") count++;
    return count;
  }, [filters]);

  return (
    <Card sx={{ mb: 3 }}>
      <MDBox p={3}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <MDInput
              fullWidth
              placeholder="Tìm theo tên hoặc số điện thoại..."
              value={filters.search}
              onChange={(e) => {
                handleFilterChange("search", e.target.value);
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Icon color="action">search</Icon>
                  </InputAdornment>
                ),
                endAdornment: filters.search && (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => handleFilterChange("search", "")}>
                      <Icon fontSize="small">clear</Icon>
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <MDBox display="flex" justifyContent="flex-end" gap={1}>
              <MDButton
                variant="outlined"
                color={showAdvanced ? "warning" : "info"}
                onClick={() => setShowAdvanced(!showAdvanced)}
                startIcon={<Icon>tune</Icon>}
                size="small"
              >
                Bộ lọc nâng cao
                {activeFiltersCount > 0 && (
                  <Chip
                    label={activeFiltersCount}
                    size="small"
                    color="error"
                    sx={{ ml: 1, height: 20, fontSize: "0.75rem" }}
                  />
                )}
              </MDButton>

              {activeFiltersCount > 0 && (
                <MDButton
                  variant="outlined"
                  color="warning"
                  onClick={clearAllFilters}
                  startIcon={<Icon>clear_all</Icon>}
                  size="small"
                >
                  Xóa bộ lọc
                </MDButton>
              )}
            </MDBox>
          </Grid>
        </Grid>

        <Collapse in={showAdvanced}>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Điểm tích lũy</InputLabel>
                <Select
                  value={filters.loyaltyRange}
                  onChange={(e) => {
                    handleFilterChange("loyaltyRange", e.target.value);
                  }}
                  label="Điểm tích lũy"
                >
                  <MenuItem value="all">Tất cả</MenuItem>
                  <MenuItem value="0-50">0-50 điểm</MenuItem>
                  <MenuItem value="51-100">51-100 điểm</MenuItem>
                  <MenuItem value="101-200">101-200 điểm</MenuItem>
                  <MenuItem value="200+">200+ điểm</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Mức chi tiêu</InputLabel>
                <Select
                  value={filters.spentRange}
                  onChange={(e) => {
                    handleFilterChange("spentRange", e.target.value);
                  }}
                  label="Mức chi tiêu"
                >
                  <MenuItem value="all">Tất cả</MenuItem>
                  <MenuItem value="0-5000000">Dưới 5 triệu</MenuItem>
                  <MenuItem value="5000000-10000000">5-10 triệu</MenuItem>
                  <MenuItem value="10000000-20000000">10-20 triệu</MenuItem>
                  <MenuItem value="20000000+">Trên 20 triệu</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Sắp xếp theo</InputLabel>
                <Select
                  value={filters.sortBy}
                  onChange={(e) => {
                    handleFilterChange("sortBy", e.target.value);
                  }}
                  label="Sắp xếp theo"
                >
                  <MenuItem value="total_spent">Chi tiêu</MenuItem>
                  <MenuItem value="loyalty_points">Điểm tích lũy</MenuItem>
                  <MenuItem value="name">Tên A-Z</MenuItem>
                  <MenuItem value="created_at">Ngày tham gia</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Thứ tự</InputLabel>
                <Select
                  value={filters.sortOrder}
                  onChange={(e) => {
                    handleFilterChange("sortOrder", e.target.value);
                  }}
                  label="Thứ tự"
                >
                  <MenuItem value="desc">Giảm dần</MenuItem>
                  <MenuItem value="asc">Tăng dần</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {activeFiltersCount > 0 && (
            <MDBox mt={2}>
              <MDTypography variant="caption" color="text" mb={1} display="block">
                Bộ lọc đang áp dụng:
              </MDTypography>
              <MDBox display="flex" gap={1} flexWrap="wrap">
                {filters.search && filters.search.trim() && (
                  <Chip
                    label={`Tìm kiếm: "${filters.search}"`}
                    onDelete={() => handleFilterChange("search", "")}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                )}
                {filters.loyaltyRange !== "all" && (
                  <Chip
                    label={`Điểm: ${filters.loyaltyRange}`}
                    onDelete={() => handleFilterChange("loyaltyRange", "all")}
                    size="small"
                    color="secondary"
                    variant="outlined"
                  />
                )}
                {filters.spentRange !== "all" && (
                  <Chip
                    label={`Chi tiêu: ${filters.spentRange}`}
                    onDelete={() => handleFilterChange("spentRange", "all")}
                    size="small"
                    color="info"
                    variant="outlined"
                  />
                )}
              </MDBox>
            </MDBox>
          )}
        </Collapse>

        <MDBox mt={2} display="flex" justifyContent="space-between" alignItems="center">
          <MDTypography variant="body2" color="text">
            {totalCount > 0 ? (
              <>
                Hiển thị <strong>{totalCount}</strong> khách hàng
              </>
            ) : (
              "Không tìm thấy khách hàng nào"
            )}
          </MDTypography>

          <MDBox display="flex" alignItems="center" gap={1}>
            <Icon fontSize="small" color="action">
              info
            </Icon>
            <MDTypography variant="caption" color="text">
              Sử dụng bộ lọc để tìm kiếm chính xác hơn
            </MDTypography>
          </MDBox>
        </MDBox>
      </MDBox>
    </Card>
  );
};

CustomerFilters.propTypes = {
  onFilterChange: PropTypes.func.isRequired,
  totalCount: PropTypes.number.isRequired,
};

// Main Customer Component
function Customer() {
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;
  const theme = useTheme();

  // State
  const [customers, setCustomers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [filters, setFilters] = useState({
    search: "",
    loyaltyRange: "all",
    spentRange: "all",
    sortBy: "total_spent",
    sortOrder: "desc",
  });

  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState("view");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    loyalty_points: 0,
    total_spent: 0,
  });
  const [loyaltyHistory, setLoyaltyHistory] = useState([]);

  const fetchCustomers = useCallback(
    async (page = 1, currentFilters = null, forceRefresh = false) => {
      setIsLoading(true);
      setError(null);

      try {
        const filtersToUse = currentFilters || filters;

        // THÊM: Sử dụng refreshCustomers nếu forceRefresh = true
        const data = forceRefresh
          ? await refreshCustomers(page, filtersToUse)
          : await getCustomers(page, filtersToUse);

        if (data && Array.isArray(data.results)) {
          let customersToDisplay = data.results;
          let totalCountToDisplay = data.count;

          // Apply client-side filtering if needed
          const hasActiveFilters =
            (filtersToUse.loyaltyRange && filtersToUse.loyaltyRange !== "all") ||
            (filtersToUse.spentRange && filtersToUse.spentRange !== "all");

          if (hasActiveFilters) {
            customersToDisplay = applyClientSideFilters(data.results, filtersToUse);
            totalCountToDisplay = customersToDisplay.length;
          }

          setCustomers(customersToDisplay);
          setTotalPages(Math.ceil(totalCountToDisplay / 10));
          setTotalCount(totalCountToDisplay);
          setCurrentPage(page);

          // THÊM: Success message khi force refresh
          if (forceRefresh) {
            console.log("🔄 Force refresh completed - data updated from server");
          }
        } else {
          console.error("Invalid data format:", data);
          setError("Dữ liệu không đúng định dạng");
          setCustomers([]);
          setTotalCount(0);
        }
      } catch (error) {
        console.error("Error loading customers:", error);
        setError("Không thể tải danh sách khách hàng");
        setCustomers([]);
        setTotalCount(0);
      } finally {
        setIsLoading(false);
      }
    },
    [filters]
  );

  // THÊM: Force refresh function
  const handleForceRefresh = useCallback(() => {
    console.log("🔄 Force refreshing customer data...");
    fetchCustomers(currentPage, filters, true); // forceRefresh = true
  }, [fetchCustomers, currentPage, filters]);

  const handleFilterChange = useCallback(
    (newFilters) => {
      setFilters(newFilters);
      setCurrentPage(1);
      fetchCustomers(1, newFilters);
    },
    [fetchCustomers]
  );

  const handlePageChange = useCallback(
    (page) => {
      fetchCustomers(page, filters);
    },
    [fetchCustomers, filters]
  );

  useEffect(() => {
    fetchCustomers(1);
  }, [fetchCustomers]);

  // THÊM: Listen for bill creation events
  useEffect(() => {
    const handleBillCreated = (event) => {
      console.log("🔄 Bill created event received, refreshing customer data");
      handleForceRefresh();
    };

    const handleCustomerDataUpdate = (event) => {
      console.log("🔄 Customer data update event received");
      handleForceRefresh();
    };

    window.addEventListener("billCreatedFromTable", handleBillCreated);
    window.addEventListener("customerDataUpdated", handleCustomerDataUpdate);

    return () => {
      window.removeEventListener("billCreatedFromTable", handleBillCreated);
      window.removeEventListener("customerDataUpdated", handleCustomerDataUpdate);
    };
  }, [handleForceRefresh]);

  // Handle view customer details
  const handleView = async (id) => {
    try {
      setIsLoading(true);

      // ✅ FORCE REFRESH: Bypass cache cho customer detail
      const data = await getCustomerDetail(id, true); // forceRefresh = true
      console.log("🔄 Customer detail refreshed:", data);

      try {
        // ✅ FORCE REFRESH: Bypass cache cho loyalty history
        const loyaltyData = await getCustomerLoyaltyHistory(id, true); // forceRefresh = true
        console.log("🔄 Loyalty history refreshed:", loyaltyData);
        console.log("📊 Total bills:", loyaltyData.history?.length || 0);
        console.log("📊 Expected total points:", data.loyalty_points);
        console.log("📊 Expected total spent:", data.total_spent);

        setLoyaltyHistory(loyaltyData.history || []);
      } catch (err) {
        console.error("Error fetching loyalty history:", err);
        setLoyaltyHistory([]);
      }

      setSelectedCustomer(data);
      setFormData(data); // ✅ Sử dụng data fresh từ server
      setDialogMode("view");
      setOpenDialog(true);
    } catch (error) {
      console.error("Error fetching customer details:", error);
      alert("Không thể tải thông tin khách hàng. Vui lòng thử lại sau.");
    } finally {
      setIsLoading(false);
    }
  };
  const handleRefreshDialog = async () => {
    if (selectedCustomer?.id) {
      console.log("🔄 Refreshing dialog data...");
      await handleView(selectedCustomer.id);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedCustomer(null);
    setLoyaltyHistory([]);
  };

  // Table data
  const handlers = { handleView };
  const tableData = buildCustomerTableData(customers, handlers);
  const columns = tableData.columns;
  const rows = tableData.rows;

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <CustomerFilters onFilterChange={handleFilterChange} totalCount={totalCount} />

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
                <MDBox>
                  <MDTypography variant="h6" color="white">
                    Danh sách khách hàng thân thiết
                  </MDTypography>
                  <MDTypography variant="body2" color="white" opacity={0.8}>
                    Quản lý thông tin và điểm tích lũy khách hàng
                  </MDTypography>
                </MDBox>

                <MDBox display="flex" gap={1}>
                  {/* CẬP NHẬT: Nút làm mới với force refresh */}
                  <MDButton
                    variant="contained"
                    color="dark"
                    onClick={handleForceRefresh}
                    disabled={isLoading}
                    startIcon={<Icon>refresh</Icon>}
                  >
                    {isLoading ? "Đang tải..." : "Làm mới"}
                  </MDButton>

                  {/* THÊM: Nút refresh nhanh (cache) */}
                  <MDButton
                    variant="outlined"
                    color="white"
                    onClick={() => fetchCustomers(currentPage, filters, false)}
                    disabled={isLoading}
                    startIcon={<Icon>cached</Icon>}
                    sx={{ color: "white", borderColor: "white" }}
                  >
                    Cache
                  </MDButton>
                </MDBox>
              </MDBox>

              {error && (
                <MDBox p={2}>
                  <Alert
                    severity="error"
                    action={
                      <MDButton color="error" size="small" onClick={handleForceRefresh}>
                        Thử lại
                      </MDButton>
                    }
                  >
                    {error}
                  </Alert>
                </MDBox>
              )}

              {isLoading ? (
                <MDBox display="flex" justifyContent="center" p={5}>
                  <CircularProgress color="info" />
                </MDBox>
              ) : customers.length === 0 ? (
                <MDBox textAlign="center" p={5}>
                  <Icon sx={{ fontSize: "4rem", color: "text.secondary", mb: 2 }}>
                    people_outline
                  </Icon>
                  <MDTypography variant="h5" color="text" mb={1}>
                    Không tìm thấy khách hàng
                  </MDTypography>
                  <MDTypography variant="body2" color="text" mb={3}>
                    {filters.search ||
                    filters.loyaltyRange !== "all" ||
                    filters.spentRange !== "all"
                      ? "Thử điều chỉnh bộ lọc để tìm thấy kết quả phù hợp"
                      : "Chưa có khách hàng nào trong hệ thống"}
                  </MDTypography>
                </MDBox>
              ) : (
                <MDBox pt={3}>
                  <DataTable
                    table={{ columns, rows }}
                    isSorted={false}
                    entriesPerPage={false}
                    showTotalEntries={false}
                    noEndBorder
                    noPagination
                  />
                </MDBox>
              )}

              {totalPages > 1 && (
                <MDBox display="flex" justifyContent="center" alignItems="center" p={3}>
                  <MDBox display="flex" alignItems="center" gap={1}>
                    <MDButton
                      variant="outlined"
                      color="info"
                      size="small"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1 || isLoading}
                    >
                      <Icon>chevron_left</Icon>
                    </MDButton>

                    {Array.from({ length: Math.min(totalPages, 5) }).map((_, index) => {
                      const pageNumber = Math.max(1, currentPage - 2) + index;
                      if (pageNumber <= totalPages) {
                        return (
                          <MDButton
                            key={pageNumber}
                            variant={currentPage === pageNumber ? "contained" : "outlined"}
                            color="info"
                            size="small"
                            onClick={() => handlePageChange(pageNumber)}
                            disabled={isLoading}
                            sx={{ minWidth: "40px" }}
                          >
                            {pageNumber}
                          </MDButton>
                        );
                      }
                      return null;
                    })}

                    <MDButton
                      variant="outlined"
                      color="info"
                      size="small"
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages || isLoading}
                    >
                      <Icon>chevron_right</Icon>
                    </MDButton>
                  </MDBox>

                  <MDBox ml={3}>
                    <MDTypography variant="caption" color="text">
                      Trang {currentPage} / {totalPages} • {totalCount} khách hàng
                    </MDTypography>
                  </MDBox>
                </MDBox>
              )}
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      {/* Customer Details Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        fullWidth
        maxWidth="lg"
        PaperProps={{
          sx: {
            bgcolor: darkMode ? theme.palette.background.card : theme.palette.background.paper,
            color: darkMode ? theme.palette.white.main : theme.palette.text.main,
            boxShadow: darkMode ? theme.boxShadows.xxl : theme.boxShadows.lg,
            borderRadius: "12px",
            minHeight: "600px",
          },
        }}
      >
        {selectedCustomer && (
          <>
            <DialogTitle>
              <MDBox display="flex" justifyContent="space-between" alignItems="center">
                <MDBox display="flex" alignItems="center">
                  <Icon sx={{ mr: 2, fontSize: "2rem", color: "info.main" }}>person</Icon>
                  <MDTypography variant="h4" fontWeight="bold">
                    Chi tiết khách hàng
                  </MDTypography>
                </MDBox>
                <MDButton
                  variant="text"
                  color="secondary"
                  onClick={handleCloseDialog}
                  sx={{
                    minWidth: "auto",
                    p: 1,
                    borderRadius: "50%",
                    "&:hover": { backgroundColor: "error.main", color: "white" },
                  }}
                >
                  <Icon>close</Icon>
                </MDButton>
              </MDBox>
            </DialogTitle>

            <DialogContent sx={{ p: 0 }}>
              {/* Header Section */}
              <MDBox
                sx={{
                  background: `linear-gradient(135deg, ${theme.palette.info.main} 0%, ${theme.palette.info.dark} 100%)`,
                  color: "white",
                  p: 4,
                }}
              >
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} md={8}>
                    <MDBox>
                      <MDTypography variant="h3" fontWeight="bold" color="white" mb={1}>
                        {formData.name || "Khách hàng"}
                      </MDTypography>
                      <MDBox display="flex" alignItems="center" mb={2}>
                        <Icon sx={{ mr: 1 }}>phone</Icon>
                        <MDTypography variant="h6" color="white" fontWeight="medium">
                          {formData.phone || "Chưa có số điện thoại"}
                        </MDTypography>
                      </MDBox>
                    </MDBox>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <MDBox display="flex" flexDirection="column" alignItems="center">
                      <MDBox
                        sx={{
                          width: 100,
                          height: 100,
                          borderRadius: "50%",
                          backgroundColor: "rgba(255,255,255,0.2)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          mb: 2,
                        }}
                      >
                        <Icon sx={{ fontSize: "3rem", color: "white" }}>person</Icon>
                      </MDBox>
                      <MDTypography variant="body2" color="white" textAlign="center">
                        Khách hàng thân thiết
                      </MDTypography>
                    </MDBox>
                  </Grid>
                </Grid>
              </MDBox>

              {/* Stats Section */}
              <MDBox sx={{ p: 3, backgroundColor: darkMode ? "grey.900" : "grey.50" }}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <MDBox
                      sx={{
                        backgroundColor: "success.main",
                        borderRadius: "16px",
                        p: 3,
                        textAlign: "center",
                        color: "white",
                        height: "180px",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "center",
                        alignItems: "center",
                      }}
                    >
                      <Icon sx={{ fontSize: "3rem", mb: 1 }}>stars</Icon>
                      <MDTypography variant="h2" fontWeight="bold" color="white">
                        {formData.loyalty_points || 0}
                      </MDTypography>
                      <MDTypography variant="h6" color="white">
                        Điểm tích lũy
                      </MDTypography>
                    </MDBox>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <MDBox
                      sx={{
                        backgroundColor: "warning.main",
                        borderRadius: "16px",
                        p: 3,
                        textAlign: "center",
                        color: "white",
                        height: "180px",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "center",
                        alignItems: "center",
                      }}
                    >
                      <Icon sx={{ fontSize: "3rem", mb: 1 }}>account_balance_wallet</Icon>
                      <MDTypography variant="h2" fontWeight="bold" color="white">
                        {Number(formData.total_spent || 0).toLocaleString("vi-VN")}
                      </MDTypography>
                      <MDTypography variant="h6" color="white">
                        Tổng chi tiêu (VNĐ)
                      </MDTypography>
                    </MDBox>
                  </Grid>
                </Grid>
              </MDBox>

              {/* Transaction History Section */}
              <MDBox sx={{ p: 3 }}>
                <MDBox display="flex" alignItems="center" mb={3}>
                  <Icon sx={{ mr: 2, fontSize: "1.5rem", color: "info.main" }}>history</Icon>
                  <MDTypography variant="h5" fontWeight="bold">
                    Lịch sử giao dịch
                  </MDTypography>
                </MDBox>

                <MDBox
                  sx={{
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: "12px",
                    overflow: "hidden",
                  }}
                >
                  {/* Table Header */}
                  <MDBox
                    sx={{
                      backgroundColor: darkMode ? "grey.800" : "grey.100",
                      p: 2,
                    }}
                  >
                    <Grid container spacing={1} alignItems="center">
                      <Grid item xs={2}>
                        <MDTypography
                          variant="button"
                          fontWeight="bold"
                          color="text"
                          textAlign="center"
                        >
                          Mã HĐ
                        </MDTypography>
                      </Grid>
                      <Grid item xs={3}>
                        <MDTypography
                          variant="button"
                          fontWeight="bold"
                          color="text"
                          textAlign="center"
                        >
                          Ngày giao dịch
                        </MDTypography>
                      </Grid>
                      <Grid item xs={3}>
                        <MDTypography
                          variant="button"
                          fontWeight="bold"
                          color="text"
                          textAlign="center"
                        >
                          Số tiền
                        </MDTypography>
                      </Grid>
                      <Grid item xs={2}>
                        <MDTypography
                          variant="button"
                          fontWeight="bold"
                          color="text"
                          textAlign="center"
                        >
                          Điểm +
                        </MDTypography>
                      </Grid>
                      <Grid item xs={2}>
                        <MDTypography
                          variant="button"
                          fontWeight="bold"
                          color="text"
                          textAlign="center"
                        >
                          Trạng thái
                        </MDTypography>
                      </Grid>
                    </Grid>
                  </MDBox>

                  {/* Table Body */}
                  <MDBox sx={{ maxHeight: "300px", overflowY: "auto" }}>
                    {loyaltyHistory && loyaltyHistory.length > 0 ? (
                      loyaltyHistory.map((item, index) => {
                        // Tính số điểm đã cộng: nếu không dùng điểm (points_used = 0) thì cộng điểm
                        // Điểm = original_total / 10000 (1 điểm per 10,000 VNĐ chi tiêu)
                        const originalTotal = Number(item.original_total || item.total || 0);
                        const pointsUsed = Number(item.points_used || 0);
                        // Nếu có dùng điểm thì không được cộng điểm
                        const pointsEarned = pointsUsed > 0 ? 0 : Math.floor(originalTotal / 10000);
                        const billTotal = Number(item.total || 0);

                        return (
                          <MDBox
                            key={item.id || index}
                            sx={{
                              p: 2,
                              borderBottom:
                                index < loyaltyHistory.length - 1 ? "1px solid" : "none",
                              borderColor: "divider",
                              "&:hover": {
                                backgroundColor: darkMode ? "grey.800" : "grey.50",
                              },
                            }}
                          >
                            <Grid container spacing={1} alignItems="center">
                              {/* Mã HĐ */}
                              <Grid item xs={2}>
                                <MDBox
                                  sx={{
                                    backgroundColor: "info.main",
                                    color: "white",
                                    px: 1.5,
                                    py: 0.5,
                                    borderRadius: "8px",
                                    display: "inline-block",
                                  }}
                                >
                                  <MDTypography variant="caption" fontWeight="bold">
                                    #{item.id || "N/A"}
                                  </MDTypography>
                                </MDBox>
                              </Grid>

                              {/* Ngày giao dịch */}
                              <Grid item xs={3}>
                                <MDBox>
                                  <MDTypography variant="body2">
                                    {item.date
                                      ? new Date(item.date).toLocaleDateString("vi-VN", {
                                          day: "2-digit",
                                          month: "2-digit",
                                          year: "numeric",
                                        })
                                      : "N/A"}
                                  </MDTypography>
                                </MDBox>
                              </Grid>

                              {/* Số tiền */}
                              <Grid item xs={3}>
                                <MDBox>
                                  <MDTypography variant="h6" fontWeight="bold" color="warning.main">
                                    {billTotal.toLocaleString("vi-VN")}
                                  </MDTypography>
                                  <MDTypography variant="caption" color="text">
                                    VNĐ
                                    {pointsUsed > 0 && ` (gốc: ${originalTotal.toLocaleString()})`}
                                  </MDTypography>
                                </MDBox>
                              </Grid>

                              {/* Điểm +/- */}
                              <Grid item xs={2}>
                                {pointsUsed > 0 ? (
                                  <MDBox
                                    sx={{
                                      backgroundColor: "error.main",
                                      color: "white",
                                      borderRadius: "50%",
                                      width: 40,
                                      height: 40,
                                      display: "inline-flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                    }}
                                  >
                                    <MDTypography variant="caption" fontWeight="bold">
                                      -{pointsUsed}
                                    </MDTypography>
                                  </MDBox>
                                ) : (
                                  <MDBox
                                    sx={{
                                      backgroundColor: "success.main",
                                      color: "white",
                                      borderRadius: "50%",
                                      width: 40,
                                      height: 40,
                                      display: "inline-flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                    }}
                                  >
                                    <MDTypography variant="caption" fontWeight="bold">
                                      +{pointsEarned}
                                    </MDTypography>
                                  </MDBox>
                                )}
                              </Grid>

                              {/* Trạng thái */}
                              <Grid item xs={2}>
                                <MDBox
                                  sx={{
                                    backgroundColor: "success.light",
                                    color: "success.dark",
                                    px: 1,
                                    py: 0.5,
                                    borderRadius: "16px",
                                    display: "inline-block",
                                  }}
                                >
                                  <MDTypography variant="caption" fontWeight="medium">
                                    Hoàn thành
                                  </MDTypography>
                                </MDBox>
                              </Grid>
                            </Grid>
                          </MDBox>
                        );
                      })
                    ) : (
                      <MDBox p={4} textAlign="center">
                        <Icon sx={{ fontSize: "3rem", color: "text.secondary", mb: 2 }}>
                          history
                        </Icon>
                        <MDTypography variant="h6" color="text" mb={1}>
                          Chưa có giao dịch nào
                        </MDTypography>
                        <MDTypography variant="body2" color="text">
                          Khách hàng chưa thực hiện giao dịch nào
                        </MDTypography>
                      </MDBox>
                    )}
                  </MDBox>

                  {/* Summary Footer */}
                  <MDBox
                    sx={{
                      backgroundColor: darkMode ? "grey.800" : "grey.100",
                      p: 2,
                      borderTop: "2px solid",
                      borderColor: "info.main",
                    }}
                  >
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={6}>
                        <MDTypography variant="body1" fontWeight="bold" textAlign="left">
                          Tổng cộng: {loyaltyHistory?.length || 0} giao dịch
                        </MDTypography>
                      </Grid>
                      <Grid item xs={6}>
                        <MDTypography
                          variant="body1"
                          fontWeight="bold"
                          color="info.main"
                          textAlign="right"
                        >
                          Tích điểm: 1 điểm / 10,000 VNĐ
                        </MDTypography>
                      </Grid>
                    </Grid>
                  </MDBox>
                </MDBox>
              </MDBox>
            </DialogContent>

            <DialogActions
              sx={{
                p: 3,
                borderTop: "1px solid",
                borderColor: "divider",
                backgroundColor: darkMode ? "grey.900" : "grey.50",
              }}
            >
              <MDButton
                variant="outlined"
                color="secondary"
                onClick={handleCloseDialog}
                size="large"
              >
                <Icon sx={{ mr: 1 }}>close</Icon>
                Đóng
              </MDButton>
              <MDButton
                variant="outlined"
                color="info"
                onClick={handleRefreshDialog}
                size="large"
                sx={{ mx: 1 }}
              >
                <Icon sx={{ mr: 1 }}>refresh</Icon>
                Làm mới
              </MDButton>
              <MDButton
                variant="gradient"
                color="warning"
                size="large"
                onClick={() => {
                  alert(`Chỉnh sửa thông tin: ${formData.name}`);
                }}
                sx={{ mx: 1 }}
              >
                <Icon sx={{ mr: 1 }}>edit</Icon>
                Chỉnh sửa
              </MDButton>
            </DialogActions>
          </>
        )}
      </Dialog>

      <Footer />
    </DashboardLayout>
  );
}

export default Customer;
