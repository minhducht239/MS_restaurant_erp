// react-router-dom components
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
// @mui material components
import Card from "@mui/material/Card";
import Checkbox from "@mui/material/Checkbox";
import Alert from "@mui/material/Alert";
import CircularProgress from "@mui/material/CircularProgress";
import InputAdornment from "@mui/material/InputAdornment";
import IconButton from "@mui/material/IconButton";

// @mui icons
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Authentication layout components
import CoverLayout from "layouts/authentication/components/CoverLayout";

// Images
import bgImage from "assets/images/Background-sign-up.jpg";

function Cover() {
  const [formData, setFormData] = useState({
    name: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeTerms: false,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, checked } = e.target;

    if (name === "agreeTerms") {
      setFormData({
        ...formData,
        [name]: checked,
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });

      // Clear validation error for this field
      if (validationErrors[name]) {
        setValidationErrors({
          ...validationErrors,
          [name]: "",
        });
      }
    }

    // Clear general error
    if (error) {
      setError("");
    }
  };

  const validateForm = () => {
    const errors = {};

    // Validate name
    if (!formData.name.trim()) {
      errors.name = "Tên không được để trống";
    } else if (formData.name.trim().length < 2) {
      errors.name = "Tên phải có ít nhất 2 ký tự";
    }

    // Validate username
    if (!formData.username.trim()) {
      errors.username = "Tên đăng nhập không được để trống";
    } else if (formData.username.trim().length < 3) {
      errors.username = "Tên đăng nhập phải có ít nhất 3 ký tự";
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      errors.username = "Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới";
    }

    // Validate email
    if (!formData.email.trim()) {
      errors.email = "Email không được để trống";
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        errors.email = "Email không hợp lệ";
      }
    }

    // Validate password
    if (!formData.password) {
      errors.password = "Mật khẩu không được để trống";
    } else if (formData.password.length < 8) {
      errors.password = "Mật khẩu phải có ít nhất 8 ký tự";
    } else {
      // Check password complexity
      const hasUpperCase = /[A-Z]/.test(formData.password);
      const hasLowerCase = /[a-z]/.test(formData.password);
      const hasNumbers = /\d/.test(formData.password);

      if (!hasUpperCase) {
        errors.password = "Mật khẩu phải chứa ít nhất 1 chữ hoa";
      } else if (!hasLowerCase) {
        errors.password = "Mật khẩu phải chứa ít nhất 1 chữ thường";
      } else if (!hasNumbers) {
        errors.password = "Mật khẩu phải chứa ít nhất 1 số";
      }
    }

    // Validate confirm password
    if (!formData.confirmPassword) {
      errors.confirmPassword = "Vui lòng xác nhận mật khẩu";
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = "Mật khẩu xác nhận không khớp";
    }

    // Validate terms agreement
    if (!formData.agreeTerms) {
      errors.agreeTerms = "Bạn phải đồng ý với điều khoản và điều kiện";
    }

    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setValidationErrors({});

    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setLoading(true);

    try {
      // Tách họ và tên
      const nameParts = formData.name.trim().split(/\s+/);
      const firstName = nameParts[0] || "";
      const lastName = nameParts.slice(1).join(" ") || "";

      console.log("Sending registration request:", {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.confirmPassword,
        first_name: firstName,
        last_name: lastName,
      });

      const response = await fetch("http://localhost:8000/api/auth/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password_confirm: formData.confirmPassword,
          first_name: firstName,
          last_name: lastName,
        }),
      });

      console.log("Response status:", response.status);
      const data = await response.json().catch((e) => {
        console.error("Error parsing JSON:", e);
        return {};
      });
      console.log("Response data:", data);

      if (!response.ok) {
        // Handle validation errors from backend
        if (data.errors) {
          setValidationErrors(data.errors);
        } else {
          throw new Error(data.message || data.detail || "Đăng ký thất bại");
        }
        return;
      }

      // Success - redirect to sign in
      navigate("/authentication/sign-in", {
        state: {
          message: "Đăng ký thành công! Vui lòng đăng nhập.",
          email: formData.email,
        },
      });
    } catch (error) {
      console.error("Registration error:", error);
      setError(error.message || "Có lỗi xảy ra trong quá trình đăng ký");
    } finally {
      setLoading(false);
    }
  };

  const toggleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const toggleShowConfirmPassword = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  return (
    <CoverLayout image={bgImage}>
      <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="success"
          mx={2}
          mt={-3}
          p={3}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            Tham gia cùng chúng tôi
          </MDTypography>
          <MDTypography display="block" variant="button" color="white" my={1}>
            Nhập thông tin để tạo tài khoản mới
          </MDTypography>
        </MDBox>
        <MDBox pt={4} pb={3} px={3}>
          <MDBox component="form" role="form" onSubmit={handleSubmit}>
            {/* General Error */}
            {error && (
              <MDBox mb={2}>
                <Alert severity="error" sx={{ fontSize: "0.875rem" }}>
                  {error}
                </Alert>
              </MDBox>
            )}

            {/* Name Field */}
            <MDBox mb={2}>
              <MDInput
                type="text"
                label="Họ và tên"
                variant="standard"
                fullWidth
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                error={!!validationErrors.name}
                disabled={loading}
              />
              {validationErrors.name && (
                <MDTypography variant="caption" color="error" fontWeight="light" mt={0.5}>
                  {validationErrors.name}
                </MDTypography>
              )}
            </MDBox>

            {/* Username Field */}
            <MDBox mb={2}>
              <MDInput
                type="text"
                label="Tên đăng nhập"
                variant="standard"
                fullWidth
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                error={!!validationErrors.username}
                disabled={loading}
                placeholder="vd: nguyenvana"
              />
              {validationErrors.username && (
                <MDTypography variant="caption" color="error" fontWeight="light" mt={0.5}>
                  {validationErrors.username}
                </MDTypography>
              )}
            </MDBox>

            {/* Email Field */}
            <MDBox mb={2}>
              <MDInput
                type="email"
                label="Email"
                variant="standard"
                fullWidth
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                error={!!validationErrors.email}
                disabled={loading}
              />
              {validationErrors.email && (
                <MDTypography variant="caption" color="error" fontWeight="light" mt={0.5}>
                  {validationErrors.email}
                </MDTypography>
              )}
            </MDBox>

            {/* Password Field */}
            <MDBox mb={2}>
              <MDInput
                type={showPassword ? "text" : "password"}
                label="Mật khẩu"
                variant="standard"
                fullWidth
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                error={!!validationErrors.password}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={toggleShowPassword}
                        edge="end"
                        size="small"
                        disabled={loading}
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              {validationErrors.password && (
                <MDTypography variant="caption" color="error" fontWeight="light" mt={0.5}>
                  {validationErrors.password}
                </MDTypography>
              )}
            </MDBox>

            {/* Confirm Password Field */}
            <MDBox mb={2}>
              <MDInput
                type={showConfirmPassword ? "text" : "password"}
                label="Xác nhận mật khẩu"
                variant="standard"
                fullWidth
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                error={!!validationErrors.confirmPassword}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={toggleShowConfirmPassword}
                        edge="end"
                        size="small"
                        disabled={loading}
                      >
                        {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              {validationErrors.confirmPassword && (
                <MDTypography variant="caption" color="error" fontWeight="light" mt={0.5}>
                  {validationErrors.confirmPassword}
                </MDTypography>
              )}
            </MDBox>

            {/* Password Requirements */}
            <MDBox mb={2}>
              <MDTypography variant="caption" color="text" fontWeight="light">
                Mật khẩu phải có:
              </MDTypography>
              <MDBox component="ul" sx={{ margin: 0, paddingLeft: 2 }}>
                <MDTypography component="li" variant="caption" color="text" fontWeight="light">
                  Ít nhất 8 ký tự
                </MDTypography>
                <MDTypography component="li" variant="caption" color="text" fontWeight="light">
                  Ít nhất 1 chữ hoa (A-Z)
                </MDTypography>
                <MDTypography component="li" variant="caption" color="text" fontWeight="light">
                  Ít nhất 1 chữ thường (a-z)
                </MDTypography>
                <MDTypography component="li" variant="caption" color="text" fontWeight="light">
                  Ít nhất 1 số (0-9)
                </MDTypography>
              </MDBox>
            </MDBox>

            {/* Terms Agreement */}
            <MDBox display="flex" alignItems="flex-start" ml={-1} mb={2}>
              <Checkbox
                checked={formData.agreeTerms}
                name="agreeTerms"
                onChange={handleChange}
                disabled={loading}
                sx={{ padding: "4px 8px" }}
              />
              <MDBox>
                <MDTypography
                  variant="button"
                  fontWeight="regular"
                  color="text"
                  sx={{ cursor: "pointer", userSelect: "none" }}
                  onClick={() =>
                    !loading && setFormData({ ...formData, agreeTerms: !formData.agreeTerms })
                  }
                >
                  Tôi đồng ý với&nbsp;
                  <MDTypography
                    component="a"
                    href="#"
                    variant="button"
                    fontWeight="bold"
                    color="info"
                    textGradient
                  >
                    Điều khoản và Điều kiện
                  </MDTypography>
                </MDTypography>
                {validationErrors.agreeTerms && (
                  <MDTypography variant="caption" color="error" fontWeight="light" display="block">
                    {validationErrors.agreeTerms}
                  </MDTypography>
                )}
              </MDBox>
            </MDBox>

            {/* Submit Button */}
            <MDBox mt={4} mb={1}>
              <MDButton type="submit" variant="gradient" color="info" fullWidth disabled={loading}>
                {loading ? (
                  <MDBox display="flex" alignItems="center" gap={1}>
                    <CircularProgress size={20} color="inherit" />
                    Đang đăng ký...
                  </MDBox>
                ) : (
                  "Đăng ký"
                )}
              </MDButton>
            </MDBox>

            {/* Sign In Link */}
            <MDBox mt={3} mb={1} textAlign="center">
              <MDTypography variant="button" color="text">
                Đã có tài khoản?{" "}
                <MDTypography
                  component={Link}
                  to="/authentication/sign-in"
                  variant="button"
                  color="info"
                  fontWeight="medium"
                  textGradient
                >
                  Đăng nhập
                </MDTypography>
              </MDTypography>
            </MDBox>
          </MDBox>
        </MDBox>
      </Card>
    </CoverLayout>
  );
}

export default Cover;
