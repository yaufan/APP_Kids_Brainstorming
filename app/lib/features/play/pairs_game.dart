import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/strings.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/rounds.dart';
import 'play_screen.dart';

/// 連連看: two columns of paper cards; draw a line with a finger from a card
/// to its partner on the other side. The line starts the moment the finger
/// touches (raw pointer events).
class PairsGame extends StatefulWidget {
  const PairsGame({super.key, required this.round, required this.hooks});

  final PairsRound round;
  final PlayHooks hooks;

  static const colors = [Color(0xFFE5674F), Color(0xFF4F8FD9), Color(0xFF6DAE4C), Color(0xFFB36BD6)];

  @override
  State<PairsGame> createState() => _PairsGameState();
}

/// A card: which pair and which side.
typedef _End = ({Pair pair, bool left});

class _PairsGameState extends State<PairsGame> {
  final _joined = <Pair>[];
  _End? _from;
  Offset? _to;
  int? _pointer;
  var _shake = 0;
  _End? _wrong;

  String _name(String id) => pairThings[id]?.zh ?? id;

  void _down(PointerDownEvent e, Map<_End, Rect> cards) {
    if (_pointer != null) return;
    for (final c in cards.entries) {
      if (c.value.inflate(6).contains(e.localPosition) && !_joined.contains(c.key.pair)) {
        _pointer = e.pointer;
        final id = c.key.left ? c.key.pair.a : c.key.pair.b;
        widget.hooks.sfx('crayon');
        widget.hooks.say(_name(id), en: pairThings[id]?.en);
        setState(() {
          _from = c.key;
          _to = e.localPosition;
        });
        return;
      }
    }
  }

  void _move(PointerMoveEvent e) {
    if (e.pointer != _pointer) return;
    setState(() => _to = e.localPosition);
  }

  void _up(PointerEvent e, Map<_End, Rect> cards) {
    if (e.pointer != _pointer) return;
    _pointer = null;
    final from = _from;
    final at = _to;
    setState(() {
      _from = null;
      _to = null;
    });
    if (from == null || at == null) return;
    for (final c in cards.entries) {
      if (c.key.left == from.left || !c.value.inflate(10).contains(at)) continue;
      if (_joined.contains(c.key.pair)) return;
      if (c.key.pair == from.pair) {
        setState(() => _joined.add(from.pair));
        widget.hooks.sfx('snap');
        if (_joined.length == widget.round.left.length) {
          widget.hooks.done(from.pair.why);
        } else {
          widget.hooks.good(from.pair.why);
        }
      } else {
        setState(() {
          _wrong = c.key;
          _shake++;
        });
        widget.hooks.miss(Strings.notPair);
      }
      return;
    }
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final n = widget.round.left.length;
        final size = math.min(math.min((w - 40) * 0.36, 190.0), (h - 16) / n - 14);
        final gap = (h - n * size) / (n + 1);
        final lx = w * 0.06, rx = w * 0.94 - size;
        final cards = <_End, Rect>{
          for (final (i, p) in widget.round.left.indexed) (pair: p, left: true): Rect.fromLTWH(lx, gap + i * (size + gap), size, size),
          for (final (i, p) in widget.round.right.indexed) (pair: p, left: false): Rect.fromLTWH(rx, gap + i * (size + gap), size, size),
        };
        Offset dot(_End e) {
          final r = cards[e]!;
          return e.left ? r.centerRight + const Offset(8, 0) : r.centerLeft - const Offset(8, 0);
        }

        final lines = [
          for (final (i, p) in _joined.indexed) (dot((pair: p, left: true)), dot((pair: p, left: false)), PairsGame.colors[i % PairsGame.colors.length]),
        ];
        return Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (e) => _down(e, cards),
          onPointerMove: _move,
          onPointerUp: (e) => _up(e, cards),
          onPointerCancel: (e) => _up(e, cards),
          child: Stack(children: [
            for (final c in cards.entries)
              Positioned.fromRect(
                rect: c.value,
                child: Wiggle(
                  trigger: c.key == _wrong ? _shake : 0,
                  child: Semantics(
                    label: _name(c.key.left ? c.key.pair.a : c.key.pair.b),
                    child: LandCard(
                      land: Land.forest,
                      seed: cards.keys.toList().indexOf(c.key),
                      ring: _joined.contains(c.key.pair) ? PairsGame.colors[_joined.indexOf(c.key.pair) % PairsGame.colors.length] : (_from == c.key ? const Color(0xFFFFC53D) : null),
                      padding: EdgeInsets.all(size * 0.1),
                      child: Art(Land.forest, c.key.left ? c.key.pair.a : c.key.pair.b),
                    ),
                  ),
                ),
              ),
            Positioned.fill(
              child: IgnorePointer(
                child: CustomPaint(
                  painter: _Lines(
                    lines: lines,
                    dots: [for (final c in cards.keys) dot(c)],
                    live: _from == null || _to == null ? null : (dot(_from!), _to!),
                  ),
                ),
              ),
            ),
          ]),
        );
      });
}

/// The drawn lines: wobbly like a crayon, with a dot at each end.
class _Lines extends CustomPainter {
  _Lines({required this.lines, required this.dots, this.live});

  final List<(Offset, Offset, Color)> lines;
  final List<Offset> dots;
  final (Offset, Offset)? live;

  Path _wobbly(Offset a, Offset b) {
    final path = Path()..moveTo(a.dx, a.dy);
    const n = 12;
    final d = b - a;
    final normal = d.distance == 0 ? Offset.zero : Offset(-d.dy, d.dx) / d.distance;
    for (var i = 1; i <= n; i++) {
      final t = i / n;
      final wob = math.sin(t * math.pi * 3) * 3 * (1 - (2 * t - 1).abs());
      final p = Offset.lerp(a, b, t)! + normal * wob;
      path.lineTo(p.dx, p.dy);
    }
    return path;
  }

  @override
  void paint(Canvas canvas, Size size) {
    for (final d in dots) {
      canvas.drawCircle(d, 7, Paint()..color = const Color(0xFFFFF8EC));
      canvas.drawCircle(d, 7, Paint()
        ..color = const Color(0xFFB59B70)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2);
    }
    for (final (a, b, c) in lines) {
      canvas.drawPath(_wobbly(a, b), Paint()
        ..color = c
        ..style = PaintingStyle.stroke
        ..strokeWidth = 9
        ..strokeCap = StrokeCap.round);
      canvas.drawCircle(a, 8, Paint()..color = c);
      canvas.drawCircle(b, 8, Paint()..color = c);
    }
    final l = live;
    if (l != null) {
      canvas.drawPath(_wobbly(l.$1, l.$2), Paint()
        ..color = const Color(0xCCF2A93B)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 9
        ..strokeCap = StrokeCap.round);
      canvas.drawCircle(l.$1, 8, Paint()..color = const Color(0xFFF2A93B));
    }
  }

  @override
  bool shouldRepaint(_Lines old) => true;
}
