import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Things that wait at [homes] and go onto [targets]: drag one with a finger
/// (raw pointer events, so it moves the moment it is touched), or tap it and
/// then tap where it goes. A wrong place springs it back home; after two
/// misses with the same thing its right place glows (docs/design.md
/// "不會失敗").
class DropBoard extends StatefulWidget {
  const DropBoard({
    super.key,
    required this.things,
    required this.homes,
    required this.targets,
    required this.slot,
    required this.thingView,
    required this.targetView,
    required this.check,
    required this.rightTarget,
    this.background,
    this.onPick,
  });

  final List<String> things;
  final Map<String, Rect> homes;
  final Map<String, Rect> targets;

  /// Where a thing sits once it is on [target] (the [n]th thing there).
  final Rect Function(String thing, String target, int n) slot;
  final Widget Function(String thing, {required bool lifted}) thingView;
  final Widget Function(String target, {required bool glow, required List<String> on}) targetView;

  /// Whether [thing] belongs on [target]; the game says why or gives a hint.
  final bool Function(String thing, String target) check;
  final String Function(String thing) rightTarget;
  final Widget? background;

  /// A thing was picked up (the game says its name).
  final void Function(String thing)? onPick;

  @override
  State<DropBoard> createState() => DropBoardState();
}

class DropBoardState extends State<DropBoard> {
  final _placed = <String, String>{};
  final _misses = <String, int>{};
  String? _dragging;
  String? _selected;
  Offset _at = Offset.zero;
  Offset _grab = Offset.zero;
  Offset _down = Offset.zero;
  var _moved = false;
  int? _pointer;

  /// Things still waiting.
  List<String> get waiting => [for (final t in widget.things) if (!_placed.containsKey(t)) t];

  String? _thingAt(Offset p) {
    for (final t in waiting.reversed) {
      if (widget.homes[t]!.inflate(6).contains(p)) return t;
    }
    return null;
  }

  String? _targetAt(Offset p) {
    for (final e in widget.targets.entries) {
      if (e.value.contains(p)) return e.key;
    }
    return null;
  }

  void _down_(PointerDownEvent e) {
    if (_pointer != null) return;
    final p = e.localPosition;
    final thing = _thingAt(p);
    if (thing != null) {
      _pointer = e.pointer;
      setState(() {
        _dragging = thing;
        _grab = p - widget.homes[thing]!.center;
        _at = p;
        _down = p;
        _moved = false;
      });
      widget.onPick?.call(thing);
      return;
    }
    // Tap a thing, then tap where it goes.
    final picked = _selected;
    final target = _targetAt(p);
    if (picked != null && target != null) _drop(picked, target);
  }

  void _move(PointerMoveEvent e) {
    if (e.pointer != _pointer || _dragging == null) return;
    setState(() {
      _at = e.localPosition;
      if ((_at - _down).distance > 12) _moved = true;
    });
  }

  void _up(PointerEvent e) {
    if (e.pointer != _pointer) return;
    _pointer = null;
    final thing = _dragging;
    if (thing == null) return;
    if (!_moved) {
      setState(() {
        _dragging = null;
        _selected = _selected == thing ? null : thing;
      });
      return;
    }
    final target = _targetAt(_at - _grab) ?? _targetAt(_at);
    setState(() => _dragging = null);
    if (target != null) {
      _drop(thing, target);
    } else {
      setState(() {});
    }
  }

  void _drop(String thing, String target) {
    final right = widget.check(thing, target);
    setState(() {
      _selected = null;
      if (right) {
        _placed[thing] = target;
      } else {
        _misses[thing] = (_misses[thing] ?? 0) + 1;
        _bounced = thing;
        _bounceKey++;
      }
    });
  }

  String? _bounced;
  var _bounceKey = 0;

  /// The place to glow: the right one for a thing picked up or chosen after
  /// two misses.
  String? get _glow {
    final t = _dragging ?? _selected;
    if (t == null || (_misses[t] ?? 0) < 2) return null;
    return widget.rightTarget(t);
  }

  @override
  Widget build(BuildContext context) {
    final glow = _glow;
    final on = <String, List<String>>{};
    for (final e in _placed.entries) {
      (on[e.value] ??= []).add(e.key);
    }
    Rect where(String t) {
      final target = _placed[t];
      if (target != null) return widget.slot(t, target, on[target]!.indexOf(t));
      if (t == _dragging) {
        final home = widget.homes[t]!;
        return Rect.fromCenter(center: _at - _grab, width: home.width * 1.12, height: home.height * 1.12);
      }
      return widget.homes[t]!;
    }

    final order = [...widget.things.where((t) => t != _dragging), ?_dragging];
    return Listener(
      behavior: HitTestBehavior.opaque,
      onPointerDown: _down_,
      onPointerMove: _move,
      onPointerUp: _up,
      onPointerCancel: _up,
      child: Stack(clipBehavior: Clip.none, children: [
        if (widget.background != null) Positioned.fill(child: widget.background!),
        for (final e in widget.targets.entries)
          Positioned.fromRect(rect: e.value, child: widget.targetView(e.key, glow: e.key == glow, on: on[e.key] ?? const [])),
        for (final t in order)
          AnimatedPositioned.fromRect(
            key: ValueKey('thing-$t'),
            rect: where(t),
            duration: t == _dragging ? Duration.zero : Duration(milliseconds: _placed.containsKey(t) ? 320 : 520),
            curve: _placed.containsKey(t) ? Curves.easeOutBack : Curves.elasticOut,
            child: _Shake(
              trigger: t == _bounced ? _bounceKey : 0,
              child: Semantics(
                container: true,
                selected: t == _selected,
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    boxShadow: t == _selected ? const [BoxShadow(color: Color(0x88FFC53D), blurRadius: 18, spreadRadius: 6)] : null,
                  ),
                  child: widget.thingView(t, lifted: t == _dragging || t == _selected),
                ),
              ),
            ),
          ),
      ]),
    );
  }
}

class _Shake extends StatefulWidget {
  const _Shake({required this.trigger, required this.child});

  final int trigger;
  final Widget child;

  @override
  State<_Shake> createState() => _ShakeState();
}

class _ShakeState extends State<_Shake> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 500));

  @override
  void didUpdateWidget(_Shake old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger && widget.trigger != 0) _c.forward(from: 0);
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) {
          final t = _c.value;
          return Transform.rotate(angle: math.sin(t * math.pi * 6) * (1 - t) * 0.22, child: child);
        },
        child: widget.child,
      );
}
