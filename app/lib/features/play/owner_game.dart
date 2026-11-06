import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/rounds.dart';
import 'drop_board.dart';
import 'play_screen.dart';
import 'sort_game.dart';

/// 是誰的？: people and animals in a row, each thinking of what they need;
/// the things wait on a shelf below.
class OwnerGame extends StatefulWidget {
  const OwnerGame({super.key, required this.round, required this.hooks});

  final OwnerRound round;
  final PlayHooks hooks;

  /// The sound someone makes when they get their thing.
  static String voice(Owner o, int i) => switch (o.id) {
        'dog' => 'say_dog',
        'cat' => 'say_cat',
        'rabbit' => 'say_rabbit',
        'baby' => 'say_baby',
        _ => ['thanks_a', 'thanks_b', 'thanks_c'][i % 3],
      };

  @override
  State<OwnerGame> createState() => _OwnerGameState();
}

class _OwnerGameState extends State<OwnerGame> {
  final _given = <String>{};

  String _name(String id) => ownerThings[id]?.zh ?? id;

  Owner _owner(String id) => widget.round.people.firstWhere((o) => o.id == id);

  bool _check(String thing, String target) {
    final o = _owner(target);
    if (o.wants == thing) {
      _given.add(o.id);
      widget.hooks.sfx(OwnerGame.voice(o, widget.round.people.indexOf(o)));
      if (_given.length == widget.round.people.length) {
        widget.hooks.done(o.why);
      } else {
        widget.hooks.good(o.why);
      }
      setState(() {});
      return true;
    }
    widget.hooks.sfx('bounce');
    widget.hooks.miss(Strings.notTheirs(_name(thing), o.zh));
    return false;
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final people = widget.round.people;
        final trayH = (h * 0.24).clamp(100.0, 180.0);
        final sceneH = h - trayH - 6;
        final colW = math.min((w - 16) / people.length, sceneH * 0.62);
        final left = (w - colW * people.length) / 2;
        final targets = {
          for (final (i, o) in people.indexed) o.id: Rect.fromLTWH(left + i * colW + 3, sceneH * 0.04, colW - 6, sceneH * 0.94),
        };
        final things = widget.round.things;
        final cell = math.min((w - 24) / things.length, trayH - 16);
        final size = cell * 0.82;
        final trayTop = h - trayH;
        final homes = {
          for (final (i, t) in things.indexed)
            t: Rect.fromCenter(center: Offset(w / 2 + (i - (things.length - 1) / 2) * cell, trayTop + trayH / 2), width: size, height: size),
        };
        return DropBoard(
          things: things,
          homes: homes,
          targets: targets,
          slot: (t, target, _) {
            final r = targets[target]!;
            final s = r.width * 0.42;
            return Rect.fromCenter(center: Offset(r.center.dx + r.width * 0.22, r.bottom - r.height * 0.3), width: s, height: s);
          },
          background: Stack(children: [
            Positioned(
              left: 8,
              right: 8,
              top: 0,
              height: sceneH,
              child: ClipRRect(borderRadius: BorderRadius.circular(18), child: const Art(Land.city, 'scene_street', fit: BoxFit.cover)),
            ),
            Positioned(left: 8, right: 8, top: trayTop, bottom: 0, child: const LandCard(land: Land.city, color: Color(0xFFFFF1D6))),
          ]),
          thingView: (t, {required lifted}) => AnimatedScale(
            scale: lifted ? 1.12 : 1,
            duration: const Duration(milliseconds: 120),
            child: Semantics(label: _name(t), child: Art(Land.city, t)),
          ),
          targetView: (id, {required glow, required on}) {
            final o = _owner(id);
            final given = _given.contains(id);
            return GlowRing(
              glow: glow,
              child: Semantics(
                label: o.zh,
                child: Column(children: [
                  Expanded(flex: 4, child: _Thought(thing: o.wants, given: given)),
                  Expanded(flex: 7, child: Wiggle(trigger: given ? 1 : 0, child: Art(Land.city, o.id))),
                ]),
              ),
            );
          },
          check: _check,
          rightTarget: (t) => people.firstWhere((o) => o.wants == t, orElse: () => people.first).id,
          onPick: (t) {
            widget.hooks.sfx('pick');
            widget.hooks.say(Strings.whose(_name(t)), en: widget.hooks.english ? ownerThings[t]?.en : null);
          },
        );
      });
}

/// A thought bubble with a pale outline of what someone needs (a check once
/// they have it).
class _Thought extends StatelessWidget {
  const _Thought({required this.thing, required this.given});

  final String thing;
  final bool given;

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final s = math.min(box.maxWidth, box.maxHeight) * 0.92;
        return Center(
          child: Container(
            width: s,
            height: s,
            padding: EdgeInsets.all(s * 0.16),
            decoration: BoxDecoration(
              color: given ? const Color(0xFFDFF7E9) : Colors.white.withValues(alpha: 0.85),
              shape: BoxShape.circle,
              border: Border.all(color: given ? Park.go : const Color(0xFFB9A6E0), width: 2.5),
            ),
            child: given
                ? const FittedBox(child: Icon(Icons.check_rounded, color: Park.go))
                : ColorFiltered(colorFilter: const ColorFilter.mode(Color(0x999A8CC0), BlendMode.srcIn), child: Art(Land.city, thing)),
          ),
        );
      });
}
