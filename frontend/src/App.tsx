import { Box, Flex } from "@chakra-ui/react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import DashboardHome from "./pages/DashboardHome";
import ActivityPage from "./pages/ActivityPage";
import LiveAnalysisPage from "./pages/LiveAnalysisPage";
import PortfolioPage from './pages/PortfolioPage'
import SettingsPage from './pages/SettingsPage'

import StrategyPage from "./pages/StrategyPage";
import BacktestPage from "./pages/BacktestPage";
import RiskPage from "./pages/RiskPage";
import WalletPage from "./pages/WalletPage";

export default function App() {
  return (
    <Router>
      <Flex h="100vh" bg="gray.900" color="white" overflow="hidden">
        {/* LEFT SIDEBAR (Fixed Width) */}
        <Sidebar />

        {/* RIGHT CONTENT (Full Width) */}
        <Box flex="1" p={8} overflowY="auto">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/live-analysis" element={<LiveAnalysisPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/wallet" element={<WalletPage />} />
            <Route path="/strategies" element={<StrategyPage />} />
            <Route path="/backtest" element={<BacktestPage />} />
            <Route path="/risk" element={<RiskPage />} />
            <Route path="/activity" element={<ActivityPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Box>
      </Flex>
    </Router>
  );
}
