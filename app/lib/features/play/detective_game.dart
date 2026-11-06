import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/rounds.dart';
import 'play_screen.dart';

/// 小偵探: forest friends in a row and clue cards below. Each clue looked at
/// greys out the ones it rules out; then tap the one who did it, who says
/// sorry and gives the thing back.
class DetectiveGame extends StatefulWidget {
  const DetectiveGame({super.key, required this.round, required this.hooks});

  final DetectiveRound round;
  final PlayHooks hooks;

  @override
  State<DetectiveGame> createState() => _DetectiveGameState();
}

class _DetectiveGameState extends State<DetectiveGame> {
  var _used = 0;
  var _found = false;
  final _shake = <Suspect, int>{};
  var _nudge = 0;

  DetectiveRound get _r => widget.round;

  void _clue(int i) {
    if (_found) return;
    if (i != _used) {
      widget.hooks.say(_r.clues[i].zh);
      return;
    }
    widget.hooks.sfx('clue');
    setState(() => _used++);
    widget.hooks.say(_r.clues[i].zh);
  }

  void _pick(Suspect s) {
    if (_found) return;
    final left = _r.left(_used);
    if (!left.contains(s)) {
      final clue = _r.clues.take(_used).firstWhere((c) => !c.fits(s));
      setState(() => _shake[s] = (_shake[s] ?? 0) + 1);
      widget.hooks.miss('線索說${clue.zh}，${Strings.notThem(s.zh)}');
      return;
    }
    if (_used < _r.clues.length) {
      setState(() => _nudge++);
      widget.hooks.say(Strings.lookAtClues);
      return;
    }
    // Only the one who did it is left now.
    setState(() => _found = true);
    widget.hooks.sfx('abu_yay');
    widget.hooks.done('${_r.why}${_r.mystery.sorry}');
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final n = _r.suspects.length;
        final size = math.min((w - 24) / n - 8, h * 0.38);
        final left = _r.left(_used);
        return Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          SizedBox(
            height: size * 1.25,
            child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              for (final (i, s) in _r.suspects.indexed)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: _SuspectCard(
                    suspect: s,
                    size: size,
                    seed: i,
                    out: !left.contains(s),
                    found: _found && s == _r.culprit,
                    thing: _r.mystery.thing,
                    shake: _shake[s] ?? 0,
                    onTap: () => _pick(s),
                  ),
                ),
            ]),
          ),
          SizedBox(height: math.min(40, h * 0.06)),
          for (final (i, c) in _r.clues.indexed)
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
              child: Wiggle(
                trigger: i == _used ? _nudge : 0,
                child: Semantics(
                  container: true,
                  button: true,
                  label: '${Strings.clue(i + 1)}：${c.zh}',
                  excludeSemantics: true,
                  onTap: () => _clue(i),
                  child: Pressable(
                    onTap: () => _clue(i),
                    sound: null,
                    child: LandCard(
                      land: Land.forest,
                      seed: 10 + i,
                      ring: i == _used && !_found ? const Color(0xFFF2A93B) : null,
                      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
                      child: Row(children: [
                        Icon(Icons.search_rounded, size: 30, color: i < _used ? const Color(0xFF6E9E5A) : Park.inkSoft),
                        const SizedBox(width: 10),
                        Text('${Strings.clue(i + 1)}：', style: const TextStyle(fontSize: 19, color: Park.inkSoft)),
                        Expanded(child: Text(c.zh, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w700))),
                        if (i < _used) const Icon(Icons.check_circle_rounded, color: Color(0xFF6E9E5A), size: 30),
                      ]),
                    ),
                  ),
                ),
              ),
            ),
        ]);
      });
}

class _SuspectCard extends StatelessWidget {
  const _SuspectCard({
    required this.suspect,
    required this.size,
    required this.seed,
    required this.out,
    required this.found,
    required this.thing,
    required this.shake,
    required this.onTap,
  });

  final Suspect suspect;
  final double size;
  final int seed;
  final bool out;
  final bool found;
  final String thing;
  final int shake;
  final VoidCallback onTap;

  static const _grey = ColorFilter.matrix([0.25, 0.5, 0.1, 0, 30, 0.25, 0.5, 0.1, 0, 30, 0.25, 0.5, 0.1, 0, 30, 0, 0, 0, 0.55, 0]);

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: suspect.zh,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: null,
          child: Wiggle(
            trigger: shake,
            child: SizedBox(
              width: size,
              height: size * 1.2,
              child: Stack(clipBehavior: Clip.none, children: [
                Positioned.fill(
                  child: LandCard(
                    land: Land.forest,
                    seed: seed,
                    ring: found ? Park.gold : null,
                    padding: EdgeInsets.all(size * 0.06),
                    child: AnimatedSwitcher(
                      duration: const Duration(milliseconds: 400),
                      child: out
                          ? ColorFiltered(key: const ValueKey('out'), colorFilter: _grey, child: Art(Land.forest, suspect.id))
                          : Art(Land.forest, suspect.id, key: const ValueKey('in')),
                    ),
                  ),
                ),
                if (out) Center(child: Icon(Icons.close_rounded, size: size * 0.7, color: const Color(0xCCD9534F))),
                if (found)
                  Positioned(
                    right: -size * 0.12,
                    bottom: -size * 0.08,
                    width: size * 0.55,
                    height: size * 0.55,
                    child: Art(Land.forest, thing),
                  ),
              ]),
            ),
          ),
        ),
      );
}
