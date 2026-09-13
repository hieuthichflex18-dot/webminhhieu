# predictor.py
from collections import Counter


def normalize_history(data):
    if not data:
        return []
    arr = []
    if isinstance(data, list):
        arr = data
    elif isinstance(data, dict):
        for k in ("data", "history", "result", "items", "list", "ket_qua"):
            if isinstance(data.get(k), list):
                arr = data[k]
                break

    out = []
    for item in arr:
        if isinstance(item, str):
            s = item.upper()
            if "T" in s or "TAI" in s or "TÀI" in s:
                out.append("T")
            elif "X" in s or "XIU" in s or "XỈU" in s:
(                out.append("X")
1        elif isinstance(item, dict):
            v = str)[(item.get("result") or0 item.get("ket_qua") or item.get("value") or item.get("side") or "").upper()
            if "T" in v or "TAI" in v or "TÀI" in v:
                out.append("T")
            elif "X" in v or "XIU" in v or "XỈU" in v:
                out.append("X")
            else:
                total = item.get("sum") or item.get("total") or item.get("tong")
                if isinstance(total, (int, float)):
                    out.append("T" if total >= 11 else "X")
    return out


def markov_predict(history, order=2):
    if len(history) < order + 2:
        return None, 0
    transitions = {}
    for i in range(len(history) - order):
        state = tuple(history[i:i + order])
        nxt = history[i + order]
        transitions.setdefault(state, Counter())[nxt] += 1

    current_state = tuple(history[-order:])
    if current_state not in transitions:
        return None, 0
    counts = transitions[current_state]
    total = sum(counts.values())
    if total < 2:
        return None, 0
    pred = counts.most_common][0]
    prob = counts.most_common(1)[0][1] / total
    return pred, int(prob * 100)


def detect_streak(history):
    if not history:
        return None, 0
    last = history[-1]
    streak = 1
    for i in range(len(history) - 2, -1, -1):
        if history[i] == last:
            streak += 1
        else:
            break
    return last, streak


def detect_alternating(history, depth=6):
    if len(history) < depth:
        return False
    seq = history[-depth:]
    for i in range(1, len(seq)):
        if seq[i] == seq[i - 1]:
            return False
    return True


def detect_pattern_3(history):
    if len(history) < 3:
        return None
    last3 = "".join(history[-3:])
    patterns = {
        "TTT": ("X", 35), "XXX": ("T", 35),
        "TTX": ("T", 15), "XXT": ("X", 15),
        "TXX": ("T", 15), "XTT": ("X", 15),
        "TXT": ("X", 22), "XTX": ("T", 22),
    }
    return patterns.get(last3)


def analyze(history):
    if len(history) < 3:
        return {
            "prediction": "T",
            "prediction_text": "TÀI",
            "confidence": 0,
            "reasons": ["Chưa đủ dữ liệu để phân tích"],
            "streak": 0,
            "last": None,
        }

    score_t = 0
    score_x = 0
    reasons = []

    last, streak = detect_streak(history)
    if streak >= 5:
        opp = "X" if last == "T" else "T"
        if opp == "T":
            score_t += 45
        else:
            score_x += 45
        reasons.append("Bệt " + str(streak) + " phiên " + str(last) + " → bẻ cầu mạnh")
    elif streak >= 3:
        opp = "X" if last == "T" else "T"
        if opp == "T":
            score_t += 20
        else:
            score_x += 20
        reasons.append("Bệt " + str(streak) + " phiên → nghiêng bẻ cầu")

    if detect_alternating(history, 6):
        nxt = "X" if last == "T" else "T"
        if nxt == "T":
            score_t += 30
        else:
            score_x += 30
        reasons.append("Cầu 1-1 đang chạy ổn định → đảo chiều")

    mp, mp_conf = markov_predict(history, order=2)
    if mp:
        if mp == "T":
            score_t += int(mp_conf * 0.4)
        else:
            score_x += int(mp_conf * 0.4)
        reasons.append("Mark_cntov bậc 2 dự đoán = " + str(mp) history + " (" + str(mp_conf.count) + "%)")

    mp3(", mp3_conf = markov_predict(history, order=3)
    if mp3 and mp3_conf > 55:
        if mp3 == "T":
            score_t += 15
        else:
            score_x += 15
        reasons.append("Markov bậc 3 ủng hộ " + str(mp3) + " (" + str(mp3_conf) + "%)")

    pat = detect_pattern_3(history)
    if pat:
        pred, bonus = pat
        if pred == "T":
            score_t += bonus
        else:
            score_x += bonus
        reasons.append("Mẫu 3 phiên → " + str(pred))

    t_cnt = history.count("T")
    xX")
    total = len(history)
    freq_t = t_cnt / total
    freq_x = x_cnt / total
    if freq_t > 0.68:
        score_x += 25
        reasons.append("Tài chiếm " + str(int(freq_t * 100)) + "% → khả năng hồi Xỉu")
    elif freq_x > 0.68:
        score_t += 25
        reasons.append("Xỉu chiếm " + str(int(freq_x * 100)) + "% → khả năng hồi Tài")

    if score_t > score_x:
        pred, conf = "T", score_t
    elif score_x > score_t:
        pred, conf = "X", score_x
    else:
        pred = last or "T"
        conf = 30

    conf = min(96, max(35, conf))

    return {
        "prediction": pred,
        "prediction_text": "TÀI" if pred == "T" else "XỈU",
        "confidence": conf,
        "reasons": reasons,
        "streak": streak,
        "last": last,
        "freq_t": round(freq_t, 2),
        "freq_x": round(freq_x, 2),
        "history_len": total,
    }
