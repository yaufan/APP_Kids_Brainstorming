import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/rounds.dart';
import '../../core/sounds.dart';
import 'detective_game.dart';
import 'next_game.dart';
import 'odd_game.dart';
import 'owner_game.dart';
import 'pairs_game.dart';
import 'sort_game.dart';

/// What a game tells the play screen.
class PlayHooks {
  const PlayHooks({required this.say, required this.good, required this.miss, required this.done, required this.sfx, required this.english});

  /// Say something (a thing's name, a clue).
  final void Function(String zh, {String? en}) say;

  /// A right step that does not end the round: why it is right.
  final void Function(String why) good;

  /// A wrong try: a hint.
  final void Function(String hint) miss;

  /// The round is solved: why.
  final void Function(String why) done;
  final void Function(String sound) sfx;

  /// Whether to say English names too.
  final bool english;
}

/// One case of a game: a few rounds, each explained when it is solved; a
/// star and a sticker at the end (docs/design.md "獎勵").
class PlayScreen extends ConsumerStatefulWidget {
  const PlayScreen({super.key, required this.game});

  final GameKind game;

  /// The scene behind the forest and block games (the city games draw
  /// their own scene inside).
  static const backdrop = {
    GameKind.pairs: 'scene_meadow',
    GameKind.detective: 'scene_woods',
    GameKind.odd: 'scene_kingdom',
    GameKind.next: 'scene_kingdom',
  };

  @override
  ConsumerState<PlayScreen> createState() => _PlayScreenState();
}

class _PlayScreenState extends ConsumerState<PlayScreen> {
  late final Sounds _sounds;
  late final math.Random _random;
  late Object _round;
  var _roundNo = 0;
  var _done = 0;
  var _wrong = 0;
  var _solved = false;
  String _line = '';
  String? _sticker;
  var _cheer = false;
  Timer? _next;
  String? _lastId;
  Set<String> _lastSet = const {};

  GameKind get _game => widget.game;

  /// The round on the screen (tests play it).
  @visibleForTesting
  Object get debugRound => _round;

  Land get _land => _game.land;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _random = ref.read(randomProvider);
    _sounds.hold(this, Music.values.byName(_land.name));
    _deal();
    WidgetsBinding.instance.addPostFrameCallback((_) => _ask());
  }

  @override
  void dispose() {
    _next?.cancel();
    _wait?.cancel();
    _cap?.cancel();
    _sounds.release(this);
    super.dispose();
  }

  void _deal() {
    final level = ref.read(gameProvider).levelFor(_game);
    final r = _random;
    switch (_game) {
      case GameKind.sort:
        final round = SortRound.deal(level, r, last: _lastId);
        _lastId = round.scene.id;
        _round = round;
      case GameKind.owner:
        final round = OwnerRound.deal(level, r, last: _lastSet);
        _lastSet = {for (final o in round.people) o.id};
        _round = round;
      case GameKind.pairs:
        final round = PairsRound.deal(level, r, last: _lastSet);
        _lastSet = {for (final p in round.left) p.a};
        _round = round;
      case GameKind.detective:
        final round = DetectiveRound.deal(level == Level.small ? Level.mid : level, r, last: _lastId);
        _lastId = round.mystery.id;
        _round = round;
      case GameKind.odd:
        _round = OddRound.deal(level, r);
      case GameKind.next:
        final round = NextRound.deal(level, r, last: _lastId);
        if (round is SequenceRound) _lastId = round.sequence.id;
        _round = round;
    }
    _wrong = 0;
    _cheer = false;
    _roundNo++;
    if (_game == GameKind.sort && (_round as SortRound).scene.id == 'recycling') _sounds.play('garbage_truck');
    if (_game == GameKind.next && _round is PatternRound) _sounds.play('train');
  }

  /// The question of this round.
  String get _prompt => switch (_round) {
        DetectiveRound(:final mystery) => '${mystery.zh}${Strings.ask[_game]}',
        PatternRound() => Strings.train,
        SequenceRound() => Strings.steps,
        _ => Strings.ask[_game]!,
      };

  /// Says [zh] (and [en] if the parent turned English on); completes when
  /// it has been said.
  Future<void> _say(String zh, {String? en}) async {
    final s = ref.read(gameProvider).settings;
    if (mounted && s.voice) await ref.read(voiceProvider).say(zh, en: s.english ? en : null);
  }

  void _ask() {
    if (!mounted) return;
    setState(() => _line = _prompt);
    _say(_prompt);
  }

  void _good(String why) {
    _sounds.play('drop');
    _sounds.play('sparkle');
    setState(() => _line = why);
    _say(why);
  }

  void _miss(String hint) {
    _wrong++;
    _sounds.play('try');
    setState(() => _line = hint);
    _say(hint);
  }

  void _doneRound(String why) {
    _sounds.play('right');
    final praise = Strings.right[_random.nextInt(Strings.right.length)];
    setState(() {
      _line = '$praise$why';
      _cheer = true;
    });
    ref.read(gameProvider.notifier).change((g) => g.round(_game, wrong: _wrong));
    // The next round comes once 阿布 has finished explaining (and at least a
    // moment to look), but never waits longer than [_longest].
    final round = _roundNo;
    var said = false, waited = false, gone = false;
    void go() {
      if (gone || !mounted || round != _roundNo || _solved) return;
      gone = true;
      _cap?.cancel();
      _next?.cancel();
      _next = Timer(const Duration(milliseconds: 700), _advance);
    }

    _say('$praise$why').then((_) {
      said = true;
      if (waited) go();
    });
    _wait?.cancel();
    _wait = Timer(_least, () {
      waited = true;
      if (said) go();
    });
    _cap?.cancel();
    _cap = Timer(_longest, go);
  }

  Timer? _wait;
  Timer? _cap;

  static const _least = Duration(milliseconds: 1800);
  static const _longest = Duration(seconds: 12);

  void _advance() {
    if (!mounted) return;
    _done++;
    if (_done >= _game.rounds) {
      final notifier = ref.read(gameProvider.notifier);
      final sticker = stickerFor(_game, ref.read(gameProvider).stickers, _random);
      notifier.change((g) => g.solved(_game, sticker: sticker));
      _sounds.play('solved');
      final name = nameOf(_land, sticker.split('/').last) ?? '';
      setState(() {
        _solved = true;
        _sticker = sticker;
        _line = '${Strings.solved}${Strings.gotSticker(name)}';
      });
      _say(_line);
      return;
    }
    setState(_deal);
    _ask();
  }

  void _again() {
    setState(() {
      _solved = false;
      _sticker = null;
      _done = 0;
      _deal();
    });
    _ask();
  }

  void _home() => context.canPop() ? context.pop() : context.go('/');

  Widget _board(PlayHooks hooks) {
    final key = ValueKey('round-$_roundNo');
    return switch (_round) {
      SortRound r => SortGame(key: key, round: r, hooks: hooks),
      OwnerRound r => OwnerGame(key: key, round: r, hooks: hooks),
      PairsRound r => PairsGame(key: key, round: r, hooks: hooks),
      DetectiveRound r => DetectiveGame(key: key, round: r, hooks: hooks),
      OddRound r => OddGame(key: key, round: r, hooks: hooks),
      NextRound r => NextGame(key: key, round: r, hooks: hooks),
      _ => const SizedBox(),
    };
  }

  @override
  Widget build(BuildContext context) {
    final look = LandLook.of(_land);
    final english = ref.watch(gameProvider.select((g) => g.settings.english));
    final hooks = PlayHooks(say: _say, good: _good, miss: _miss, done: _doneRound, sfx: _sounds.play, english: english);
    final backdrop = PlayScreen.backdrop[_game];
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [look.top, look.bottom])),
        child: Stack(children: [
          if (backdrop != null) Positioned.fill(child: Art(_land, backdrop, fit: BoxFit.cover)),
          SafeArea(
            child: Column(children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
                child: Row(children: [
                  LandButton(land: _land, label: Strings.home, icon: Icons.home_rounded, onTap: _home, size: 52),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: LandCard(
                        land: _land,
                        color: look.accent,
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                        child: Text(_game.zh, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: Colors.white)),
                      ),
                    ),
                  ),
                  RoundDots(count: _game.rounds, done: _solved ? _game.rounds : _done, color: look.accent),
                ]),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 10, 12, 6),
                child: SpeakBubble(land: _land, text: _line.isEmpty ? _prompt : _line, onTap: () => _say(_line.isEmpty ? _prompt : _line), size: 20),
              ),
              Expanded(child: _solved ? const SizedBox() : _board(hooks)),
              SizedBox(
                height: 92,
                child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
                  const SizedBox(width: 8),
                  Semantics(
                    container: true,
                    button: true,
                    label: '阿布',
                    excludeSemantics: true,
                    onTap: _ask,
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: () {
                        _sounds.play('abu_hmm');
                        _ask();
                      },
                      child: SizedBox(width: 88, height: 88, child: Abu(land: _land, pose: _cheer ? 'cheer' : 'think')),
                    ),
                  ),
                ]),
              ),
            ]),
          ),
          if (_solved) _Solved(land: _land, sticker: _sticker!, onAgain: _again, onHome: _home),
        ]),
      ),
    );
  }
}

/// A case solved: the sticker, a star, play again or back to the park.
class _Solved extends StatefulWidget {
  const _Solved({required this.land, required this.sticker, required this.onAgain, required this.onHome});

  final Land land;
  final String sticker;
  final VoidCallback onAgain;
  final VoidCallback onHome;

  @override
  State<_Solved> createState() => _SolvedState();
}

class _SolvedState extends State<_Solved> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..forward();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final parts = widget.sticker.split('/');
    final land = Land.values.byName(parts.first);
    return Positioned.fill(
      child: ColoredBox(
        color: Colors.white.withValues(alpha: 0.82),
        child: SafeArea(
          child: Center(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              const Text(Strings.solved, style: TextStyle(fontSize: 34, fontWeight: FontWeight.w700, color: Park.orange)),
              const SizedBox(height: 12),
              ScaleTransition(
                scale: CurvedAnimation(parent: _c, curve: Curves.elasticOut),
                child: Stack(clipBehavior: Clip.none, children: [
                  LandCard(land: land, padding: const EdgeInsets.all(18), child: SizedBox(width: 150, height: 150, child: Art(land, parts.last))),
                  const Positioned(right: -18, top: -18, child: Icon(Icons.star_rounded, color: Park.gold, size: 64)),
                ]),
              ),
              const SizedBox(height: 10),
              SizedBox(width: 150, height: 150, child: Abu(land: widget.land, pose: 'cheer')),
              const SizedBox(height: 12),
              WideButton(label: Strings.again, icon: Icons.refresh_rounded, onTap: widget.onAgain),
              const SizedBox(height: 14),
              WideButton(label: Strings.toPark, icon: Icons.home_rounded, color: Colors.white, onTap: widget.onHome),
            ]),
          ),
        ),
      ),
    );
  }
}
