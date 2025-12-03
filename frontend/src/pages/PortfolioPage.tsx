import { useState, useEffect } from 'react'
import axios from 'axios'
import {
    Box, Heading, SimpleGrid, Text, Badge, Table, Stat
} from '@chakra-ui/react'
import TradeModal from '../components/TradeModal'

interface Position {
    symbol: string
    qty: number
    market_value: number
    avg_entry_price: number
    current_price: number
    unrealized_pl: number
    unrealized_plpc: number
    type: 'US' | 'CRYPTO'
}

export default function PortfolioPage() {
    const [positions, setPositions] = useState<Position[]>([])
    const [loading, setLoading] = useState(true)
    const [totalEquity, setTotalEquity] = useState(0)
    const [totalPL, setTotalPL] = useState(0)

    const fetchData = async () => {
        try {
            const [usRes, cryptoRes] = await Promise.all([
                axios.get('/api/us/positions'),
                axios.get('/api/crypto/positions')
            ])

            const usPos = usRes.data.map((p: any) => ({ ...p, type: 'US' }))
            const cryptoPos = cryptoRes.data.map((p: any) => ({ ...p, type: 'CRYPTO' }))

            const allPos = [...usPos, ...cryptoPos]
            setPositions(allPos)

            // Calculate Totals
            const equity = allPos.reduce((sum, p) => sum + p.market_value, 0)
            const pl = allPos.reduce((sum, p) => sum + p.unrealized_pl, 0)

            setTotalEquity(equity)
            setTotalPL(pl)
            setLoading(false)
        } catch (e) {
            console.error("Error fetching portfolio:", e)
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
        const interval = setInterval(fetchData, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <Box>
            <Heading mb={6}>Global Portfolio</Heading>

            {/* Summary Cards */}
            <SimpleGrid columns={{ base: 1, md: 3 }} gap={5} mb={8}>
                <Box bg="gray.800" p={5} borderRadius="xl" shadow="dark-lg" border="1px solid" borderColor="gray.700">
                    <Stat.Root>
                        <Stat.Label color="gray.400">Total Equity</Stat.Label>
                        <Stat.ValueText fontSize="2xl">${totalEquity.toFixed(2)}</Stat.ValueText>
                        <Stat.HelpText>Combined US & Crypto</Stat.HelpText>
                    </Stat.Root>
                </Box>
                <Box bg="gray.800" p={5} borderRadius="xl" shadow="dark-lg" border="1px solid" borderColor="gray.700">
                    <Stat.Root>
                        <Stat.Label color="gray.400">Total P/L</Stat.Label>
                        <Stat.ValueText fontSize="2xl" color={totalPL >= 0 ? "green.400" : "red.400"}>
                            {totalPL >= 0 ? "+" : ""}${totalPL.toFixed(2)}
                        </Stat.ValueText>
                        <Stat.HelpText>
                            Unrealized
                        </Stat.HelpText>
                    </Stat.Root>
                </Box>
                <Box bg="gray.800" p={5} borderRadius="xl" shadow="dark-lg" border="1px solid" borderColor="gray.700">
                    <Stat.Root>
                        <Stat.Label color="gray.400">Active Positions</Stat.Label>
                        <Stat.ValueText fontSize="2xl">{positions.length}</Stat.ValueText>
                        <Stat.HelpText>Assets Held</Stat.HelpText>
                    </Stat.Root>
                </Box>
            </SimpleGrid>

            {/* Holdings Table */}
            <Box bg="gray.800" p={6} borderRadius="xl" shadow="dark-lg" border="1px solid" borderColor="gray.700" overflowX="auto">
                <Heading size="md" mb={4}>Holdings</Heading>
                {loading ? (
                    <Text>Loading Portfolio...</Text>
                ) : positions.length === 0 ? (
                    <Text color="gray.500">No active positions.</Text>
                ) : (
                    <Table.Root variant="outline" size="sm">
                        <Table.Header>
                            <Table.Row>
                                <Table.ColumnHeader color="gray.400">Asset</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400">Type</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">Qty</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">Avg Price</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">Current</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">Value</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">P/L ($)</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">P/L (%)</Table.ColumnHeader>
                                <Table.ColumnHeader color="gray.400" textAlign="right">Action</Table.ColumnHeader>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {positions.map((p, i) => (
                                <Table.Row key={i} _hover={{ bg: "gray.700" }}>
                                    <Table.Cell fontWeight="bold">{p.symbol}</Table.Cell>
                                    <Table.Cell>
                                        <Badge colorPalette={p.type === 'US' ? 'blue' : 'orange'}>{p.type}</Badge>
                                    </Table.Cell>
                                    <Table.Cell textAlign="right">{p.qty}</Table.Cell>
                                    <Table.Cell textAlign="right">${p.avg_entry_price.toFixed(2)}</Table.Cell>
                                    <Table.Cell textAlign="right">${p.current_price.toFixed(2)}</Table.Cell>
                                    <Table.Cell textAlign="right" fontWeight="bold">${p.market_value.toFixed(2)}</Table.Cell>
                                    <Table.Cell textAlign="right" color={p.unrealized_pl >= 0 ? "green.400" : "red.400"}>
                                        {p.unrealized_pl >= 0 ? "+" : ""}{p.unrealized_pl.toFixed(2)}
                                    </Table.Cell>
                                    <Table.Cell textAlign="right" color={p.unrealized_plpc >= 0 ? "green.400" : "red.400"}>
                                        {p.unrealized_plpc >= 0 ? "+" : ""}{(p.unrealized_plpc * 100).toFixed(2)}%
                                    </Table.Cell>
                                    <Table.Cell textAlign="right">
                                        <TradeModal symbol={p.symbol} />
                                    </Table.Cell>
                                </Table.Row>
                            ))}
                        </Table.Body>
                    </Table.Root>
                )}
            </Box>
        </Box>
    )
}
