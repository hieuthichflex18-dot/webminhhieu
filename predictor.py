# predictor.py
from collections import Counter


def normalize_history(data):
    if not data:
        return []
    arr = []
    if isinstance(data, list):
        arr = data
    elif isinstance(data, dict):
        for k in ["data", "history", "result", "items", "list", "ket_qua"]:
            if isinstance(data.get(k), list):
                arr = data[k]
                break

    out = []
    for item in arr:
        if isinstance(item, str):
            s = item.upper()
            if "T" in s:
                out.append("T")
            elif "X" in s:
                out.append("X")
        elif isinstance(item, dict):
            v = str(item.get("result") or item.get("ket_qua") or item.get("value") or "").upper()
            if "T" in v:
                out.append("T")
            elif "X" in v:
                out.append("X")
            else:
                total = item.get("sum") or item.get("total") or item.get("tong")
                if isinstance(total, (int, float)):
                    if total >= 11:
                        out.append("T")
                    else:
                        out.append("X")
    return out


def markov_predict(history, order):
    if len(history) < order + 2:
        return None, 0
    transitions = {}
    for i in range(len(history) - order):
        state = tuple(history[i:i + order])
        nxt = history[i + order]
        if state not in transitions:
            transitions[state] = Counter()
        transitions[state][nxt] = transitions[state][nxt] + 1

    current_state = tuple(history[-order:])
    if current_state not in transitions:
        return None, 0
    counts = transitions[current_state]
    total = sum(counts.values())
    if total < 2:
        return None, 0
    top = counts.most_common(1)[0]
    pred = top[0]
    prob = top[1] / total
    return pred, int(prob * 100)


def detect_streak(history):
    if not history:
        return None, 0
    last = history[-1]
    streak = 1
    i = len(history) - 2
    while i >= 0:
        if history[i] == last:
            streak = streak + 1
        else:
            break
        i = i - 1
    return last, streak


def detect_alternating(history, depth):
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
    last3 = history[-3] + history[-2] + history[-1]
    patterns = {}
    patterns["TTT"] = ("X", 35)
    patterns["XXX"] = ("T", 35)
    patterns["TTX"] = ("T", 15)
    patterns["XXT"] = ("X", 15)
    patterns["TXX"] = ("T", 15)
    patterns["XTT"] = ("X", 15)
    patterns["TXT"] = ("X", 22)
    patterns["XTX"] = ("T", 22)
    if last3 in patterns:
        return patterns[last3]
    return None


def analyze(history):
    if len(history) < 3:
        return {
            "prediction": "T",
            "prediction_text": "TAI",
            "confidence": 0,
            "reasons": ["Chua du du lieu"],
            "streak": 0,
            "last": None,
            "freq_t": 0,
            "freq_x": 0,
            "history_len": 0
        }

    score_t = 0
    score_x = 0
    reasons = []

    last, streak = detect_streak(history)

    if streak >= 5:
        if last == "T":
            score_x = score_x + 45
            reasons.append("Bet " + str(streak) + " phien TAI")
        else:
            score_t = score_t + 45
            reasons.append("Bet " + str(streak) + " phien XIU")
    elif streak >= 3:
        if last == "T":
            score_x = score_x + 20
            reasons.append("Bet " + str(streak) + " phien TAI nhe")
        else:
            score_t = score_t + 20
            reasons.append("Bet " + str(streak) + " phien XIU nhe")

    if detect_alternating(history, 6):
        if last == "T":
            score_x = score_x + 30
        else:
            score_t = score_t + 30
        reasons.append("Cau 1-1 dao chieu")

    mp, mp_conf = markov_predict(history, 2)
    if mp is not None:
        if mp == "T":
            score_t = score_t + int(mp_conf * 0.4)
        else:
            score_x = score_x + int(mp_conf * 0.4)
        reasons.append("Markov 2: " + str(mp) + " " + str(mp_conf) + "%")

    mp3, mp3_conf = markov_predict(history, 3)
    if mp3 is not None and mp3_conf > 55:
        if mp3 == "T":
            score_t = score_t + 15
        else:
            score_x = score_x + 15
        reasons.append("Markov 3: " + str(mp3) + " " + str(mp3_conf) + "%")

    pat = detect_pattern_3(history)
    if pat is not None:
        pred = pat[0]
        bonus = pat[1]
        if pred == "T":
            score_t = score_t + bonus
        else:
            score_x = score_x + bonus
        reasons.append("Mau 3 phien: " + str(pred))

    t_cnt = history.count("T")
    x_cnt = history.count("X")
    total = len(history)
    freq_t = t_cnt / total
    freq_x = x_cnt / total

    if freq_t > 0.68:
        score_x = score_x + 25
        reasons.append("TAI nhieu: " + str(int(freq_t * 100)) + "%")
    elif freq_x > 0.68:
        score_t = score_t + 25
        reasons.append("XIU nhieu: " + str(int(freq_x * 100)) + "%")

    if score_t > score_x:
        pred = "T"
        conf = score_t
    elif score_x > score_t:
        pred = "X"
        conf = score_x
    else:
        if last is not None:
            pred = last
        else:
            pred = "T"
        conf = 30

    if conf > 96:
        conf = 96
    if conf < 35:
        conf = 35

    if pred == "T":
        pred_text = "TAI"
    else:
        pred_text = "XIU"

    return {
        "prediction": pred,
        "prediction_text": pred_text,
        "confidence": conf,
        "reasons": reasons,
        "streak": streak,
        "last": last,
        "freq_t": round(freq_t, 2),
        "freq_x": round(freq_x, 2),
        "history_len": total
    }
