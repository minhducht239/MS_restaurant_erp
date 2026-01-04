// @mui material components
import { useState, useEffect } from "react"; // Thêm useEffect

// react-router-dom components
import { Link, useNavigate, useLocation } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";
import Switch from "@mui/material/Switch";
import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";
import Alert from "@mui/material/Alert"; // Thêm Alert component
import Divider from "@mui/material/Divider";
import CircularProgress from "@mui/material/CircularProgress";

// @mui icons
import GoogleIcon from "@mui/icons-material/Google";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Authentication layout components
import BasicLayout from "layouts/authentication/components/BasicLayout";

// Images
import bgImage from "assets/images/Background-sign-in.jpg";
import { useAuth } from "context/AuthContext"; // Import useAuth hook

function Basic() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError] = useState(""); // Thay đổi từ null thành ""
  const [validationErrors, setValidationErrors] = useState({}); // Thêm validation errors state

  const navigate = useNavigate();
  const location = useLocation();
  const { login, error: authError, getGoogleLoginUrl, loginWithGoogle } = useAuth();

  const handleSetRememberMe = () => setRememberMe(!rememberMe);

  const handleChange = (e) => {
    const { name, value } = e.target;
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

    // Clear general error
    if (error) {
      setError("");
    }
  };

  // Cập nhật handleSubmit với validation tốt hơn
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setValidationErrors({});

    // Basic validation
    const errors = {};

    if (!formData.username?.trim()) {
      errors.username = "Username hoặc Email không được để trống";
    }

    if (!formData.password) {
      errors.password = "Mật khẩu không được để trống";
    }

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    setLoading(true);

    try {
      console.log("Attempting login with:", formData.username);

      // Sử dụng AuthContext login function
      const success = await login(formData.username, formData.password);

      if (success) {
        console.log("Login successful, redirecting to dashboard");

        // Lưu username nếu chọn "remember me"
        if (rememberMe) {
          localStorage.setItem("remember_user", formData.username);
        } else {
          localStorage.removeItem("remember_user");
        }

        // Chuyển hướng đến dashboard
        navigate("/dashboard");
      } else {
        console.log("Login failed");
        // AuthContext đã set error, lấy từ đó
        setError(authError || "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin đăng nhập.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError(err.message || "Có lỗi xảy ra khi đăng nhập. Vui lòng thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  // Sử dụng useEffect thay vì useState cho việc load remembered username
  useEffect(() => {
    const savedUser = localStorage.getItem("remember_user");
    if (savedUser) {
      setFormData((prev) => ({ ...prev, username: savedUser }));
      setRememberMe(true);
    }
  }, []);

  // Handle Google OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");
    const googleError = urlParams.get("error");

    if (googleError) {
      setError("Google login was cancelled or failed");
      // Clear URL params
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    if (code) {
      handleGoogleCallback(code);
    }
  }, [location.search]);

  const handleGoogleCallback = async (code) => {
    setGoogleLoading(true);
    setError("");

    try {
      const result = await loginWithGoogle(code);

      if (result.success) {
        console.log("Google login successful");
        if (result.isNewUser) {
          // Có thể redirect đến trang hoàn thiện profile nếu cần
          console.log("New user created from Google account");
        }
        navigate("/dashboard");
      } else {
        setError(result.error || "Google login failed");
      }
    } catch (err) {
      console.error("Google callback error:", err);
      setError("Google login failed. Please try again.");
    } finally {
      setGoogleLoading(false);
      // Clear URL params
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const handleGoogleLogin = async () => {
    setGoogleLoading(true);
    setError("");

    try {
      const googleUrl = await getGoogleLoginUrl();
      if (googleUrl) {
        // Redirect to Google OAuth
        window.location.href = googleUrl;
      } else {
        setError("Could not get Google login URL. Please try again.");
        setGoogleLoading(false);
      }
    } catch (err) {
      console.error("Google login error:", err);
      setError("Google login is not configured or unavailable.");
      setGoogleLoading(false);
    }
  };

  return (
    <BasicLayout image={bgImage}>
      <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="info"
          mx={2}
          mt={-3}
          p={2}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            Sign in
          </MDTypography>
        </MDBox>
        <MDBox pt={4} pb={3} px={3}>
          {/* Google Loading Overlay */}
          {googleLoading && (
            <MDBox
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              py={4}
            >
              <CircularProgress color="info" />
              <MDTypography variant="body2" color="text" mt={2}>
                Đang xử lý đăng nhập Google...
              </MDTypography>
            </MDBox>
          )}

          {!googleLoading && (
            <MDBox component="form" role="form" onSubmit={handleSubmit}>
              {/* Error Display - cải tiến */}
              {(error || authError) && (
                <MDBox mb={2}>
                  <Alert severity="error" sx={{ fontSize: "0.875rem" }}>
                    {error || authError}
                  </Alert>
                </MDBox>
              )}

              <MDBox mb={2}>
                <MDInput
                  type="text"
                  label="Username or Email"
                  fullWidth
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  error={!!validationErrors.username}
                  disabled={loading}
                  required
                />
                {validationErrors.username && (
                  <MDTypography
                    variant="caption"
                    color="error"
                    sx={{ fontSize: "0.75rem", mt: 0.5 }}
                  >
                    {validationErrors.username}
                  </MDTypography>
                )}
              </MDBox>

              <MDBox mb={2}>
                <MDInput
                  type="password"
                  label="Password"
                  fullWidth
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  error={!!validationErrors.password}
                  disabled={loading}
                  required
                />
                {validationErrors.password && (
                  <MDTypography
                    variant="caption"
                    color="error"
                    sx={{ fontSize: "0.75rem", mt: 0.5 }}
                  >
                    {validationErrors.password}
                  </MDTypography>
                )}
              </MDBox>

              <MDBox display="flex" alignItems="center" ml={-1}>
                <Switch checked={rememberMe} onChange={handleSetRememberMe} disabled={loading} />
                <MDTypography
                  variant="button"
                  fontWeight="regular"
                  color="text"
                  onClick={handleSetRememberMe}
                  sx={{ cursor: "pointer", userSelect: "none", ml: -1 }}
                >
                  &nbsp;&nbsp;Remember me
                </MDTypography>
              </MDBox>

              <MDBox mt={4} mb={1}>
                <MDButton
                  type="submit"
                  variant="gradient"
                  color="info"
                  fullWidth
                  disabled={loading}
                >
                  {loading ? "Signing in..." : "Sign in"}
                </MDButton>
              </MDBox>

              {/* Divider */}
              <MDBox mt={3} mb={2}>
                <Divider>
                  <MDTypography variant="caption" color="text">
                    hoặc
                  </MDTypography>
                </Divider>
              </MDBox>

              {/* Google Login Button */}
              <MDBox mb={2}>
                <MDButton
                  variant="outlined"
                  color="dark"
                  fullWidth
                  onClick={handleGoogleLogin}
                  disabled={loading || googleLoading}
                  startIcon={<GoogleIcon />}
                >
                  Đăng nhập với Google
                </MDButton>
              </MDBox>

              <MDBox mt={3} mb={1} textAlign="center">
                <MDTypography variant="button" color="text">
                  Don&apos;t have an account?{" "}
                  <MDTypography
                    component={Link}
                    to="/authentication/sign-up"
                    variant="button"
                    color="info"
                    fontWeight="medium"
                    textGradient
                  >
                    Sign up
                  </MDTypography>
                </MDTypography>
              </MDBox>
            </MDBox>
          )}
        </MDBox>
      </Card>
    </BasicLayout>
  );
}

export default Basic;
