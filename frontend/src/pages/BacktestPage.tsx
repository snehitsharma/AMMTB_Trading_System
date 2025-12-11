import { Box, Heading, SimpleGrid, Button, VStack, HStack, Text, Icon, Flex } from "@chakra-ui/react";
import { FiTrendingUp, FiTrendingDown, FiActivity } from "react-icons/fi";
import { useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function BacktestPage() {
    const [symbol, setSymbol] = useState("AAPL");
    const [strategy, setStrategy] = useState("TECHNICAL");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const runBacktest = async () => {
        setLoading(true);
        try {
            const res = await axios.post("/api/ai/api/v1/backtest", {
                symbol, strategy, days: 90
            });
            setResult(res.data);
        } catch (e) { console.error(e); }
        setLoading(false);
    };

    return (
        <Box>
            <Heading mb={6}>Strategy Time Machine</Heading>

            {/* CONTROLS */}
            <HStack mb={8} spacing={4}>
                <Box>
                    <select
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        style={{ padding: '8px', borderRadius: '4px', backgroundColor: '#2D3748', color: 'white', border: '1px solid #4A5568' }}
                    >
                        <option value="AAPL">AAPL</option>
                        <option value="NVDA">NVDA</option>
                        <option value="BTC/USD">BTC/USD</option>
                    </select>
                </Box>
                <Box>
                    <select
                        value={strategy}
                        onChange={(e) => setStrategy(e.target.value)}
                        style={{ padding: '8px', borderRadius: '4px', backgroundColor: '#2D3748', color: 'white', border: '1px solid #4A5568' }}
                    >
                        <option value="TECHNICAL">Technical (RSI/MACD)</option>
                        <option value="INSIDER">Insider Momentum</option>
                    </select>
                </Box>
                <Button colorScheme="cyan" isLoading={loading} onClick={runBacktest} leftIcon={<Icon as={FiActivity} />}>
                    Run Simulation
                </Button>
            </HStack>

            {/* RESULTS */}
            {result && (
                <VStack spacing={8} align="stretch">
                    <SimpleGrid columns={3} spacing={6}>
                        <Box p={5} bg="gray.800" borderRadius="lg">
                            <VStack align="start" spacing={1}>
                                <Text color="gray.400">Total Return</Text>
                                <Text fontSize="2xl" fontWeight="bold" color={result.metrics.return_pct >= 0 ? "green.400" : "red.400"}>
                                    {result.metrics.return_pct}%
                                </Text>
                                <Flex align="center" gap={2} color="gray.500" fontSize="sm">
                                    <Icon as={result.metrics.return_pct >= 0 ? FiTrendingUp : FiTrendingDown} /> 90 Days
                                </Flex>
                            </VStack>
                        </Box>
                        <Box p={5} bg="gray.800" borderRadius="lg">
                            <VStack align="start" spacing={1}>
                                <Text color="gray.400">Win Rate</Text>
                                <Text fontSize="2xl" fontWeight="bold">{result.metrics.win_rate}%</Text>
                                <Text color="gray.500" fontSize="sm">{result.metrics.total_trades} Trades</Text>
                            </VStack>
                        </Box>
                        <Box p={5} bg="gray.800" borderRadius="lg">
                            <VStack align="start" spacing={1}>
                                <Text color="gray.400">Max Drawdown</Text>
                                <Text fontSize="2xl" fontWeight="bold" color="red.300">{result.metrics.max_drawdown}%</Text>
                            </VStack>
                        </Box>
                    </SimpleGrid>

                    {/* CHART */}
                    <Box h="400px" bg="gray.800" p={4} borderRadius="lg">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={result.equity_curve}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="date" stroke="#888" />
                                <YAxis stroke="#888" domain={['auto', 'auto']} />
                                <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none' }} />
                                <Line type="monotone" dataKey="equity" stroke="#00bcd4" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </Box>
                </VStack>
            )}
        </Box>
    );
}
