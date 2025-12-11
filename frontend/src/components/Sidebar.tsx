import { Box, VStack, Icon, Text, Flex, Link } from "@chakra-ui/react";
import { FiHome, FiActivity, FiSettings, FiPieChart, FiCpu, FiClock, FiShield, FiDollarSign, FiZap, FiTarget, FiSearch } from "react-icons/fi";
import { FaWallet, FaChartLine, FaHome, FaGem, FaSkull } from "react-icons/fa";
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

export default function Sidebar({ mode }: { mode?: 'INSTITUTIONAL' | 'HODL' }) {
    // Default to INSTITUTIONAL if no mode provided (fallback)
    const currentMode = mode || 'INSTITUTIONAL';

    return (
        <Box w="64" pos="fixed" h="full" bg={currentMode === 'INSTITUTIONAL' ? "gray.900" : "black"} borderRight="1px" borderColor="whiteAlpha.200">
            <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
                <Text fontSize="2xl" fontFamily="monospace" fontWeight="bold" color={currentMode === 'INSTITUTIONAL' ? "white" : "pink.400"}>
                    {currentMode === 'INSTITUTIONAL' ? 'AMMTB' : 'DEGEN'}
                </Text>
            </Flex>
            <VStack gap={2} align="stretch">
                {currentMode === 'INSTITUTIONAL' ? (
                    <>
                        <NavItem icon={FaHome} label="Dashboard" to="/" />
                        <NavItem icon={FiActivity} label="Live Analysis" to="/live-analysis" />
                        <NavItem icon={FaWallet} label="Portfolio" to="/portfolio" />
                        <NavItem icon={FiDollarSign} label="Wallet" to="/wallet" />
                        <NavItem icon={FiCpu} label="Strategies" to="/strategies" />
                        <NavItem icon={FiClock} label="Backtest" to="/backtest" />
                        <NavItem icon={FiShield} label="Risk Desk" to="/risk" />
                        <NavItem icon={FiActivity} label="Activity Logs" to="/activity" />
                        <NavItem icon={FiSettings} label="Settings" to="/settings" />
                    </>
                ) : (
                    <>
                        <NavItem icon={FiZap} label="HODL Dashboard" to="/hodl" />
                        <NavItem icon={FiSearch} label="Scanner" to="/scanner" />
                        <NavItem icon={FaGem} label="Gem Hunter" to="/gem-hunter" />
                        <NavItem icon={FaSkull} label="Rug Check" to="/rug-check" />
                        <NavItem icon={FiTarget} label="Sniper" to="/sniper" />
                        <NavItem icon={FiSettings} label="Settings" to="/settings" />
                    </>
                )}
            </VStack>
        </Box>
    );
}
