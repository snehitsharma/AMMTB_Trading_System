import { Box, Heading, Text, Badge, Icon } from "@chakra-ui/react";
import { FiCpu, FiUsers } from "react-icons/fi";
import { useEffect, useState } from "react";
import axios from "axios";

export default function StrategyPage() {
    const [toggles, setToggles] = useState<any>({});

    const refresh = async () => {
        try {
            const res = await axios.get("/api/ai/api/v1/strategies");
            setToggles(res.data);
        } catch (e) { console.error(e); }
    };

    const handleToggle = async (name: string, isChecked: boolean) => {
        setToggles({ ...toggles, [name]: isChecked }); // Optimistic UI update
        await axios.post("/api/ai/api/v1/strategies/toggle", { name, enabled: isChecked });
        refresh();
    };

    useEffect(() => { refresh(); }, []);

    return (
        <Box p={6}>
            <Heading mb={8} size="xl">Strategy Control Panel</Heading>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>

                {/* TECHNICAL ENGINE CARD */}
                <div style={{
                    backgroundColor: '#171923',
                    padding: '24px',
                    borderRadius: '12px',
                    border: toggles["TECHNICAL"] ? '1px solid #3182ce' : '1px solid #2d3748'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <Icon as={FiCpu} color="blue.400" boxSize={6} />
                            <Text fontWeight="bold" fontSize="lg" color="white">Technical Engine</Text>
                        </div>
                        <label style={{ position: 'relative', display: 'inline-block', width: '60px', height: '34px' }}>
                            <input
                                type="checkbox"
                                checked={!!toggles["TECHNICAL"]}
                                onChange={(e) => handleToggle("TECHNICAL", e.target.checked)}
                                style={{ opacity: 0, width: 0, height: 0 }}
                            />
                            <span style={{
                                position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0,
                                backgroundColor: toggles["TECHNICAL"] ? '#3182ce' : '#ccc',
                                transition: '.4s', borderRadius: '34px'
                            }}></span>
                            <span style={{
                                position: 'absolute', content: '""', height: '26px', width: '26px', left: '4px', bottom: '4px',
                                backgroundColor: 'white', transition: '.4s', borderRadius: '50%',
                                transform: toggles["TECHNICAL"] ? 'translateX(26px)' : 'translateX(0px)'
                            }}></span>
                        </label>
                    </div>
                    <Text color="gray.400" mb={4}>
                        Algorithmic analysis using RSI (Momentum), MACD (Trend), and EMA crossovers. Best for volatile markets.
                    </Text>
                    <Badge colorScheme={toggles["TECHNICAL"] ? "green" : "gray"}>
                        {toggles["TECHNICAL"] ? "ACTIVE" : "DISABLED"}
                    </Badge>
                </div>

                {/* INSIDER ENGINE CARD */}
                <div style={{
                    backgroundColor: '#171923',
                    padding: '24px',
                    borderRadius: '12px',
                    border: toggles["INSIDER"] ? '1px solid #805ad5' : '1px solid #2d3748'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <Icon as={FiUsers} color="purple.400" boxSize={6} />
                            <Text fontWeight="bold" fontSize="lg" color="white">Insider Tracking</Text>
                        </div>
                        <label style={{ position: 'relative', display: 'inline-block', width: '60px', height: '34px' }}>
                            <input
                                type="checkbox"
                                checked={!!toggles["INSIDER"]}
                                onChange={(e) => handleToggle("INSIDER", e.target.checked)}
                                style={{ opacity: 0, width: 0, height: 0 }}
                            />
                            <span style={{
                                position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0,
                                backgroundColor: toggles["INSIDER"] ? '#805ad5' : '#ccc',
                                transition: '.4s', borderRadius: '34px'
                            }}></span>
                            <span style={{
                                position: 'absolute', content: '""', height: '26px', width: '26px', left: '4px', bottom: '4px',
                                backgroundColor: 'white', transition: '.4s', borderRadius: '50%',
                                transform: toggles["INSIDER"] ? 'translateX(26px)' : 'translateX(0px)'
                            }}></span>
                        </label>
                    </div>
                    <Text color="gray.400" mb={4}>
                        Monitors SEC Form 4 filings for CEO/CFO cluster buying events {'>'} $250k. High conviction setup.
                    </Text>
                    <Badge colorScheme={toggles["INSIDER"] ? "green" : "gray"}>
                        {toggles["INSIDER"] ? "ACTIVE" : "DISABLED"}
                    </Badge>
                </div>

            </div>
        </Box>
    );
}
