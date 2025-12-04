import { Box, Heading, SimpleGrid, Switch, Text, HStack, Icon, Badge } from "@chakra-ui/react";
import { FiCpu, FiUsers } from "react-icons/fi";
import { useEffect, useState } from "react";
import axios from "axios";

export default function StrategyPage() {
    const [toggles, setToggles] = useState<any>({});

    const refresh = async () => {
        try {
            const res = await axios.get("/api/ai/api/v1/strategies");
            setToggles(res.data);
        } catch (e) { console.error(e); }
    };

    const handleToggle = async (name: string, isChecked: boolean) => {
        setToggles({ ...toggles, [name]: isChecked }); // Optimistic UI update
        await axios.post("/api/ai/api/v1/strategies/toggle", { name, enabled: isChecked });
        refresh();
    };

    useEffect(() => { refresh(); }, []);

    return (
        <Box>
            <Heading mb={6}>Strategy Control Panel</Heading>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>

                {/* TECHNICAL ENGINE CARD */}
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor={toggles["TECHNICAL"] ? "blue.500" : "gray.700"}>
                    <HStack justify="space-between" mb={4}>
                        <HStack>
                            <Icon as={FiCpu} color="blue.400" boxSize={6} />
                            <Text fontWeight="bold" fontSize="lg">Technical Engine</Text>
                        </HStack>
                        <Switch
                            size="lg"
                            colorScheme="blue"
                            isChecked={!!toggles["TECHNICAL"]}
                            onChange={(e) => handleToggle("TECHNICAL", e.target.checked)}
                        />
                    </HStack>
                    <Text color="gray.400" mb={4}>
                        Algorithmic analysis using RSI (Momentum), MACD (Trend), and EMA crossovers. Best for volatile markets.
                    </Text>
                    <Badge colorScheme={toggles["TECHNICAL"] ? "green" : "gray"}>
                        {toggles["TECHNICAL"] ? "ACTIVE" : "DISABLED"}
                    </Badge>
                </Box>

                {/* INSIDER ENGINE CARD */}
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor={toggles["INSIDER"] ? "purple.500" : "gray.700"}>
                    <HStack justify="space-between" mb={4}>
                        <HStack>
                            <Icon as={FiUsers} color="purple.400" boxSize={6} />
                            <Text fontWeight="bold" fontSize="lg">Insider Tracking</Text>
                        </HStack>
                        <Switch
                            size="lg"
                            colorScheme="purple"
                            isChecked={!!toggles["INSIDER"]}
                            onChange={(e) => handleToggle("INSIDER", e.target.checked)}
                        />
                    </HStack>
                    <Text color="gray.400" mb={4}>
                        Monitors SEC Form 4 filings for CEO/CFO cluster buying events {'>'} $250k. High conviction setup.
                    </Text>
                    <Badge colorScheme={toggles["INSIDER"] ? "green" : "gray"}>
                        {toggles["INSIDER"] ? "ACTIVE" : "DISABLED"}
                    </Badge>
                </Box>

            </SimpleGrid>
        </Box>
    );
}
