import { useState, useEffect } from 'react'
import axios from 'axios'
import {
    Box, Heading, Table, Badge, Text, Spinner, Flex
} from '@chakra-ui/react'

interface AnalysisResult {
    asset: string
    price: number
    action: string
    reason: string
    indicators?: {
        rsi: number
        macd: number
        atr: number
    }
}

export default function LiveAnalysisPage() {
    const [results, setResults] = useState<AnalysisResult[]>([])
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        try {
            const res = await axios.get('/api/ai/live_analysis')
            setResults(res.data)
            setLoading(false)
        } catch (e) {
            console.error(e)
        }
    }

    useEffect(() => {
        fetchData()
        const interval = setInterval(fetchData, 3000)
        return () => clearInterval(interval)
    }, [])

    return (
        <Box>
            <Flex justify="space-between" align="center" mb={6}>
                <Heading>Live Analysis Feed</Heading>
                {loading && <Spinner color="blue.500" />}
            </Flex>

            <Box bg="gray.800" p={6} borderRadius="xl" shadow="dark-lg" border="1px solid" borderColor="gray.700" overflowX="auto">
                <Table.Root variant="outline" size="sm">
                    <Table.Header>
                        <Table.Row>
                            <Table.ColumnHeader color="gray.400">Asset</Table.ColumnHeader>
                            <Table.ColumnHeader color="gray.400" textAlign="right">Price</Table.ColumnHeader>
                            <Table.ColumnHeader color="gray.400">Decision</Table.ColumnHeader>
                            <Table.ColumnHeader color="gray.400">Reason</Table.ColumnHeader>
                            <Table.ColumnHeader color="gray.400" textAlign="right">RSI</Table.ColumnHeader>
                            <Table.ColumnHeader color="gray.400" textAlign="right">MACD</Table.ColumnHeader>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {results.map((r, i) => (
                            <Table.Row key={i} _hover={{ bg: "gray.700" }}>
                                <Table.Cell fontWeight="bold">{r.asset}</Table.Cell>
                                <Table.Cell textAlign="right">${r.price.toFixed(2)}</Table.Cell>
                                <Table.Cell>
                                    <Badge
                                        colorPalette={
                                            r.action === "BUY" ? "green" :
                                                r.action === "SELL" ? "red" : "gray"
                                        }
                                    >
                                        {r.action}
                                    </Badge>
                                </Table.Cell>
                                <Table.Cell fontSize="xs" color="gray.300">{r.reason}</Table.Cell>
                                <Table.Cell textAlign="right" color={r.indicators?.rsi && (r.indicators.rsi > 70 || r.indicators.rsi < 30) ? "orange.300" : "white"}>
                                    {r.indicators?.rsi?.toFixed(1) || "-"}
                                </Table.Cell>
                                <Table.Cell textAlign="right">
                                    {r.indicators?.macd?.toFixed(3) || "-"}
                                </Table.Cell>
                            </Table.Row>
                        ))}
                    </Table.Body>
                </Table.Root>
                {results.length === 0 && !loading && (
                    <Text color="gray.500" mt={4} textAlign="center">Waiting for AI Scan...</Text>
                )}
            </Box>
        </Box>
    )
}
