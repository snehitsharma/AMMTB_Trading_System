import { Box, VStack, Text, Badge, HStack, Card } from '@chakra-ui/react'
import { useEffect, useState } from 'react'
import axios from 'axios'

interface LogEntry {
    timestamp: string
    source: string
    event: string
    details: any
}

export const ActivityLog = () => {
    const [logs, setLogs] = useState<LogEntry[]>([])

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const response = await axios.get('/api/orchestrator/logs')
                if (response.data && response.data.logs) {
                    setLogs(response.data.logs)
                }
            } catch (error) {
                console.error("Failed to fetch logs", error)
            }
        }

        fetchLogs()
        const interval = setInterval(fetchLogs, 2000)
        return () => clearInterval(interval)
    }, [])

    return (
        <Card.Root width="full" height="300px" overflow="hidden">
            <Card.Header>
                <Card.Title>System Activity Log</Card.Title>
            </Card.Header>
            <Card.Body overflowY="auto">
                <VStack align="stretch" gap={2}>
                    {logs.length === 0 ? (
                        <Text color="gray.500">No activity logged yet.</Text>
                    ) : (
                        logs.map((log, index) => (
                            <Box key={index} p={2} borderWidth="1px" borderRadius="md" bg="gray.800">
                                <HStack justify="space-between">
                                    <HStack>
                                        <Badge colorPalette="blue">{log.source}</Badge>
                                        <Text fontWeight="bold">{log.event}</Text>
                                    </HStack>
                                    <Text fontSize="xs" color="gray.400">
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </Text>
                                </HStack>
                                {log.details && Object.keys(log.details).length > 0 && (
                                    <Text fontSize="sm" color="gray.300" mt={1}>
                                        {JSON.stringify(log.details)}
                                    </Text>
                                )}
                            </Box>
                        ))
                    )}
                </VStack>
            </Card.Body>
        </Card.Root>
    )
}
