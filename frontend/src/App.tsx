import { Box, Flex, Switch, Text, HStack, Icon } from "@chakra-ui/react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { FiBriefcase, FiZap } from "react-icons/fi";
import Sidebar from "./components/Sidebar";
import DashboardHome from "./pages/DashboardHome";
import HodlPage from "./pages/HodlPage";
import ActivityPage from "./pages/ActivityPage";
import LiveAnalysisPage from "./pages/LiveAnalysisPage";
import PortfolioPage from './pages/PortfolioPage'
import SettingsPage from './pages/SettingsPage'
import StrategyPage from "./pages/StrategyPage";
import BacktestPage from "./pages/BacktestPage";
import RiskPage from "./pages/RiskPage";
import WalletPage from "./pages/WalletPage";
import OptimizePage from "./pages/OptimizePage";
import { ModeProvider, useSystemMode } from "./context/ModeContext";

function AppContent() {
  const { mode, toggleMode } = useSystemMode();
  const bg = mode === 'INSTITUTIONAL' ? 'gray.900' : 'black';

  return (
    <Flex minH="100vh" bg={bg} color="white" transition="background 0.3s">
      {/* SIDEBAR WITH TOGGLE */}
      <Box pos="fixed" left="0" top="0" h="100vh" w="64" zIndex="sticky" borderRight="1px" borderColor="whiteAlpha.200">
        <Sidebar mode={mode} />

        {/* THE GLOBAL SWITCH */}
        <Box pos="absolute" bottom="0" w="full" p="6" borderTop="1px" borderColor="whiteAlpha.200" bg={mode === 'INSTITUTIONAL' ? "gray.900" : "black"}>
          <HStack justify="space-between" bg="whiteAlpha.100" p={3} borderRadius="full">
            <Icon as={FiBriefcase} color={mode === 'INSTITUTIONAL' ? "blue.400" : "gray.600"} />
            <Switch
              isChecked={mode === 'HODL'}
              onChange={toggleMode}
              colorScheme="pink"
              size="lg"
            />
            <Icon as={FiZap} color={mode === 'HODL' ? "pink.400" : "gray.600"} />
          </HStack>
          <Text textAlign="center" mt={2} fontSize="xs" color="gray.500" fontWeight="bold">
            {mode} MODE
          </Text>
        </Box>
      </Box>

      {/* MAIN CONTENT */}
      <Box ml="64" w="full" p="8">
        <Routes>
          {/* DYNAMIC ROUTING BASED ON MODE */}
          <Route path="/" element={mode === 'INSTITUTIONAL' ? <DashboardHome /> : <HodlPage />} />

          {/* INSTITUTIONAL ROUTES */}
          <Route path="/live-analysis" element={<LiveAnalysisPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/strategies" element={<StrategyPage />} />
          <Route path="/risk" element={<RiskPage />} />
          <Route path="/wallet" element={<WalletPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
          <Route path="/activity" element={<ActivityPage />} />

          {/* HODL ROUTES */}
          <Route path="/hodl" element={<HodlPage />} />
          <Route path="/scanner" element={<HodlPage />} /> {/* Placeholder */}
          <Route path="/gem-hunter" element={<HodlPage />} /> {/* Placeholder */}
          <Route path="/rug-check" element={<HodlPage />} /> {/* Placeholder */}
          <Route path="/sniper" element={<HodlPage />} /> {/* Placeholder */}

          {/* SHARED */}
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Box>
    </Flex>
  );
}

export default function App() {
  return (
    <ModeProvider>
      <Router>
        <AppContent />
      </Router>
    </ModeProvider>
  );
}
