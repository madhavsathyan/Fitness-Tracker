/**
 * Data Context for Real-Time Dashboard Sync
 * Triggers Dashboard refresh when data is saved in any page
 */

import { createContext, useContext, useState, useCallback } from 'react';

interface DataContextType {
    refreshTrigger: number;
    triggerRefresh: () => void;
    lastUpdatedPage: string | null;
    setLastUpdatedPage: (page: string) => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: React.ReactNode }) {
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [lastUpdatedPage, setLastUpdatedPage] = useState<string | null>(null);

    const triggerRefresh = useCallback(() => {
        setRefreshTrigger(prev => prev + 1);
        console.log('🔄 Dashboard refresh triggered');
    }, []);

    return (
        <DataContext.Provider value={{
            refreshTrigger,
            triggerRefresh,
            lastUpdatedPage,
            setLastUpdatedPage
        }}>
            {children}
        </DataContext.Provider>
    );
}

export function useData() {
    const context = useContext(DataContext);
    if (context === undefined) {
        throw new Error('useData must be used within a DataProvider');
    }
    return context;
}
