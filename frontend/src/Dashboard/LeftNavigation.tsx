import { Text, Flex, Heading, Box, Card } from "@radix-ui/themes";
import { useNavigate } from "react-router";

function LeftNavigation() {
  const navigate = useNavigate();
  return (
    <Flex
      direction="column"
      position="fixed"
      style={{
        width: 250,
        borderRight: "1px solid #ededed",
        padding: "20px 20px",
        height: "100%",
      }}
    >
      <Heading size="3">Features</Heading>
      <Box
        maxWidth="350px"
        style={{ marginLeft: -10, marginTop: 10 }}
        onClick={() => navigate("/")}
      >
        <Card>
          <Text as="div" size="2" weight="bold">
            Chat
          </Text>
          <Text as="div" color="gray" size="2">
            Start building your next project in minutes
          </Text>
        </Card>
      </Box>
      <Box
        maxWidth="350px"
        style={{ marginLeft: -10, marginTop: 10 }}
        onClick={() => navigate("/profile")}
      >
        <Card>
          <Text as="div" size="2" weight="bold">
            Profile
          </Text>
          <Text as="div" color="gray" size="2">
            View your profile
          </Text>
        </Card>
      </Box>
    </Flex>
  );
}

export default LeftNavigation;
