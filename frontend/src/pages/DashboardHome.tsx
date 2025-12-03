import { useState, useEffect, useMemo } from 'react'
import axios from 'axios'
import {
    Box, Flex, Heading, Badge, Stat,
    SimpleGrid, VStack, HStack, Avatar, Button, Text
} from '@chakra-ui/react'
import { ActivityLog } from '../components/ActivityLog'
import { WithdrawModal } from '../components/WithdrawModal'
import TradeModal from '../components/TradeModal'

interface AccountSummary {
    broker: string
    cash_balance: number
    unrealized_pl: number
    total_equity: number
}

interface Quote {
    symbol: string
    price: number
    currency: string
}

interface AgentData {
    summary: AccountSummary | null
    quote: Quote | null
}

interface ScanResult {
    asset: string
    price: number
    action: string
    reason: string
}

interface AISignal {
    regime: string
    signal: string
    confidence: number
    scan_results?: ScanResult[]
}

export default function DashboardHome() {
    const [usData, setUsData] = useState<AgentData>({ summary: null, quote: null })
    const [cryptoData, setCryptoData] = useState<AgentData>({ summary: null, quote: null })
    const [indiaData, setIndiaData] = useState<AgentData>({ summary: null, quote: null })
    const [aiData, setAiData] = useState<AISignal | null>(null)


    const fetchUS = async () => {
        try {
            const summary = await axios.get('/api/us/account/summary')
            setUsData(prev => ({ ...prev, summary: summary.data }))
        } catch (e) { console.error(e) }
    }

    const fetchCrypto = async () => {
        try {
            const summary = await axios.get('/api/crypto/account/summary')
            const quote = await axios.get('/api/crypto/quote')
            setCryptoData({ summary: summary.data, quote: quote.data })
        } catch (e) { console.error(e) }
    }

    const fetchIndia = async () => {
        try {
            const summary = await axios.get('/api/india/account/summary')
            const quote = await axios.get('/api/india/quote')
            setIndiaData({ summary: summary.data, quote: quote.data })
        } catch (e) { console.error(e) }
    }

    const fetchAI = async () => {
        try {
            const res = await axios.get('/api/ai/signals')
            setAiData(res.data)
        } catch (e) { console.error(e) }
    }

    const buyUS = async () => {
        try {
            await axios.post('/api/us/trade', { symbol: 'AAPL', qty: 10, side: 'buy' })
            fetchUS()
        } catch (e) { alert('Trade Failed') }
    }

    const buyCrypto = async () => {
        try {
            await axios.post('/api/crypto/trade', { symbol: 'BTC/USD', qty: 0.01, side: 'buy' })
            fetchCrypto()
        } catch (e) { alert('Trade Failed') }
    }

    const buyIndia = async () => {
        try {
            await axios.post('/api/india/trade', { symbol: 'NIFTY', qty: 1, side: 'buy' })
            fetchIndia()
        } catch (e) { alert('Trade Failed') }
    }

    useEffect(() => {
        const interval = setInterval(() => {
            fetchUS()
            fetchCrypto()
            fetchIndia()
            fetchAI()
        }, 3000)

        // Initial fetch
        fetchUS()
        fetchCrypto()
        fetchIndia()
        fetchAI()

        return () => clearInterval(interval)
    }, [])

    // Calculate Total Equity Safely
    const totalEquityUSD = useMemo(() => {
        const us = usData.summary?.total_equity ? Number(usData.summary.total_equity) : 0;
        const crypto = cryptoData.summary?.total_equity ? Number(cryptoData.summary.total_equity) : 0;

        // safe conversion for India, treating offline as 0
        let india = 0;
        if (indiaData.summary?.total_equity) {
            india = Number(indiaData.summary.total_equity) / 84.0;
        }

        // Only show loading if US AND Crypto are BOTH missing
        if (!usData.summary && !cryptoData.summary) return null;

        // FIX: If US and Crypto are identical (same Alpaca account), don't double count
        // We assume if they are within 1% of each other and non-zero, they are the same.
        if (us > 0 && crypto > 0 && Math.abs(us - crypto) < 1.0) {
            return us + india;
        }

        return us + crypto + india;
    }, [usData, cryptoData, indiaData]);

    const getRegimeColor = (regime: string) => {
        if (regime === 'RISK_ON') return 'green'
        if (regime === 'RISK_OFF') return 'orange'
        return 'gray'
    }

    return (
        <Box>
            {/* HEADER */}
            <Flex justify="space-between" align="center" mb={10}>
                <Heading size="lg" bgGradient="linear(to-r, teal.400, blue.500)" bgClip="text">
                    AMMTB Terminal
                </Heading>
                <HStack>
                    <Button
                        colorPalette="red"
                        variant="solid"
                        size="sm"
                        onClick={async () => {
                            if (confirm("⚠️ EMERGENCY STOP: This will kill all system processes. Are you sure?")) {
                                try {
                                    await axios.post('/api/orchestrator/shutdown');
                                    alert("System Shutdown Initiated.");
                                } catch (e) {
                                    alert("Shutdown Failed (Orchestrator might be offline).");
                                }
                            }
                        }}
                    >
                        ⛔ STOP SYSTEM
                    </Button>
                    <TradeModal trigger={<Button size="sm" colorPalette="blue">⚡ Quick Trade</Button>} />
                    <WithdrawModal />
                    <Badge colorPalette="green" p={2} borderRadius="md">System Online</Badge>
                </HStack>
            </Flex>

            {/* AI COMMAND CENTER */}
            {aiData && (
                <Box
                    bg={`${getRegimeColor(aiData.regime)}.900`}
                    border="1px solid"
                    borderColor={`${getRegimeColor(aiData.regime)}.500`}
                    p={4}
                    borderRadius="xl"
                    mb={8}
                >
                    <Flex justify="space-between" align="center">
                        <VStack align="start" gap={0}>
                            <Text fontSize="sm" color="gray.400">MARKET REGIME</Text>
                            <Heading size="md" color={`${getRegimeColor(aiData.regime)}.300`}>
                                {aiData.regime}
                            </Heading>
                        </VStack>
                        <VStack align="end" gap={0}>
                            <Text fontSize="sm" color="gray.400">AI SIGNAL (Conf: {aiData.confidence})</Text>
                            <Heading size="md" color="white">
                                {aiData.signal}
                            </Heading>
                        </VStack>
                    </Flex>
                </Box>
            )}

            {/* TOTAL EQUITY CARD (HERO) */}
            <Box bg="gray.800" p={6} borderRadius="xl" shadow="2xl" mb={8} border="1px solid" borderColor="gray.700">
                <Stat.Root>
                    <Stat.Label color="gray.400">Total Net Worth (USD)</Stat.Label>
                    <Stat.ValueText fontSize="4xl" fontWeight="bold">
                        ${totalEquityUSD ? totalEquityUSD.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "Loading..."}
                    </Stat.ValueText>
                    <Stat.HelpText>
                        <Stat.UpIndicator /> Global Combined Equity
                    </Stat.HelpText>
                </Stat.Root>
            </Box>

            {/* MARKETS GRID */}
            <SimpleGrid columns={{ base: 1, md: 3 }} gap={8}>

                {/* 1. US MARKET CARD */}
                <Box bg="gray.800" p={6} borderRadius="xl" shadow="dark-lg" position="relative" overflow="hidden">
                    <Box position="absolute" top={0} right={0} bg="blue.500" px={3} py={1} borderBottomLeftRadius="xl" fontSize="xs" fontWeight="bold">US</Box>
                    <VStack align="start" gap={4}>
                        <HStack>
                            <Avatar.Root size="sm">
                                <Avatar.Image src="https://flagcdn.com/us.svg" />
                                <Avatar.Fallback>US</Avatar.Fallback>
                            </Avatar.Root>
                            <Heading size="md">NYSE / NASDAQ</Heading>
                        </HStack>
                        <Box h="1px" bg="gray.600" w="full" />
                        <Stat.Root>
                            <Stat.Label>Cash Balance</Stat.Label>
                            <Stat.ValueText>${usData.summary?.cash_balance?.toFixed(2) || "---"}</Stat.ValueText>
                        </Stat.Root>
                        <Button colorPalette="blue" width="full" mt={4} onClick={buyUS}>
                            Buy AAPL (Sim)
                        </Button>
                    </VStack>
                </Box>

                {/* 2. CRYPTO MARKET CARD */}
                <Box bg="gray.800" p={6} borderRadius="xl" shadow="dark-lg" position="relative" overflow="hidden">
                    <Box position="absolute" top={0} right={0} bg="orange.400" px={3} py={1} borderBottomLeftRadius="xl" fontSize="xs" fontWeight="bold">CRYPTO</Box>
                    <VStack align="start" gap={4}>
                        <HStack>
                            <Avatar.Root size="sm" bg="orange.500">
                                <Avatar.Fallback>₿</Avatar.Fallback>
                            </Avatar.Root>
                            <Heading size="md">Crypto Live</Heading>
                        </HStack>
                        <Box h="1px" bg="gray.600" w="full" />
                        <Stat.Root>
                            <Stat.Label>BTC Price (Live)</Stat.Label>
                            <Stat.ValueText color="orange.300">${cryptoData.quote?.price?.toLocaleString() || "---"}</Stat.ValueText>
                            <Stat.HelpText fontSize="xs" color="gray.500">Source: Alpaca</Stat.HelpText>
                        </Stat.Root>
                        <Button colorPalette="orange" width="full" mt={4} onClick={buyCrypto}>
                            Buy BTC (Live)
                        </Button>
                    </VStack>
                </Box>

                {/* 3. INDIA MARKET CARD */}
                <Box bg="gray.800" p={6} borderRadius="xl" shadow="dark-lg" position="relative" overflow="hidden">
                    <Box position="absolute" top={0} right={0} bg="green.500" px={3} py={1} borderBottomLeftRadius="xl" fontSize="xs" fontWeight="bold">IN</Box>
                    <VStack align="start" gap={4}>
                        <HStack>
                            <Avatar.Root size="sm">
                                <Avatar.Image src="https://flagcdn.com/in.svg" />
                                <Avatar.Fallback>IN</Avatar.Fallback>
                            </Avatar.Root>
                            <Heading size="md">NSE / BSE</Heading>
                        </HStack>
                        <Box h="1px" bg="gray.600" w="full" />
                        <Stat.Root>
                            <Stat.Label>NIFTY50</Stat.Label>
                            <Stat.ValueText>₹{indiaData.quote?.price?.toLocaleString() || "---"}</Stat.ValueText>
                        </Stat.Root>
                        <Button colorPalette="green" width="full" mt={4} onClick={buyIndia}>
                            Buy NIFTY (Sim)
                        </Button>
                    </VStack>
                </Box>

            </SimpleGrid>

            {/* SYSTEM LOGS */}
            <Box mt={8}>
                <ActivityLog />
            </Box>
        </Box >
    )
}
