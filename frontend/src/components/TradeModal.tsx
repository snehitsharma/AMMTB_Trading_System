import { useState } from 'react'
import axios from 'axios'
import {
    Box, Button, Input, VStack, HStack, Text, Dialog
} from '@chakra-ui/react'

interface TradeModalProps {
    symbol?: string
    isOpen?: boolean
    onClose?: () => void
    trigger?: React.ReactNode
}

export default function TradeModal({ symbol: initialSymbol = "", trigger }: TradeModalProps) {
    const [symbol, setSymbol] = useState(initialSymbol)
    const [side, setSide] = useState("buy")
    const [qty, setQty] = useState("")
    const [type, setType] = useState("market")
    const [limitPrice, setLimitPrice] = useState("")
    const [loading, setLoading] = useState(false)

    const handleTrade = async () => {
        if (!symbol || !qty) {
            alert("Please enter symbol and quantity")
            return
        }

        setLoading(true)
        try {
            const payload: any = {
                symbol: symbol.toUpperCase(),
                side,
                qty: parseFloat(qty),
                type
            }
            if (type === "limit") {
                if (!limitPrice) {
                    alert("Limit Price required for Limit Orders")
                    setLoading(false)
                    return
                }
                payload.limit_price = parseFloat(limitPrice)
            }

            const res = await axios.post('/api/ai/manual_trade', payload)

            if (res.data.status === "filled" || res.data.id) {
                alert(`Order Submitted: ${res.data.id}`)
                // Reset form?
            } else {
                alert(`Error: ${res.data.message}`)
            }
        } catch (e: any) {
            alert(`Trade Failed: ${e.message}`)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog.Root>
            <Dialog.Trigger asChild>
                {trigger || <Button size="sm" colorPalette="blue">Trade</Button>}
            </Dialog.Trigger>
            <Dialog.Content>
                <Dialog.Header>
                    <Dialog.Title>Manual Execution</Dialog.Title>
                </Dialog.Header>
                <Dialog.Body>
                    <VStack gap={4} align="stretch">
                        <Box>
                            <Text mb={1} fontSize="sm" fontWeight="medium">Symbol</Text>
                            <Input
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                placeholder="AAPL or BTC/USD"
                                disabled={!!initialSymbol}
                            />
                        </Box>

                        <HStack gap={4}>
                            <Button
                                flex={1}
                                colorPalette={side === "buy" ? "green" : "gray"}
                                onClick={() => setSide("buy")}
                            >
                                BUY
                            </Button>
                            <Button
                                flex={1}
                                colorPalette={side === "sell" ? "red" : "gray"}
                                onClick={() => setSide("sell")}
                            >
                                SELL
                            </Button>
                        </HStack>

                        <HStack gap={4}>
                            <Box flex={1}>
                                <Text mb={1} fontSize="sm" fontWeight="medium">Quantity</Text>
                                <Input
                                    type="number"
                                    value={qty}
                                    onChange={(e) => setQty(e.target.value)}
                                    placeholder="0.00"
                                />
                            </Box>
                            <Box flex={1}>
                                <Text mb={1} fontSize="sm" fontWeight="medium">Order Type</Text>
                                <select
                                    value={type}
                                    onChange={(e) => setType(e.target.value)}
                                    style={{
                                        width: "100%",
                                        padding: "8px",
                                        borderRadius: "6px",
                                        background: "#2D3748",
                                        color: "white",
                                        border: "1px solid #4A5568"
                                    }}
                                >
                                    <option value="market">Market</option>
                                    <option value="limit">Limit</option>
                                </select>
                            </Box>
                        </HStack>

                        {type === "limit" && (
                            <Box>
                                <Text mb={1} fontSize="sm" fontWeight="medium">Limit Price</Text>
                                <Input
                                    type="number"
                                    value={limitPrice}
                                    onChange={(e) => setLimitPrice(e.target.value)}
                                    placeholder="0.00"
                                />
                            </Box>
                        )}
                    </VStack>
                </Dialog.Body>
                <Dialog.Footer>
                    <Dialog.ActionTrigger asChild>
                        <Button variant="outline">Cancel</Button>
                    </Dialog.ActionTrigger>
                    <Button colorPalette={side === "buy" ? "green" : "red"} loading={loading} onClick={handleTrade}>
                        Submit Order
                    </Button>
                </Dialog.Footer>
                <Dialog.CloseTrigger />
            </Dialog.Content>
        </Dialog.Root>
    )
}
