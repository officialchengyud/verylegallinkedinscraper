import { Flex, Text } from "@radix-ui/themes";
import TopNav from "./TopNav";
import LeftNavigation from "./LeftNavigation";
import { Route, Routes } from "react-router";
import Chat from "../Chat/Chat";

function DashboardPage() {
  return (
    <Flex direction="column" minHeight="100vh">
      <TopNav />
      <Flex direction="row" flexGrow="1">
        <LeftNavigation />
        <Routes>
          <Route path="/profile" element={<>Prof</>} />
          <Route path="/" element={<Chat />} />
        </Routes>
      </Flex>
    </Flex>
  );
}

export default DashboardPage;
