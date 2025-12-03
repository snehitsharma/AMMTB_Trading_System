import { useState, useEffect } from 'react'
import axios from 'axios'
import {
    Box, Heading, VStack, Input, Button, HStack, Text, Separator
} from '@chakra-ui/react'

export default function SettingsPage() {
    const [settings, setSettings] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchSettings()
    }, [])

    const fetchSettings = async () => {
        try {
            const res = await axios.get('/api/ai/settings')
            setSettings(res.data)
            setLoading(false)
        } catch (e) {
            console.error("Failed to fetch settings", e)
            setLoading(false)
        }
    }

    const handleSave = async () => {
        try {
            await axios.post('/api/ai/settings', settings)
            alert("Settings Saved Successfully!")
        } catch (e) {
            alert("Failed to save settings.")
        }
    }

    const handleChange = (key: string, value: any) => {
        setSettings({ ...settings, [key]: value })
    }

    if (loading || !settings) return <Box p={8}>Loading Settings...</Box>

    return (
        <Box maxW="container.md">
            <Heading mb={6}>AI Configuration</Heading>

            <VStack align="stretch" gap={6} bg="gray.800" p={6} borderRadius="xl" border="1px solid" borderColor="gray.700">

                <Box>
                    <Heading size="sm" mb={4} color="blue.400">Risk Management</Heading>
                    <VStack gap={4} align="start">
                        <Box w="full">
                            <Text mb={1} fontWeight="medium">Max Positions</Text>
                            <Input
                                type="number"
                                value={settings.max_positions}
                                onChange={(e) => handleChange('max_positions', parseInt(e.target.value))}
                                bg="gray.900"
                            />
                            <Text fontSize="xs" color="gray.500">Maximum number of simultaneous assets to hold.</Text>
                        </Box>
                        <Box w="full">
                            <Text mb={1} fontWeight="medium">Risk Per Trade (%)</Text>
                            <Input
                                type="number"
                                step="0.01"
                                value={settings.risk_per_trade}
                                onChange={(e) => handleChange('risk_per_trade', parseFloat(e.target.value))}
                                bg="gray.900"
                            />
                        </Box>
                    </VStack>
                </Box>

                <Separator borderColor="gray.600" />

                <Box>
                    <Heading size="sm" mb={4} color="purple.400">Strategy Parameters</Heading>
                    <HStack gap={4}>
                        <Box w="full">
                            <Text mb={1} fontWeight="medium">RSI Buy Threshold</Text>
                            <Input
                                type="number"
                                value={settings.rsi_buy_threshold}
                                onChange={(e) => handleChange('rsi_buy_threshold', parseInt(e.target.value))}
                                bg="gray.900"
                            />
                        </Box>
                        <Box w="full">
                            <Text mb={1} fontWeight="medium">RSI Sell Threshold</Text>
                            <Input
                                type="number"
                                value={settings.rsi_sell_threshold}
                                onChange={(e) => handleChange('rsi_sell_threshold', parseInt(e.target.value))}
                                bg="gray.900"
                            />
                        </Box>
                    </HStack>
                    <HStack gap={4} mt={4}>
                        <Box w="full">
                            <Text mb={1} fontWeight="medium">Stop Loss (ATR Multiplier)</Text>
                            <Input
                                type="number"
                                step="0.1"
                                value={settings.stop_loss_atr_multiplier}
                                onChange={(e) => handleChange('stop_loss_atr_multiplier', parseFloat(e.target.value))}
                                bg="gray.900"
                            />
                        </Box>
                        <Box w="full">
                            <Text mb={1} fontWeight="medium">Take Profit (ATR Multiplier)</Text>
                            <Input
                                type="number"
                                step="0.1"
                                value={settings.take_profit_atr_multiplier}
                                onChange={(e) => handleChange('take_profit_atr_multiplier', parseFloat(e.target.value))}
                                bg="gray.900"
                            />
                        </Box>
                    </HStack>
                </Box>

                <Separator borderColor="gray.600" />

                <Box>
                    <Heading size="sm" mb={4} color="green.400">Intelligence Modules</Heading>
                    <VStack align="start" gap={4}>
                        <HStack justify="space-between" w="full">
                            <Text>Enable Sentiment Analysis (News/Insider)</Text>
                            <Button
                                size="xs"
                                colorPalette={settings.enable_sentiment ? "green" : "red"}
                                onClick={() => handleChange('enable_sentiment', !settings.enable_sentiment)}
                            >
                                {settings.enable_sentiment ? "ENABLED" : "DISABLED"}
                            </Button>
                        </HStack>
                        <HStack justify="space-between" w="full">
                            <Text>Enable EVT Risk Engine</Text>
                            <Button
                                size="xs"
                                colorPalette={settings.enable_risk_engine ? "green" : "red"}
                                onClick={() => handleChange('enable_risk_engine', !settings.enable_risk_engine)}
                            >
                                {settings.enable_risk_engine ? "ENABLED" : "DISABLED"}
                            </Button>
                        </HStack>
                    </VStack>
                </Box>

                <Button colorPalette="blue" size="lg" onClick={handleSave} mt={4}>
                    Save Configuration
                </Button>
            </VStack>
        </Box>
    )
}
