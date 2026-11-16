import React, { createContext, useContext, useState, useEffect } from 'react';
import { Train } from '../types';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

interface SavedTrainsContextType {
  savedTrains: Train[];
  isSaved: (trainNumber: string) => boolean;
  toggleSave: (train: Train) => Promise<void>;
  loading: boolean;
}

const SavedTrainsContext = createContext<SavedTrainsContextType | undefined>(undefined);

export const SavedTrainsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [savedTrains, setSavedTrains] = useState<Train[]>(() => {
    try {
      const stored = localStorage.getItem('railtrack_saved_trains');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      setLoading(true);
      api.getSavedTrains()
        .then((trains) => {
          if (trains && trains.length > 0) {
            setSavedTrains(trains);
            localStorage.setItem('railtrack_saved_trains', JSON.stringify(trains));
          }
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated]);

  const isSaved = (trainNumber: string) => {
    return savedTrains.some((t) => t.train_number.toUpperCase() === trainNumber.toUpperCase());
  };

  const toggleSave = async (train: Train) => {
    const saved = isSaved(train.train_number);
    let updated: Train[];

    if (saved) {
      updated = savedTrains.filter((t) => t.train_number.toUpperCase() !== train.train_number.toUpperCase());
      if (isAuthenticated) {
        try {
          await api.unsaveTrain(train.train_number);
        } catch {}
      }
    } else {
      updated = [...savedTrains, train];
      if (isAuthenticated) {
        try {
          await api.saveTrain(train.train_number);
        } catch {}
      }
    }

    setSavedTrains(updated);
    localStorage.setItem('railtrack_saved_trains', JSON.stringify(updated));
  };

  return (
    <SavedTrainsContext.Provider value={{ savedTrains, isSaved, toggleSave, loading }}>
      {children}
    </SavedTrainsContext.Provider>
  );
};

export const useSavedTrains = () => {
  const context = useContext(SavedTrainsContext);
  if (!context) throw new Error('useSavedTrains must be used within SavedTrainsProvider');
  return context;
};
