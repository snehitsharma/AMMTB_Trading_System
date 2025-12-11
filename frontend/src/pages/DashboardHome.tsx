import { Box, SimpleGrid, VStack, HStack, Button, Text, Heading, Badge, Flex, Icon, Spinner, Alert, AlertTitle, AlertDescription, Divider } from "@chakra-ui/react";
import { useEffect, useState, useMemo } from "react";
import { FiTrendingUp, FiActivity, FiCheckCircle } from "react-icons/fi";
import api from "../api";
import AgentStatus from "../components/AgentStatus";

export default function DashboardHome() {
    const [usData, setUsData] = useState<any>({});
    const [cryptoData, setCryptoData] = useState<any>({});
    const [regime, setRegime] = useState("LOADING...");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch Standardized Endpoints
                const us = await api.get("/api/us/account/summary").catch(() => ({ data: { equity: 0, cash: 0, status: "OFFLINE" } }));
                const usPnl = await api.get("/api/us/pnl").catch(() => ({ data: { realized_pnl: 0, unrealized_pnl: 0, total_pnl: 0 } }));

                // Merge Data
                setUsData({ ...us.data, ...usPnl.data });
                const crypto = await api.get("/api/crypto/account/summary").catch(() => ({ data: { equity: 0, cash: 0, status: "OFFLINE" } }));

                setCryptoData(crypto.data);

                // Check Signals for Regime
                const sigs = await api.get("/api/us/signals").catch(() => ({ data: [] }));
                if (Array.isArray(sigs.data) && sigs.data.length > 0) setRegime("ACTIVE TRADING");
                else setRegime("WAITING");

            } catch (e) {
                console.error("Dash Error", e);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 4000);
        return () => clearInterval(interval);
    }, []);

    const totalEquity = useMemo(() => {
        // Avoid double counting shared Alpaca account
        const us = Number(usData.equity || 0);
        const cry = Number(cryptoData.equity || 0);
        return Math.max(us, cry);
    }, [usData, cryptoData]);

    // Custom Stat Component
    const StatBox = ({ label, value, subtext, color = "white" }: any) => (
        <Box>
            <Text color="gray.400" fontSize="sm">{label}</Text>
            <Text fontSize="2xl" fontWeight="bold" color={color}>{value}</Text>
            <Text fontSize="xs" color="gray.500">{subtext}</Text>
        </Box>
    );

    if (loading) return <Flex justify="center" p={10}><Spinner color="blue.500" /></Flex>;

    return (
        <Box p={6}>
            {/* HEADER */}
            <Flex justify="space-between" align="center" mb={6}>
                <Heading size="lg" bgGradient="linear(to-r, teal.400, blue.500)" bgClip="text" display="flex" alignItems="center" gap={2}>
                    <Icon as={FiActivity} color="purple.400" /> Control Center
                </Heading>
                <Badge colorScheme="green" p={2} borderRadius="md">
                    SYSTEM ONLINE
                </Badge>
            </Flex>

            {/* AGENT STATUS WIDGET */}
            <AgentStatus />

            {/* TOTAL EQUITY HERO */}
            {/* TOTAL EQUITY & BUYING POWER HERO */}
            <Box bg="gray.900" p={8} borderRadius="2xl" shadow="xl" mb={8} border="1px solid" borderColor="gray.700">
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8} divider={<Divider orientation="vertical" borderColor="whiteAlpha.200" h="auto" />}>
                    {/* Total Liquidity */}
                    <VStack align="start" spacing={1}>
                        <Text color="gray.400" fontSize="lg">Total Liquidity</Text>
                        <Text fontSize="5xl" fontWeight="extrabold" lineHeight="1" color="white">
                            ${totalEquity.toLocaleString()}
                        </Text>
                        <HStack mt={2}>
                            <Icon as={FiTrendingUp} color="green.400" />
                            <Text color="green.400">Global Assets</Text>
                        </HStack>
                    </VStack>

                    {/* Buying Power */}
                    <VStack align="start" spacing={1}>
                        <Text color="gray.400" fontSize="lg">Buying Power</Text>
                        <Text fontSize="5xl" fontWeight="extrabold" lineHeight="1" color="blue.300">
                            ${Number(usData.buying_power || 0).toLocaleString()}
                        </Text>
                        <HStack mt={2}>
                            <Icon as={FiCheckCircle} color="blue.400" />
                            <Text color="blue.400">Available to Trade</Text>
                        </HStack>
                    </VStack>
                </SimpleGrid>
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
                {/* US MARKET */}
                <Box bg="gray.800" p={6} borderRadius="xl" borderTop="4px solid" borderColor="blue.500">
                    <Heading size="md" mb={4} color="blue.300">🇺🇸 US Equities</Heading>
                    <StatBox
                        label="Buying Power"
                        value={`$${Number(usData.buying_power || 0).toLocaleString()}`}
                        subtext={`Net Equity: $${Number(usData.equity || 0).toLocaleString()}`}
                    />

                    {/* PnL Section */}
                    <Box mt={4} p={3} bg="blackAlpha.300" borderRadius="md">
                        <HStack justify="space-between">
                            <Text fontSize="xs" color="gray.400">Realized PnL</Text>
                            <Text fontSize="sm" fontWeight="bold" color={Number(usData.realized_pnl || 0) >= 0 ? "green.300" : "red.300"}>
                                ${Number(usData.realized_pnl || 0).toFixed(2)}
                            </Text>
                        </HStack>
                        <HStack justify="space-between">
                            <Text fontSize="xs" color="gray.400">Unrealized PnL</Text>
                            <Text fontSize="sm" fontWeight="bold" color={Number(usData.unrealized_pnl || 0) >= 0 ? "green.300" : "red.300"}>
                                ${Number(usData.unrealized_pnl || 0).toFixed(2)}
                            </Text>
                        </HStack>
                        <Divider my={2} borderColor="gray.600" />
                        <HStack justify="space-between">
                            <Text fontSize="xs" color="gray.300">Total Profit</Text>
                            <Text fontSize="sm" fontWeight="bold" color={Number(usData.total_pnl || 0) >= 0 ? "green.400" : "red.400"}>
                                ${Number(usData.total_pnl || 0).toFixed(2)}
                            </Text>
                        </HStack>
                    </Box>

                    <Button mt={4} w="full" colorScheme="blue" size="sm" onClick={() => api.post("/api/us/trade", { symbol: "AAPL", qty: 1, side: "buy" })}>
                        Quick Buy AAPL
                    </Button>
                </Box>

                {/* CRYPTO MARKET */}
                <Box bg="gray.800" p={6} borderRadius="xl" borderTop="4px solid" borderColor="orange.500">
                    <Heading size="md" mb={4} color="orange.300">₿ Crypto Assets</Heading>
                    <StatBox
                        label="Solana Balance"
                        value={`${Number(cryptoData.balance || 0).toFixed(4)} SOL`}
                        subtext={`Status: ${cryptoData.status || "ONLINE"}`}
                    />
                    <Button mt={4} w="full" colorScheme="orange" size="sm" onClick={() => api.post("/api/crypto/trade", { symbol: "SOL", qty: 0.1, side: "buy" })}>
                        Quick Snipe SOL
                    </Button>
                </Box>
            </SimpleGrid>

            {/* INDIA MARKET */}
            <Box mt={8} bg="gray.800" p={6} borderRadius="xl" borderTop="4px solid" borderColor="purple.500">
                <Heading size="md" mb={4} color="purple.300">🇮🇳 India Market (NSE/BSE)</Heading>
                <Text color="gray.500" fontSize="sm">Status: COMING SOON</Text>
                <Text fontSize="xs" color="gray.600" mt={2}>Agent is online on Port 8003. Strategy Engine ready for Zerodha/Upstox integration.</Text>
            </Box>
        </Box >
    );
}
