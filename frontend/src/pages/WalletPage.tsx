import { Box, Heading, Text, VStack, HStack, Button, Badge, Table, Thead, Tbody, Tr, Th, Td, Stat, StatLabel, StatNumber, StatHelpText, Icon, SimpleGrid, Alert, AlertIcon } from "@chakra-ui/react";
import { FiCheck, FiX } from "react-icons/fi";
import { useEffect, useState } from "react";
import axios from "axios";

export default function WalletPage() {
    const [balance, setBalance] = useState(0);
    const [transactions, setTransactions] = useState([]);
    const [notification, setNotification] = useState<{ status: "success" | "error" | "info" | "warning", msg: string } | null>(null);

    const fetchData = async () => {
        try {
            const balRes = await axios.get("/api/orchestrator/wallet/balance");
            setBalance(balRes.data.balance || 0);

            const txRes = await axios.get("/api/orchestrator/transactions");
            setTransactions(txRes.data.transactions || []);
        } catch (e) {
            console.error("Wallet Fetch Error", e);
        }
    };

    const handleAction = async (id: string, action: "APPROVE" | "REJECT") => {
        try {
            await axios.patch(`/api/orchestrator/transactions/${id}`, { action });
            setNotification({ status: "success", msg: `Transaction ${action}D` });
            fetchData();
        } catch (e) {
            setNotification({ status: "error", msg: "Action Failed" });
        }
        setTimeout(() => setNotification(null), 3000);
    };

    useEffect(() => { fetchData(); }, []);

    return (
        <Box>
            <Heading mb={6}>Fund Management</Heading>

            {notification && (
                <Alert status={notification.status} mb={6} borderRadius="md">
                    <AlertIcon />
                    {notification.msg}
                </Alert>
            )}

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8} mb={8}>
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="green.500">
                    <Stat>
                        <StatLabel color="gray.400">Available Liquidity</StatLabel>
                        <StatNumber fontSize="3xl">${balance.toLocaleString()}</StatNumber>
                        <StatHelpText>Ready for deployment</StatHelpText>
                    </Stat>
                </Box>

                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="gray.700">
                    <Heading size="md" mb={4}>Pending Approvals</Heading>
                    {transactions.filter((t: any) => t.status === "PENDING").length === 0 ? (
                        <Text color="gray.500">No pending requests.</Text>
                    ) : (
                        <VStack align="stretch">
                            {transactions.filter((t: any) => t.status === "PENDING").map((t: any) => (
                                <HStack key={t.id} justify="space-between" bg="gray.800" p={3} borderRadius="md">
                                    <VStack align="start" spacing={0}>
                                        <Text fontWeight="bold">${t.amount}</Text>
                                        <Text fontSize="xs" color="gray.400">{t.market}</Text>
                                    </VStack>
                                    <HStack>
                                        <Button size="sm" colorScheme="green" onClick={() => handleAction(t.id, "APPROVE")}><Icon as={FiCheck} /></Button>
                                        <Button size="sm" colorScheme="red" onClick={() => handleAction(t.id, "REJECT")}><Icon as={FiX} /></Button>
                                    </HStack>
                                </HStack>
                            ))}
                        </VStack>
                    )}
                </Box>
            </SimpleGrid>

            <Box overflowX="auto" bg="gray.900" p={4} borderRadius="xl" border="1px solid" borderColor="gray.700">
                <Table variant="simple">
                    <Thead><Tr><Th>ID</Th><Th>Type</Th><Th>Amount</Th><Th>Status</Th></Tr></Thead>
                    <Tbody>
                        {transactions.map((t: any) => (
                            <Tr key={t.id}>
                                <Td fontSize="xs" fontFamily="monospace">{t.id.substring(0, 8)}</Td>
                                <Td><Badge>{t.type}</Badge></Td>
                                <Td>${t.amount}</Td>
                                <Td><Badge>{t.status}</Badge></Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            </Box>
        </Box>
    );
}
