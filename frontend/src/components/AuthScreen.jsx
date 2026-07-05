import { useState } from 'react';
import { authApi, setToken } from '../api/client';

export default function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!form.email || !form.password) {
      setError('Email dan password wajib diisi!');
      return;
    }
    if (mode === 'signup' && !form.name) {
      setError('Nama wajib diisi!');
      return;
    }
    setError('');
    setLoading(true);
    try {
      if (mode === 'signup') {
        const res = await authApi.register({
          username: form.name,
          email: form.email,
          password: form.password,
          full_name: form.name,
        });
        setToken(res.token);
        onLogin(res.user.username);
      } else {
        const res = await authApi.login({ email: form.email, password: form.password });
        setToken(res.token);
        onLogin(res.user.username);
      }
    } catch (err) {
      setError(err.message || 'Gagal terhubung ke server. Coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuest = () => {
    onLogin('Tamu');
  };

  return (
    <div className="auth-screen">
      <div className="auth-header">
        <div className="auth-avatar">
          <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
            <circle cx="19" cy="14" r="8" fill="#f5c518" opacity="0.9" />
            <ellipse cx="19" cy="30" rx="13" ry="8" fill="#f5c518" opacity="0.7" />
          </svg>
        </div>
        <h1 className="auth-title">{mode === 'login' ? 'Masuk' : 'Daftar'}</h1>
      </div>

      <div className="auth-body">
        {mode === 'signup' && (
          <p className="auth-subtitle">
            Simpan progres & ikuti papan peringkat detektif laptop!
          </p>
        )}

        {mode === 'signup' && (
          <div className="input-group">
            <input
              type="text"
              placeholder="Nama"
              value={form.name}
              onChange={(e) => { setForm({ ...form, name: e.target.value }); setError(''); }}
              className="auth-input"
            />
          </div>
        )}

        <div className="input-group">
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => { setForm({ ...form, email: e.target.value }); setError(''); }}
            className="auth-input"
          />
        </div>

        <div className="input-group input-password">
          <input
            type={showPass ? 'text' : 'password'}
            placeholder="Password"
            value={form.password}
            onChange={(e) => { setForm({ ...form, password: e.target.value }); setError(''); }}
            className="auth-input"
          />
          <button className="toggle-pass" onClick={() => setShowPass(!showPass)} type="button">
            {showPass ? '⊘' : '◉'}
          </button>
        </div>

        {mode === 'login' && (
          <p className="forgot-pass">Lupa password?</p>
        )}

        {error && <p className="auth-error">{error}</p>}

        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Memproses...' : mode === 'login' ? 'Masuk' : 'Daftar'}
        </button>

        <div className="auth-switch">
          {mode === 'login' ? (
            <span>Belum punya akun?{' '}
              <button className="link-btn" onClick={() => { setMode('signup'); setError(''); }}>Daftar</button>
            </span>
          ) : (
            <span>Sudah punya akun?{' '}
              <button className="link-btn" onClick={() => { setMode('login'); setError(''); }}>Masuk</button>
            </span>
          )}
        </div>

        <div className="divider"><span>atau</span></div>

        <button className="btn-ghost" onClick={handleGuest}>
          Lanjut sebagai Tamu
        </button>
      </div>
    </div>
  );
}
