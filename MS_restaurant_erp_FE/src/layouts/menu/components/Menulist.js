import React from "react";
import PropTypes from "prop-types";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import MDBox from "components/MDBox";
import MDButton from "components/MDButton";
import { Icon } from "@mui/material";

function MenuList({ menuItems = [], onEdit, onDelete, onDetail, onQuickToggleAvailability }) {
  if (!Array.isArray(menuItems)) {
    console.warn("MenuList: menuItems is not an array:", menuItems);
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography variant="body2" color="text.secondary">
          Dữ liệu không hợp lệ
        </Typography>
      </MDBox>
    );
  }

  if (menuItems.length === 0) {
    return (
      <MDBox display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography variant="body2" color="text.secondary">
          Không có món ăn nào
        </Typography>
      </MDBox>
    );
  }

  const formatPrice = (price) => {
    if (typeof price === "number") {
      return `${price.toLocaleString("vi-VN")} VNĐ`;
    }
    if (typeof price === "string") {
      if (price.includes("VNĐ") || price.includes("VND")) {
        const numericValue = parseFloat(price.replace(/[^\d]/g, ""));
        if (!isNaN(numericValue)) {
          return `${numericValue.toLocaleString("vi-VN")} VNĐ`;
        }
        return price;
      }
      const numericValue = parseFloat(price);
      if (!isNaN(numericValue)) {
        return `${numericValue.toLocaleString("vi-VN")} VNĐ`;
      }
    }
    return price || "0 VNĐ";
  };

  const getImageSrc = (item) => {
    // Use image_url from serializer (already has absolute URL)
    if (item.image_url) {
      return item.image_url;
    }
    // Fallback to default placeholder based on category
    return item.category === "drink" ? "/images/default-drink.jpg" : "/images/default-food.jpg";
  };

  return (
    <Grid container spacing={3}>
      {menuItems.map((item) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
          <Card
            sx={{
              height: "100%",
              display: "flex",
              flexDirection: "column",
              position: "relative",
              transition: "transform 0.2s",
              "&:hover": {
                transform: "translateY(-2px)",
                boxShadow: 3,
              },
            }}
          >
            <Chip
              label={item.is_available ? "Còn món" : "Hết món"}
              color={item.is_available ? "success" : "error"}
              size="small"
              sx={{
                position: "absolute",
                top: 8,
                right: 8,
                zIndex: 1,
                fontWeight: "bold",
              }}
            />

            <CardMedia
              component="img"
              height="180"
              image={getImageSrc(item)}
              alt={item.name}
              onError={(e) => {
                e.target.src =
                  item.category === "drink"
                    ? "/images/default-drink.jpg"
                    : "/images/default-food.jpg";
              }}
              sx={{
                objectFit: "cover",
                opacity: item.is_available ? 1 : 0.6,
              }}
            />

            <CardContent sx={{ flexGrow: 1, pb: 1 }}>
              <MDBox display="flex" alignItems="center" gap={1} mb={1}>
                <Icon
                  sx={{
                    color: item.category === "drink" ? "success.main" : "warning.main",
                    fontSize: "1.2rem",
                  }}
                >
                  {item.category === "drink" ? "local_drink" : "restaurant"}
                </Icon>
                <Typography
                  variant="h6"
                  fontWeight="medium"
                  sx={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    flex: 1,
                  }}
                >
                  {item.name}
                </Typography>
              </MDBox>

              <Typography variant="h6" color="primary" fontWeight="bold" mb={1}>
                {formatPrice(item.price)}
              </Typography>

              {item.description && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  mb={2}
                  sx={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    minHeight: "2.4em",
                  }}
                >
                  {item.description}
                </Typography>
              )}

              <MDBox mb={2}>
                <Chip
                  label={item.category === "food" ? "Món ăn" : "Đồ uống"}
                  color={item.category === "food" ? "warning" : "success"}
                  size="small"
                  variant="outlined"
                />
              </MDBox>
            </CardContent>

            <MDBox p={2} pt={0}>
              <Grid container spacing={1}>
                {/* Edit Button */}
                <Grid item xs={3}>
                  <Tooltip title="Chỉnh sửa">
                    <MDButton
                      variant="text"
                      color="info"
                      onClick={() => onEdit(item)}
                      size="small"
                      sx={{ minWidth: "auto", p: 1 }}
                    >
                      <Icon>edit</Icon>
                    </MDButton>
                  </Tooltip>
                </Grid>

                {/* Delete Button */}
                <Grid item xs={3}>
                  <Tooltip title="Xóa món">
                    <MDButton
                      variant="text"
                      color="error"
                      onClick={() => onDelete(item.id)}
                      size="small"
                      sx={{ minWidth: "auto", p: 1 }}
                    >
                      <Icon>delete</Icon>
                    </MDButton>
                  </Tooltip>
                </Grid>

                {/* Detail Button */}
                <Grid item xs={3}>
                  <Tooltip title="Xem chi tiết">
                    <MDButton
                      variant="text"
                      color="dark"
                      onClick={() => onDetail(item.id)}
                      size="small"
                      sx={{ minWidth: "auto", p: 1 }}
                    >
                      <Icon>info</Icon>
                    </MDButton>
                  </Tooltip>
                </Grid>

                <Grid item xs={3}>
                  {onQuickToggleAvailability && (
                    <Tooltip title={item.is_available ? "Đánh dấu hết món" : "Đánh dấu còn món"}>
                      <MDButton
                        variant="text"
                        color={item.is_available ? "success" : "error"}
                        onClick={() => onQuickToggleAvailability(item)}
                        size="small"
                        sx={{ minWidth: "auto", p: 1 }}
                      >
                        <Icon>{item.is_available ? "check_circle" : "cancel"}</Icon>
                      </MDButton>
                    </Tooltip>
                  )}
                </Grid>
              </Grid>
            </MDBox>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

MenuList.propTypes = {
  menuItems: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      name: PropTypes.string.isRequired,
      price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      category: PropTypes.oneOf(["food", "drink"]).isRequired,
      image: PropTypes.string,
      description: PropTypes.string,
      is_available: PropTypes.bool,
    })
  ),
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
  onDetail: PropTypes.func.isRequired,
  onQuickToggleAvailability: PropTypes.func,
};

MenuList.defaultProps = {
  menuItems: [],
  onQuickToggleAvailability: null,
};

export default MenuList;
