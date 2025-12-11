import { Box, Heading, SimpleGrid, Stat, StatNumber, StatHelpText, Table, Thead, Tbody, Tr, Th, Td, Badge, Text, VStack, HStack, Button, Flex, Icon } from "@chakra-ui/react";
import { useEffect, useState, useRef } from "react";
import { FiActivity, FiDollarSign, FiCpu, FiExternalLink } from "react-icons/fi";
import axios from "axios";

export default function HodlPage() {
    const [balanceSOL, setBalanceSOL] = useState(0);
    const [solPrice, setSolPrice] = useState(150);
    const [pnl, setPnl] = useState(0);
    const [myBags, setMyBags] = useState<any[]>([]);
    const [logs, setLogs] = useState<string[]>([]);
    const [status, setStatus] = useState("IDLE");

    // Ref for auto-scrolling logs
    const logEndRef = useRef<HTMLDivElement>(null);

    const fetchData = async () => {
        try {
            // 1. Get Wallet & Positions
            const posRes = await axios.get("/api/hodl/positions").catch(() => ({ data: { data: [] } }));
            // Defensive Check: Ensure data is array
            const rawPos = posRes.data?.data;
            const positions = Array.isArray(rawPos) ? rawPos : [];
            setMyBags(positions);

            // Calculate P&L from positions safely
            let totalPnl = 0;
            positions.forEach((p: any) => {
                if (p.entry && p.qty && p.current_price) {
                    const gain = (p.current_price - p.entry) * p.qty;
                    if (!isNaN(gain)) totalPnl += gain;
                }
            });
            setPnl(totalPnl);

            // 2. Mock Balance (Until we have a real endpoint or fetch from Orchestrator)
            const balRes = await axios.get("/api/hodl/balance").catch(() => ({ data: { balance: 0 } }));
            setBalanceSOL(balRes.data?.balance || 0);

            // 3. Real Logs from Brain (DB)
            const logsRes = await axios.get("/api/hodl/logs").catch(() => ({ data: { logs: [] } }));
            if (logsRes.data.logs && logsRes.data.logs.length > 0) {
                setLogs(logsRes.data.logs);
            } else {
                setLogs(prev => [...prev.slice(-19), `[${new Date().toLocaleTimeString()}] System Idle...`]);
            }
            setStatus("SCANNING");

        } catch (e) {
            console.error("HODL Page Error:", e);
            setStatus("OFFLINE");
        }
    };

    useEffect(() => {
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll logs
    useEffect(() => {
        logEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    const balanceUSD = balanceSOL * solPrice;

    const formatPrice = (val: any) => {
        const num = parseFloat(val);
        if (isNaN(num)) return "0.00";
        return num.toFixed(6);
    };

    const formatPct = (start: any, end: any) => {
        const s = parseFloat(start);
        const e = parseFloat(end);
        if (isNaN(s) || isNaN(e) || s === 0) return "0.00";
        return ((e - s) / s * 100).toFixed(2);
    };

    return (
        <Box>
            <Flex mb={6} justify="space-between" align="center">
                <Heading size="lg" bgGradient="linear(to-r, pink.400, purple.500)" bgClip="text">
                    HODL SNIPER COMMAND
                </Heading>
                <Badge colorScheme={status === "OFFLINE" ? "red" : "green"} p={2} borderRadius="md">
                    SYSTEM: {status}
                </Badge>
            </Flex>

            <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6} mb={6}>

                {/* COL 1: WALLET & P&L */}
                <VStack spacing={6} align="stretch">
                    <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="pink.500">
                        <HStack mb={2} color="pink.400"><Icon as={FiDollarSign} /><Text fontWeight="bold">WAR CHEST</Text></HStack>
                        <Stat>
                            <StatNumber fontSize="3xl" color="white">{Number(balanceSOL || 0).toFixed(4)} SOL</StatNumber>
                            <StatHelpText>≈ ${balanceUSD.toFixed(2)} USD</StatHelpText>
                        </Stat>
                    </Box>
                    <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor={pnl >= 0 ? "green.500" : "red.500"}>
                        <HStack mb={2} color={pnl >= 0 ? "green.400" : "red.400"}><Icon as={FiActivity} /><Text fontWeight="bold">SESSION P&L</Text></HStack>
                        <Stat>
                            <StatNumber fontSize="3xl" color={pnl >= 0 ? "green.300" : "red.300"}>
                                {pnl >= 0 ? "+" : ""}${Number(pnl || 0).toFixed(2)}
                            </StatNumber>
                            <StatHelpText>Realized + Unrealized</StatHelpText>
                        </Stat>
                    </Box>
                </VStack>

                {/* COL 2: AI BRAIN LOGS (SCROLLING TERMINAL) */}
                <Box gridColumn={{ lg: "span 2" }} bg="black" borderRadius="xl" p={4} border="1px solid" borderColor="gray.700" height="300px" overflowY="auto" fontFamily="monospace">
                    <HStack mb={4} borderBottom="1px solid" borderColor="gray.800" pb={2}>
                        <Icon as={FiCpu} color="purple.400" />
                        <Text color="purple.400" fontWeight="bold">LIVE BRAIN FEED</Text>
                    </HStack>
                    <VStack align="start" spacing={1}>
                        {logs.map((log, i) => (
                            <Text key={i} color="gray.300" fontSize="sm">
                                <Text as="span" color="green.500">$</Text> {log}
                            </Text>
                        ))}
                        <div ref={logEndRef} />
                    </VStack>
                </Box>

            </SimpleGrid>

            {/* ACTIVE POSITIONS TABLE */}
            <Box bg="gray.900" borderRadius="xl" border="1px solid" borderColor="gray.700" p={6}>
                <Heading size="md" mb={4} color="white">Active Positions</Heading>
                <Table variant="simple" size="sm">
                    <Thead>
                        <Tr>
                            <Th color="gray.400">Token</Th>
                            <Th color="gray.400" isNumeric>Entry</Th>
                            <Th color="gray.400" isNumeric>Current</Th>
                            <Th color="gray.400" isNumeric>ROI</Th>
                            <Th color="gray.400">Status</Th>
                            <Th color="gray.400">Action</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {myBags.length === 0 ? (
                            <Tr><Td colSpan={6} textAlign="center" py={8} color="gray.500">No active snipes. Scanning...</Td></Tr>
                        ) : myBags.map((bag: any, i) => (
                            <Tr key={i} _hover={{ bg: "whiteAlpha.50" }}>
                                <Td fontWeight="bold" color="pink.200">{bag.token || bag.symbol || "UNKNOWN"}</Td>
                                <Td isNumeric>${formatPrice(bag.entry || bag.entry_price)}</Td>
                                <Td isNumeric>${formatPrice(bag.current_price || bag.peak_price)}</Td>
                                <Td isNumeric color={(bag.current_price || 0) > (bag.entry_price || 0) ? "green.400" : "red.400"}>
                                    {formatPct(bag.entry || bag.entry_price, bag.current_price || bag.peak_price)}%
                                </Td>
                                <Td><Badge colorScheme="purple">{bag.status || bag.current_status || "OPEN"}</Badge></Td>
                                <Td><Button size="xs" variant="outline" colorScheme="pink" rightIcon={<FiExternalLink />}>Chart</Button></Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </Box>

        </Box>
    );
}
