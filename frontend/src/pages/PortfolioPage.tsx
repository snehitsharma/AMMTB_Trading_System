import { Box, Heading, SimpleGrid, Table, Thead, Tbody, Tr, Th, Td, Badge, Text, HStack, Progress, useToast } from "@chakra-ui/react";
import { useEffect, useState, useMemo } from "react";
import axios from "axios";

export default function PortfolioPage() {
    // [Keep existing State & useEffect logic...]
    const [usData, setUsData] = useState<any>(null);
    const [cryptoData, setCryptoData] = useState<any>(null);
    const [positions, setPositions] = useState<any[]>([]);
    const toast = useToast();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const us = await axios.get("/api/us/account/summary").catch(() => ({ data: {} }));
                const crypto = await axios.get("/api/crypto/account/summary").catch(() => ({ data: {} }));
                setUsData(us.data);
                setCryptoData(crypto.data);

                const usPos = await axios.get("/api/us/positions").catch(() => ({ data: [] }));
                const cryptoPos = await axios.get("/api/crypto/positions").catch(() => ({ data: { positions: [] } }));

                // Handle List vs Object { positions: [] }
                const usList = Array.isArray(usPos.data) ? usPos.data : (usPos.data.positions || []);
                const cryList = Array.isArray(cryptoPos.data) ? cryptoPos.data : (cryptoPos.data.positions || []);

                setPositions([...usList, ...cryList]);
            } catch (e) {
                console.error(e);
                toast({
                    title: "Data Sync Error",
                    description: "Failed to fetch portfolio data.",
                    status: "warning",
                    duration: 5000,
                    isClosable: true,
                });
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [toast]);

    const stats = useMemo(() => {
        const primary = usData?.equity ? usData : cryptoData || {};
        const equity = Number(primary.equity || 0);
        const cashRaw = Number(primary.cash || primary.cash_balance || 0);
        const buyingPower = Number(primary.buying_power || 0);
        const marginUsed = cashRaw < 0 ? Math.abs(cashRaw) : 0;
        const grossAssets = equity + marginUsed;
        const leverageRatio = equity > 0 ? (grossAssets / equity).toFixed(2) : "0";
        return { equity, marginUsed, grossAssets, buyingPower, leverageRatio };
    }, [usData, cryptoData]);

    return (
        <Box>
            <Heading mb={6}>Portfolio Breakdown</Heading>

            {/* METRICS */}
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="green.500">
                    <Text color="gray.400" fontSize="sm" fontWeight="bold">NET EQUITY</Text>
                    <Text fontSize="3xl" fontWeight="bold" color="white">${stats.equity.toLocaleString()}</Text>
                    <Text fontSize="sm" color="gray.500">Liquidation Value</Text>
                </Box>
                <Box p={6} bg="gray.800" borderRadius="xl" borderTop="4px solid" borderColor="blue.500">
                    <Text color="gray.400" fontSize="sm" fontWeight="bold">GROSS ASSETS</Text>
                    <Text fontSize="3xl" fontWeight="bold">${stats.grossAssets.toLocaleString()}</Text>
                    <Text fontSize="sm" color="gray.500">Total Holdings</Text>
                </Box>
                <Box p={6} bg="gray.800" borderRadius="xl" borderTop="4px solid" borderColor={stats.marginUsed > 0 ? "orange.500" : "gray.600"}>
                    <Text color="gray.400" fontSize="sm" fontWeight="bold">MARGIN DEBT</Text>
                    <Text fontSize="3xl" fontWeight="bold" color={stats.marginUsed > 0 ? "orange.300" : "gray.500"}>
                        ${stats.marginUsed.toLocaleString()}
                    </Text>
                    <Text fontSize="sm" color="gray.500">Leverage: {stats.leverageRatio}x</Text>
                </Box>
            </SimpleGrid>

            {/* BUYING POWER */}
            <Box mb={8} p={5} bg="gray.800" borderRadius="xl" border="1px solid" borderColor="gray.700">
                <HStack justify="space-between" mb={2}>
                    <Text color="gray.400">Buying Power Available</Text>
                    <Text fontWeight="bold" color="blue.300">${stats.buyingPower.toLocaleString()}</Text>
                </HStack>
                <Progress value={stats.equity > 0 ? (stats.buyingPower / (stats.equity * 4)) * 100 : 0} size="sm" colorScheme="blue" mt={2} borderRadius="full" />
            </Box>

            {/* POSITIONS TABLE */}
            <Box overflowX="auto" bg="gray.900" p={6} borderRadius="xl" border="1px solid" borderColor="gray.700">
                <Heading size="md" mb={4}>Holdings</Heading>
                <Table variant="simple">
                    <Thead>
                        <Tr>
                            <Th color="gray.400">Symbol</Th>
                            <Th color="gray.400" isNumeric>Qty</Th>
                            <Th color="gray.400" isNumeric>Avg Entry</Th>
                            <Th color="gray.400" isNumeric>Current</Th>
                            <Th color="gray.400" isNumeric>Market Value</Th>
                            <Th color="gray.400" isNumeric>P/L</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {positions.map((p: any, i) => {
                            const pl = Number(p.unrealized_pl || 0);
                            return (
                                <Tr key={i} _hover={{ bg: "gray.800" }}>
                                    <Td fontWeight="bold">{p.symbol}</Td>
                                    <Td isNumeric>{p.qty}</Td>
                                    <Td isNumeric>${Number(p.avg_entry_price).toFixed(2)}</Td>
                                    <Td isNumeric>${Number(p.current_price).toFixed(2)}</Td>
                                    <Td isNumeric fontWeight="semibold">${Number(p.market_value).toLocaleString()}</Td>
                                    <Td isNumeric color={pl >= 0 ? "green.400" : "red.400"}>
                                        {pl > 0 ? "+" : ""}{pl.toFixed(2)}
                                    </Td>
                                </Tr>
                            );
                        })}
                    </Tbody>
                </Table>
                {positions.length === 0 && <Box textAlign="center" py={10} color="gray.500">No active positions.</Box>}
            </Box>
        </Box>
    );
}
