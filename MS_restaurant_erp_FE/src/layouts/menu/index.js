import { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import TextField from "@mui/material/TextField";
import InputAdornment from "@mui/material/InputAdornment";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Switch from "@mui/material/Switch";
import FormControlLabel from "@mui/material/FormControlLabel";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Custom components
import MenuList from "./components/Menulist";
import MenuDialog from "./components/MenuDialog";
import MenuItemDetail from "./components/MenuItemDetail";

// Service
import { getMenuItems, createMenuItem, updateMenuItem, deleteMenuItem } from "services/MenuService";

function Menu() {
  const [menuItems, setMenuItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState(null);
  const [formData, setFormData] = useState({});

  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [availabilityFilter, setAvailabilityFilter] = useState("all");

  useEffect(() => {
    fetchMenuItems();
  }, []);

  const fetchMenuItems = async () => {
    try {
      setIsLoading(true);
      setError(null);

      console.log("Fetching menu items...");
      const data = await getMenuItems();

      // Debug logs
      console.log("Raw API response:", data);
      console.log("Type of data:", typeof data);
      console.log("Is array?", Array.isArray(data));
      console.log("Has results?", data?.results);

      const items = data?.results || data || [];
      console.log("Final items:", items);
      console.log("Items is array?", Array.isArray(items));

      setMenuItems(Array.isArray(items) ? items : []);
    } catch (error) {
      console.error("Error fetching menu items:", error);
      setError("Không thể tải danh sách thực đơn. Vui lòng thử lại sau.");
      setMenuItems([]); // Set empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  const filteredMenuItems = (menuItems || []).filter((item) => {
    // Safety check for item object
    if (!item || typeof item !== "object") {
      console.warn("Invalid menu item:", item);
      return false;
    }

    const matchesSearch =
      (item.name && item.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.description && item.description.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesCategory = categoryFilter === "all" || item.category === categoryFilter;

    const matchesAvailability =
      availabilityFilter === "all" ||
      (availabilityFilter === "available" && item.is_available) ||
      (availabilityFilter === "unavailable" && !item.is_available);

    return matchesSearch && matchesCategory && matchesAvailability;
  });

  const handleAddClick = () => {
    setFormData({
      name: "",
      description: "",
      price: "",
      category: "food",
      is_available: true,
    });
    setIsDialogOpen(true);
  };

  const handleEditClick = (item) => {
    setFormData({
      id: item.id,
      name: item.name,
      description: item.description || "",
      price: item.price,
      category: item.category,
      is_available: item.is_available,
      image: item.image,
    });
    setIsDialogOpen(true);
  };

  const handleDeleteClick = async (id) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa món này không?")) {
      try {
        await deleteMenuItem(id);
        setMenuItems((prevItems) => prevItems.filter((item) => item.id !== id));
        console.log(`Successfully deleted menu item with ID: ${id}`);
      } catch (error) {
        console.error("Error deleting menu item:", error);
        alert("Không thể xóa món. Vui lòng thử lại sau.");
      }
    }
  };

  const handleSave = async () => {
    try {
      // Validation
      if (!formData.name?.trim()) {
        alert("Vui lòng nhập tên món!");
        return;
      }

      if (!formData.price || parseFloat(formData.price) <= 0) {
        alert("Vui lòng nhập giá hợp lệ!");
        return;
      }

      console.log("=== SAVE PROCESS START ===");
      console.log("Original formData:", formData);
      console.log("Image type:", typeof formData.image);
      console.log("Image instanceof File:", formData.image instanceof File);

      const hasNewImageFile = formData.image && formData.image instanceof File;
      console.log("Has new image file:", hasNewImageFile);

      let savedItem;

      if (hasNewImageFile) {
        console.log("Creating FormData for file upload...");

        const formDataToSend = new FormData();

        formDataToSend.append("name", formData.name.trim());
        formDataToSend.append("description", formData.description || "");
        formDataToSend.append("price", parseFloat(formData.price).toString());
        formDataToSend.append("category", formData.category);
        formDataToSend.append("is_available", formData.is_available ? "true" : "false");

        formDataToSend.append("image", formData.image, formData.image.name);

        console.log("FormData contents:");
        for (let [key, value] of formDataToSend.entries()) {
          if (value instanceof File) {
            console.log(`${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
          } else {
            console.log(`${key}: ${value}`);
          }
        }

        if (formData.id) {
          console.log(`Updating item ${formData.id} with FormData...`);
          savedItem = await updateMenuItem(formData.id, formDataToSend);
        } else {
          console.log("Creating new item with FormData...");
          savedItem = await createMenuItem(formDataToSend);
        }
      } else {
        console.log("Using JSON data (no new image)...");

        const dataToSend = {
          name: formData.name.trim(),
          description: formData.description || "",
          price: parseFloat(formData.price),
          category: formData.category,
          is_available: Boolean(formData.is_available),
        };

        console.log("Sending JSON data:", dataToSend);

        if (formData.id) {
          savedItem = await updateMenuItem(formData.id, dataToSend);
        } else {
          savedItem = await createMenuItem(dataToSend);
        }
      }

      console.log("API response:", savedItem);

      if (formData.id) {
        setMenuItems((prevItems) =>
          prevItems.map((item) => (item.id === formData.id ? savedItem : item))
        );
      } else {
        setMenuItems((prevItems) => [...prevItems, savedItem]);
      }

      setIsDialogOpen(false);
      setFormData({});

      console.log("=== SAVE PROCESS SUCCESS ===");
      alert(formData.id ? "Cập nhật món thành công!" : "Thêm món mới thành công!");
    } catch (error) {
      console.error("=== SAVE PROCESS ERROR ===");
      console.error("Error saving menu item:", error);
      console.error("Error response:", error.response);

      // Enhanced error handling
      let errorMessage = "Không thể lưu món.";

      if (error.response?.data) {
        const errorData = error.response.data;
        console.error("Error response data:", errorData);

        if (typeof errorData === "object") {
          if (errorData.details) {
            const errorMessages = [];
            Object.keys(errorData.details).forEach((field) => {
              const fieldErrors = errorData.details[field];
              if (Array.isArray(fieldErrors)) {
                errorMessages.push(`${field}: ${fieldErrors.join(", ")}`);
              } else {
                errorMessages.push(`${field}: ${fieldErrors}`);
              }
            });
            errorMessage =
              errorMessages.length > 0
                ? `Lỗi validation: ${errorMessages.join("; ")}`
                : `Lỗi: ${errorData.error || JSON.stringify(errorData)}`;
          } else {
            const errorMessages = [];
            Object.keys(errorData).forEach((field) => {
              if (Array.isArray(errorData[field])) {
                errorMessages.push(`${field}: ${errorData[field].join(", ")}`);
              } else {
                errorMessages.push(`${field}: ${errorData[field]}`);
              }
            });
            errorMessage =
              errorMessages.length > 0
                ? `Lỗi: ${errorMessages.join("; ")}`
                : `Lỗi: ${JSON.stringify(errorData)}`;
          }
        } else {
          errorMessage = `Lỗi: ${errorData}`;
        }
      } else if (error.message) {
        errorMessage = `Lỗi: ${error.message}`;
      } else {
        errorMessage = "Lỗi không xác định. Vui lòng thử lại.";
      }

      alert(errorMessage);
    }
  };

  const handleDetailClick = (itemId) => {
    setSelectedItemId(itemId);
    setIsDetailOpen(true);
  };

  const handleClearSearch = () => {
    setSearchTerm("");
    setCategoryFilter("all");
    setAvailabilityFilter("all");
  };

  const handleQuickToggleAvailability = async (item) => {
    try {
      console.log(`Toggling availability for item: ${item.name} (ID: ${item.id})`);
      console.log(`Current status: ${item.is_available} -> ${!item.is_available}`);

      // Only send necessary fields to avoid image URL being sent as file
      const updatedData = {
        name: item.name,
        description: item.description || "",
        price: item.price,
        category: item.category,
        is_available: !item.is_available,
      };

      console.log("Sending updated data:", updatedData);

      const savedItem = await updateMenuItem(item.id, updatedData);

      console.log("API response:", savedItem);

      // Update state
      setMenuItems((prevItems) =>
        prevItems.map((menuItem) => (menuItem.id === item.id ? savedItem : menuItem))
      );

      const statusText = savedItem.is_available ? "còn món" : "hết món";
      console.log(` Successfully changed ${item.name} to ${statusText}`);
    } catch (error) {
      console.error("Error toggling availability:", error);

      // Enhanced error handling for toggle
      let errorMessage = "Không thể thay đổi trạng thái món.";

      if (error.response?.data) {
        const errorData = error.response.data;
        console.error("Error response data:", errorData);

        if (typeof errorData === "object") {
          const errorMessages = [];
          Object.keys(errorData).forEach((field) => {
            if (Array.isArray(errorData[field])) {
              errorMessages.push(`${field}: ${errorData[field].join(", ")}`);
            } else {
              errorMessages.push(`${field}: ${errorData[field]}`);
            }
          });
          errorMessage =
            errorMessages.length > 0
              ? `Lỗi: ${errorMessages.join("; ")}`
              : `Lỗi: ${JSON.stringify(errorData)}`;
        } else {
          errorMessage = `Lỗi: ${errorData}`;
        }
      } else if (error.message) {
        errorMessage = `Lỗi: ${error.message}`;
      }

      alert(errorMessage);
    }
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              {/* Header Section */}
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDBox display="flex" justifyContent="space-between" alignItems="center">
                  <MDTypography variant="h6" color="white">
                    Quản lý thực đơn
                  </MDTypography>
                  <MDButton variant="contained" color="white" onClick={handleAddClick}>
                    <Icon sx={{ mr: 1 }}>add</Icon>
                    Thêm món mới
                  </MDButton>
                </MDBox>
              </MDBox>

              {/* Content Section */}
              <MDBox p={3}>
                {/* Enhanced Search and Filter Section */}
                <Grid container spacing={3} mb={3}>
                  {/* Search Box */}
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Tìm kiếm món ăn"
                      variant="outlined"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Icon>search</Icon>
                          </InputAdornment>
                        ),
                      }}
                      sx={{ height: "56px" }}
                    />
                  </Grid>

                  {/* Category Filter */}
                  <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                      <InputLabel>Danh mục</InputLabel>
                      <Select
                        value={categoryFilter}
                        label="Danh mục"
                        onChange={(e) => setCategoryFilter(e.target.value)}
                        sx={{ height: "56px" }}
                      >
                        <MenuItem value="all">
                          <MDBox display="flex" alignItems="center" gap={1}>
                            <Icon>restaurant_menu</Icon>
                            Tất cả
                          </MDBox>
                        </MenuItem>
                        <MenuItem value="food">
                          <MDBox display="flex" alignItems="center" gap={1}>
                            <Icon sx={{ color: "warning.main" }}>restaurant</Icon>
                            Món ăn
                          </MDBox>
                        </MenuItem>
                        <MenuItem value="drink">
                          <MDBox display="flex" alignItems="center" gap={1}>
                            <Icon sx={{ color: "success.main" }}>local_drink</Icon>
                            Đồ uống
                          </MDBox>
                        </MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  {/* Availability Filter */}
                  <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                      <InputLabel>Trạng thái</InputLabel>
                      <Select
                        value={availabilityFilter}
                        label="Trạng thái"
                        onChange={(e) => setAvailabilityFilter(e.target.value)}
                        sx={{ height: "56px" }}
                      >
                        <MenuItem value="all">
                          <MDBox display="flex" alignItems="center" gap={1}>
                            <Icon>list</Icon>
                            Tất cả
                          </MDBox>
                        </MenuItem>
                        <MenuItem value="available">
                          <MDBox display="flex" alignItems="center" gap={1}>
                            <Icon sx={{ color: "success.main" }}>check_circle</Icon>
                            Còn món
                          </MDBox>
                        </MenuItem>
                        <MenuItem value="unavailable">
                          <MDBox display="flex" alignItems="center" gap={1}>
                            <Icon sx={{ color: "error.main" }}>cancel</Icon>
                            Hết món
                          </MDBox>
                        </MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  {/* Clear Filters Button */}
                  <Grid item xs={12} md={2}>
                    <MDButton
                      variant="outlined"
                      color="secondary"
                      fullWidth
                      onClick={handleClearSearch}
                      sx={{ height: "56px" }}
                    >
                      <Icon sx={{ mr: 1 }}>refresh</Icon>
                      Xóa bộ lọc
                    </MDButton>
                  </Grid>
                </Grid>

                {/* Filter Results Summary */}
                <MDBox mb={2}>
                  <MDTypography variant="body2" color="text">
                    Hiển thị {filteredMenuItems?.length || 0} / {menuItems?.length || 0} món
                    {searchTerm && <span> • Tìm kiếm: &quot;{searchTerm}&quot;</span>}
                    {categoryFilter !== "all" && (
                      <span> • Danh mục: {categoryFilter === "food" ? "Món ăn" : "Đồ uống"}</span>
                    )}
                    {availabilityFilter !== "all" && (
                      <span>
                        {" "}
                        • Trạng thái: {availabilityFilter === "available" ? "Còn món" : "Hết món"}
                      </span>
                    )}
                  </MDTypography>
                </MDBox>

                {/* Enhanced Menu List with better error handling */}
                {isLoading ? (
                  <MDBox
                    display="flex"
                    justifyContent="center"
                    alignItems="center"
                    minHeight="400px"
                  >
                    <MDTypography variant="h6" color="text">
                      Đang tải...
                    </MDTypography>
                  </MDBox>
                ) : error ? (
                  <MDBox
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    minHeight="400px"
                    justifyContent="center"
                  >
                    <Icon sx={{ fontSize: "4rem", color: "error.main", mb: 2 }}>error</Icon>
                    <MDTypography variant="h6" color="error" mb={2}>
                      {error}
                    </MDTypography>
                    <MDButton variant="outlined" color="error" onClick={fetchMenuItems}>
                      <Icon sx={{ mr: 1 }}>refresh</Icon>
                      Thử lại
                    </MDButton>
                  </MDBox>
                ) : !Array.isArray(filteredMenuItems) || filteredMenuItems.length === 0 ? (
                  <MDBox
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    minHeight="400px"
                    justifyContent="center"
                  >
                    {!Array.isArray(menuItems) || menuItems.length === 0 ? (
                      <MDBox textAlign="center">
                        <Icon sx={{ fontSize: "4rem", color: "grey.400", mb: 2 }}>
                          restaurant_menu
                        </Icon>
                        <MDTypography variant="h6" color="text" mb={1}>
                          Chưa có món ăn nào trong thực đơn
                        </MDTypography>
                        <MDTypography variant="body2" color="text" mb={2}>
                          Hãy thêm món ăn đầu tiên để bắt đầu
                        </MDTypography>
                        <MDButton variant="gradient" color="info" onClick={handleAddClick}>
                          <Icon sx={{ mr: 1 }}>add</Icon>
                          Thêm món mới
                        </MDButton>
                      </MDBox>
                    ) : (
                      <MDBox textAlign="center">
                        <Icon sx={{ fontSize: "4rem", color: "grey.400", mb: 2 }}>search_off</Icon>
                        <MDTypography variant="h6" color="text" mb={1}>
                          Không tìm thấy món ăn nào
                        </MDTypography>
                        <MDTypography variant="body2" color="text" mb={2}>
                          Thử thay đổi từ khóa tìm kiếm hoặc bộ lọc
                        </MDTypography>
                        <MDButton
                          variant="outlined"
                          color="info"
                          onClick={handleClearSearch}
                          size="small"
                        >
                          <Icon sx={{ mr: 0.5 }}>refresh</Icon>
                          Xóa bộ lọc
                        </MDButton>
                      </MDBox>
                    )}
                  </MDBox>
                ) : (
                  <MenuList
                    menuItems={filteredMenuItems}
                    onEdit={handleEditClick}
                    onDelete={handleDeleteClick}
                    onDetail={handleDetailClick}
                    onQuickToggleAvailability={handleQuickToggleAvailability}
                  />
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />

      {/* Dialog Components */}
      <MenuDialog
        open={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onSave={handleSave}
        formData={formData}
        setFormData={setFormData}
      />

      <MenuItemDetail
        open={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        itemId={selectedItemId}
        menuItems={menuItems}
      />
    </DashboardLayout>
  );
}

export default Menu;
