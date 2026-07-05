import { useState, useEffect } from 'react';
import { diagnosisApi } from '../api/client';
import { LuHouse, LuArrowLeft } from "react-icons/lu";

const ANSWERS = [
  { value: 'yes', label: 'Ya' },
  { value: 'probably_yes', label: 'Mungkin Ya' },
  { value: 'dont_know', label: 'Tidak Tahu' },
  { value: 'probably_not', label: 'Mungkin Tidak' },
  { value: 'no', label: 'Tidak' },
];

export default function GameScreen({ onResult, onHome }) {
  const [consultationId, setConsultationId] = useState(null);
  const [currentSymptom, setCurrentSymptom] = useState(null);
  const [questionCount, setQuestionCount] = useState(0);
  const [animKey, setAnimKey] = useState(0);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const res = await diagnosisApi.start();
        if (!active) return;
        setConsultationId(res.consultation_id);
        setCurrentSymptom(res.question);
      } catch (err) {
        if (!active) return;
        setError('Tidak bisa terhubung ke server diagnosis. Pastikan backend berjalan.');
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const normalizeResult = (result) => {
    if (!result) return null;
    return {
      id: result.damage_id,
      name: result.name,
      icon: result.icon,
      solution: result.solution,
      confidence: result.confidence,
      alternatives: result.alternatives || [],
    };
  };

  const handleAnswer = async (value) => {
    if (!consultationId || !currentSymptom || submitting) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await diagnosisApi.answer(consultationId, currentSymptom.id, value);
      setHistory((h) => [...h, { symptom: currentSymptom, answer: value }]);
      setQuestionCount(res.question_count);
      setAnimKey((k) => k + 1);

      if (res.finished) {
        setTimeout(() => onResult(normalizeResult(res.result), res.question_count, consultationId), 300);
        return;
      }
      setCurrentSymptom(res.next_question);
    } catch (err) {
      setError('Gagal mengirim jawaban. Coba lagi.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    // Kembali secara visual ke pertanyaan sebelumnya (jawaban di server tidak
    // dihapus, jadi mundur di sini murni membantu pengguna meninjau ulang).
    if (history.length === 0) return;
    const prev = [...history];
    const last = prev.pop();
    setHistory(prev);
    setCurrentSymptom(last.symptom);
    setQuestionCount(Math.max(0, questionCount - 1));
  };

  if (loading) {
    return (
      <div className="game-screen">
        <p className="game-genie-caption">Memulai sesi diagnosis...</p>
      </div>
    );
  }

  if (error && !currentSymptom) {
    return (
      <div className="game-screen">
        <p className="game-genie-caption">{error}</p>
        <button className="glass-btn home-btn" onClick={onHome}>
          <LuHouse size={24} />
        </button>
      </div>
    );
  }

  if (!currentSymptom) return null;

  return (
    <div className="game-screen">
      <div className="game-topbar">
        <button
          className="glass-btn home-btn"
          onClick={onHome}
        >
          <LuHouse size={24} />
        </button>

        {history.length > 0 && (
          <button
            className="glass-btn back-btn"
            onClick={handleBack}
          >
            <LuArrowLeft size={22} />
            <span>Kembali</span>
          </button>
        )}
      </div>

      <div className="game-genie-area">
        <div className="game-genie-laptop">
          <svg width="90" height="90" viewBox="0 0 90 90" fill="none">
            <rect x="12" y="18" width="66" height="44" rx="5" fill="#6b21a8" stroke="#f5c518" strokeWidth="2" />
            <rect x="18" y="24" width="54" height="32" rx="3" fill="#1a0530" />
            <rect x="5" y="62" width="80" height="8" rx="4" fill="#4c1d95" stroke="#f5c518" strokeWidth="1.5" />
            <circle cx="45" cy="66" r="2" fill="#f5c518" opacity="0.6" />
            <circle cx="45" cy="36" r="6" fill="none" stroke="#f5c518" strokeWidth="1.5" opacity="0.5" />
            <path d="M39 36 L45 30 L51 36 L45 42 Z" stroke="#f5c518" strokeWidth="1.5" fill="none" opacity="0.7" />
          </svg>
        </div>
        <p className="game-genie-caption">Apakah laptop kamu mengalami gejala berikut?</p>
      </div>

      <div className="game-question-card">
        <div className="question-badge">
          <span className="q-label">Pertanyaan No. {questionCount + 1}</span>
          <span className="q-id">Gejala {currentSymptom.id}</span>
        </div>

        <p key={animKey} className="question-text anim-fadein">
          {currentSymptom.text}
        </p>
      </div>

      {error && <p className="auth-error">{error}</p>}

      <div className="answer-grid">
        {ANSWERS.map((ans) => (
          <button
            key={ans.value}
            className={`btn-answer btn-answer--${ans.value}`}
            onClick={() => handleAnswer(ans.value)}
            disabled={submitting}
          >
            {ans.label}
          </button>
        ))}
      </div>

      <div className="game-progress">
        <span className="progress-text">{questionCount} gejala telah diperiksa</span>
        <div className="progress-dots">
          {Array.from({ length: Math.min(questionCount, 12) }).map((_, i) => (
            <span key={i} className="dot dot--done" />
          ))}
          <span className="dot dot--current" />
        </div>
      </div>
    </div>
  );
}
