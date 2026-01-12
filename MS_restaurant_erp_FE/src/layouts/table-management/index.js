import { useState, useEffect } from "react";
import { Card, Grid, Tabs, Tab, Box, Typography, CircularProgress } from "@mui/material";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import Icon from "@mui/material/Icon";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import { API_BASE_URL } from "services/config";
// Custom hooks
import useTableManagement from "./hooks/useTableManagement";
import useMenuItems from "./hooks/useMenuItems";

// Components
import TableCard from "./components/TableCard";
import OrderDetailsDialog from "./components/OrderDetailsDialog";
import AddOrderDialog from "./components/AddOrderDialog";
import AddTableDialog from "./components/AddTableDialog";

function TableManagement() {
  const [activeFloor, setActiveFloor] = useState(0);
  const [openOrderDialog, setOpenOrderDialog] = useState(false);
  const [openAddOrderDialog, setOpenAddOrderDialog] = useState(false);
  const [openAddTableDialog, setOpenAddTableDialog] = useState(false);
  const floors = ["Tầng 1", "Tầng 2", "Tầng 3"];

  const handleFloorChange = (event, newValue) => {
    console.log(`Chuyển sang tầng: ${newValue + 1}`);
    setActiveFloor(newValue);
  };

  // Sử dụng custom hooks
  const {
    tables,
    loading,
    error,
    selectedTable,
    setSelectedTable,
    tableOrders,
    fetchTables,
    fetchTableOrders,
    addTable,
    removeTable,
    createBill,
    updateTableStatus,
    setError,
    setLoading,
  } = useTableManagement();

  const menuHook = useMenuItems(setError);

  // State cho dialog thêm bàn mới
  const [newTableData, setNewTableData] = useState({
    name: "",
    capacity: 4,
    floor: 0,
    status: "available",
  });
  useEffect(() => {
    const loadTables = async () => {
      try {
        console.log(`🔄 Đang tải danh sách bàn... (activeFloor: ${activeFloor})`);
        const tableData = await fetchTables();
        console.log(`📊 Tất cả bàn từ API (${tableData.length} bàn):`, tableData);

        // Phân tích giá trị tầng từ API
        if (tableData && tableData.length > 0) {
          console.log("🔍 Các giá trị tầng trong dữ liệu:", [
            ...new Set(tableData.map((t) => t.floor)),
          ]);

          // Chi tiết từng bàn
          tableData.forEach((table, index) => {
            console.log(
              `Bàn ${index}: id=${table.id}, name=${table.name}, floor=${table.floor
              } (${typeof table.floor})`
            );
          });

          // Kiểm tra khớp với activeFloor
          const matchCount = tableData.filter(
            (t) => Number(t.floor) === Number(activeFloor)
          ).length;
          console.log(`🎯 Có ${matchCount}/${tableData.length} bàn ở tầng ${activeFloor}`);
        }
      } catch (error) {
        console.error("❌ Lỗi khi tải bàn:", error);
        setError("Không thể tải danh sách bàn. Vui lòng thử lại.");
      }
    };

    loadTables();
  }, [fetchTables, activeFloor]);

  useEffect(() => {
    console.log("🚀 Component TableManagement mounted, fetching tables...");
    fetchTables();
  }, [fetchTables]);

  // Xử lý mở dialog thêm bàn với số tự động
  const handleOpenAddTableDialog = () => {
    // Tìm số bàn cao nhất của tầng hiện tại
    const tablesInCurrentFloor = tables.filter((table) => table.floor === activeFloor);
    let nextNumber = 1;

    if (tablesInCurrentFloor.length > 0) {
      // Tìm số bàn lớn nhất trong tầng hiện tại
      const tableNumbers = tablesInCurrentFloor
        .map((table) => {
          // Trích xuất số từ tên bàn (nếu tên bàn có định dạng "Bàn X" hoặc chỉ là số)
          const match = table.name.toString().match(/\d+/);
          return match ? parseInt(match[0]) : 0;
        })
        .filter((num) => !isNaN(num));

      if (tableNumbers.length > 0) {
        nextNumber = Math.max(...tableNumbers) + 1;
      }
    }

    // Đặt dữ liệu mặc định cho bàn mới với tầng hiện tại
    setNewTableData({
      name: nextNumber,
      capacity: 4,
      floor: activeFloor,
      status: "available",
    });

    setOpenAddTableDialog(true);
  };
  const handleTableClick = async (table) => {
    console.log("🎯 handleTableClick called with table:", table);
    console.log("- table.id:", table?.id);
    console.log("- table.status:", table?.status);

    if (!table || !table.id) {
      console.error("❌ Invalid table object:", table);
      setError("Thông tin bàn không hợp lệ");
      return;
    }

    setSelectedTable(table);
    console.log(" selectedTable set to:", table);

    if (table.status === "occupied") {
      // Bàn có khách → Xem chi tiết
      console.log("🍽️ Opening order details for occupied table");
      try {
        await fetchTableOrders(table);
        setOpenOrderDialog(true);
      } catch (error) {
        console.error("❌ Error fetching table orders:", error);
        setError("Không thể tải thông tin bàn");
      }
    } else {
      // Bàn trống hoặc đặt trước → Gọi món
      console.log("➕ Opening add order dialog for available/reserved table");
      setOpenAddOrderDialog(true);
    }
  };

  const handleCloseOrderDialog = () => {
    setOpenOrderDialog(false);
  };

  // Sửa handleCreateBill để CHỈ chuyển hướng (không tạo bill trực tiếp)
  const handleCreateBill = async (table) => {
    console.log("🧾 handleCreateBill called with table:", table);

    if (!table || !table.id) {
      setError("Không thể tạo hóa đơn: Thiếu thông tin bàn");
      return;
    }

    try {
      console.log("📤 Preparing to redirect to bill creation page for table:", table.id);

      const createBillUrl = `/create-payment-bill?tableId=${table.id
        }&tableName=${encodeURIComponent(table.name)}`;
      console.log("🔄 Redirecting to:", createBillUrl);

      setOpenOrderDialog(false);
      setSelectedTable(null);

      window.open(createBillUrl, "_blank");

      // navigate(createBillUrl);
    } catch (error) {
      console.error("❌ Error in handleCreateBill:", error);
      setError(`Lỗi: ${error.message}`);
    }
  };

  // Xử lý gọi thêm món
  const openAddOrderDialogHandler = () => {
    console.log("🔄 openAddOrderDialogHandler called");
    console.log("- selectedTable:", selectedTable);
    console.log("- selectedTable.id:", selectedTable?.id);

    if (!selectedTable || !selectedTable.id) {
      console.error("❌ No valid table selected for adding order");
      setError("Vui lòng chọn bàn trước khi gọi món");
      return;
    }

    console.log(" Opening add order dialog for table:", selectedTable.id);
    setOpenAddOrderDialog(true);
  };

  // Sửa hàm handleAddItemsToTable
  const handleAddItemsToTable = async (tableId) => {
    const validTableId = typeof tableId === "object" ? tableId.id : tableId;

    console.log("🍽️ handleAddItemsToTable called:");
    console.log("- Original tableId:", tableId, typeof tableId);
    console.log("- Valid tableId:", validTableId, typeof validTableId);

    if (!validTableId) {
      console.error("❌ No valid table ID provided");
      setError("Không thể thêm món: Thiếu thông tin bàn");
      return false;
    }

    try {
      setLoading(true);

      console.log("📤 Adding items to table...");
      const success = await menuHook.addItemsToTable(validTableId);

      if (success) {
        console.log("Items added successfully");

        const currentTable = tables.find(
          (t) => t.id === validTableId || t.id === Number(validTableId)
        );
        console.log("🔍 Found table:", currentTable);
        console.log("🔄 Current table status:", currentTable?.status);

        if (currentTable && currentTable.status !== "occupied") {
          console.log("🔄 Auto-updating table status to occupied");

          try {
            // Gọi API cập nhật trạng thái từ hook với tableId hợp lệ
            const statusUpdateSuccess = await updateTableStatus(validTableId, "occupied");

            if (statusUpdateSuccess) {
              console.log("Table status updated to occupied");
            } else {
              console.warn("⚠️ Failed to update table status, but items were added");
            }
          } catch (statusError) {
            console.error("❌ Failed to update table status:", statusError);
            // Không throw error vì món đã được thêm thành công
          }
        } else {
          console.log("ℹ️ Table already occupied or not found");
        }

        console.log("🔄 Refreshing data...");
        await fetchTables();

        if (currentTable) {
          await fetchTableOrders(currentTable);
        }

        setOpenAddOrderDialog(false);

        console.log("🎉 Order process completed successfully");
        return true;
      } else {
        console.error("❌ Failed to add items to table");
        setError("Không thể thêm món vào bàn");
        return false;
      }
    } catch (error) {
      console.error("❌ Error in handleAddItemsToTable:", error);
      setError(`Không thể thêm món: ${error.message}`);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Thêm bàn mới
  const handleAddTable = async () => {
    if (!newTableData.name) {
      setError("Vui lòng nhập số bàn");
      return;
    }

    // Format tên bàn dựa trên số và tầng
    const formattedTableData = {
      ...newTableData,
      name: `Bàn ${newTableData.name}`, // Định dạng tên bàn
      floor: activeFloor, // Đảm bảo bàn được thêm vào tầng hiện tại
    };

    const success = await addTable(formattedTableData);
    if (success) {
      setOpenAddTableDialog(false);
      // Giữ nguyên tầng hiện tại cho lần thêm tiếp theo
      setNewTableData({
        name: "",
        capacity: 4,
        floor: activeFloor,
        status: "available",
      });
      alert("Thêm bàn thành công!");
    }
  };

  // Xóa bàn
  const handleDeleteTable = async (tableId) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa bàn này?")) {
      const success = await removeTable(tableId);
      if (success) {
        alert("Xóa bàn thành công!");
      }
    }
  };

  const handleToggleReservation = async (table) => {
    console.log("🔄 handleToggleReservation called:");
    console.log("- table:", table);
    console.log("- table.id:", table?.id);

    if (!table || !table.id) {
      console.error("❌ Invalid table object:", table);
      setError("Không thể cập nhật trạng thái: Thông tin bàn không hợp lệ");
      return;
    }

    try {
      const newStatus = table.status === "available" ? "reserved" : "available";
      console.log(`🔄 Changing table ${table.id} status: ${table.status} -> ${newStatus}`);

      const success = await updateTableStatus(table.id, newStatus);

      if (success) {
        console.log(`Successfully updated table ${table.id} status`);
      } else {
        console.error(`❌ Failed to update table ${table.id} status`);
        setError("Không thể cập nhật trạng thái bàn");
      }
    } catch (error) {
      console.error("❌ Error in handleToggleReservation:", error);
      setError(`Không thể thay đổi trạng thái bàn: ${error.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "available":
        return "success";
      case "occupied":
        return "error";
      case "reserved":
        return "warning";
      default:
        return "info";
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "available":
        return "Trống";
      case "occupied":
        return "Đã có khách";
      case "reserved":
        return "Đã đặt trước";
      default:
        return "Không xác định";
    }
  };

  const calculateTotal = (orders) => {
    if (!orders || !orders.length) return 0;
    return orders.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        {loading && (
          <MDBox display="flex" justifyContent="center" mb={2}>
            <CircularProgress />
          </MDBox>
        )}

        {error && (
          <MDBox mb={2}>
            <Typography color="error" align="center">
              {error}
            </Typography>
          </MDBox>
        )}

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
                <MDTypography variant="h6" color="white">
                  Quản lý bàn
                </MDTypography>
                <Box display="flex" gap={1}>
                  <MDButton variant="gradient" color="success" onClick={handleOpenAddTableDialog}>
                    <Icon>add</Icon>&nbsp; Thêm bàn
                  </MDButton>
                  <MDButton variant="gradient" color="dark" onClick={() => fetchTables()}>
                    <Icon>refresh</Icon>&nbsp; Làm mới
                  </MDButton>
                  <MDButton
                    variant="outlined"
                    color="info"
                    onClick={async () => {
                      try {
                        const response = await fetch(`${API_BASE_URL}/api/tables/`, {
                          headers: {
                            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                          },
                        });
                        const data = await response.json();
                        console.log("🧪 Test API direct call:", data);
                        alert(`Tìm thấy ${data.length} bàn từ API`);
                      } catch (err) {
                        console.error("Test API error:", err);
                        alert("Lỗi: " + err.message);
                      }
                    }}
                  >
                    <Icon>bug_report</Icon>&nbsp; Test API
                  </MDButton>
                  <MDButton
                    variant="outlined"
                    color="error"
                    onClick={() => {
                      console.log("=== DEBUG FULL STATE ===");
                      console.log("tables:", tables);
                      console.log("tables.length:", tables?.length);
                      console.log("activeFloor:", activeFloor, typeof activeFloor);
                      console.log("loading:", loading);
                      console.log("error:", error);

                      if (tables && tables.length > 0) {
                        console.log("Sample table:", tables[0]);
                        const filtered = tables.filter(
                          (t) => Number(t.floor) === Number(activeFloor)
                        );
                        console.log(`Filtered tables for floor ${activeFloor}:`, filtered);
                      }

                      alert(`🔍 Debug Info:
                                - Tables: ${tables?.length || 0}
                                - Active Floor: ${activeFloor}
                                - Loading: ${loading}
                                - Error: ${error || "None"}
                                - Check console for details`);
                    }}
                  >
                    <Icon>bug_report</Icon>&nbsp; Full Debug
                  </MDButton>
                </Box>
              </MDBox>

              <MDBox p={3}>
                <Tabs value={activeFloor} onChange={handleFloorChange} centered>
                  {floors.map((floor, index) => (
                    <Tab key={index} label={floor} />
                  ))}
                </Tabs>

                <MDBox mt={3}>
                  {loading ? (
                    <Box textAlign="center" py={5}>
                      <CircularProgress />
                      <Typography variant="body1" sx={{ mt: 2 }}>
                        Đang tải danh sách bàn...
                      </Typography>
                    </Box>
                  ) : tables.length === 0 ? (
                    <Box textAlign="center" py={5}>
                      <Typography variant="h5" color="text.secondary" gutterBottom>
                        Không có bàn nào trong hệ thống.
                      </Typography>
                      <Box mt={1} mb={3}>
                        <Typography variant="body2" color="error">
                          {error && `Lỗi: ${error}`}
                        </Typography>
                      </Box>
                      <MDButton
                        variant="gradient"
                        color="info"
                        onClick={handleOpenAddTableDialog}
                        sx={{ mt: 2 }}
                      >
                        <Icon>add</Icon>&nbsp; Thêm bàn mới
                      </MDButton>
                    </Box>
                  ) : (
                    <Grid container spacing={3} sx={{ mt: 1, mb: 6 }}>
                      {console.log("🔍 RENDER DEBUG:")}
                      {console.log("- activeFloor:", activeFloor, typeof activeFloor)}
                      {console.log("- tables count:", tables.length)}

                      {tables
                        .filter((table) => {
                          // Backend: floor 0 = "Tầng 1", floor 1 = "Tầng 2", floor 2 = "Tầng 3"
                          // UI: activeFloor 0 = tab "Tầng 1", activeFloor 1 = tab "Tầng 2", etc.
                          const tableFloor = Number(table.floor);
                          const currentFloor = Number(activeFloor);
                          const match = tableFloor === currentFloor;

                          console.log(
                            `📍 Bàn ${table.id} (${table.name}): floor=${tableFloor}, activeFloor=${currentFloor}, match=${match}`
                          );
                          return match;
                        })
                        .map((table) => {
                          console.log(`Rendering table: ${table.name}`);
                          return (
                            <Grid item xs={12} sm={6} md={4} lg={3} key={table.id}>
                              <TableCard
                                table={table}
                                onTableClick={handleTableClick}
                                onDeleteTable={handleDeleteTable}
                                onToggleReservation={handleToggleReservation}
                                getStatusColor={getStatusColor}
                                getStatusText={getStatusText}
                              />
                            </Grid>
                          );
                        })}

                      {/* Hiển thị số lượng bàn được filter */}
                      <Grid item xs={12}>
                        <MDBox textAlign="center" mt={2}>
                          <Typography variant="caption" color="text">
                            Hiển thị{" "}
                            {tables.filter((t) => Number(t.floor) === Number(activeFloor)).length} /{" "}
                            {tables.length} bàn
                          </Typography>
                        </MDBox>
                      </Grid>
                    </Grid>
                  )}
                </MDBox>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      {/* Dialog chi tiết bàn */}
      <OrderDetailsDialog
        open={openOrderDialog}
        onClose={handleCloseOrderDialog}
        table={selectedTable}
        tableOrders={tableOrders}
        onAddOrder={openAddOrderDialogHandler}
        onCreateBill={handleCreateBill}
        calculateTotal={calculateTotal}
      />

      {/* Dialog gọi thêm món */}
      <AddOrderDialog
        open={openAddOrderDialog}
        onClose={() => setOpenAddOrderDialog(false)}
        tableName={selectedTable?.name}
        tableId={selectedTable?.id}
        tableStatus={selectedTable?.status} // Thêm prop mới
        categories={menuHook.categories}
        selectedCategory={menuHook.selectedCategory}
        setSelectedCategory={menuHook.setSelectedCategory}
        searchTerm={menuHook.searchTerm}
        setSearchTerm={menuHook.setSearchTerm}
        filteredMenuItems={menuHook.filteredMenuItems}
        selectedItems={menuHook.selectedItems}
        addItemToSelection={menuHook.addItemToSelection}
        removeItemFromSelection={menuHook.removeItemFromSelection}
        changeItemQuantity={menuHook.changeItemQuantity}
        onAddItems={handleAddItemsToTable}
      />

      {/* Dialog thêm bàn mới */}
      <AddTableDialog
        open={openAddTableDialog}
        onClose={() => setOpenAddTableDialog(false)}
        tableData={newTableData}
        setTableData={setNewTableData}
        onAddTable={handleAddTable}
        error={error}
      />

      <Footer />
    </DashboardLayout>
  );
}

export default TableManagement;
