"""
Mesin inferensi: Forward Chaining + Certainty Factor (CF).

Alur:
1. Setiap jawaban user terhadap gejala diubah jadi CF_user (data.ANSWER_CF).
2. CF_evidence(gejala, kerusakan) = CF_pakar(gejala, kerusakan) * CF_user(gejala)
3. Untuk tiap kerusakan, semua CF_evidence yang relevan (CF_pakar > 0) digabung
   memakai rumus kombinasi CF berurutan (CF combine).
4. Kerusakan dengan CF gabungan tertinggi = hasil diagnosis.
   Akurasi/keyakinan yang ditampilkan ke user = CF gabungan tsb dalam persen.
5. Pemilihan pertanyaan berikutnya bersifat adaptif: gejala yang paling
   membedakan kandidat kerusakan yang sedang unggul akan ditanyakan lebih dulu.
"""
from .data import SYMPTOMS, DAMAGES, WEIGHTS, ANSWER_CF, MAX_QUESTIONS, CONCLUDE_CF_THRESHOLD


def cf_combine(cf1: float, cf2: float) -> float:
    if cf1 >= 0 and cf2 >= 0:
        return cf1 + cf2 * (1 - cf1)
    if cf1 < 0 and cf2 < 0:
        return cf1 + cf2 * (1 + cf1)
    denom = 1 - min(abs(cf1), abs(cf2))
    if denom == 0:
        return 0.0
    return (cf1 + cf2) / denom


def compute_scores(answers: dict) -> dict:
    """answers: {symptom_id: answer_value} -> {damage_id: cf_gabungan}"""
    scores = {}
    for symptom_id, answer_value in answers.items():
        cf_user = ANSWER_CF.get(answer_value)
        if cf_user is None:
            continue
        for damage_id, cf_pakar in WEIGHTS.get(symptom_id, {}).items():
            cf_evidence = cf_pakar * cf_user
            if damage_id not in scores:
                scores[damage_id] = cf_evidence
            else:
                scores[damage_id] = cf_combine(scores[damage_id], cf_evidence)
    return scores


def ranked_damages(answers: dict):
    scores = compute_scores(answers)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return ranked  # list of (damage_id, cf) sorted desc


def get_next_question(answers: dict):
    """Pilih gejala berikutnya secara adaptif berdasarkan kandidat kerusakan
    yang sedang unggul. Mengembalikan dict {id, text} atau None jika selesai."""
    answered = set(answers.keys())
    unanswered = [sid for sid in SYMPTOMS if sid not in answered]
    if not unanswered:
        return None
    if len(answered) >= MAX_QUESTIONS:
        return None

    ranked = ranked_damages(answers)
    top_damage_ids = [d for d, cf in ranked[:3] if cf > 0]

    def symptom_priority(sid):
        weights = WEIGHTS.get(sid, {})
        # Prioritaskan gejala yang relevan dengan kandidat teratas saat ini
        top_weight = max((weights.get(d, 0) for d in top_damage_ids), default=0)
        overall_weight = max(weights.values(), default=0)
        return (top_weight, overall_weight)

    best = max(unanswered, key=symptom_priority)
    # Jika gejala terbaik sama sekali tidak relevan (bobot 0 di semua kerusakan
    # yang tersisa) dan sudah ada kandidat yang cukup yakin, hentikan sesi.
    if ranked and ranked[0][1] >= CONCLUDE_CF_THRESHOLD and symptom_priority(best)[0] == 0:
        return None

    return {"id": best, "text": SYMPTOMS[best]}


def should_conclude(answers: dict) -> bool:
    if len(answers) >= MAX_QUESTIONS:
        return True
    return get_next_question(answers) is None


def build_result(answers: dict):
    ranked = ranked_damages(answers)
    if not ranked or ranked[0][1] <= 0:
        return None
    top_id, top_cf = ranked[0]
    confidence = round(max(0.0, min(top_cf, 1.0)) * 100, 1)
    damage = DAMAGES[top_id]
    alternatives = [
        {
            "damage_id": did,
            "name": DAMAGES[did]["name"],
            "confidence": round(max(0.0, min(cf, 1.0)) * 100, 1),
        }
        for did, cf in ranked[1:4] if cf > 0
    ]
    return {
        "damage_id": top_id,
        "name": damage["name"],
        "icon": damage["icon"],
        "solution": damage["solution"],
        "confidence": confidence,
        "alternatives": alternatives,
    }
