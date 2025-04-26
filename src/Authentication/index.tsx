import {
  Box,
  Card,
  Flex,
  Heading,
  Button,
  TextField,
  Text,
} from "@radix-ui/themes";
import { SubmitHandler, useForm } from "react-hook-form";
import { useAuth } from "../Context/AuthContext";
import { useState } from "react";

interface LoginForm {
  email: string;
  password: string;
}

function Login() {
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit } = useForm<LoginForm>();
  const { login } = useAuth();
  const onSubmit: SubmitHandler<LoginForm> = (data) => {
    setLoading(true);
    login(data.email, data.password).then(() => setLoading(false));
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Flex direction="column" justify="between" height="100vh">
        <Flex
          justify="between"
          align="center"
          height="100px"
          style={{ marginLeft: "80px" }}
        >
          <Box>
            <Heading size="3">VERY LEGAL LINKEDIN SCRAPER</Heading>
          </Box>
        </Flex>
        <Flex justify="center">
          <Box width="500px" style={{ marginTop: -180 }}>
            <Card style={{ padding: 30 }}>
              <Flex direction="column" gap="6">
                <Heading as="h1">Sign in</Heading>
                <Flex direction="column" gap="4">
                  <Box>
                    <Text as="label" size="2">
                      <strong>Email Address</strong>
                    </Text>
                    <TextField.Root
                      variant="surface"
                      placeholder="Email Address"
                      {...register("email")}
                      required
                    />
                  </Box>
                  <Box>
                    <Text as="label" size="2">
                      <strong>Password</strong>
                    </Text>
                    <TextField.Root
                      type="password"
                      variant="surface"
                      placeholder="Password"
                      {...register("password")}
                      required
                    />
                  </Box>
                </Flex>
                <Flex gap="2" align="center" justify="end">
                  <Button size="2" variant="outline">
                    Create Account
                  </Button>
                  <Button
                    size="2"
                    variant="solid"
                    type="submit"
                    loading={loading}
                  >
                    Sign In
                  </Button>
                </Flex>
              </Flex>
            </Card>
          </Box>
        </Flex>
        <Flex height="80px" justify="center">
          <Heading size="3" color="gray">
            © VERY LEGAL LINKEDIN SCRAPER 2025
          </Heading>
        </Flex>
      </Flex>
    </form>
  );
}

export default Login;
