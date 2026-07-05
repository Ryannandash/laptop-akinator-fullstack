import { useState } from 'react';
import { LuArrowLeft } from "react-icons/lu";
import { diagnosisApi } from '../api/client';

function confidenceLevel(confidence) {
  if (confidence >= 70) return { label: 'Tinggi', className: 'confidence--high' };
  if (confidence >= 40) return { label: 'Sedang', className: 'confidence--medium' };
  return { label: 'Rendah', className: 'confidence--low' };
}

export default function ResultScreen({ diagnosis, questionCount, consultationId, onPlayAgain, onHome }) {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState('');

  const sendFeedback = async (isCorrect) => {
    if (consultationId && !feedbackSent) {
      try {
        await diagnosisApi.feedback(consultationId, isCorrect, isCorrect ? diagnosis?.id : null);
      } catch {
        // Feedback gagal terkirim tidak menghalangi pengguna melanjutkan
      }
    }
    setFeedbackSent(true);
    setFeedbackMsg(isCorrect ? 'Terima kasih atas konfirmasinya!' : 'Terima kasih, masukanmu membantu sistem belajar.');
    setTimeout(() => onPlayAgain(), 700);
  };

  if (!diagnosis) {
    return (
      <div className="result-screen">
        <div className="result-genie-area">
          <div className="result-genie-emoji">😅</div>
        </div>
        <div className="result-card result-card--fail">
          <h2 className="result-card-title">Aku Menyerah!</h2>
          <p className="result-card-subtitle">
            Masalah laptopmu sangat unik! Aku tidak berhasil mendiagnosanya setelah {questionCount} pertanyaan.
            Coba konsultasikan ke teknisi langsung ya.
          </p>
          <div className="result-actions">
            <button className="btn-primary" onClick={onPlayAgain}>Coba Lagi</button>
            <button className="btn-ghost" onClick={onHome}>Kembali ke Awal</button>
          </div>
        </div>
      </div>
    );
  }

  const confidence = typeof diagnosis.confidence === 'number' ? diagnosis.confidence : null;
  const level = confidence !== null ? confidenceLevel(confidence) : null;

  return (
    <div className="result-screen">
      <div className="result-genie-area">
        <div className="result-genie-thinking">🩺</div>
        <div className="result-think-text">Diagnosa Selesai</div>
      </div>

      <div className="result-card">
        <div className="result-diagnosis-icon">{diagnosis.icon}</div>
        <h2 className="result-diagnosis-name">{diagnosis.name}</h2>
        <div className="result-code-badge">Kode: {diagnosis.id}</div>

        {confidence !== null && (
          <div className={`result-confidence-badge ${level.className}`}>
            <div className="confidence-ring" style={{ '--pct': `${confidence}%` }}>
              <span className="confidence-value">{confidence}%</span>
            </div>
            <div className="confidence-text">
              <span className="confidence-label">Akurasi Diagnosis</span>
              <span className="confidence-sub">Tingkat keyakinan: {level.label}</span>
            </div>
          </div>
        )}

        {diagnosis.alternatives && diagnosis.alternatives.length > 0 && (
          <div className="result-alternatives">
            <span className="result-alternatives-label">Kemungkinan lain:</span>
            {diagnosis.alternatives.map((alt) => (
              <span key={alt.damage_id} className="result-alternative-chip">
                {alt.name} ({alt.confidence}%)
              </span>
            ))}
          </div>
        )}

        <div className="result-divider" />

        <div className="result-solution-section">
          <div className="result-solution-label">💡 Solusi yang Disarankan</div>
          <p className="result-solution-text">{diagnosis.solution}</p>
        </div>

        <div className="result-stats">
          <div className="stat-item">
            <span className="stat-value">{questionCount}</span>
            <span className="stat-label">Pertanyaan</span>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <span className="stat-value">{diagnosis.id}</span>
            <span className="stat-label">Diagnosis</span>
          </div>
        </div>

        {feedbackMsg ? (
          <div className="result-confirm-label">{feedbackMsg}</div>
        ) : (
          <>
            <div className="result-confirm-label">Apakah diagnosa sudah tepat?</div>
            <div className="result-confirm-btns">
              <button className="btn-confirm btn-confirm--yes" onClick={() => sendFeedback(true)}>
                Ya, Solusi Tepat!
              </button>
              <button className="btn-confirm btn-confirm--no" onClick={() => sendFeedback(false)}>
                Tidak
              </button>
            </div>
          </>
        )}
      </div>

      <button className="back-home-btn" onClick={onHome}>
        <LuArrowLeft size={18} />
        <span>Kembali ke Awal</span>
      </button>
    </div>
  );
}
