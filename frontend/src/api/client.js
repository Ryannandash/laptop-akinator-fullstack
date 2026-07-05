const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('akinator_token');
}

export function setToken(token) {
  if (token) localStorage.setItem('akinator_token', token);
  else localStorage.removeItem('akinator_token');
}

async function request(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || 'Terjadi kesalahan pada server');
  }
  return data;
}

// ---- Auth ----
export const authApi = {
  register: (payload) => request('/api/auth/register', { method: 'POST', body: payload }),
  login: (payload) => request('/api/auth/login', { method: 'POST', body: payload }),
  me: () => request('/api/auth/me', { auth: true }),
};

// ---- Diagnosis ----
export const diagnosisApi = {
  symptoms: () => request('/api/diagnosis/symptoms'),
  damages: () => request('/api/diagnosis/damages'),
  start: () => request('/api/diagnosis/start', { method: 'POST', body: {}, auth: true }),
  nextQuestion: (consultationId) => request(`/api/diagnosis/${consultationId}/next-question`),
  answer: (consultationId, symptomId, answerValue) =>
    request(`/api/diagnosis/${consultationId}/answer`, {
      method: 'POST',
      body: { symptom_id: symptomId, answer_value: answerValue },
    }),
  result: (consultationId) => request(`/api/diagnosis/${consultationId}/result`),
  feedback: (consultationId, isCorrect, actualDamageId) =>
    request(`/api/diagnosis/${consultationId}/feedback`, {
      method: 'POST',
      body: { is_correct: isCorrect, actual_damage_id: actualDamageId || null },
    }),
};
