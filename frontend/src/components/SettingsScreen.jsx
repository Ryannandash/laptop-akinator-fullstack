import { useState } from 'react';

export default function SettingsScreen({ user, onBack, onLogout }) {
  const [settings, setSettings] = useState({
    language: 'Indonesia',
    music: true,
    effects: true,
    voice: false,
    animations: true,
    sensitiveFilter: false,
  });

  const toggle = (key) => {
    setSettings({ ...settings, [key]: !settings[key] });
  };

  return (
    <div className="settings-screen">
      <div className="settings-header">
        <button className="icon-btn" onClick={onBack}>◀</button>
        <h1 className="settings-screen-title">Pengaturan</h1>
        <div style={{ width: 36 }} />
      </div>

      <div className="settings-profile">
        <div className="settings-avatar">{user.charAt(0).toUpperCase()}</div>
        <div className="settings-profile-info">
          <div className="settings-username">{user}</div>
          <div className="settings-role">Detektif Laptop</div>
        </div>
      </div>

      <div className="settings-section-label">PENGATURAN</div>

      <div className="settings-list">
        <div className="settings-item settings-item--arrow">
          <span className="settings-item-icon">🌐</span>
          <span className="settings-item-label">Bahasa</span>
          <div className="settings-item-right">
            <span className="settings-item-value">{settings.language}</span>
            <span className="settings-chevron">›</span>
          </div>
        </div>

        <div className="settings-item settings-item--arrow">
          <span className="settings-item-icon">🔞</span>
          <span className="settings-item-label">Filter Konten Sensitif</span>
          <div className="settings-item-right">
            <span className="settings-item-value">{settings.sensitiveFilter ? 'Aktif' : 'Nonaktif'}</span>
            <span className="settings-chevron">›</span>
          </div>
        </div>

        {[
          { key: 'music', icon: '🎵', label: 'Musik' },
          { key: 'effects', icon: '✨', label: 'Efek Suara' },
          { key: 'voice', icon: '🎤', label: 'Mode Suara' },
          { key: 'animations', icon: '🎬', label: 'Animasi' },
        ].map(({ key, icon, label }) => (
          <div className="settings-item" key={key}>
            <span className="settings-item-icon">{icon}</span>
            <span className="settings-item-label">{label}</span>
            <div
              className={`toggle-switch ${settings[key] ? 'toggle-switch--on' : ''}`}
              onClick={() => toggle(key)}
            >
              <div className="toggle-thumb" />
            </div>
          </div>
        ))}
      </div>

      <div className="settings-section-label">TENTANG</div>
      <div className="settings-list">
        <div className="settings-item settings-item--arrow">
          <span className="settings-item-icon">📋</span>
          <span className="settings-item-label">Basis Pengetahuan</span>
          <span className="settings-chevron">›</span>
        </div>
        <div className="settings-item settings-item--arrow">
          <span className="settings-item-icon">⭐</span>
          <span className="settings-item-label">Beri Rating Aplikasi</span>
          <span className="settings-chevron">›</span>
        </div>
      </div>

      <button className="btn-logout" onClick={onLogout}>
        Keluar
      </button>

      <div className="settings-footer">
        Laptop Akinator v1.0 · Sistem Pakar Forward Chaining
      </div>
    </div>
  );
}
