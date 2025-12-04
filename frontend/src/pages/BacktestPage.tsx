import React, { useState } from 'react';
import {
    Box, Button, Input, Select, SimpleGrid, Text, Table, Thead, Tbody, Tr, Th, Td,
    Stat, StatLabel, StatNumber, StatHelpText, StatArrow, Badge, Spinner
} from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const BacktestPage = () => {
    const [symbol, setSymbol] = useState("AAPL");
    const [strategy, setStrategy] = useState("TECHNICAL");
    const [days, setDays] = useState(180);
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<any>(null);

    const runBacktest = async () => {
        setLoading(true);
        setResults(null);
        try {
            const res = await axios.post("/api/ai/api/v1/backtest", { symbol, strategy, days });
            setResults(res.data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box p={5}>
            <Text fontSize="2xl" mb={5} fontWeight="bold">⏳ Time Machine (Backtester)</Text>

            {/* Controls */}
            <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4} mb={8}>
                <Input placeholder="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
                <Select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                    <option value="TECHNICAL">Technical Engine</option>
                    <option value="INSIDER">Insider Tracking</option>
                </Select>
                <Select value={days} onChange={(e) => setDays(parseInt(e.target.value))}>
                    <option value={30}>Last 30 Days</option>
                    <option value={90}>Last 90 Days</option>
                    <option value={180}>Last 6 Months</option>
                    <option value={365}>Last 1 Year</option>
                </Select>
                <Button colorScheme="blue" onClick={runBacktest} isLoading={loading}>Run Simulation</Button>
            </SimpleGrid>

            {/* Results */}
            {results && !results.error && (
                <>
                    {/* Metrics */}
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={5} mb={8}>
                        <Stat p={4} shadow="md" borderRadius="md" bg="gray.800">
                            <StatLabel>Total Return</StatLabel>
                            <StatNumber color={results.metrics.total_return >= 0 ? "green.400" : "red.400"}>
                                {results.metrics.total_return}%
                            </StatNumber>
                            <StatHelpText>
                                <StatArrow type={results.metrics.total_return >= 0 ? "increase" : "decrease"} />
                                Initial $100k
                            </StatHelpText>
                        </Stat>
                        <Stat p={4} shadow="md" borderRadius="md" bg="gray.800">
                            <StatLabel>Win Rate</StatLabel>
                            <StatNumber>{results.metrics.win_rate}%</StatNumber>
                            <StatHelpText>{results.metrics.trades_count} Trades</StatHelpText>
                        </Stat>
                        <Stat p={4} shadow="md" borderRadius="md" bg="gray.800">
                            <StatLabel>Max Drawdown</StatLabel>
                            <StatNumber color="red.400">{results.metrics.max_drawdown}%</StatNumber>
                        </Stat>
                        <Stat p={4} shadow="md" borderRadius="md" bg="gray.800">
                            <StatLabel>Strategy</StatLabel>
                            <StatNumber fontSize="lg">{results.strategy}</StatNumber>
                            <StatHelpText>{results.symbol}</StatHelpText>
                        </Stat>
                    </SimpleGrid>

                    {/* Chart */}
                    <Box h="400px" bg="gray.900" p={4} borderRadius="md" mb={8}>
                        <Text mb={2}>Equity Curve</Text>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={results.equity_curve}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="date" stroke="#888" tickFormatter={(str) => new Date(str).toLocaleDateString()} />
                                <YAxis stroke="#888" domain={['auto', 'auto']} />
                                <Tooltip contentStyle={{ backgroundColor: '#1A202C', border: 'none' }} />
                                <Line type="monotone" dataKey="equity" stroke="#48BB78" strokeWidth={2} dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </Box>

                    {/* Trade Log */}
                    <Box overflowX="auto">
                        <Text fontSize="xl" mb={4}>Trade Log</Text>
                        <Table variant="simple" size="sm">
                            <Thead>
                                <Tr>
                                    <Th>Date</Th>
                                    <Th>Type</Th>
                                    <Th isNumeric>Price</Th>
                                    <Th isNumeric>Qty</Th>
                                    <Th isNumeric>Value</Th>
                                    <Th isNumeric>PnL</Th>
                                </Tr>
                            </Thead>
                            <Tbody>
                                {results.trades.map((t: any, i: number) => (
                                    <Tr key={i}>
                                        <Td>{new Date(t.date).toLocaleDateString()}</Td>
                                        <Td>
                                            <Badge colorScheme={t.type === "BUY" ? "green" : "red"}>{t.type}</Badge>
                                        </Td>
                                        <Td isNumeric>${t.price.toFixed(2)}</Td>
                                        <Td isNumeric>{t.qty}</Td>
                                        <Td isNumeric>${t.value.toFixed(2)}</Td>
                                        <Td isNumeric color={t.pnl > 0 ? "green.400" : t.pnl < 0 ? "red.400" : "white"}>
                                            {t.pnl ? `$${t.pnl.toFixed(2)}` : "-"}
                                        </Td>
                                    </Tr>
                                ))}
                            </Tbody>
                        </Table>
                    </Box>
                </>
            )}

            {results && results.error && (
                <Text color="red.500">Error: {results.error}</Text>
            )}
        </Box>
    );
};

export default BacktestPage;
