import { createContext, useState, useContext, ReactNode } from 'react';

type SystemMode = 'INSTITUTIONAL' | 'HODL';

interface ModeContextType {
    mode: SystemMode;
    toggleMode: () => void;
}

const ModeContext = createContext<ModeContextType | undefined>(undefined);

export function ModeProvider({ children }: { children: ReactNode }) {
    const [mode, setMode] = useState<SystemMode>('INSTITUTIONAL');

    const toggleMode = () => {
        setMode((prev) => (prev === 'INSTITUTIONAL' ? 'HODL' : 'INSTITUTIONAL'));
    };

    return (
        <ModeContext.Provider value={{ mode, toggleMode }}>
            {children}
        </ModeContext.Provider>
    );
}

export function useSystemMode() {
    const context = useContext(ModeContext);
    if (!context) throw new Error("useSystemMode must be used within ModeProvider");
    return context;
}
