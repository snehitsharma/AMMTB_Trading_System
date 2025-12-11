import { Box, Heading, VStack, HStack, Text, Select, Button, SimpleGrid, Spinner, Badge, Stat, StatLabel, StatNumber, StatHelpText, StatArrow } from "@chakra-ui/react";
import { useState } from "react";
import axios from "axios";
import { FiCpu, FiCheckCircle } from "react-icons/fi";

export default function OptimizePage() {
    const [symbol, setSymbol] = useState("BTC/USD");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);

    const runOptimization = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await axios.post("http://localhost:8004/api/v1/optimize", { symbol });
            setResult(res.data);
        } catch (e) {
            console.error(e);
        }
        setLoading(false);
    };

    return (
        <Box>
            <Heading mb={6}>Strategy Auto-Tuner 🛠️</Heading>

            <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="gray.700" mb={8}>
                <VStack align="stretch" spacing={4}>
                    <Text color="gray.400">Select an asset to find the mathematically perfect parameters for current market conditions.</Text>
                    <HStack>
                        <Select value={symbol} onChange={(e) => setSymbol(e.target.value)} bg="gray.800" maxW="300px">
                            <option value="BTC/USD">Bitcoin (BTC/USD)</option>
                            <option value="ETH/USD">Ethereum (ETH/USD)</option>
                            <option value="SOL/USD">Solana (SOL/USD)</option>
                            <option value="AAPL">Apple (AAPL)</option>
                            <option value="NVDA">Nvidia (NVDA)</option>
                            <option value="TSLA">Tesla (TSLA)</option>
                        </Select>
                        <Button
                            leftIcon={loading ? <Spinner size="sm" /> : <FiCpu />}
                            colorScheme="blue"
                            onClick={runOptimization}
                            isDisabled={loading}
                        >
                            {loading ? "Optimizing..." : "Run Auto-Tune"}
                        </Button>
                    </HStack>
                </VStack>
            </Box>

            {result && (
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
                    {/* BASELINE */}
                    <Box p={6} bg="gray.800" borderRadius="xl" border="1px dashed" borderColor="gray.600" opacity={0.7}>
                        <Heading size="md" mb={4} color="gray.400">Current Strategy</Heading>
                        <VStack align="start" spacing={2}>
                            <Text>RSI Buy: <Badge>{result.baseline.params.rsi_buy}</Badge></Text>
                            <Text>Stop Loss: <Badge>{result.baseline.params.sl_mult}x ATR</Badge></Text>
                            <Text>Take Profit: <Badge>{result.baseline.params.tp_mult}x ATR</Badge></Text>
                            <Stat mt={4}>
                                <StatLabel>Simulated Profit</StatLabel>
                                <StatNumber>${result.baseline.profit.toFixed(2)}</StatNumber>
                            </Stat>
                        </VStack>
                    </Box>

                    {/* OPTIMIZED */}
                    <Box p={6} bg="blue.900" borderRadius="xl" border="1px solid" borderColor="blue.400">
                        <HStack justify="space-between" mb={4}>
                            <Heading size="md" color="blue.200">AI Optimized</Heading>
                            <Badge colorScheme="green" fontSize="1em">{result.improvement}</Badge>
                        </HStack>
                        <VStack align="start" spacing={2}>
                            <Text>RSI Buy: <Badge colorScheme="blue">{result.optimized.params.rsi_buy}</Badge></Text>
                            <Text>Stop Loss: <Badge colorScheme="blue">{result.optimized.params.sl_mult}x ATR</Badge></Text>
                            <Text>Take Profit: <Badge colorScheme="blue">{result.optimized.params.tp_mult}x ATR</Badge></Text>
                            <Stat mt={4}>
                                <StatLabel>Potential Profit</StatLabel>
                                <StatNumber color="green.300">${result.optimized.profit.toFixed(2)}</StatNumber>
                                <StatHelpText>
                                    <StatArrow type="increase" />
                                    vs Baseline
                                </StatHelpText>
                            </Stat>
                            <Button w="full" mt={4} colorScheme="green" leftIcon={<FiCheckCircle />}>
                                Apply Settings
                            </Button>
                        </VStack>
                    </Box>
                </SimpleGrid>
            )}
        </Box>
    );
}
