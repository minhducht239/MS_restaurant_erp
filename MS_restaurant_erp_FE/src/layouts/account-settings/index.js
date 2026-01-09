import React, { useState, useEffect, useRef } from "react";
import { Grid, Card, Tabs, Tab, Box, Avatar, Button, CircularProgress, Alert } from "@mui/material";
import { PhotoCamera } from "@mui/icons-material";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Services
import {
  getCurrentUser,
  updateUserProfile,
  changeUserPassword,
  uploadAvatar,
  getAvatarUrl,
} from "services/AccountService";

// Auth Context
import { useAuth } from "context/AuthContext";

function AccountSettings() {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);

  const [profileData, setProfileData] = useState({
    name: "",
    email: "",
    phone: "",
    role: "staff",
    avatar: "",
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const fileInputRef = useRef(null);

  useEffect(() => {
    const fetchUserData = async () => {
      if (isLoading) return; // Prevent multiple calls

      try {
        setIsLoading(true);
        setError(null);

        console.log("Fetching user data...");

        let userData = user;
        if (!user || !user.email) {
          userData = await getCurrentUser();
          updateUser(userData);
        }

        console.log("User data received:", userData);

        const fullName =
          userData.full_name ||
          `${userData.first_name || ""} ${userData.last_name || ""}`.trim() ||
          userData.username ||
          "";

        const avatarUrl =
          userData.avatar_url_absolute || userData.avatar_url || userData.avatar || "";

        setProfileData({
          name: fullName,
          email: userData.email || "",
          phone: userData.phone_number || "",
          role: userData.role || "staff",
          avatar: avatarUrl,
        });
      } catch (error) {
        console.error("Error fetching user data:", error);
        setError(`Không thể tải thông tin người dùng: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    if (!profileData.email && user?.email) {
      fetchUserData();
    }
  }, [user?.email]);
  const validateProfile = () => {
    const errors = {};

    if (!profileData.name.trim()) {
      errors.name = "Tên không được để trống";
    }

    if (!profileData.email.trim()) {
      errors.email = "Email không được để trống";
    } else if (!/\S+@\S+\.\S+/.test(profileData.email)) {
      errors.email = "Email không hợp lệ";
    }

    if (profileData.phone && !/^\d{10,11}$/.test(profileData.phone.replace(/\s/g, ""))) {
      errors.phone = "Số điện thoại không hợp lệ";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validatePassword = () => {
    const errors = {};

    if (!passwordData.currentPassword) {
      errors.currentPassword = "Vui lòng nhập mật khẩu hiện tại";
    }

    if (!passwordData.newPassword) {
      errors.newPassword = "Vui lòng nhập mật khẩu mới";
    } else if (passwordData.newPassword.length < 6) {
      errors.newPassword = "Mật khẩu mới phải có ít nhất 6 ký tự";
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      errors.confirmPassword = "Xác nhận mật khẩu không khớp";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log("Selected file:", file);

    // Validate file
    if (!file.type.startsWith("image/")) {
      setError("Vui lòng chọn file hình ảnh");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("File quá lớn. Vui lòng chọn file dưới 5MB");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => setAvatarPreview(e.target.result);
      reader.readAsDataURL(file);

      console.log("Uploading avatar...");

      const response = await uploadAvatar(file);

      console.log("Avatar upload response:", response);

      const newAvatarUrl =
        response.user?.avatar_url_absolute ||
        response.user?.avatar_url ||
        response.user?.avatar ||
        response.avatar_url ||
        response.avatar;

      setProfileData((prev) => ({
        ...prev,
        avatar: newAvatarUrl,
      }));

      updateUser({
        ...user,
        avatar: newAvatarUrl,
        avatar_url: newAvatarUrl,
        avatar_url_absolute: newAvatarUrl,
      });

      setSuccess("Cập nhật ảnh đại diện thành công!");
      setAvatarFile(file);
    } catch (error) {
      console.error("Avatar upload error:", error);
      setError(`Lỗi upload ảnh: ${error.message}`);
      setAvatarPreview(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getImageSrc = (imagePath) => {
    if (avatarPreview) return avatarPreview;
    if (!imagePath) return null;
    return getAvatarUrl(imagePath);
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setError(null);
    setSuccess(null);
    setValidationErrors({});
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({
        ...prev,
        [name]: null,
      }));
    }
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => ({
        ...prev,
        [name]: null,
      }));
    }
  };

  const updateProfile = async () => {
    if (!validateProfile()) return;

    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      console.log("Updating profile with data:", profileData);
      const response = await updateUserProfile(profileData);

      console.log("Profile update response:", response);

      updateUser(response);

      setSuccess("Cập nhật thông tin thành công!");
    } catch (error) {
      console.error("Profile update error:", error);
      setError(`Lỗi cập nhật thông tin: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const changePassword = async () => {
    if (!validatePassword()) return;

    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      await changeUserPassword(passwordData);

      setSuccess("Đổi mật khẩu thành công!");
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (error) {
      console.error("Password change error:", error);
      setError(`Lỗi đổi mật khẩu: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !profileData.email && !user?.email) {
    return (
      <DashboardLayout>
        <DashboardNavbar />
        <MDBox py={3} display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress color="info" />
        </MDBox>
        <Footer />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} lg={8}>
            <Card>
              <MDBox p={3}>
                <MDTypography variant="h4" fontWeight="medium" mb={3}>
                  Cài đặt tài khoản
                </MDTypography>

                {error && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                  </Alert>
                )}

                {success && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {success}
                  </Alert>
                )}

                <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
                  <Tab label="Thông tin cá nhân" />
                  <Tab label="Đổi mật khẩu" />
                </Tabs>

                {/* Profile Tab */}
                {activeTab === 0 && (
                  <MDBox>
                    {/* Avatar Section */}
                    <MDBox display="flex" alignItems="center" mb={3}>
                      <Avatar
                        src={getImageSrc(profileData.avatar)}
                        sx={{ width: 100, height: 100, mr: 3 }}
                      />
                      <MDBox>
                        <MDTypography variant="h6" mb={1}>
                          Ảnh đại diện
                        </MDTypography>
                        <Button
                          variant="outlined"
                          startIcon={<PhotoCamera />}
                          onClick={triggerFileInput}
                          disabled={isLoading}
                        >
                          {isLoading ? "Đang tải..." : "Thay đổi ảnh"}
                        </Button>
                        <input
                          type="file"
                          ref={fileInputRef}
                          style={{ display: "none" }}
                          accept="image/*"
                          onChange={handleAvatarUpload}
                        />
                      </MDBox>
                    </MDBox>

                    {/* Profile Form */}
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <MDInput
                          fullWidth
                          label="Họ và tên"
                          name="name"
                          value={profileData.name}
                          onChange={handleProfileChange}
                          error={!!validationErrors.name}
                          helperText={validationErrors.name}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <MDInput
                          fullWidth
                          label="Email"
                          name="email"
                          type="email"
                          value={profileData.email}
                          onChange={handleProfileChange}
                          error={!!validationErrors.email}
                          helperText={validationErrors.email}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <MDInput
                          fullWidth
                          label="Số điện thoại"
                          name="phone"
                          value={profileData.phone}
                          onChange={handleProfileChange}
                          error={!!validationErrors.phone}
                          helperText={validationErrors.phone}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <MDInput fullWidth label="Vai trò" value={profileData.role} disabled />
                      </Grid>
                    </Grid>

                    <MDBox mt={3}>
                      <MDButton
                        variant="gradient"
                        color="info"
                        onClick={updateProfile}
                        disabled={isLoading}
                      >
                        {isLoading ? "Đang cập nhật..." : "Cập nhật thông tin"}
                      </MDButton>
                    </MDBox>
                  </MDBox>
                )}

                {/* Password Tab */}
                {activeTab === 1 && (
                  <MDBox>
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <MDInput
                          fullWidth
                          label="Mật khẩu hiện tại"
                          name="currentPassword"
                          type="password"
                          value={passwordData.currentPassword}
                          onChange={handlePasswordChange}
                          error={!!validationErrors.currentPassword}
                          helperText={validationErrors.currentPassword}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <MDInput
                          fullWidth
                          label="Mật khẩu mới"
                          name="newPassword"
                          type="password"
                          value={passwordData.newPassword}
                          onChange={handlePasswordChange}
                          error={!!validationErrors.newPassword}
                          helperText={validationErrors.newPassword}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <MDInput
                          fullWidth
                          label="Xác nhận mật khẩu mới"
                          name="confirmPassword"
                          type="password"
                          value={passwordData.confirmPassword}
                          onChange={handlePasswordChange}
                          error={!!validationErrors.confirmPassword}
                          helperText={validationErrors.confirmPassword}
                        />
                      </Grid>
                    </Grid>

                    <MDBox mt={3}>
                      <MDButton
                        variant="gradient"
                        color="info"
                        onClick={changePassword}
                        disabled={isLoading}
                      >
                        {isLoading ? "Đang đổi..." : "Đổi mật khẩu"}
                      </MDButton>
                    </MDBox>
                  </MDBox>
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default AccountSettings;
