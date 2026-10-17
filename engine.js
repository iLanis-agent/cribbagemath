// Cribbage Math engine - the hand everyone counts twice, counted once.
// Mirrored float-for-float by oracle.py; keep the op order identical.

var _RANKS = {A:1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, T:10, J:11, Q:12, K:13};
var _WORDS = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten"};

function _parse(code) {
  var m = /^(A|[2-9]|10|T|J|Q|K)(H|D|C|S)$/.exec(String(code).trim().toUpperCase());
  if (!m) throw new Error(code + " is not a card");
  var rank = _RANKS[m[1]];
  return { rank: rank, value: Math.min(rank, 10), suit: m[2], code: m[1] + m[2] };
}

function _word(n) {
  return _WORDS[n] || String(n);
}

// The hand truth: fifteens, pairs, runs, flush, nobs - all of it, once.
function handTruth(handCodes, starterCode) {
  if (handCodes.length !== 4) throw new Error("four cards in hand plus the starter");
  var codes = handCodes.concat([starterCode]);
  for (var i = 0; i < 5; i++) {
    if (String(codes[i]).trim() === "") throw new Error("enter all 5 cards: four in hand plus the starter");
  }
  var cards = codes.map(_parse);
  var seen = {};
  for (var j = 0; j < 5; j++) {
    if (seen[cards[j].code]) throw new Error("the " + cards[j].code + " shows up twice");
    seen[cards[j].code] = true;
  }

  // fifteens: every subset summing to 15 is 2.
  var fifteens = 0;
  for (var mask = 1; mask < 32; mask++) {
    var s = 0;
    for (var b = 0; b < 5; b++) if (mask & (1 << b)) s += cards[b].value;
    if (s === 15) fifteens++;
  }

  // pairs: 2 per pair across the five cards.
  var pairs = 0;
  for (var a = 0; a < 5; a++) for (var b2 = a + 1; b2 < 5; b2++) {
    if (cards[a].rank === cards[b2].rank) pairs++;
  }

  // runs: only the longest runs count, each instance scores its length.
  var mult = {};
  for (var c = 0; c < 5; c++) mult[cards[c].rank] = (mult[cards[c].rank] || 0) + 1;
  var runLen = 0, runCount = 0;
  for (var L = 5; L >= 3 && runCount === 0; L--) {
    for (var r = 1; r <= 13 - L + 1; r++) {
      var p = 1;
      for (var k = 0; k < L; k++) {
        var m2 = mult[r + k] || 0;
        if (m2 === 0) { p = 0; break; }
        p *= m2;
      }
      runCount += p;
    }
    if (runCount > 0) runLen = L;
  }

  // flush: four in hand is 4, starter matching makes 5.
  var flush = 0;
  if (cards[0].suit === cards[1].suit && cards[1].suit === cards[2].suit && cards[2].suit === cards[3].suit) {
    flush = cards[3].suit === cards[4].suit ? 5 : 4;
  }

  // nobs: jack in hand matching the starter's suit.
  var nobs = 0;
  for (var n = 0; n < 4; n++) {
    if (cards[n].rank === 11 && cards[n].suit === cards[4].suit) nobs = 1;
  }

  var comps = [];
  comps.push(fifteens === 0 ? "no fifteens" : _word(fifteens) + " fifteen" + (fifteens === 1 ? "" : "s") + " (" + 2 * fifteens + ")");
  comps.push(pairs === 0 ? "no pairs" : (pairs === 1 ? "a pair" : _word(pairs) + " pairs") + " (" + 2 * pairs + ")");
  comps.push(runLen === 0 ? "no runs" : (runCount === 1 ? "a run of " + _word(runLen) : _word(runCount) + " runs of " + _word(runLen)) + " (" + runCount * runLen + ")");
  comps.push(flush === 0 ? "no flush" : flush === 4 ? "a flush (4)" : "a five-card flush (5)");
  comps.push(nobs === 0 ? "no nobs" : "nobs (1)");
  var total = 2 * fifteens + 2 * pairs + runCount * runLen + flush + nobs;
  return comps.slice(0, 4).join(", ") + ", and " + comps[4] + " - " + total + " point" + (total === 1 ? "" : "s") + ".";
}

// The count truth: the 31 limit, run honestly.
function pegTruth(current, pip) {
  if (!isFinite(current) || current < 0 || current > 30) throw new Error("the count must be under 31");
  if (!isFinite(pip) || pip < 1 || pip > 10) throw new Error("a card is worth 1 to 10");
  var art = pip === 8 ? "an" : "a";
  var sum = current + pip;
  if (sum === 31) return current + " plus " + art + " " + pip + " is 31 for 2.";
  if (sum < 31) return current + " plus " + art + " " + pip + " is " + sum + " - " + (31 - sum) + " short of the 2.";
  return current + " plus " + art + " " + pip + " is " + sum + " - it doesn't go.";
}

// The win truth: the last holes to 121.
function winTruth(score, points) {
  if (!isFinite(score) || score < 0 || score > 120) throw new Error("the game is already over");
  if (!isFinite(points) || points < 0 || points > 29) throw new Error("a hand scores at most 29");
  var total = score + points;
  if (total >= 121) return score + " plus " + points + " is " + total + " - pegged out.";
  return score + " plus " + points + " is " + total + " - " + (121 - total) + " to go.";
}
