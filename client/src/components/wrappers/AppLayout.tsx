import { Outlet } from "react-router-dom";
import Menu from "../layouts/Menu/Menu";

const AppLayout = () => {
  return (
      <Menu>
        <Outlet />
      </Menu>
  );
};
export default AppLayout;
