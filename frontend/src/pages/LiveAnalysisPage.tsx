import { Box, Heading, Table, Thead, Tbody, Tr, Th, Td, Badge, Spinner, Text, Flex, Icon, Alert } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import React from "react";
import { FiActivity, FiAlertCircle } from "react-icons/fi";
import api from "../api";

export default function LiveAnalysisPage() {
    const [scanResults, setScanResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<string>("");
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchSignals = async () => {
            try {
                // Decentralized Fetching from all 3 agents
                // We use Promise.allSettled to ensure one failure doesn't break the whole page
                // Use api.get for Retries
                const results = await Promise.allSettled([
                    api.get("/api/us/signals"),
                    api.get("/api/crypto/signals"),
                    api.get("/api/hodl/scan")
                ]);

                const signals = [];

                // 1. US SIGNALS
                if (results[0].status === "fulfilled") {
                    const data = results[0].value.data;
                    if (Array.isArray(data)) signals.push(...data);
                }

                // 2. CRYPTO SIGNALS
                if (results[1].status === "fulfilled") {
                    const data = results[1].value.data;
                    if (Array.isArray(data)) signals.push(...data);
                }

                // 3. HODL SIGNALS
                if (results[2].status === "fulfilled") {
                    const data = results[2].value.data;
                    const tokens = data.tokens || [];
                    const formatted = tokens.map((t: any) => ({
                        asset: t.token,
                        price: 0, // usually unknown for memecoins in this simple scan
                        action: "SNIPE",
                        reason: `Risk: ${t.risk} | Liq: ${t.liq}`,
                        source: "HODL"
                    }));
                    signals.push(...formatted);
                }

                setScanResults(signals);
                setLastUpdated(new Date().toLocaleTimeString());
                setError("");
            } catch (error) {
                console.error("Failed to fetch signals", error);
                setError("Partial Swarm Sync Failure");
            } finally {
                setLoading(false);
            }
        };

        fetchSignals();
        const interval = setInterval(fetchSignals, 5000); // 5s Refresh
        return () => clearInterval(interval);
    }, []);

    // LOADING STATE
    if (loading) return (
        <Flex justify="center" align="center" h="50vh" direction="column">
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text mt={4} color="gray.400">Connecting to Swarm Agents...</Text>
        </Flex>
    );

    return (
        <Box>
            <Heading mb={4} display="flex" alignItems="center" gap={2}>
                <Icon as={FiActivity} color="blue.400" /> Live Market Scan
            </Heading>

            {/* ERROR BANNER */}
            {error && (
                <Alert status="warning" mb={4} borderRadius="md">
                    <Icon as={FiAlertCircle} mr={2} />
                    {error}
                </Alert>
            )}

            <Text color="gray.400" mb={6}>
                Swarm Status: <Badge colorScheme="green">ACTIVE</Badge>
                &bull; Last Update: {lastUpdated || "---"}
            </Text>

            <Box overflowX="auto" bg="gray.900" borderRadius="lg" p={4} border="1px solid" borderColor="gray.700">
                <Heading size="sm" mb={4} color="gray.300">🤖 AI Decisions (Insider & Technicals)</Heading>
                <Table variant="simple" size="sm">
                    <Thead>
                        <Tr>
                            <Th color="gray.400">Asset</Th>
                            <Th color="gray.400">Price</Th>
                            <Th color="gray.400">Action</Th>
                            <Th color="gray.400">Reasoning</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {scanResults.map((row: any, i: number) => (
                            <Tr key={i} _hover={{ bg: "gray.800" }}>
                                <Td fontWeight="bold">
                                    {row.asset}
                                    {row.source && <Badge ml={2} fontSize="0.6em" colorScheme={row.source.includes("SCANNER") ? "purple" : "blue"}>{row.source}</Badge>}
                                </Td>
                                <Td>${row.price?.toFixed(2) || "---"}</Td>
                                <Td>
                                    <Badge
                                        colorScheme={row.action === "BUY" || row.action === "SNIPE" ? "green" : row.action === "SELL" ? "red" : "gray"}
                                        px={2} py={1} borderRadius="md"
                                    >
                                        {row.action}
                                    </Badge>
                                </Td>
                                <Td color="gray.300" fontSize="sm" fontFamily="monospace">{row.reason}</Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
                {(!scanResults || scanResults.length === 0) && (
                    <Text textAlign="center" p={4} color="gray.500">No scan data available.</Text>
                )}
            </Box>

            {/* RAW INSIDER FEED SECTION */}
            <InsiderFeed />

            {/* US BRAIN FEED */}
            <BrainFeed />
        </Box>
    );
}

function BrainFeed() {
    const [logs, setLogs] = useState<string[]>([]);
    const endRef = React.useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await api.get("/api/us/logs");
                if (res.data && res.data.logs) {
                    setLogs(res.data.logs);
                }
            } catch (e) { }
        };
        fetchLogs();
        const interval = setInterval(fetchLogs, 2000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    return (
        <Box mt={8} bg="black" p={4} borderRadius="lg" border="1px solid" borderColor="green.500" height="250px" overflowY="auto" fontFamily="monospace">
            <Heading size="sm" mb={2} color="green.400" display="flex" alignItems="center" gap={2}>
                <Icon as={FiActivity} /> US Agent Live Thought Stream
            </Heading>
            <Box>
                {logs.length === 0 ? (
                    <Text color="gray.500">Waiting for neural link...</Text>
                ) : logs.map((log, i) => (
                    <Text key={i} color="gray.300" fontSize="xs" borderBottom="1px solid" borderColor="whiteAlpha.100" py={1}>
                        <Text as="span" color="green.500" mr={2}>&gt;</Text>
                        {log}
                    </Text>
                ))}
                <div ref={endRef} />
            </Box>
        </Box>
    )
}

function InsiderFeed() {
    const [candidates, setCandidates] = useState<string[]>([]);

    useEffect(() => {
        const fetchInsider = async () => {
            try {
                // Fetch from US Agent Scanner Endpoint
                const res = await api.get("/api/us/scanner/insider");
                if (res.data && res.data.candidates) {
                    setCandidates(res.data.candidates);
                }
            } catch (e) { }
        };
        fetchInsider();
        const interval = setInterval(fetchInsider, 10000); // 10s Refresh
        return () => clearInterval(interval);
    }, []);

    if (candidates.length === 0) {
        return (
            <Box mt={8} bg="gray.800" p={5} borderRadius="lg" borderLeft="4px solid" borderColor="gray.600">
                <Heading size="sm" mb={2} color="gray.400">🕵️ Raw Open Insider Feed</Heading>
                <Text fontSize="sm" color="gray.500" fontStyle="italic">
                    Scanning Complete: No "Cluster Buys" found in the last scan.
                    The scanner checks for multiple insider purchases within the last 72 hours.
                </Text>
            </Box>
        );
    }

    return (
        <Box mt={8} bg="gray.800" p={5} borderRadius="lg" borderLeft="4px solid" borderColor="purple.500">
            <Heading size="sm" mb={2} color="purple.300">🕵️ Raw Open Insider Feed</Heading>
            <Text fontSize="xs" color="gray.400" mb={3}>
                These tickers were detected by the scraper as having recent "Cluster Buys".
                The AI analyzes these candidates above.
            </Text>
            <Flex wrap="wrap" gap={2}>
                {candidates.map((c, i) => (
                    <Badge key={i} colorScheme="purple" variant="solid" fontSize="md" p={1}>{c}</Badge>
                ))}
            </Flex>
        </Box>
    )
}

