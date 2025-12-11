import { Box, Heading, VStack, HStack, Text, Switch, Divider, Button, Input, FormControl, FormLabel, Select, useColorMode } from "@chakra-ui/react";
import { useState } from "react";

export default function SettingsPage() {
    const { colorMode, toggleColorMode } = useColorMode();
    const [riskLimit, setRiskLimit] = useState("10");
    const [apiKey, setApiKey] = useState("****************");

    return (
        <Box>
            <Heading mb={6}>System Configuration</Heading>

            <VStack spacing={8} align="stretch">

                {/* GENERAL SETTINGS */}
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="gray.700">
                    <Heading size="md" mb={4}>General</Heading>
                    <VStack spacing={4} align="stretch">
                        <HStack justify="space-between">
                            <Text>Dark Mode</Text>
                            <Switch isChecked={colorMode === "dark"} onChange={toggleColorMode} />
                        </HStack>
                        <Divider borderColor="gray.700" />
                        <HStack justify="space-between">
                            <Text>Notifications</Text>
                            <Switch defaultChecked />
                        </HStack>
                    </VStack>
                </Box>

                {/* RISK PARAMETERS */}
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="gray.700">
                    <Heading size="md" mb={4}>Risk Management</Heading>
                    <VStack spacing={4} align="stretch">
                        <FormControl>
                            <FormLabel>Max Position Size (% of Equity)</FormLabel>
                            <Select value={riskLimit} onChange={(e) => setRiskLimit(e.target.value)} bg="gray.800">
                                <option value="5">Conservative (5%)</option>
                                <option value="10">Balanced (10%)</option>
                                <option value="20">Aggressive (20%)</option>
                            </Select>
                        </FormControl>
                        <FormControl>
                            <FormLabel>Daily Loss Limit (%)</FormLabel>
                            <Input type="number" defaultValue={3} bg="gray.800" />
                        </FormControl>
                        <Button colorScheme="blue" w="full">Save Risk Settings</Button>
                    </VStack>
                </Box>

                {/* API KEYS (Masked) */}
                <Box p={6} bg="gray.900" borderRadius="xl" border="1px solid" borderColor="gray.700">
                    <Heading size="md" mb={4}>API Credentials</Heading>
                    <VStack spacing={4} align="stretch">
                        <FormControl>
                            <FormLabel>Alpaca API Key</FormLabel>
                            <Input value={apiKey} isReadOnly bg="gray.800" />
                        </FormControl>
                        <Button colorScheme="red" variant="outline" w="full">Reset Keys</Button>
                    </VStack>
                </Box>

            </VStack>
        </Box>
    );
}
