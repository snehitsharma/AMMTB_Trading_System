import { Box, SimpleGrid, Text, Badge, Icon, Flex, Tooltip } from "@chakra-ui/react";
import { FiCheckCircle, FiXCircle, FiCpu, FiShield, FiDollarSign } from "react-icons/fi";
import { useEffect, useState } from "react";
import api from "../api";

export default function AgentStatus() {
    const [hodlHealth, setHodlHealth] = useState<any>(null);
    const [usHealth, setUsHealth] = useState<any>(null);

    const fetchHealth = async () => {
        try {
            const [hRes, uRes] = await Promise.allSettled([
                api.get("/api/hodl/health"),
                api.get("/api/us/health")
            ]);

            if (hRes.status === "fulfilled") setHodlHealth(hRes.value.data);
            if (uRes.status === "fulfilled") setUsHealth(uRes.value.data);
        } catch (e) {
            console.error("Health Check Failed", e);
        }
    };

    useEffect(() => {
        fetchHealth();
        const interval = setInterval(fetchHealth, 10000); // Check every 10s
        return () => clearInterval(interval);
    }, []);

    const StatusRow = ({ label, status, tooltip }: { label: string, status: string | boolean, tooltip?: string }) => {
        const isOk = status === "ok" || status === true;
        const color = isOk ? "green.400" : "red.400";
        const icon = isOk ? FiCheckCircle : FiXCircle;

        return (
            <Flex justify="space-between" align="center" mb={1}>
                <Tooltip label={tooltip} hasArrow>
                    <Text fontSize="xs" color="gray.400" borderBottom={tooltip ? "1px dotted" : "none"}>{label}</Text>
                </Tooltip>
                <Flex align="center" gap={1}>
                    <Icon as={icon} color={color} boxSize={3} />
                    <Text fontSize="xs" fontWeight="bold" color={color}>{isOk ? "OK" : "FAIL"}</Text>
                </Flex>
            </Flex>
        );
    }

    return (
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mb={6}>
            {/* HODL AGENT */}
            <Box bg="gray.900" p={4} borderRadius="lg" borderTop="4px solid" borderColor="purple.500">
                <Flex justify="space-between" mb={3}>
                    <Flex align="center" gap={2}>
                        <Icon as={FiCpu} color="purple.400" />
                        <Text fontWeight="bold" color="white">HODL Agent</Text>
                    </Flex>
                    <Badge colorScheme={hodlHealth?.mode === "LIVE" ? "red" : "gray"}>
                        {hodlHealth?.mode || "OFFLINE"}
                    </Badge>
                </Flex>

                {hodlHealth ? (
                    <Box>
                        <StatusRow label="Solana Wallet" status={hodlHealth.solana_key_loaded} tooltip="Is Private Key Loaded?" />
                        <StatusRow label="Jupiter API" status={hodlHealth.jupiter_status} />
                        <StatusRow label="DexScreener" status={hodlHealth.dexscreener_status} />
                        <StatusRow label="RugCheck.xyz" status={hodlHealth.rugcheck_status} />
                    </Box>
                ) : (
                    <Text fontSize="xs" color="gray.500">Connecting...</Text>
                )}
            </Box>

            {/* US AGENT */}
            <Box bg="gray.900" p={4} borderRadius="lg" borderTop="4px solid" borderColor="blue.500">
                <Flex justify="space-between" mb={3}>
                    <Flex align="center" gap={2}>
                        <Icon as={FiDollarSign} color="blue.400" />
                        <Text fontWeight="bold" color="white">US Stock Agent</Text>
                    </Flex>
                    <Flex gap={2}>
                        {usHealth?.auto_buy === "True" && <Badge colorScheme="green">AUTO-BUY</Badge>}
                        <Badge colorScheme={usHealth?.mode === "LIVE" ? "red" : "gray"}>
                            {usHealth?.mode || "OFFLINE"}
                        </Badge>
                    </Flex>
                </Flex>

                {usHealth ? (
                    <Box>
                        <StatusRow label="Alpaca Connection" status={usHealth.alpaca_status} />
                        <StatusRow label="Insider Scanner" status={usHealth.scanner_status} />
                    </Box>
                ) : (
                    <Text fontSize="xs" color="gray.500">Connecting...</Text>
                )}
            </Box>
        </SimpleGrid>
    );
}
