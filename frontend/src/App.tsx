import React, { useState, useEffect } from 'react';
import { AuthProvider } from './context/AuthContext';
import { SavedTrainsProvider } from './context/SavedTrainsContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import { SearchResultsPage } from './pages/SearchResultsPage';
import { TrainDetailPage } from './pages/TrainDetailPage';
import { StationDetailPage } from './pages/StationDetailPage';
import { SavedTrainsPage } from './pages/SavedTrainsPage';
import { ServiceAlertsPage } from './pages/ServiceAlertsPage';
import { AdminConsolePage } from './pages/AdminConsolePage';
import { LoginPage } from './pages/LoginPage';
import { StationSearchCard } from './components/StationSearchCard';
import { api } from './services/api';
import { Station, Train, ServiceAlert } from './types';

export const AppContent: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [stations, setStations] = useState<Station[]>([]);
  const [alerts, setAlerts] = useState<ServiceAlert[]>([]);
  const [searchResults, setSearchResults] = useState<{ items: Train[]; total: number }>({ items: [], total: 0 });
  const [searchParams, setSearchParams] = useState<{ query?: string; source?: string; destination?: string; category?: string }>({});
  const [selectedTrainNumber, setSelectedTrainNumber] = useState<string>('12951');
  const [selectedStationCode, setSelectedStationCode] = useState<string>('NDLS');

  useEffect(() => {
    // Initial fetch of stations and alerts
    api.getStations(undefined, 200)
      .then((res) => setStations(res))
      .catch((err) => console.error('Failed to load stations', err));

    api.getAlerts()
      .then((res) => setAlerts(res))
      .catch((err) => console.error('Failed to load alerts', err));
  }, []);

  const handleSearchTrains = async (params: { query?: string; source?: string; destination?: string; category?: string }) => {
    setSearchParams(params);
    try {
      const res = await api.searchTrains({ ...params, limit: 50 });
      setSearchResults({ items: res.items, total: res.total });
      setCurrentPage('search-results');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectTrain = (num: string) => {
    setSelectedTrainNumber(num);
    setCurrentPage('train-detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectStation = (code: string) => {
    setSelectedStationCode(code);
    setCurrentPage('station-detail');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar
        currentPage={currentPage}
        onNavigate={(page, params) => {
          if (page === 'train-detail' && params?.trainNumber) {
            handleSelectTrain(params.trainNumber);
          } else if (page === 'station-detail' && params?.stationCode) {
            handleSelectStation(params.stationCode);
          } else {
            setCurrentPage(page);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
        }}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {currentPage === 'home' && (
          <HomePage
            stations={stations}
            alerts={alerts}
            onSearchTrains={handleSearchTrains}
            onSelectTrain={handleSelectTrain}
            onSelectStation={handleSelectStation}
            onViewAllAlerts={() => setCurrentPage('alerts')}
          />
        )}

        {currentPage === 'search-results' && (
          <SearchResultsPage
            trains={searchResults.items}
            total={searchResults.total}
            searchParams={searchParams}
            onSelectTrain={handleSelectTrain}
            onBack={() => setCurrentPage('home')}
          />
        )}

        {currentPage === 'train-detail' && (
          <TrainDetailPage
            trainNumber={selectedTrainNumber}
            onBack={() => setCurrentPage('home')}
            onSelectStation={handleSelectStation}
          />
        )}

        {currentPage === 'station-detail' && (
          <StationDetailPage
            stationCode={selectedStationCode}
            onBack={() => setCurrentPage('stations')}
            onSelectTrain={handleSelectTrain}
          />
        )}

        {currentPage === 'stations' && (
          <div className="space-y-6 pb-16">
            <div className="text-center md:text-left space-y-1">
              <h2 className="text-2xl font-extrabold text-white">Indian Railways Station Live Telemetry Boards</h2>
              <p className="text-xs text-slate-400">Select any junction to view real-time arrival and departure movements</p>
            </div>
            <StationSearchCard
              stations={stations}
              onSelectStation={handleSelectStation}
            />
          </div>
        )}

        {currentPage === 'saved' && (
          <SavedTrainsPage
            onSelectTrain={handleSelectTrain}
            onExplore={() => setCurrentPage('home')}
          />
        )}

        {currentPage === 'alerts' && (
          <ServiceAlertsPage
            alerts={alerts}
            onSelectTrain={handleSelectTrain}
            onBack={() => setCurrentPage('home')}
          />
        )}

        {currentPage === 'admin' && (
          <AdminConsolePage />
        )}

        {currentPage === 'login' && (
          <LoginPage
            onSuccess={() => {
              setCurrentPage('home');
            }}
          />
        )}
      </main>

      <Footer />
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <SavedTrainsProvider>
        <AppContent />
      </SavedTrainsProvider>
    </AuthProvider>
  );
}
