import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:think_park/app/strings.dart';
import 'package:think_park/core/content.dart';
import 'package:think_park/core/game.dart';
import 'package:think_park/core/rounds.dart';
import 'package:think_park/features/play/play_screen.dart';

import 'helpers.dart';

/// A child plays a case of every game, looks at the sticker book, rests
/// when the time is up, and a parent opens parent mode; on a phone and a
/// tablet. Screenshots go to `build/screenshots/<device>/`.
void main() {
  Object round(TestApp app) => (app.tester.state(find.byType(PlayScreen)) as dynamic).debugRound as Object;

  Future<void> drag(TestApp app, Offset from, Offset to) async {
    final g = await app.tester.startGesture(from);
    await app.tester.pump(const Duration(milliseconds: 30));
    for (var i = 1; i <= 8; i++) {
      await g.moveTo(Offset.lerp(from, to, i / 8)!);
      await app.tester.pump(const Duration(milliseconds: 16));
    }
    await g.up();
    await app.settle(500);
  }

  Offset at(TestApp app, String label) => app.tester.getCenter(find.bySemanticsLabel(label).last);

  Future<void> open(TestApp app, GameKind g) async {
    await app.tapLabel(g.zh, ms: 1600);
    await app.settle(800);
    expect(app.location, '/play/${g.name}');
  }

  /// Waits for the explanation and the next round (or the solved case).
  Future<void> next(TestApp app) => app.settle(4800);

  Future<void> backHome(TestApp app, String device, String shot) async {
    expect(find.text(Strings.solved), findsOneWidget);
    expect(app.sounds.played, contains('solved'));
    await shoot(app.tester, device, shot);
    // The solved card's button (the home button under it says the same).
    await app.tester.tap(find.bySemanticsLabel(Strings.toPark).last);
    await app.settle(800);
    expect(app.location, '/');
  }

  Future<void> walk(WidgetTester tester, String device, Size size, double ratio) async {
    await tester.runAsync(loadFonts);
    final app = await TestApp.start(tester, size: size, ratio: ratio);
    await app.settle(1000);
    expect(app.voice.said.first, Strings.welcome);
    await shoot(tester, device, '01_park');

    // 卡通城：放哪裡？ The first thing goes to a wrong place once.
    await open(app, GameKind.sort);
    expect(app.sounds.played, contains('poof'));
    await shoot(tester, device, '02_sort');
    for (var r = 0; r < GameKind.sort.rounds; r++) {
      final sort = round(app) as SortRound;
      for (final (i, t) in sort.things.indexed) {
        final name = sortThings[t.id]!.zh;
        if (r == 0 && i == 0) {
          final wrong = sort.places.firstWhere((p) => p.id != t.place);
          await drag(app, at(app, name), at(app, wrong.zh));
          expect(app.sounds.played.last, 'try');
          expect(app.voice.said.last, Strings.notHere(name, wrong.zh));
          await shoot(tester, device, '03_sort_wrong');
        }
        await drag(app, at(app, name), at(app, sort.scene.place(t.place).zh));
        if (r == 0 && i == 0) expect(app.voice.said.last, t.why);
      }
      if (r == 0) await shoot(tester, device, '04_sort_done');
      await next(app);
    }
    expect(app.game.cases[GameKind.sort], 1);
    await backHome(app, device, '05_sort_solved');

    // 卡通城：是誰的？
    await open(app, GameKind.owner);
    await shoot(tester, device, '06_owner');
    for (var r = 0; r < GameKind.owner.rounds; r++) {
      final owner = round(app) as OwnerRound;
      for (final (i, o) in owner.people.indexed) {
        await drag(app, at(app, ownerThings[o.wants]!.zh), at(app, o.zh));
        if (r == 0 && i == 0) await shoot(tester, device, '07_owner_given');
      }
      await next(app);
    }
    await backHome(app, device, '08_owner_solved');

    // 紙片森林：連連看
    await open(app, GameKind.pairs);
    await shoot(tester, device, '09_pairs');
    for (var r = 0; r < GameKind.pairs.rounds; r++) {
      final pairs = round(app) as PairsRound;
      for (final (i, p) in pairs.left.indexed) {
        await drag(app, at(app, pairThings[p.a]!.zh), at(app, pairThings[p.b]!.zh));
        if (r == 0 && i == 0) {
          expect(app.sounds.played, contains('snap'));
          await shoot(tester, device, '10_pairs_line');
        }
      }
      await next(app);
    }
    await backHome(app, device, '11_pairs_solved');

    // 紙片森林：小偵探 (中: one clue).
    await open(app, GameKind.detective);
    await shoot(tester, device, '12_detective');
    for (var r = 0; r < GameKind.detective.rounds; r++) {
      final d = round(app) as DetectiveRound;
      for (final (i, c) in d.clues.indexed) {
        await app.tapLabel('${Strings.clue(i + 1)}：${c.zh}', ms: 600);
      }
      if (r == 0) await shoot(tester, device, '13_detective_clue');
      await app.tapLabel(d.culprit.zh, ms: 800);
      expect(app.voice.said.last, contains(d.mystery.sorry));
      if (r == 0) await shoot(tester, device, '14_detective_found');
      await next(app);
    }
    await backHome(app, device, '15_detective_solved');

    // 積木王國：哪個不一樣？ One wrong card first.
    await open(app, GameKind.odd);
    await shoot(tester, device, '16_odd');
    for (var r = 0; r < GameKind.odd.rounds; r++) {
      final odd = round(app) as OddRound;
      if (r == 0) {
        await app.tapLabel(odd.cards.firstWhere((c) => c != odd.odd).zh, ms: 500);
        expect(app.sounds.played.last, 'try');
      }
      await app.tapLabel(odd.odd.zh, ms: 800);
      expect(app.voice.said.last, contains(odd.why));
      if (r == 0) await shoot(tester, device, '17_odd_found');
      await next(app);
    }
    await backHome(app, device, '18_odd_solved');

    // 積木王國：接下來是什麼？
    await open(app, GameKind.next);
    await app.settle(1200);
    await shoot(tester, device, '19_next');
    var sawSteps = false;
    for (var r = 0; r < GameKind.next.rounds; r++) {
      final n = round(app) as NextRound;
      switch (n) {
        case PatternRound():
          await app.tapLabel(n.answer.zh, ms: 800);
        case SequenceRound():
          await app.tapLabel(sequenceThings[n.answer]!.zh, ms: 800);
          if (!sawSteps) await shoot(tester, device, '20_next_steps');
          sawSteps = true;
      }
      await next(app);
    }
    await backHome(app, device, '21_next_solved');

    // Stars and stickers.
    for (final g in GameKind.values) {
      expect(app.game.starsOf(g), 1, reason: g.name);
    }
    expect(app.game.stickers.length, 6);
    await shoot(tester, device, '22_park_stars');
    await app.tapLabel(Strings.book, ms: 800);
    await shoot(tester, device, '23_book');
    await app.tapLabel(Land.forest.zh, ms: 600);
    await shoot(tester, device, '24_book_forest');
    await app.tapLabel(Strings.home, ms: 600);

    // Time is up.
    app.now = app.now.add(const Duration(minutes: 15, seconds: 1));
    await app.settle(2400);
    expect(app.location, '/rest');
    expect(app.sounds.music?.file, 'music_rest');
    await shoot(tester, device, '25_rest');

    // A parent lets play go on, then opens parent mode.
    const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    Future<void> gate() async {
      final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
      for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
        await tester.tap(find.byKey(ValueKey('gate-key-$d')));
        await app.settle(200);
      }
      await app.settle(800);
    }

    await app.tapLabel(Strings.parent, ms: 800);
    await shoot(tester, device, '26_parent_gate');
    await gate();
    expect(app.location, '/');
    expect(app.game.restSince, isNull);
    await app.tapLabel(Strings.parent, ms: 800);
    await gate();
    expect(app.location, '/parent');
    await shoot(tester, device, '27_parent');
    await tester.tap(find.byKey(const ValueKey('level-big')));
    await app.settle();
    expect(app.game.settings.level, Level.big);
    await tester.scrollUntilVisible(find.text(Strings.progress), 300);
    await app.settle();
    await shoot(tester, device, '28_parent_progress');
    await app.end();
  }

  testWidgets('phone: a case of every game, the book, the rest, parent mode', (tester) async {
    await walk(tester, 'phone', const Size(1080, 2340), 2.75);
  });

  testWidgets('tablet: the same on a big screen', (tester) async {
    await walk(tester, 'tablet', const Size(2048, 2732), 2);
  });

  testWidgets('the littlest ones: two places, tap a thing and then its place', (tester) async {
    await tester.runAsync(loadFonts);
    final app = await TestApp.start(tester, game: const Game(settings: Settings(level: Level.small)));
    expect(find.bySemanticsLabel(GameKind.detective.zh), findsNothing, reason: '小偵探 starts at 中');
    await open(app, GameKind.sort);
    final sort = round(app) as SortRound;
    expect(sort.places.length, 2);
    for (final t in sort.things) {
      await tester.tapAt(at(app, sortThings[t.id]!.zh));
      await app.settle(300);
      await tester.tapAt(at(app, sort.scene.place(t.place).zh));
      await app.settle(500);
    }
    expect(app.sounds.played.where((s) => s == 'right').length, 1);
    await shoot(tester, 'phone', '30_small_sort');
    await app.end();
  });
}
