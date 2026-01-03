// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import PropTypes from "prop-types";

export default function data() {
  const Employee = ({ name, phone }) => (
    <MDBox display="flex" alignItems="center" lineHeight={1}>
      <MDBox lineHeight={1}>
        <MDTypography display="block" variant="button" fontWeight="medium">
          {name}
        </MDTypography>
        <MDTypography variant="caption">{phone}</MDTypography>
      </MDBox>
    </MDBox>
  );

  Employee.propTypes = {
    name: PropTypes.string.isRequired,
    phone: PropTypes.string.isRequired,
  };

  const Info = ({ role, salary }) => (
    <MDBox lineHeight={1} textAlign="left">
      <MDTypography display="block" variant="caption" color="text" fontWeight="medium">
        {role}
      </MDTypography>
      <MDTypography variant="caption">{Number(salary).toLocaleString("vi-VN")} đ</MDTypography>
    </MDBox>
  );

  Info.propTypes = {
    role: PropTypes.string.isRequired,
    salary: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  };

  const initialRows = [
    {
      id: 1,
      employee: <Employee name="Nguyễn Văn A" phone="0901234567" />,
      info: <Info role="manager" salary="12000000" />,
      hire_date: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          2023-04-10
        </MDTypography>
      ),
      action: null,
    },
    {
      id: 2,
      employee: <Employee name="Trần Thị B" phone="0912345678" />,
      info: <Info role="cashier" salary="8500000" />,
      hire_date: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          2022-08-15
        </MDTypography>
      ),
      action: null,
    },
    {
      id: 3,
      employee: <Employee name="Lê Văn C" phone="0987654321" />,
      info: <Info role="chef" salary="10000000" />,
      hire_date: (
        <MDTypography variant="caption" color="text" fontWeight="medium">
          2021-11-05
        </MDTypography>
      ),
      action: null,
    },
  ];

  return {
    columns: [
      { Header: "Tên nhân viên", accessor: "employee", width: "30%", align: "left" },
      { Header: "Chức vụ", accessor: "info", align: "left" },
      { Header: "Ngày vào làm", accessor: "hire_date", align: "center" },
      { Header: "Hành động", accessor: "action", align: "center" },
    ],
    rows: initialRows,
  };
}
