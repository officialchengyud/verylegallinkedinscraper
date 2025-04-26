import { Navigate, Outlet } from "react-router";
import { useAuth } from "../Context/AuthContext";
import { Spinner } from "@radix-ui/themes";

const AuthLayout = () => {
  const { user, loading } = useAuth();
  if (!loading && !user) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return <Spinner />;
  }

  return <Outlet />;
};

export default AuthLayout;
