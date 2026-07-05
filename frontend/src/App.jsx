import { useState } from 'react';
import AuthScreen from './components/AuthScreen';
import HomeScreen from './components/HomeScreen';
import GameScreen from './components/GameScreen';
import ResultScreen from './components/ResultScreen';
import SettingsScreen from './components/SettingsScreen';
import { setToken } from './api/client';
import './App.css';

export default function App() {
  const [screen, setScreen] = useState('auth');
  const [user, setUser] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [questionCount, setQuestionCount] = useState(0);
  const [consultationId, setConsultationId] = useState(null);

  const handleLogin = (name) => {
    setUser(name);
    setScreen('home');
  };

  const handleStart = () => {
    setDiagnosis(null);
    setQuestionCount(0);
    setScreen('game');
  };

  const handleResult = (diag, count, cid) => {
    setDiagnosis(diag);
    setQuestionCount(count);
    setConsultationId(cid);
    setScreen('result');
  };

  const handleLogout = () => {
    setUser('');
    setToken(null);
    setScreen('auth');
  };

  return (
    <div className="app-container">
      <div className="phone-frame">
        {screen === 'auth' && <AuthScreen onLogin={handleLogin} />}
        {screen === 'home' && (
          <HomeScreen
            user={user}
            onStart={handleStart}
            onSettings={() => setScreen('settings')}
            onLogout={handleLogout}
          />
        )}
        {screen === 'game' && (
          <GameScreen
            onResult={handleResult}
            onHome={() => setScreen('home')}
          />
        )}
        {screen === 'result' && (
          <ResultScreen
            diagnosis={diagnosis}
            questionCount={questionCount}
            consultationId={consultationId}
            onPlayAgain={handleStart}
            onHome={() => setScreen('home')}
          />
        )}
        {screen === 'settings' && (
          <SettingsScreen
            user={user}
            onBack={() => setScreen('home')}
            onLogout={handleLogout}
          />
        )}
      </div>
    </div>
  );
}
