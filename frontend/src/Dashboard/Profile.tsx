import { Badge, Box, DataList, Link } from "@radix-ui/themes";
import { useAuth } from "../Context/AuthContext";

const Profile = () => {
  const { userInfo } = useAuth();
  return (
    <Box style={{ marginTop: 25, marginLeft: 300 }}>
      <DataList.Root>
        <DataList.Item align="center">
          <DataList.Label minWidth="88px">Status</DataList.Label>
          <DataList.Value>
            <Badge color="jade" variant="soft" radius="full">
              Active
            </Badge>
          </DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label minWidth="88px">First Name</DataList.Label>
          <DataList.Value>{userInfo?.firstName}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label minWidth="88px">Last Name</DataList.Label>
          <DataList.Value>{userInfo?.lastName}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label minWidth="88px">Company</DataList.Label>
          <DataList.Value>{userInfo?.company}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label minWidth="88px">Role</DataList.Label>
          <DataList.Value>{userInfo?.role}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label minWidth="88px">Industry</DataList.Label>
          <DataList.Value>{userInfo?.industry}</DataList.Value>
        </DataList.Item>
      </DataList.Root>
    </Box>
  );
};

export default Profile;
