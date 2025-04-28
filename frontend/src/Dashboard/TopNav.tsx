import {
  Avatar,
  Box,
  Card,
  DropdownMenu,
  Flex,
  Heading,
  Text,
} from "@radix-ui/themes";
import { useAuth } from "../Context/AuthContext";

const TopNav = () => {
  const { userInfo, signOut } = useAuth();

  return (
    <Flex
      justify="between"
      align="center"
      position="sticky"
      top="0"
      style={{
        height: "60px",
        padding: "0px 80px 0px 20px",
        zIndex: 10,
        borderBottom: "1px solid #ededed",
        background: "white",
      }}
    >
      <Box>
        <Heading size="3">VERY LEGAL LINKEDIN SCRAPER</Heading>
      </Box>
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          <Box maxWidth="240px">
            <Card variant="ghost">
              <Flex gap="3" align="center">
                <Avatar
                  size="3"
                  radius="full"
                  fallback={userInfo?.firstName.charAt(0) || "A"}
                  color="indigo"
                />
                <Box>
                  <Text as="div" size="2" weight="bold">
                    {userInfo?.firstName} {userInfo?.lastName}
                  </Text>
                </Box>
                <DropdownMenu.TriggerIcon />
              </Flex>
            </Card>
          </Box>
        </DropdownMenu.Trigger>
        <DropdownMenu.Content variant="soft" color="indigo">
          <DropdownMenu.Item color="red" onClick={() => signOut()}>
            Sign Out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Root>
    </Flex>
  );
};

export default TopNav;
