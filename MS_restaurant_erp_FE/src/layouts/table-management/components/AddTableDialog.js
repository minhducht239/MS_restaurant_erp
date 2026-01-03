import React from "react";
import PropTypes from "prop-types";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
} from "@mui/material";
import MDButton from "components/MDButton";

function AddTableDialog({ open, onClose, tableData, setTableData, onAddTable, error }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setTableData({
      ...tableData,
      [name]: name === "capacity" || name === "name" ? parseInt(value) || 0 : value,
    });
  };

  // Xác định tên tầng từ floor number
  const getFloorName = (floorNumber) => {
    const floors = ["Tầng 1", "Tầng 2", "Tầng 3"];
    return floors[floorNumber] || `Tầng ${floorNumber + 1}`;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Thêm bàn mới - {getFloorName(tableData.floor)}</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ p: 1 }}>
          <TextField
            fullWidth
            label="Số bàn"
            name="name"
            type="number"
            value={tableData.name}
            onChange={handleChange}
            margin="normal"
            required
            error={!tableData.name && error}
            helperText={
              !tableData.name && error
                ? "Vui lòng nhập số bàn"
                : "Số bàn được đề xuất tự động, bạn có thể thay đổi"
            }
            size="medium"
            sx={{ mb: 2 }}
            InputProps={{
              inputProps: { min: 1 },
            }}
          />

          <TextField
            fullWidth
            label="Sức chứa"
            type="number"
            name="capacity"
            value={tableData.capacity}
            onChange={handleChange}
            margin="normal"
            InputProps={{ inputProps: { min: 1 } }}
            size="medium"
            sx={{ mb: 2 }}
          />

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Bàn sẽ được thêm vào {getFloorName(tableData.floor)}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Trạng thái mặc định: Trống
            </Typography>
          </Box>

          {/* Đã loại bỏ dropdown chọn trạng thái */}
        </Box>
      </DialogContent>
      <DialogActions>
        <MDButton onClick={onClose} color="dark">
          Hủy
        </MDButton>
        <MDButton onClick={onAddTable} color="success" disabled={!tableData.name}>
          Thêm bàn
        </MDButton>
      </DialogActions>
    </Dialog>
  );
}

AddTableDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  tableData: PropTypes.object.isRequired,
  setTableData: PropTypes.func.isRequired,
  onAddTable: PropTypes.func.isRequired,
  error: PropTypes.string,
};

export default AddTableDialog;
