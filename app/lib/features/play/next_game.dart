import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/rounds.dart';
import 'play_screen.dart';

/// 接下來是什麼？: a block train with a pattern and an empty wagon, or a row
/// of pictures in order with the last one missing; pick what comes next.
class NextGame extends StatefulWidget {
  const NextGame({super.key, required this.round, required this.hooks});

  final NextRound round;
  final PlayHooks hooks;

  @override
  State<NextGame> createState() => _NextGameState();
}

class _NextGameState extends State<NextGame> with SingleTickerProviderStateMixin {
  late final _drive = AnimationController(vsync: this, duration: const Duration(milliseconds: 1100))..forward();
  final _shake = <Object, int>{};
  var _found = false;

  @override
  void dispose() {
    _drive.dispose();
    super.dispose();
  }

  void _pick(Object choice) {
    if (_found) return;
    final round = widget.round;
    final right = switch (round) {
      PatternRound() => choice == round.answer,
      SequenceRound() => choice == round.answer,
    };
    if (right) {
      setState(() => _found = true);
      widget.hooks.sfx(round is PatternRound ? 'train' : 'sparkle');
      widget.hooks.done(switch (round) { PatternRound() => round.why, SequenceRound() => round.why });
      return;
    }
    setState(() => _shake[choice] = (_shake[choice] ?? 0) + 1);
    widget.hooks.sfx('bounce');
    widget.hooks.miss(round is PatternRound ? Strings.notNext : Strings.notNextStep);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final round = widget.round;
        final choices = switch (round) { PatternRound() => round.choices as List<Object>, SequenceRound() => round.choices as List<Object> };
        final size = math.min((w - 32) / choices.length - 14, h * 0.26).clamp(56.0, 170.0);
        return Column(children: [
          SizedBox(height: h * 0.04),
          SizedBox(
            height: h * 0.4,
            child: switch (round) {
              PatternRound() => AnimatedBuilder(
                  animation: _drive,
                  builder: (_, child) => Transform.translate(offset: Offset((1 - Curves.easeOut.transform(_drive.value)) * w, 0), child: child),
                  child: _Train(round: round, filled: _found),
                ),
              SequenceRound() => _Steps(round: round, filled: _found),
            },
          ),
          const Spacer(),
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            for (final c in choices)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 7),
                child: Semantics(
                  container: true,
                  button: true,
                  label: c is Token ? c.zh : (sequenceThings[c]?.zh ?? '$c'),
                  excludeSemantics: true,
                  onTap: () => _pick(c),
                  child: Pressable(
                    onTap: () => _pick(c),
                    sound: null,
                    child: Wiggle(
                      trigger: _shake[c] ?? 0,
                      child: SizedBox(
                        width: size,
                        height: size,
                        child: LandCard(
                          land: Land.blocks,
                          ring: _found && (c == (round is PatternRound ? round.answer : (round as SequenceRound).answer)) ? Park.gold : null,
                          padding: EdgeInsets.all(size * 0.12),
                          child: c is Token ? FittedBox(child: TokenView(c, size: 80)) : Art(Land.blocks, c as String),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ]),
          SizedBox(height: h * 0.06),
        ]);
      });
}

/// The block train: an engine and wagons carrying the pattern, the last one
/// empty with a question mark (or the answer once found).
class _Train extends StatelessWidget {
  const _Train({required this.round, required this.filled});

  final PatternRound round;
  final bool filled;

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final cars = round.shown.length + 1;
        final unit = math.min(box.maxWidth / (cars * 1.08 + 1.3), box.maxHeight * 0.55);
        return Center(
          child: SizedBox(
            height: unit * 1.6,
            child: FittedBox(
              child: Row(crossAxisAlignment: CrossAxisAlignment.end, children: [
                for (final t in round.shown) _Wagon(unit: unit, child: TokenView(t, size: unit)),
                _Wagon(
                  unit: unit,
                  dashed: !filled,
                  child: filled ? TokenView(round.answer, size: unit) : Text('?', style: TextStyle(fontSize: unit * 0.55, fontWeight: FontWeight.w700, color: const Color(0xFF7A6FB0))),
                ),
                _Engine(unit: unit),
              ].reversed.toList()),
            ),
          ),
        );
      });
}

class _Wagon extends StatelessWidget {
  const _Wagon({required this.unit, required this.child, this.dashed = false});

  final double unit;
  final Widget child;
  final bool dashed;

  @override
  Widget build(BuildContext context) => SizedBox(
        width: unit * 1.08,
        height: unit * 1.45,
        child: Stack(children: [
          Positioned(left: unit * 0.04, right: unit * 0.04, top: 0, height: unit, child: Center(child: child)),
          Positioned(
            left: unit * 0.04,
            right: unit * 0.04,
            top: unit * 0.9,
            height: unit * 0.32,
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: dashed ? Colors.white : const Color(0xFFFFC21F),
                borderRadius: BorderRadius.circular(unit * 0.08),
                border: dashed ? Border.all(color: const Color(0xFF7A6FB0), width: 3) : null,
              ),
            ),
          ),
          for (final x in [0.26, 0.74])
            Positioned(
              left: unit * x - unit * 0.12,
              top: unit * 1.14,
              width: unit * 0.24,
              height: unit * 0.24,
              child: const DecoratedBox(decoration: BoxDecoration(color: Color(0xFF3B2F55), shape: BoxShape.circle)),
            ),
        ]),
      );
}

class _Engine extends StatelessWidget {
  const _Engine({required this.unit});

  final double unit;

  @override
  Widget build(BuildContext context) => SizedBox(
        width: unit * 1.3,
        height: unit * 1.45,
        child: Stack(children: [
          Positioned(left: unit * 0.08, top: unit * 0.12, width: unit * 0.22, height: unit * 0.46, child: const ColoredBox(color: Color(0xFF3B2F55))),
          Positioned(left: 0, top: unit * 0.55, width: unit * 0.9, height: unit * 0.67, child: DecoratedBox(decoration: BoxDecoration(color: const Color(0xFFFF5A4E), borderRadius: BorderRadius.circular(unit * 0.08)))),
          Positioned(left: unit * 0.62, top: unit * 0.2, width: unit * 0.66, height: unit * 1.02, child: DecoratedBox(decoration: BoxDecoration(color: const Color(0xFF3D7BFF), borderRadius: BorderRadius.circular(unit * 0.08)))),
          Positioned(left: unit * 0.76, top: unit * 0.34, width: unit * 0.38, height: unit * 0.32, child: DecoratedBox(decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(unit * 0.06)))),
          for (final x in [0.22, 0.62, 1.02])
            Positioned(
              left: unit * x - unit * 0.15,
              top: unit * 1.06,
              width: unit * 0.3,
              height: unit * 0.3,
              child: const DecoratedBox(decoration: BoxDecoration(color: Color(0xFF3B2F55), shape: BoxShape.circle)),
            ),
        ]),
      );
}

/// Pictures in order with arrows, the last one a question mark.
class _Steps extends StatelessWidget {
  const _Steps({required this.round, required this.filled});

  final SequenceRound round;
  final bool filled;

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final n = round.sequence.steps.length;
        final size = math.min((box.maxWidth - 24) / n - 26, box.maxHeight * 0.7);
        Widget card(Widget child, {bool dashed = false}) => SizedBox(
              width: size,
              height: size,
              child: LandCard(land: Land.blocks, color: dashed ? const Color(0xFFF4F2FF) : null, padding: EdgeInsets.all(size * 0.08), child: child),
            );
        return Center(
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            for (final (i, s) in round.shown.indexed) ...[
              card(Semantics(label: sequenceThings[s]?.zh, child: Art(Land.blocks, s))),
              if (i < n - 1) const Padding(padding: EdgeInsets.symmetric(horizontal: 4), child: Icon(Icons.arrow_forward_rounded, color: Park.inkSoft, size: 22)),
            ],
            card(
              filled
                  ? Art(Land.blocks, round.answer)
                  : FittedBox(child: Text('?', style: TextStyle(fontSize: size * 0.5, fontWeight: FontWeight.w700, color: const Color(0xFF7A6FB0)))),
              dashed: !filled,
            ),
          ]),
        );
      });
}
