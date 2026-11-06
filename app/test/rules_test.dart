import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:think_park/core/content.dart';
import 'package:think_park/core/game.dart';
import 'package:think_park/core/rounds.dart';
import 'package:think_park/core/store.dart';

/// The puzzles, how they are dealt at each level, and the saved game.
void main() {
  test('every thing asked about has a name', () {
    for (final MapEntry(key: land, value: ids) in pictures.entries) {
      for (final id in ids) {
        if (id.startsWith('scene_') || id.startsWith('suspect_')) continue;
        final placeIds = {for (final s in sortScenes) for (final p in s.places) p.id};
        if (placeIds.contains(id)) continue;
        expect(nameOf(land, id), isNotNull, reason: '${land.name}/$id');
      }
    }
    for (final s in sortScenes) {
      for (final t in s.things) {
        expect(s.places.map((p) => p.id), contains(t.place), reason: '${s.id} ${t.id}');
      }
    }
  });

  test('放哪裡: places and things grow with the level, every thing has its place', () {
    final r = math.Random(1);
    for (final level in Level.values) {
      String? last;
      for (var i = 0; i < 60; i++) {
        final round = SortRound.deal(level, r, last: last);
        last = round.scene.id;
        expect(round.scene.from.index, lessThanOrEqualTo(level.index));
        expect(round.places.length, inInclusiveRange(2, level.pick(2, 3, 5)));
        expect(round.things.length, inInclusiveRange(round.places.length, SortRound.most));
        final ids = {for (final p in round.places) p.id};
        for (final t in round.things) {
          expect(ids, contains(t.place));
        }
        for (final p in round.places) {
          expect(round.things.any((t) => t.place == p.id), isTrue, reason: 'every place gets something');
          expect(p.from.index, lessThanOrEqualTo(level.index));
        }
      }
    }
  });

  test('是誰的: one thing for each owner, and a spare one at 大', () {
    final r = math.Random(2);
    for (final level in Level.values) {
      for (var i = 0; i < 40; i++) {
        final round = OwnerRound.deal(level, r);
        expect(round.people.length, level.pick(2, 3, 4));
        expect(round.things.length, round.people.length + (level == Level.big ? 1 : 0));
        for (final o in round.people) {
          expect(round.things, contains(o.wants));
        }
        expect(round.things.toSet().length, round.things.length);
      }
    }
  });

  test('連連看: never straight across', () {
    final r = math.Random(3);
    for (final level in Level.values) {
      for (var i = 0; i < 40; i++) {
        final round = PairsRound.deal(level, r);
        expect(round.left.length, level.pick(2, 3, 4));
        expect(round.right.toSet(), round.left.toSet());
        expect([for (var k = 0; k < round.left.length; k++) round.left[k] == round.right[k]].every((x) => x), isFalse);
      }
    }
  });

  test('小偵探: the clues always lead to exactly one, each clue rules someone out', () {
    final r = math.Random(4);
    for (final level in [Level.mid, Level.big]) {
      for (var i = 0; i < 200; i++) {
        final round = DetectiveRound.deal(level, r);
        final clues = level == Level.mid ? 1 : 2;
        expect(round.suspects.length, clues + 2);
        expect(round.suspects.toSet().length, round.suspects.length);
        expect(round.clues.length, clues);
        var before = round.suspects.length;
        for (var used = 1; used <= clues; used++) {
          final left = round.left(used);
          expect(left.length, lessThan(before), reason: 'clue $used rules someone out');
          before = left.length;
        }
        expect(round.left(clues), [round.culprit]);
        if (clues == 2) expect(round.left(1).length, 2, reason: 'the first clue alone is not enough');
      }
    }
    final round = DetectiveRound(mysteries.first, const [Suspect(Species.rabbit, Wear.none)], const [LookClue(Species.rabbit), WearClue(Wear.scarf, has: false)],
        const Suspect(Species.rabbit, Wear.none));
    expect(round.why, '因為牠有長耳朵，又沒有圍巾，所以就是這隻小兔子！');
  });

  test('哪個不一樣: one card breaks the rule the others share', () {
    final r = math.Random(5);
    for (final level in Level.values) {
      for (var i = 0; i < 80; i++) {
        final round = OddRound.deal(level, r);
        expect(round.cards.length, level.pick(3, 4, 4));
        expect(round.cards.toSet().length, round.cards.length);
        final rest = [for (final c in round.cards) if (c != round.odd) c];
        expect(rest.every(round.rule.fits), isTrue);
        expect(round.rule.fits(round.odd), isFalse);
        expect(round.rule.odd(round.odd), isTrue);
        expect(round.why, contains(round.odd.zh));
      }
    }
    for (final rule in oddRules) {
      expect(blockThings.where(rule.fits).length, greaterThanOrEqualTo(3), reason: '${rule.tags}');
      expect(blockThings.where(rule.odd), isNotEmpty, reason: '${rule.tags}');
    }
  });

  test('接下來是什麼: the answer continues the pattern and is among the choices', () {
    final r = math.Random(6);
    for (final level in Level.values) {
      for (var i = 0; i < 80; i++) {
        final round = NextRound.deal(level, r);
        switch (round) {
          case PatternRound():
            expect(round.choices, contains(round.answer));
            expect(round.choices.length, level.pick(2, 3, 4));
            expect(round.choices.toSet().length, round.choices.length);
            expect(round.shown.length, inInclusiveRange(4, 7));
            final unit = round.kind == 'bigger' ? 3 : round.kind.length;
            final train = [...round.shown, round.answer];
            for (var k = unit; k < train.length; k++) {
              expect(train[k], train[k - unit], reason: '${round.kind} repeats');
            }
            if (level == Level.small) expect(round.kind, 'AB');
          case SequenceRound():
            expect(level, isNot(Level.small));
            expect(round.choices, contains(round.answer));
            expect(round.choices.toSet().length, round.choices.length);
            expect(round.shown, isNot(contains(round.answer)));
        }
      }
    }
  });

  test('a hard round makes the next one a level easier, never below the game', () {
    var g = const Game(settings: Settings(level: Level.big));
    expect(g.levelFor(GameKind.sort), Level.big);
    g = g.round(GameKind.sort, wrong: 3);
    expect(g.levelFor(GameKind.sort), Level.mid);
    g = g.round(GameKind.sort, wrong: 0);
    expect(g.levelFor(GameKind.sort), Level.big);
    g = g.copyWith(settings: const Settings(level: Level.mid)).round(GameKind.detective, wrong: 5);
    expect(g.levelFor(GameKind.detective), Level.mid, reason: '小偵探 starts at 中');
    expect(const Settings(level: Level.small).shows(GameKind.detective), isFalse);
  });

  test('cases, stars, stickers, skills and the rest survive saving', () async {
    final r = math.Random(7);
    var g = const Game();
    for (var i = 0; i < 4; i++) {
      g = g.round(GameKind.odd, wrong: i % 2).solved(GameKind.odd, sticker: stickerFor(GameKind.odd, g.stickers, r));
    }
    expect(g.starsOf(GameKind.odd), 3);
    expect(g.stickers.length, 4, reason: 'a new sticker each time');
    expect(g.skills[Skill.classify]!.tried, 4);
    expect(g.skills[Skill.classify]!.right, 2);
    g = g.rest(DateTime(2026, 11, 6, 10)).copyWith(settings: const Settings(level: Level.big, minutes: 20, off: {GameKind.pairs}, english: true));
    final store = MemoryStore()..write(g.toJson());
    final back = Game.fromJson(await store.read());
    expect(back.toJson(), g.toJson());
    expect(Game.fromJson({'cases': 3, 'skills': {'classify': [1, 5]}, 'stickers': 'x', 'restSince': 4, 'settings': {'minutes': 7}}).toJson(), const Game().toJson());
  });
}
