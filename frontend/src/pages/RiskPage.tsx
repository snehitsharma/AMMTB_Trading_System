import React, { useState, useEffect } from 'react';
import {
    Box, SimpleGrid, Text, Stat,
    Progress, Badge, Card, Heading, Flex, Icon
} from '@chakra-ui/react';
import { FiShield, FiAlertTriangle, FiCheckCircle, FiActivity } from 'react-icons/fi';
import axios from 'axios';

const RiskPage = () => {
    const [metrics, setMetrics] = useState<any>(null);

    const fetchRisk = async () => {
        try {
            const res = await axios.get("/api/ai/risk");
            setMetrics(res.data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchRisk();
        const interval = setInterval(fetchRisk, 5000);
        return () => clearInterval(interval);
    }, []);

    if (!metrics) return <Box p={5}><Text>Loading Risk Desk...</Text></Box>;

    const ddPct = metrics.daily_drawdown * 100;
    const expPct = metrics.current_exposure * 100;
    const cashPct = metrics.cash_buffer * 100;

    const isKillSwitch = metrics.kill_switch;

    return (
        <Box p={5}>
            <Flex align="center" mb={6}>
                <Icon as={FiShield} fontSize="3xl" mr={3} color="blue.400" />
                <Heading size="lg">Institutional Risk Desk</Heading>
                {isKillSwitch && (
                    <Badge ml={4} colorScheme="red" fontSize="xl" p={2} borderRadius="md">
                        KILL SWITCH ACTIVE
                    </Badge>
                )}
            </Flex>

            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
                {/* Drawdown Gauge */}
                <Card.Root bg="gray.800" borderTop="4px" borderColor={ddPct > 2.5 ? "red.500" : "green.500"}>
                    <Card.Body>
                        <Stat.Root>
                            <Stat.Label>Daily Drawdown</Stat.Label>
                            <Stat.ValueText>{ddPct.toFixed(2)}%</Stat.ValueText>
                            <Stat.HelpText>Limit: 3.00%</Stat.HelpText>
                        </Stat.Root>
                        <Progress
                            value={ddPct}
                            max={3}
                            colorScheme={ddPct > 2 ? "red" : "green"}
                            size="sm"
                            mt={3}
                            borderRadius="full"
                        />
                    </Card.Body>
                </Card.Root>

                {/* Exposure Gauge */}
                <Card.Root bg="gray.800" borderTop="4px" borderColor={expPct > 20 ? "orange.500" : "blue.500"}>
                    <Card.Body>
                        <Stat.Root>
                            <Stat.Label>Total Exposure</Stat.Label>
                            <Stat.ValueText>{expPct.toFixed(2)}%</Stat.ValueText>
                            <Stat.HelpText>Limit: 25.00%</Stat.HelpText>
                        </Stat.Root>
                        <Progress
                            value={expPct}
                            max={25}
                            colorScheme={expPct > 20 ? "orange" : "blue"}
                            size="sm"
                            mt={3}
                            borderRadius="full"
                        />
                    </Card.Body>
                </Card.Root>

                {/* Cash Buffer */}
                <Card.Root bg="gray.800" borderTop="4px" borderColor="purple.500">
                    <Card.Body>
                        <Stat.Root>
                            <Stat.Label>Cash Buffer</Stat.Label>
                            <Stat.ValueText>{cashPct.toFixed(2)}%</Stat.ValueText>
                            <Stat.HelpText>Target: &gt; 75%</Stat.HelpText>
                        </Stat.Root>
                        <Progress
                            value={cashPct}
                            max={100}
                            colorScheme="purple"
                            size="sm"
                            mt={3}
                            borderRadius="full"
                        />
                    </Card.Body>
                </Card.Root>
            </SimpleGrid>

            {/* Active Rules */}
            <Box bg="gray.900" p={6} borderRadius="lg">
                <Heading size="md" mb={4}>Active Risk Protocols (Feature 6)</Heading>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <Flex align="center" bg="gray.800" p={3} borderRadius="md">
                        <Icon as={FiCheckCircle} color="green.400" mr={3} />
                        <Box>
                            <Text fontWeight="bold">Position Sizing</Text>
                            <Text fontSize="sm" color="gray.400">Fixed at 5% per trade</Text>
                        </Box>
                    </Flex>
                    <Flex align="center" bg="gray.800" p={3} borderRadius="md">
                        <Icon as={FiCheckCircle} color="green.400" mr={3} />
                        <Box>
                            <Text fontWeight="bold">Max Exposure</Text>
                            <Text fontSize="sm" color="gray.400">Capped at 25% of Equity</Text>
                        </Box>
                    </Flex>
                    <Flex align="center" bg="gray.800" p={3} borderRadius="md">
                        <Icon as={FiCheckCircle} color="green.400" mr={3} />
                        <Box>
                            <Text fontWeight="bold">Kill Switch</Text>
                            <Text fontSize="sm" color="gray.400">Triggered at 3% Daily Loss</Text>
                        </Box>
                    </Flex>
                    <Flex align="center" bg="gray.800" p={3} borderRadius="md">
                        <Icon as={FiCheckCircle} color="green.400" mr={3} />
                        <Box>
                            <Text fontWeight="bold">Hard Stops</Text>
                            <Text fontSize="sm" color="gray.400">-5% SL / +10% TP</Text>
                        </Box>
                    </Flex>
                </SimpleGrid>
            </Box>
        </Box>
    );
};

export default RiskPage;
