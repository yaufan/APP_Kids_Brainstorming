/// How each game deals a round for a level (docs/design.md "六個遊戲").
/// Every generator takes the dice, so tests can fix them.
library;

import 'dart:math' as math;

import 'content.dart';

List<T> _shuffled<T>(Iterable<T> xs, math.Random r) => xs.toList()..shuffle(r);

T _one<T>(List<T> xs, math.Random r) => xs[r.nextInt(xs.length)];

bool _at(Level from, Level level) => from.index <= level.index;

// ---------------------------------------------------------------- 放哪裡？

class SortRound {
  const SortRound(this.scene, this.places, this.things);

  final SortScene scene;

  /// The places in use this round (others stay out of the picture).
  final List<Place> places;

  /// What lies on the floor, in the order it is scattered.
  final List<Stray> things;

  /// At most this many things wait on the floor at once.
  static const most = 6;

  factory SortRound.deal(Level level, math.Random r, {String? last}) {
    final scenes = [for (final s in sortScenes) if (_at(s.from, level) && s.id != last) s];
    final scene = _one(scenes, r);
    final usable = [for (final p in scene.places) if (_at(p.from, level) && scene.things.any((t) => t.place == p.id)) p];
    final count = math.min(usable.length, level.pick(2, 3, 5));
    final places = _shuffled(usable, r).take(count).toList();
    final perPlace = count <= 2 ? 2 : (count == 3 ? 2 : 1);
    final things = <Stray>[
      for (final p in places) ..._shuffled(scene.things.where((t) => t.place == p.id), r).take(perPlace),
    ];
    // With few places, fill up with a second thing for some.
    for (final t in _shuffled(scene.things, r)) {
      if (things.length >= math.min(most, level.pick(4, 6, 6))) break;
      if (!things.contains(t) && places.any((p) => p.id == t.place)) things.add(t);
    }
    return SortRound(scene, [for (final p in scene.places) if (places.contains(p)) p], _shuffled(things.take(most), r));
  }
}

// ---------------------------------------------------------------- 是誰的？

class OwnerRound {
  const OwnerRound(this.people, this.things);

  /// Who stands in the row this round.
  final List<Owner> people;

  /// What to give out: each owner's thing, and at 大 one that is nobody's here.
  final List<String> things;

  factory OwnerRound.deal(Level level, math.Random r, {Set<String> last = const {}}) {
    final pool = [for (final o in owners) if (_at(o.from, level)) o];
    final fresh = [for (final o in pool) if (!last.contains(o.id)) o];
    final n = level.pick(2, 3, 4);
    final chosen = _shuffled(fresh.length >= n ? fresh : pool, r).take(n).toList();
    final wanted = {for (final o in chosen) o.wants};
    final extra = level == Level.big ? [_one([for (final o in pool) if (!wanted.contains(o.wants)) o.wants], r)] : const <String>[];
    return OwnerRound(chosen, _shuffled([...wanted, ...extra], r));
  }
}

// ---------------------------------------------------------------- 連連看

class PairsRound {
  const PairsRound(this.left, this.right);

  /// The pairs, top to bottom on the left.
  final List<Pair> left;

  /// The right column (each pair's second thing), shuffled.
  final List<Pair> right;

  factory PairsRound.deal(Level level, math.Random r, {Set<String> last = const {}}) {
    final pool = [for (final p in pairs) if (_at(p.from, level)) p];
    final fresh = [for (final p in pool) if (!last.contains(p.a)) p];
    final n = level.pick(2, 3, 4);
    final chosen = _shuffled(fresh.length >= n ? fresh : pool, r).take(n).toList();
    var right = _shuffled(chosen, r);
    // Never straight across: that would not need any thinking.
    for (var i = 0; i < 8 && n > 1 && _same(right, chosen); i++) {
      right = _shuffled(chosen, r);
    }
    if (n > 1 && _same(right, chosen)) right = [...chosen.skip(1), chosen.first];
    return PairsRound(chosen, right);
  }

  static bool _same(List<Pair> a, List<Pair> b) => [for (var i = 0; i < a.length; i++) a[i] == b[i]].every((x) => x);
}

// ---------------------------------------------------------------- 小偵探

/// What a clue says about the one who did it.
sealed class Clue {
  const Clue();

  bool fits(Suspect s);

  String get zh;
}

/// 「牠有長耳朵」 or, for 大, 「牠沒有長耳朵」.
class LookClue extends Clue {
  const LookClue(this.species, {this.has = true});

  final Species species;
  final bool has;

  @override
  bool fits(Suspect s) => (s.species == species) == has;

  @override
  String get zh => has ? '牠有${species.feature}' : '牠沒有${species.feature}';

  @override
  bool operator ==(Object other) => other is LookClue && other.species == species && other.has == has;

  @override
  int get hashCode => Object.hash(species, has);
}

/// 「牠戴著帽子」 or 「牠沒有戴帽子」.
class WearClue extends Clue {
  const WearClue(this.wear, {this.has = true});

  final Wear wear;
  final bool has;

  @override
  bool fits(Suspect s) => (s.wear == wear) == has;

  @override
  String get zh => has ? '牠${wear.on}' : '牠${wear.off}';

  @override
  bool operator ==(Object other) => other is WearClue && other.wear == wear && other.has == has;

  @override
  int get hashCode => Object.hash(wear, has);
}

class DetectiveRound {
  const DetectiveRound(this.mystery, this.suspects, this.clues, this.culprit);

  final Mystery mystery;
  final List<Suspect> suspects;
  final List<Clue> clues;
  final Suspect culprit;

  /// Who is still possible after the first [used] clues.
  List<Suspect> left(int used) => [for (final s in suspects) if (clues.take(used).every((c) => c.fits(s))) s];

  /// "因為牠有長耳朵，又沒有圍巾，所以是小兔子！"
  String get why {
    final said = [for (final c in clues) c.zh.replaceFirst('牠', '')];
    return '因為牠${said.join('，又')}，所以就是這隻${culprit.species.zh}！';
  }

  /// 中: three suspects and one clue; 大: four suspects and two clues, the
  /// first leaving two, the second one. Every clue rules someone out.
  factory DetectiveRound.deal(Level level, math.Random r, {String? last}) {
    final mystery = _one([for (final m in mysteries) if (m.id != last) m], r);
    final everyone = [for (final s in Species.values) for (final w in Wear.values) Suspect(s, w)];
    final two = level == Level.big;
    for (var tries = 0; tries < 500; tries++) {
      final culprit = _one(everyone, r);
      final options = <Clue>[
        LookClue(culprit.species),
        if (culprit.wear != Wear.none) WearClue(culprit.wear),
        if (two) ...[
          for (final w in Wear.values) if (w != Wear.none && w != culprit.wear) WearClue(w, has: false),
          for (final s in Species.values) if (s != culprit.species) LookClue(s, has: false),
        ],
      ];
      final first = _one(options, r);
      if (!two) {
        final others = _shuffled([for (final s in everyone) if (!first.fits(s)) s], r).take(2).toList();
        if (others.length < 2) continue;
        return DetectiveRound(mystery, _shuffled([culprit, ...others], r), [first], culprit);
      }
      final seconds = [
        for (final c in options) if (c != first && (c is LookClue) != (first is LookClue)) c,
      ];
      if (seconds.isEmpty) continue;
      final second = _one(seconds, r);
      final decoys = [for (final s in everyone) if (s != culprit && first.fits(s) && !second.fits(s)) s];
      final outs = _shuffled([for (final s in everyone) if (!first.fits(s)) s], r).take(2).toList();
      if (decoys.isEmpty || outs.length < 2) continue;
      return DetectiveRound(mystery, _shuffled([culprit, _one(decoys, r), ...outs], r), [first, second], culprit);
    }
    throw StateError('no detective round');
  }
}

// ---------------------------------------------------------------- 哪個不一樣？

class OddRound {
  const OddRound(this.rule, this.cards, this.odd);

  final OddRule rule;
  final List<Block> cards;
  final Block odd;

  String get why => rule.why(odd.zh);

  factory OddRound.deal(Level level, math.Random r, {OddRule? last}) {
    final rules = [for (final x in oddRules) if (_at(x.from, level) && level.index <= x.to.index && x != last) x];
    final rule = _one(rules, r);
    final n = level.pick(3, 4, 4);
    final group = _shuffled(blockThings.where(rule.fits), r).take(n - 1).toList();
    final odd = _one(blockThings.where(rule.odd).toList(), r);
    return OddRound(rule, _shuffled([...group, odd], r), odd);
  }
}

// ---------------------------------------------------------------- 接下來是什麼？

sealed class NextRound {
  const NextRound();

  factory NextRound.deal(Level level, math.Random r, {String? last}) {
    final seqs = [for (final s in sequences) if (_at(s.from, level) && s.id != last) s];
    if (level != Level.small && seqs.isNotEmpty && r.nextBool()) return SequenceRound.deal(level, r, seqs);
    return PatternRound.deal(level, r);
  }
}

/// A block train: [shown] wagons, then an empty one; [answer] goes there.
class PatternRound extends NextRound {
  const PatternRound(this.kind, this.shown, this.answer, this.choices);

  /// AB, AAB, ABB, ABC, AABB or "bigger".
  final String kind;
  final List<Token> shown;
  final Token answer;
  final List<Token> choices;

  /// "紅色的圓形、藍色的方形……下一個是？"
  String get why => kind == 'bigger' ? '越來越大，小、中、大，又從小的開始。' : '${[for (final t in shown.take(kind.length)) t.zh].join('、')}，一直重複。';

  factory PatternRound.deal(Level level, math.Random r) {
    final kinds = level.pick(['AB'], ['AB', 'AAB', 'ABB'], ['AAB', 'ABB', 'ABC', 'AABB', 'bigger']);
    final kind = _one(kinds, r);
    final shapes = _shuffled(Shape.values, r);
    final hues = _shuffled(Hue.values, r);
    final List<Token> unit;
    if (kind == 'bigger') {
      unit = [for (var s = 1; s <= 3; s++) Token(shapes[0], hues[0], size: s)];
    } else {
      final abc = [for (var i = 0; i < 3; i++) Token(shapes[i], hues[i])];
      unit = [for (final ch in kind.split('')) abc['ABC'.indexOf(ch)]];
    }
    // About two repeats, at most five wagons before the empty one (so the
    // wagons stay big on a phone).
    final length = math.min(5, unit.length * 2 + r.nextInt(unit.length));
    final train = [for (var i = 0; i <= length; i++) unit[i % unit.length]];
    final answer = train.last;
    final n = level.pick(2, 3, 4);
    final others = <Token>{for (final t in unit) if (t != answer) t};
    final extra = [
      for (final s in shapes)
        for (final h in hues)
          if (!others.contains(Token(s, h, size: answer.size)) && Token(s, h, size: answer.size) != answer) Token(s, h, size: answer.size),
    ]..shuffle(r);
    final choices = [answer, ...others.take(n - 1), ...extra].take(n).toList()..shuffle(r);
    return PatternRound(kind, train.sublist(0, train.length - 1), answer, choices);
  }
}

/// Things in order; the last one is asked for.
class SequenceRound extends NextRound {
  const SequenceRound(this.sequence, this.choices);

  final Sequence sequence;
  final List<String> choices;

  List<String> get shown => sequence.steps.sublist(0, sequence.steps.length - 1);

  String get answer => sequence.steps.last;

  String get why => sequence.why;

  factory SequenceRound.deal(Level level, math.Random r, List<Sequence> pool) {
    final seq = _one(pool, r);
    final n = level.pick(2, 3, 3);
    // The earlier steps make the best wrong answers: they teach the order.
    final wrong = [
      ..._shuffled(seq.steps.take(seq.steps.length - 1), r),
      ..._shuffled([for (final s in sequences) if (s != seq) s.steps.last], r),
    ];
    return SequenceRound(seq, _shuffled([seq.steps.last, ...wrong.take(n - 1)], r));
  }
}
