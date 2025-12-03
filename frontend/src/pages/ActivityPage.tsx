import { Box, Heading } from "@chakra-ui/react";
import { ActivityLog } from "../components/ActivityLog";

export default function ActivityPage() {
    return (
        <Box>
            <Heading mb={6}>System Activity Logs</Heading>
            <ActivityLog />
        </Box>
    );
}
