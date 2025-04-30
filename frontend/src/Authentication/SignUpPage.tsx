import {
  Box,
  Card,
  Flex,
  Heading,
  Button,
  TextField,
  Text,
  Callout,
  Checkbox,
} from "@radix-ui/themes";
import { SubmitHandler, useForm } from "react-hook-form";
import { useAuth } from "../Context/AuthContext";
import { useState } from "react";
import { useNavigate } from "react-router";
import { doc, setDoc, Timestamp } from "firebase/firestore";
import { db } from "../main";

interface SignUpForm {
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
  firstName?: string;
  lastName?: string;
  company?: string;
  role?: string;
  industry?: string;
  city?: string;
  country?: string;
}

function SignUpPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stage, setStage] = useState(1);
  const { register, handleSubmit, setValue } = useForm<SignUpForm>();
  const navigate = useNavigate();
  const { user, signUp } = useAuth();

  const onSubmit: SubmitHandler<SignUpForm> = (data) => {
    if (data.password !== data.confirmPassword) {
      setError("Passwords do not match!");
    } else {
      if (stage === 1) {
        signUp(data.email, data.password)
          .then(() => {
            setValue("password", "");
            setValue("confirmPassword", "");
            setError("");
            setStage(2);
          })
          .catch((error) => {
            setError(error.message);
          });
      } else {
        const { password, confirmPassword, agreeToTerms, ...rest } = data;
        if (user) {
          setDoc(doc(db, "users", user.uid), {
            ...rest,
          })
            .then(
              async () =>
                await setDoc(doc(db, "chats", user.uid), {
                  messages: [
                    {
                      role: "agent",
                      message:
                        "Welcome to Very Legal LinkedIn Scraper! Send a message to get started.",
                      timestamp: Timestamp.now(),
                    },
                  ],
                })
            )
            .finally(() => {
              navigate("/");
              window.location.reload();
            })
            .catch((error) => {
              setError(error.message);
            });
        }
      }
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Flex direction="column" justify="between" height="100vh">
        <Flex
          justify="between"
          align="center"
          position="sticky"
          flexShrink="0"
          top="0"
          style={{
            height: "80px",
            padding: "0px 80px",
            zIndex: 10,
          }}
        >
          <Box>
            <Heading size="3">VERY LEGAL LINKEDIN SCRAPER</Heading>
          </Box>
        </Flex>
        <Flex
          direction="column"
          justify="center"
          align="center"
          flexGrow="1"
          style={{ padding: "40px 20px", background: "white" }}
        >
          <Box width="500px" style={{ marginTop: stage === 1 ? -100 : 0 }}>
            <Card style={{ padding: 30 }}>
              <Flex direction="column" gap="6">
                <Heading as="h1">
                  {stage === 1 ? "Sign Up" : "Tell us a little about yourself"}
                </Heading>
                <Flex direction="column" gap="4">
                  {stage === 1 ? (
                    <>
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
                      <Box>
                        <Text as="label" size="2">
                          <strong>Confirm Password</strong>
                        </Text>
                        <TextField.Root
                          type="password"
                          variant="surface"
                          placeholder="Confirm Password"
                          {...register("confirmPassword")}
                          required
                        />
                      </Box>
                      <Text as="label" size="2">
                        <Flex gap="2">
                          <Checkbox {...register("agreeToTerms")} required />
                          Agree to Terms and Conditions
                        </Flex>
                      </Text>
                    </>
                  ) : (
                    <>
                      <Callout.Root size="1">
                        <Callout.Text>
                          Welcome! Please tell us a little more about yourself
                          so we can best cater the experience to you.
                        </Callout.Text>
                      </Callout.Root>
                      <Box>
                        <Text as="label" size="2">
                          <strong>First Name</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="First Name"
                          {...register("firstName")}
                          required
                        />
                      </Box>
                      <Box>
                        <Text as="label" size="2">
                          <strong>Last Name</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="Last Name"
                          {...register("lastName")}
                          required
                        />
                      </Box>
                      <Box>
                        <Text as="label" size="2">
                          <strong>Company</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="Company"
                          {...register("company")}
                          required
                        />
                      </Box>
                      <Box>
                        <Text as="label" size="2">
                          <strong>Role</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="Role"
                          {...register("role")}
                          required
                        />
                      </Box>
                      <Box>
                        <Text as="label" size="2">
                          <strong>Industry</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="Industry"
                          {...register("industry")}
                          required
                        />
                      </Box>
                      <Box>
                        <Text as="label" size="2">
                          <strong>Country</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="Country"
                          {...register("country")}
                          required
                        />
                      </Box>
                      <Box>
                        <Text as="label" size="2">
                          <strong>City</strong>
                        </Text>
                        <TextField.Root
                          variant="surface"
                          placeholder="City"
                          {...register("city")}
                          required
                        />
                      </Box>
                    </>
                  )}
                </Flex>
                {error && (
                  <Callout.Root color="red">
                    <Callout.Text>{error}</Callout.Text>
                  </Callout.Root>
                )}
                <Flex gap="5" align="center" justify="end">
                  {stage === 1 && (
                    <Button
                      size="2"
                      variant="ghost"
                      onClick={() => navigate("/login")}
                    >
                      Have an account? Login!
                    </Button>
                  )}
                  <Button
                    size="2"
                    variant="solid"
                    type="submit"
                    loading={loading}
                  >
                    {stage === 1 ? "Sign Up" : "Continue"}
                  </Button>
                </Flex>
              </Flex>
            </Card>
          </Box>
        </Flex>

        <Flex height="80px" justify="center" align="center" flexShrink="0">
          <Heading size="3" color="gray">
            © VERY LEGAL LINKEDIN SCRAPER 2025
          </Heading>
        </Flex>
      </Flex>
    </form>
  );
}

export default SignUpPage;
