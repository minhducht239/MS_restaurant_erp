import React, { useEffect, useState, useCallback, useMemo } from "react";
import PropTypes from "prop-types";
import Grid from "@mui/material/Grid";
import { Alert, Skeleton, Box } from "@mui/material";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";

// Services
import { getBills, getMonthlyRevenue } from "services/BillingService";
import { getStaff } from "services/StaffService";
import { getWeeklyRevenue, getTopSellingItems } from "services/DashboardService";

// Dashboard components
import Tablestate from "layouts/dashboard/components/Reservation";
import PopularItems from "layouts/dashboard/components/PopularItems";
import Statistics from "layouts/dashboard/components/Statistics";

class DashboardErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Dashboard Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <DashboardLayout>
          <DashboardNavbar />
          <MDBox py={3}>
            <Alert severity="error" sx={{ mb: 3 }}>
              Dashboard gặp lỗi không mong muốn. Vui lòng làm mới trang.
            </Alert>
          </MDBox>
          <Footer />
        </DashboardLayout>
      );
    }

    return this.props.children;
  }
}

DashboardErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
};

function Dashboard() {
  const [dashboardData, setDashboardData] = useState({
    stats: {
      totalOrders: 0,
      averageOrderValue: 0,
      monthlyRevenue: 0,
      totalSalaries: 0,
    },
    weeklyRevenue: {
      labels: [],
      datasets: { label: "", data: [] },
    },
    monthlyRevenue: {
      labels: [],
      datasets: { label: "", data: [] },
    },
    popularItems: {
      food: [],
      drinks: [],
    },
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  // Dữ liệu rỗng khi không có data thực
  const emptyData = useMemo(
    () => ({
      monthlyRevenue: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      weeklyRevenue: [0, 0, 0, 0, 0, 0, 0],
      popularItems: {
        food: [],
        drinks: [],
      },
    }),
    []
  );

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log("Fetching dashboard data...");

      const results = await Promise.allSettled([
        getMonthlyRevenue(),
        getTopSellingItems(),
        getBills({ limit: 1000 }),
        getStaff({ limit: 1000 }),
        getWeeklyRevenue(),
      ]);

      const [monthlyRes, topItemsRes, billsRes, staffRes, weeklyRes] = results;

      // Sử dụng dữ liệu rỗng thay vì fallback
      let monthlyRevenueData = emptyData.monthlyRevenue;
      if (monthlyRes.status === "fulfilled" && Array.isArray(monthlyRes.value)) {
        monthlyRevenueData = monthlyRes.value;
      }

      let weeklyRevenueData = emptyData.weeklyRevenue;
      if (weeklyRes.status === "fulfilled" && Array.isArray(weeklyRes.value)) {
        weeklyRevenueData = weeklyRes.value;
      }

      let popularItems = emptyData.popularItems;
      if (topItemsRes.status === "fulfilled" && topItemsRes.value) {
        const items = topItemsRes.value;
        popularItems = {
          food: items.food || [],
          drinks: items.drinks || [],
        };
      }

      let totalOrders = 0;
      let averageOrderValue = 0;
      let monthlyRevenue = 0;

      if (billsRes.status === "fulfilled" && billsRes.value) {
        const billsData = billsRes.value;
        totalOrders = billsData.count || 0;

        const bills = billsData.results || [];
        const totalAmount = bills.reduce((sum, bill) => sum + Number(bill.total || 0), 0);
        averageOrderValue = totalOrders > 0 ? Math.round(totalAmount / totalOrders) : 0;

        // Get current month revenue from bills
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();

        monthlyRevenue = bills
          .filter((bill) => {
            const billDate = new Date(bill.date);
            return billDate.getMonth() === currentMonth && billDate.getFullYear() === currentYear;
          })
          .reduce((sum, bill) => sum + Number(bill.total || 0), 0);
      }

      let totalSalaries = 0;
      if (staffRes.status === "fulfilled" && staffRes.value?.results) {
        totalSalaries = staffRes.value.results.reduce(
          (sum, staff) => sum + Number(staff.salary || 0),
          0
        );
      }

      setDashboardData({
        stats: {
          totalOrders,
          averageOrderValue,
          monthlyRevenue,
          totalSalaries,
        },
        weeklyRevenue: {
          labels: ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"],
          datasets: { label: "VNĐ", data: weeklyRevenueData },
        },
        monthlyRevenue: {
          labels: [
            "Tháng 1",
            "Tháng 2",
            "Tháng 3",
            "Tháng 4",
            "Tháng 5",
            "Tháng 6",
            "Tháng 7",
            "Tháng 8",
            "Tháng 9",
            "Tháng 10",
            "Tháng 11",
            "Tháng 12",
          ],
          datasets: { label: "VNĐ", data: monthlyRevenueData },
        },
        popularItems,
      });

      console.log("Dashboard data loaded successfully");
    } catch (error) {
      console.error("Critical error in dashboard:", error);
      setError("Không thể tải dữ liệu dashboard. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  }, [emptyData]);

  const handleRetry = useCallback(() => {
    setRetryCount((prev) => prev + 1);
    fetchDashboardData();
  }, [fetchDashboardData]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const LoadingSkeleton = () => (
    <MDBox py={3}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Skeleton variant="rectangular" height={120} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Skeleton variant="rectangular" height={300} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Skeleton variant="rectangular" height={300} />
        </Grid>
        <Grid item xs={12} md={8}>
          <Skeleton variant="rectangular" height={400} />
        </Grid>
        <Grid item xs={12} md={4}>
          <Skeleton variant="rectangular" height={400} />
        </Grid>
      </Grid>
    </MDBox>
  );

  return (
    <DashboardErrorBoundary>
      <DashboardLayout>
        <DashboardNavbar />

        {loading ? (
          <LoadingSkeleton />
        ) : error ? (
          <MDBox py={3}>
            <Alert
              severity="error"
              action={
                <button onClick={handleRetry} style={{ marginLeft: 10 }}>
                  Thử lại
                </button>
              }
            >
              {error}
            </Alert>
          </MDBox>
        ) : (
          <MDBox py={3}>
            <MDBox mb={3}>
              <Statistics data={dashboardData.stats} loading={loading} error={error} />
            </MDBox>

            <MDBox mt={4.5}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6} lg={6}>
                  <MDBox mb={3}>
                    <ReportsLineChart
                      color="success"
                      title="Doanh thu tuần"
                      description="Doanh thu theo ngày trong tuần hiện tại"
                      date={`Tuần ${Math.ceil(
                        new Date().getDate() / 7
                      )} - ${new Date().toLocaleDateString("vi-VN")}`}
                      chart={dashboardData.weeklyRevenue}
                    />
                  </MDBox>
                </Grid>
                <Grid item xs={12} md={6} lg={6}>
                  <MDBox mb={3}>
                    <ReportsLineChart
                      color="dark"
                      title="Doanh thu tháng"
                      description="Doanh thu theo tháng trong năm hiện tại"
                      date={`Năm ${new Date().getFullYear()}`}
                      chart={dashboardData.monthlyRevenue}
                    />
                  </MDBox>
                </Grid>
              </Grid>
            </MDBox>

            <MDBox>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6} lg={8}>
                  <Tablestate />
                </Grid>
                <Grid item xs={12} md={6} lg={4}>
                  <PopularItems
                    foodDetails={dashboardData.popularItems.food}
                    drinkDetails={dashboardData.popularItems.drinks}
                  />
                </Grid>
              </Grid>
            </MDBox>
          </MDBox>
        )}

        <Footer />
      </DashboardLayout>
    </DashboardErrorBoundary>
  );
}

export default Dashboard;
