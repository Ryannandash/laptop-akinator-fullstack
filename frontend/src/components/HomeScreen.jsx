export default function HomeScreen({ user, onStart, onSettings, onLogout }) {
  return (
    <div className="home-screen">
      <div className="home-topbar">
        <button className="icon-btn" onClick={onSettings} title="Pengaturan">⚙️</button>
        <div className="user-badge" onClick={onSettings}>
          <span className="user-avatar">{user.charAt(0).toUpperCase()}</span>
          <span className="user-name">{user}</span>
        </div>
      </div>

      <div className="home-genie-area">
        <div className="genie-wrapper">
          <div className="genie-aura" />
          <div className="genie-emoji">🧞</div>
          <div className="genie-smoke">
            <svg viewBox="0 0 120 60" className="smoke-svg">
              <ellipse cx="60" cy="50" rx="55" ry="12" fill="#7c3aed" opacity="0.18" />
              <ellipse cx="60" cy="42" rx="35" ry="8" fill="#7c3aed" opacity="0.12" />
            </svg>
          </div>
        </div>

        <div className="home-badge-icon">💻</div>
      </div>

      <div className="home-text-area">
        <h2 className="home-title">Laptop Akinator</h2>
        <p className="home-subtitle">
          Pikirkan kerusakan atau masalah pada laptopmu... Aku akan mendiagnosanya!
        </p>
      </div>

      <button className="btn-challenge" onClick={onStart}>
        <span className="btn-challenge-main">MULAI</span>
        <span className="btn-challenge-sub">Aku akan membaca masalahmu</span>
      </button>

      <button className="btn-ghost-small" onClick={onLogout}>Keluar</button>
    </div>
  );
}
