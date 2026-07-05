import { symptoms, diagnoses, rules } from '../data/knowledgeBase';

// Urutan tetap gejala yang ditanya (berurutan sesuai nomor G01-G26)
const QUESTION_ORDER = [
  'G03','G01','G02','G24', // Power/mati total dulu
  'G04','G05','G15',       // Perilaku sistem
  'G19',                   // Panas
  'G06','G07','G08','G09', // Layar
  'G10','G11','G12','G26', // Baterai & charger
  'G16','G17','G18','G25', // Boot & harddisk
  'G13','G14',             // Input
  'G20',                   // Audio
  'G21','G22','G23',       // Port & jaringan
];

export function toBoolean(answer) {
  if (answer === 'yes' || answer === 'probably_yes') return true;
  if (answer === 'no' || answer === 'probably_not') return false;
  return null;
}

export function evaluateRule(rule, answers) {
  const { conditions, type } = rule;
  if (type === 'AND') {
    return conditions.every((gId) => toBoolean(answers[gId]) === true);
  } else if (type === 'OR') {
    return conditions.some((gId) => toBoolean(answers[gId]) === true);
  }
  return false;
}

export function getDiagnosis(answers) {
  const matched = rules.filter((rule) => evaluateRule(rule, answers));
  if (matched.length === 0) return null;

  const scoreMap = {};
  matched.forEach((rule) => {
    scoreMap[rule.result] = (scoreMap[rule.result] || 0) + 1;
  });
  const topId = Object.entries(scoreMap).sort((a, b) => b[1] - a[1])[0][0];
  return diagnoses.find((d) => d.id === topId) || null;
}

// Cek apakah sebuah rule masih mungkin terpenuhi (belum ada kondisi AND yang false)
function isRuleStillPossible(rule, answers) {
  if (rule.type === 'AND') {
    return rule.conditions.every((gId) => {
      const ans = answers[gId];
      if (ans === undefined) return true; // belum dijawab, masih mungkin
      return toBoolean(ans) !== false;    // false = sudah gugur
    });
  }
  if (rule.type === 'OR') {
    // Masih mungkin kalau ada kondisi yang belum dijawab atau sudah true
    return rule.conditions.some((gId) => {
      const ans = answers[gId];
      if (ans === undefined) return true;
      return toBoolean(ans) === true;
    });
  }
  return false;
}

// Ambil semua gejala yang masih relevan dari rules yang masih mungkin
function getActiveSymptomIds(answers) {
  const activeIds = new Set();
  rules.forEach((rule) => {
    if (isRuleStillPossible(rule, answers)) {
      rule.conditions.forEach((gId) => {
        if (!(gId in answers)) activeIds.add(gId);
      });
    }
  });
  return activeIds;
}

export function getNextQuestion(answers) {
  const activeIds = getActiveSymptomIds(answers);
  if (activeIds.size === 0) return null;

  // Tanya berdasarkan urutan tetap QUESTION_ORDER
  for (const id of QUESTION_ORDER) {
    if (activeIds.has(id)) {
      return symptoms.find((s) => s.id === id) || null;
    }
  }
  return null;
}

export function shouldConclude(answers) {
  // Ada rule yang sudah terpenuhi
  const matched = rules.filter((rule) => evaluateRule(rule, answers));
  if (matched.length > 0) return true;

  // Tidak ada rule yang masih mungkin
  const next = getNextQuestion(answers);
  return next === null;
}
