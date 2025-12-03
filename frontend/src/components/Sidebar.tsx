import { Box, VStack, Icon, Text, Flex, Link } from "@chakra-ui/react";
import { FiHome, FiActivity, FiSettings, FiPieChart } from "react-icons/fi";
import { FaWallet, FaChartLine, FaHome } from "react-icons/fa";
import { Link as RouterLink, useLocation } from "react-router-dom";

const NavItem = ({ icon, label, to }: any) => {
    const location = useLocation();
    const isActive = location.pathname === to;
    return (
        <Link as={RouterLink} to={to} style={{ textDecoration: 'none' }} w="full">
            <Flex
                align="center"
                p="4"
                mx="4"
                borderRadius="lg"
                role="group"
                cursor="pointer"
                bg={isActive ? "blue.600" : "transparent"}
                color={isActive ? "white" : "gray.400"}
                _hover={{ bg: "blue.500", color: "white" }}
            >
                <Icon as={icon} mr="4" fontSize="16" />
                <Text fontSize="sm" fontWeight="medium">{label}</Text>
            </Flex>
        </Link>
    );
};

export default function Sidebar() {
    return (
        <Box w="64" pos="fixed" h="full" bg="gray.900" borderRight="1px" borderColor="gray.700">
            <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
                <Text fontSize="2xl" fontFamily="monospace" fontWeight="bold" color="white">
                    AMMTB
                </Text>
            </Flex>
            <VStack gap={2} align="stretch">
                <NavItem icon={FaHome} label="Dashboard" to="/" />
                <NavItem icon={FaChartLine} label="Live Analysis" to="/live-analysis" />
                <NavItem icon={FaWallet} label="Portfolio" to="/portfolio" />
                <NavItem icon={FiActivity} label="Activity Logs" to="/activity" />
                <NavItem icon={FiSettings} label="Settings" to="/settings" />
            </VStack>
        </Box>
    );
}
