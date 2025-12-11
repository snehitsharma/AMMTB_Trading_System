import { Box, VStack, Text, Badge, HStack, Card, CardHeader, CardBody, Button, useToast, Heading } from '@chakra-ui/react'
import { useEffect, useState, useCallback } from 'react'
import axios from 'axios'

interface LogEntry {
    timestamp: string
    source: string
    event: string
    details: any
}

export const ActivityLog = () => {
    const [logs, setLogs] = useState<LogEntry[]>([])
    const [loading, setLoading] = useState(false)
    const [page, setPage] = useState(0)
    const [hasMore, setHasMore] = useState(true)
    const toast = useToast()
    const LIMIT = 20

    const fetchLogs = useCallback(async (reset = false) => {
        if (loading) return
        setLoading(true)
        try {
            const offset = reset ? 0 : page * LIMIT
            const response = await axios.get(`/api/orchestrator/logs?limit=${LIMIT}&offset=${offset}`)

            if (response.data && response.data.logs) {
                const newLogs = response.data.logs
                if (newLogs.length < LIMIT) setHasMore(false)

                if (reset) {
                    setLogs(newLogs)
                    setPage(1)
                } else {
                    setLogs(prev => [...prev, ...newLogs])
                    setPage(prev => prev + 1)
                }
            }
        } catch (error) {
            console.error("Failed to fetch logs", error)
            toast({
                title: "Connection Error",
                description: "Failed to fetch system logs.",
                status: "error",
                duration: 3000,
                isClosable: true,
            })
        } finally {
            setLoading(false)
        }
    }, [page, loading, toast])

    // Initial Load
    useEffect(() => {
        fetchLogs(true)
        const interval = setInterval(() => {
            if (page <= 1) fetchLogs(true)
        }, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <Card width="full" height="400px" overflow="hidden" variant="outline" bg="gray.900" borderColor="gray.700">
            <CardHeader p={4} borderBottom="1px solid" borderColor="gray.700">
                <HStack justify="space-between">
                    <Heading size="md" color="white">System Activity Log</Heading>
                    <Badge colorScheme={loading ? "orange" : "green"}>
                        {loading ? "Syncing..." : "Live"}
                    </Badge>
                </HStack>
            </CardHeader>
            <CardBody overflowY="auto" p={4} css={{ '&::-webkit-scrollbar': { width: '4px' }, '&::-webkit-scrollbar-track': { width: '6px' }, '&::-webkit-scrollbar-thumb': { background: '#4A5568', borderRadius: '24px' } }}>
                <VStack align="stretch" spacing={2}>
                    {logs.length === 0 && !loading ? (
                        <Text color="gray.500" textAlign="center" py={10}>No system activity detected.</Text>
                    ) : (
                        logs.map((log, index) => (
                            <Box key={index} p={3} borderWidth="1px" borderRadius="md" bg="gray.800" borderColor="gray.700">
                                <HStack justify="space-between" mb={1}>
                                    <HStack spacing={2}>
                                        <Badge colorScheme={log.source === "US_AGENT" ? "blue" : log.source === "HODL" ? "purple" : "gray"}>
                                            {log.source}
                                        </Badge>
                                        <Text fontWeight="bold" fontSize="sm" color="white">{log.event}</Text>
                                    </HStack>
                                    <Text fontSize="xs" color="gray.500">
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </Text>
                                </HStack>

                                {log.details && typeof log.details === 'object' && Object.keys(log.details).length > 0 && (
                                    <Box mt={2} p={2} bg="blackAlpha.300" borderRadius="md">
                                        <Text fontSize="xs" color="gray.400" fontFamily="monospace" whiteSpace="pre-wrap">
                                            {(() => {
                                                try {
                                                    const str = JSON.stringify(log.details, null, 2);
                                                    return str.length > 200 ? str.slice(0, 200) + "..." : str;
                                                } catch (e) {
                                                    return "Unavailable";
                                                }
                                            })()}
                                        </Text>
                                    </Box>
                                )}
                            </Box>
                        ))
                    )}

                    {hasMore && (
                        <Button
                            size="sm"
                            onClick={() => fetchLogs(false)}
                            isLoading={loading}
                            variant="ghost"
                            colorScheme="blue"
                            width="full"
                        >
                            Load More
                        </Button>
                    )}
                </VStack>
            </CardBody>
        </Card>
    )
}
