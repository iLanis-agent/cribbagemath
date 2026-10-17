#!/usr/bin/env python3
# Cribbage Math oracle - mirrors engine.js float-for-float.
import json, math

_RANKS = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10,
          "T":10, "J":11, "Q":12, "K":13}
_WORDS = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"}

import re
def _parse(code):
    m = re.match(r"^(A|[2-9]|10|T|J|Q|K)(H|D|C|S)$", str(code).strip().upper())
    if not m:
        raise ValueError(f"{code} is not a card")
    rank = _RANKS[m.group(1)]
    return {"rank": rank, "value": min(rank, 10), "suit": m.group(2), "code": m.group(1) + m.group(2)}

def _word(n):
    return _WORDS.get(n, str(n))

def hand_truth(hand_codes, starter_code):
    if len(hand_codes) != 4:
        raise ValueError("four cards in hand plus the starter")
    codes = list(hand_codes) + [starter_code]
    for c in codes:
        if str(c).strip() == "":
            raise ValueError("enter all 5 cards: four in hand plus the starter")
    cards = [_parse(c) for c in codes]
    seen = set()
    for card in cards:
        if card["code"] in seen:
            raise ValueError(f"the {card['code']} shows up twice")
        seen.add(card["code"])

    fifteens = 0
    for mask in range(1, 32):
        s = sum(cards[b]["value"] for b in range(5) if mask & (1 << b))
        if s == 15:
            fifteens += 1

    pairs = 0
    for a in range(5):
        for b in range(a + 1, 5):
            if cards[a]["rank"] == cards[b]["rank"]:
                pairs += 1

    mult = {}
    for card in cards:
        mult[card["rank"]] = mult.get(card["rank"], 0) + 1
    run_len = 0
    run_count = 0
    for L in (5, 4, 3):
        if run_count:
            break
        for r in range(1, 13 - L + 2):
            p = 1
            for k in range(L):
                m2 = mult.get(r + k, 0)
                if m2 == 0:
                    p = 0
                    break
                p *= m2
            run_count += p
        if run_count:
            run_len = L

    flush = 0
    if cards[0]["suit"] == cards[1]["suit"] == cards[2]["suit"] == cards[3]["suit"]:
        flush = 5 if cards[3]["suit"] == cards[4]["suit"] else 4

    nobs = 0
    for n in range(4):
        if cards[n]["rank"] == 11 and cards[n]["suit"] == cards[4]["suit"]:
            nobs = 1

    comps = []
    comps.append("no fifteens" if fifteens == 0 else
                 f"{_word(fifteens)} fifteen" + ("" if fifteens == 1 else "s") + f" ({2 * fifteens})")
    comps.append(("a pair" if pairs == 1 else f"{_word(pairs)} pairs") + f" ({2 * pairs})" if pairs else "no pairs")
    comps.append("no runs" if run_len == 0 else
                 ("a run of " + _word(run_len) if run_count == 1 else f"{_word(run_count)} runs of {_word(run_len)}")
                 + f" ({run_count * run_len})")
    comps.append("no flush" if flush == 0 else ("a flush (4)" if flush == 4 else "a five-card flush (5)"))
    comps.append("no nobs" if nobs == 0 else "nobs (1)")
    total = 2 * fifteens + 2 * pairs + run_count * run_len + flush + nobs
    return ", ".join(comps[:4]) + ", and " + comps[4] + f" - {total} point" + ("" if total == 1 else "s") + "."

def peg_truth(current, pip):
    if not math.isfinite(current) or current < 0 or current > 30:
        raise ValueError("the count must be under 31")
    if not math.isfinite(pip) or pip < 1 or pip > 10:
        raise ValueError("a card is worth 1 to 10")
    art = "an" if pip == 8 else "a"
    total = current + pip
    if total == 31:
        return f"{current} plus {art} {pip} is 31 for 2."
    if total < 31:
        return f"{current} plus {art} {pip} is {total} - {31 - total} short of the 2."
    return f"{current} plus {art} {pip} is {total} - it doesn't go."

def win_truth(score, points):
    if not math.isfinite(score) or score < 0 or score > 120:
        raise ValueError("the game is already over")
    if not math.isfinite(points) or points < 0 or points > 29:
        raise ValueError("a hand scores at most 29")
    total = score + points
    if total >= 121:
        return f"{score} plus {points} is {total} - pegged out."
    return f"{score} plus {points} is {total} - {121 - total} to go."

CASES = [
    ("handTruth", (["5H", "5D", "5S", "JC"], "5C")),     # the 29 hand
    ("handTruth", (["5H", "5D", "5C", "JD"], "5S")),     # 28, no nobs
    ("handTruth", (["4H", "4D", "5S", "6C"], "AH")),     # double run territory
    ("handTruth", (["2H", "5H", "9H", "KH"], "3C")),     # four flush
    ("handTruth", (["2H", "5H", "9H", "KH"], "QH")),     # five flush
    ("handTruth", (["2H", "4D", "8S", "KC"], "6C")),     # the zero hand
    ("handTruth", (["7H", "8D", "9S", "TH"], "JC")),     # run of four + fifteen
    ("handTruth", (["5H", "5H", "5S", "JC"], "5C")),     # duplicate
    ("handTruth", (["5H", "XQ", "5S", "JC"], "5C")),     # bad code
    ("handTruth", (["5H", "", "5S", "JC"], "5C")),       # empty
    ("pegTruth", (24, 7)),
    ("pegTruth", (24, 6)),
    ("pegTruth", (24, 8)),
    ("pegTruth", (31, 5)),
    ("winTruth", (118, 6)),
    ("winTruth", (109, 6)),
    ("winTruth", (121, 4)),
    ("winTruth", (110, 30)),
]

FNS = {"handTruth": hand_truth, "pegTruth": peg_truth, "winTruth": win_truth}

out = []
for name, args in CASES:
    try:
        expected = FNS[name](*args)
    except ValueError as e:
        expected = "ERR:" + str(e)
    out.append({"fn": name, "args": list(args), "expected": expected})

with open("expected.json", "w") as f:
    f.write(json.dumps(out, indent=2) + "\n")
print(f"{len(out)} cases written")
