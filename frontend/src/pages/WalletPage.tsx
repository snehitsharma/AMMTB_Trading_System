import React, { useState, useEffect } from 'react';
import {
    Box, SimpleGrid, Text, Stat, StatLabel, StatNumber, StatHelpText,
    Button, Card, CardBody, Heading, Flex, Icon, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton, useToast
} from '@chakra-ui/react';
import { FiDollarSign, FiCheck, FiX, FiClock } from 'react-icons/fi';
import axios from 'axios';

const WalletPage = () => {
    const [balance, setBalance] = useState(0);
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const toast = useToast();

    const fetchData = async () => {
        try {
            const balRes = await axios.get("/api/orchestrator/api/v1/wallet/balance");
            setBalance(balRes.data.balance);

            const logsRes = await axios.get("/api/orchestrator/api/v1/logs");
            setTransactions(logsRes.data.transactions);
            setLoading(false);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleAction = async (id: string, action: string) => {
        try {
            await axios.patch(`/api/orchestrator/api/v1/transactions/${id}`, { action });
            toast({
                title: `Transaction ${action === "APPROVE" ? "Approved" : "Rejected"}`,
                status: action === "APPROVE" ? "success" : "error",
                duration: 3000,
                isClosable: true,
            });
            fetchData();
        } catch (e) {
            toast({ title: "Error updating transaction", status: "error" });
        }
    };

    const pending = transactions.filter((t: any) => t.status === "PENDING_APPROVAL");
    const history = transactions.filter((t: any) => t.status !== "PENDING_APPROVAL");

    return (
        <Box p={5}>
            <Flex align="center" mb={6}>
                <Icon as={FiDollarSign} fontSize="3xl" mr={3} color="green.400" />
                <Heading size="lg">Admin Banking</Heading>
            </Flex>

            {/* Master Balance */}
            <Card bg="gray.800" borderTop="4px" borderColor="green.500" mb={8}>
                <CardBody>
                    <Stat>
                        <StatLabel fontSize="lg">Available Liquidity</StatLabel>
                        <StatNumber fontSize="4xl">${balance.toLocaleString()}</StatNumber>
                        <StatHelpText>Free Cash (Deposits - Withdrawals)</StatHelpText>
                    </Stat>
                </CardBody>
            </Card>

            {/* Pending Inbox */}
            {pending.length > 0 && (
                <Box mb={8}>
                    <Heading size="md" mb={4} color="orange.300">Pending Approvals ({pending.length})</Heading>
                    <Card bg="gray.800">
                        <CardBody>
                            <Table variant="simple">
                                <Thead>
                                    <Tr>
                                        <Th>ID</Th>
                                        <Th>Type</Th>
                                        <Th>Amount</Th>
                                        <Th>Market</Th>
                                        <Th>Time</Th>
                                        <Th>Action</Th>
                                    </Tr>
                                </Thead>
                                <Tbody>
                                    {pending.map((t: any) => (
                                        <Tr key={t.id}>
                                            <Td fontSize="xs" fontFamily="monospace">{t.id.substring(0, 8)}...</Td>
                                            <Td><Badge colorScheme="purple">{t.type}</Badge></Td>
                                            <Td fontWeight="bold">${t.amount.toLocaleString()}</Td>
                                            <Td>{t.market}</Td>
                                            <Td fontSize="sm">{new Date(t.timestamp).toLocaleTimeString()}</Td>
                                            <Td>
                                                <IconButton
                                                    aria-label="Approve"
                                                    icon={<FiCheck />}
                                                    colorScheme="green"
                                                    size="sm"
                                                    mr={2}
                                                    onClick={() => handleAction(t.id, "APPROVE")}
                                                />
                                                <IconButton
                                                    aria-label="Reject"
                                                    icon={<FiX />}
                                                    colorScheme="red"
                                                    size="sm"
                                                    onClick={() => handleAction(t.id, "REJECT")}
                                                />
                                            </Td>
                                        </Tr>
                                    ))}
                                </Tbody>
                            </Table>
                        </CardBody>
                    </Card>
                </Box>
            )}

            {/* Transaction History */}
            <Box>
                <Heading size="md" mb={4}>Transaction History</Heading>
                <Card bg="gray.800">
                    <CardBody>
                        <Table variant="simple" size="sm">
                            <Thead>
                                <Tr>
                                    <Th>Status</Th>
                                    <Th>Type</Th>
                                    <Th>Amount</Th>
                                    <Th>Time</Th>
                                </Tr>
                            </Thead>
                            <Tbody>
                                {history.map((t: any) => (
                                    <Tr key={t.id}>
                                        <Td>
                                            <Badge
                                                colorScheme={
                                                    t.status === "APPROVED" ? "green" :
                                                        t.status === "REJECTED" ? "red" : "gray"
                                                }
                                            >
                                                {t.status}
                                            </Badge>
                                        </Td>
                                        <Td>{t.type}</Td>
                                        <Td>${t.amount.toLocaleString()}</Td>
                                        <Td>{new Date(t.timestamp).toLocaleString()}</Td>
                                    </Tr>
                                ))}
                            </Tbody>
                        </Table>
                    </CardBody>
                </Card>
            </Box>
        </Box>
    );
};

export default WalletPage;
