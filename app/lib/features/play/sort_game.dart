import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/rounds.dart';
import 'drop_board.dart';
import 'play_screen.dart';

/// 放哪裡？: a scene with its places on top, the things on a rug below.
class SortGame extends StatefulWidget {
  const SortGame({super.key, required this.round, required this.hooks});

  final SortRound round;
  final PlayHooks hooks;

  /// Things that blow a bubble when put in the wrong place.
  static const watery = {'fish', 'octopus'};

  @override
  State<SortGame> createState() => _SortGameState();
}

class _SortGameState extends State<SortGame> {
  var _placed = 0;

  String _name(String id) => sortThings[id]?.zh ?? id;

  bool _check(String thing, String target) {
    final stray = widget.round.things.firstWhere((t) => t.id == thing);
    if (stray.place == target) {
      _placed++;
      if (_placed == widget.round.things.length) {
        widget.hooks.done(stray.why);
      } else {
        widget.hooks.good(stray.why);
      }
      return true;
    }
    widget.hooks.sfx(SortGame.watery.contains(thing) ? 'blub' : 'bounce');
    widget.hooks.miss(Strings.notHere(_name(thing), widget.round.scene.place(target).zh));
    return false;
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final trayH = (h * 0.27).clamp(110.0, 210.0);
        final sceneH = math.min(h - trayH - 6, w * 600 / 390);
        final sceneW = sceneH * 390 / 600;
        final left = (w - sceneW) / 2;
        final scene = Rect.fromLTWH(left, 0, sceneW, sceneH);
        final targets = {
          for (final p in widget.round.places)
            p.id: Rect.fromCenter(center: Offset(left + p.x * sceneW, p.y * sceneH), width: p.w * sceneW, height: p.w * sceneW),
        };
        final things = [for (final t in widget.round.things) t.id];
        final n = things.length;
        final rows = n <= 3 ? 1 : 2;
        final cols = (n / rows).ceil();
        final cell = math.min((w - 24) / cols, (trayH - 12) / rows);
        final size = cell * 0.84;
        final trayTop = h - trayH;
        final homes = <String, Rect>{
          for (final (i, t) in things.indexed)
            t: Rect.fromCenter(
              center: Offset(
                w / 2 + ((i % cols) - (math.min(cols, n - (i ~/ cols) * cols) - 1) / 2) * cell,
                trayTop + 6 + cell / 2 + (i ~/ cols) * cell + (trayH - 12 - rows * cell) / 2,
              ),
              width: size,
              height: size,
            ),
        };
        return DropBoard(
          things: things,
          homes: homes,
          targets: targets,
          slot: (t, target, k) {
            final r = targets[target]!;
            final s = r.width * 0.4;
            return Rect.fromCenter(center: r.center + Offset(((k % 3) - 1) * s * 0.55, (k ~/ 3) * s * 0.3), width: s, height: s);
          },
          background: Stack(children: [
            Positioned.fromRect(rect: scene, child: ClipRRect(borderRadius: BorderRadius.circular(18), child: Art(Land.city, 'scene_${widget.round.scene.id}', fit: BoxFit.cover))),
            Positioned(
              left: 8,
              right: 8,
              top: trayTop,
              bottom: 0,
              child: const LandCard(land: Land.city, color: Color(0xFFFFF1D6)),
            ),
          ]),
          thingView: (t, {required lifted}) => AnimatedScale(
            scale: lifted ? 1.12 : 1,
            duration: const Duration(milliseconds: 120),
            child: Semantics(label: _name(t), child: Art(Land.city, t)),
          ),
          targetView: (p, {required glow, required on}) => _Glow(glow: glow, child: Semantics(label: widget.round.scene.place(p).zh, child: Art(Land.city, p))),
          check: _check,
          rightTarget: (t) => widget.round.things.firstWhere((x) => x.id == t).place,
          onPick: (t) {
            widget.hooks.sfx('pick');
            widget.hooks.say(_name(t), en: sortThings[t]?.en);
          },
        );
      });
}

/// A soft pulsing ring around the right place, after two misses.
class _Glow extends StatefulWidget {
  const _Glow({required this.glow, required this.child});

  final bool glow;
  final Widget child;

  @override
  State<_Glow> createState() => _GlowState();
}

class _GlowState extends State<_Glow> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))..repeat(reverse: true);

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.glow
      ? AnimatedBuilder(
          animation: _c,
          builder: (_, child) => DecoratedBox(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24),
              boxShadow: [BoxShadow(color: Park.gold.withValues(alpha: 0.35 + 0.4 * _c.value), blurRadius: 24, spreadRadius: 4 + 6 * _c.value)],
            ),
            child: child,
          ),
          child: widget.child,
        )
      : widget.child;
}

/// The glow, for the other boards.
class GlowRing extends StatelessWidget {
  const GlowRing({super.key, required this.glow, required this.child});

  final bool glow;
  final Widget child;

  @override
  Widget build(BuildContext context) => _Glow(glow: glow, child: child);
}
