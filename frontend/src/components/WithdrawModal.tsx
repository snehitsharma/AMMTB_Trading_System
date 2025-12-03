import {
    Dialog,
    Button,
    Input,
    VStack,
    Text,
    HStack,
    Portal
} from '@chakra-ui/react'
import { useState } from 'react'
import axios from 'axios'

export const WithdrawModal = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [amount, setAmount] = useState('')
    const [market, setMarket] = useState('US')
    const [loading, setLoading] = useState(false)

    const handleWithdraw = async () => {
        setLoading(true)
        try {
            await axios.post('/api/orchestrator/withdraw', {
                amount: parseFloat(amount),
                market: market
            })
            setIsOpen(false)
            setAmount('')
        } catch (error) {
            console.error("Withdrawal failed", error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog.Root open={isOpen} onOpenChange={(e) => setIsOpen(e.open)}>
            <Dialog.Trigger asChild>
                <Button colorPalette="red" variant="solid">Withdraw Funds</Button>
            </Dialog.Trigger>
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title>Withdraw Funds</Dialog.Title>
                        </Dialog.Header>
                        <Dialog.Body>
                            <VStack gap={4} align="stretch">
                                <Text>Select Market</Text>
                                <HStack>
                                    <Button
                                        variant={market === 'US' ? 'solid' : 'outline'}
                                        onClick={() => setMarket('US')}
                                        size="sm"
                                    >
                                        US Market
                                    </Button>
                                    <Button
                                        variant={market === 'CRYPTO' ? 'solid' : 'outline'}
                                        onClick={() => setMarket('CRYPTO')}
                                        size="sm"
                                    >
                                        Crypto
                                    </Button>
                                </HStack>
                                <Text>Amount ($)</Text>
                                <Input
                                    placeholder="Enter amount"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    type="number"
                                />
                            </VStack>
                        </Dialog.Body>
                        <Dialog.Footer>
                            <Dialog.CloseTrigger asChild>
                                <Button variant="outline">Cancel</Button>
                            </Dialog.CloseTrigger>
                            <Button onClick={handleWithdraw} loading={loading}>
                                Confirm Withdrawal
                            </Button>
                        </Dialog.Footer>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    )
}
