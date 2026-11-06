import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../core/content.dart';
import '../core/providers.dart';
import 'theme.dart';

/// A picture of a land (`assets/art/<land>/<id>.svg`).
class Art extends StatelessWidget {
  const Art(this.land, this.id, {super.key, this.fit = BoxFit.contain});

  final Land land;
  final String id;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) => SvgPicture.asset(art(land, id), fit: fit, excludeFromSemantics: true);
}

/// A picture outside the lands (阿布, the park map): `assets/art/park/<id>.svg`.
class ParkArt extends StatelessWidget {
  const ParkArt(this.id, {super.key, this.fit = BoxFit.contain});

  final String id;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) => SvgPicture.asset('assets/art/park/$id.svg', fit: fit, excludeFromSemantics: true);
}

/// 阿布 in a land's style: wave, think or cheer.
class Abu extends StatelessWidget {
  const Abu({super.key, required this.land, this.pose = 'wave'});

  final Land land;
  final String pose;

  @override
  Widget build(BuildContext context) => ParkArt('abu_${land.name}_$pose');
}

/// Shrinks a little while pressed and clicks.
class Pressable extends ConsumerStatefulWidget {
  const Pressable({super.key, required this.child, this.onTap, this.sound = 'tap'});

  final Widget child;
  final VoidCallback? onTap;
  final String? sound;

  @override
  ConsumerState<Pressable> createState() => _PressableState();
}

class _PressableState extends ConsumerState<Pressable> {
  var _down = false;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.onTap != null;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      excludeFromSemantics: true,
      onTapDown: enabled ? (_) => setState(() => _down = true) : null,
      onTapCancel: enabled ? () => setState(() => _down = false) : null,
      onTapUp: enabled ? (_) => setState(() => _down = false) : null,
      onTap: enabled
          ? () {
              final s = widget.sound;
              if (s != null) ref.read(soundsProvider).play(s);
              widget.onTap!();
            }
          : null,
      child: AnimatedScale(scale: _down ? 0.93 : 1, duration: const Duration(milliseconds: 90), child: widget.child),
    );
  }
}

/// A card in a land's style: A outlined with a hard coloured edge under it,
/// B a piece of paper with uneven edges and a soft shadow, C a flat block.
class LandCard extends StatelessWidget {
  const LandCard({super.key, required this.land, this.child, this.padding = EdgeInsets.zero, this.ring, this.color, this.seed = 0});

  final Land land;
  final Widget? child;
  final EdgeInsets padding;

  /// A coloured ring (gold for right, the land's accent for picked up).
  final Color? ring;
  final Color? color;

  /// Varies the paper's edge from card to card.
  final int seed;

  @override
  Widget build(BuildContext context) {
    final look = LandLook.of(land);
    final fill = color ?? look.card;
    switch (land) {
      case Land.city:
        return AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: padding,
          decoration: BoxDecoration(
            color: fill,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: ring ?? Color.lerp(look.edge, Colors.white, 0.2)!, width: ring == null ? 2.5 : 5),
            boxShadow: [BoxShadow(color: look.edge, offset: const Offset(0, 5))],
          ),
          child: child,
        );
      case Land.forest:
        return CustomPaint(
          painter: _PaperPainter(fill: fill, ring: ring, seed: seed),
          child: Padding(padding: padding, child: child),
        );
      case Land.blocks:
        return AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: padding,
          decoration: BoxDecoration(
            color: fill,
            borderRadius: BorderRadius.circular(16),
            border: ring == null ? null : Border.all(color: ring!, width: 5),
            boxShadow: [BoxShadow(color: look.edge, offset: const Offset(0, 6))],
          ),
          child: child,
        );
    }
  }
}

/// A sheet of paper: a gently uneven rounded rectangle with a soft shadow.
class _PaperPainter extends CustomPainter {
  _PaperPainter({required this.fill, required this.ring, required this.seed});

  final Color fill;
  final Color? ring;
  final int seed;

  Path _sheet(Size s) {
    final r = math.Random(seed * 7 + 3);
    const step = 14.0;
    final pts = <Offset>[];
    void edge(Offset a, Offset b) {
      final n = math.max(2, ((b - a).distance / step).round());
      for (var i = 0; i < n; i++) {
        final p = Offset.lerp(a, b, i / n)!;
        final d = (b - a);
        final normal = Offset(-d.dy, d.dx) / d.distance;
        pts.add(p + normal * (r.nextDouble() - 0.5) * 2.4);
      }
    }

    const c = 10.0;
    edge(Offset(c, 0), Offset(s.width - c, 0));
    edge(Offset(s.width, c), Offset(s.width, s.height - c));
    edge(Offset(s.width - c, s.height), Offset(c, s.height));
    edge(Offset(0, s.height - c), Offset(0, c));
    return Path()..addPolygon(pts, true);
  }

  @override
  void paint(Canvas canvas, Size size) {
    final sheet = _sheet(size);
    canvas.drawPath(sheet.shift(const Offset(2, 5)), Paint()
      ..color = const Color(0x2E5A4A30)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4));
    canvas.drawPath(sheet, Paint()..color = fill);
    canvas.drawPath(sheet, Paint()
      ..color = ring ?? const Color(0x1A5A4A30)
      ..style = PaintingStyle.stroke
      ..strokeWidth = ring == null ? 1.2 : 5);
  }

  @override
  bool shouldRepaint(_PaperPainter old) => old.fill != fill || old.ring != ring || old.seed != seed;
}

/// A round button with an icon, in a land's style.
class LandButton extends StatelessWidget {
  const LandButton({super.key, required this.land, required this.label, required this.icon, this.onTap, this.size = 56, this.filled = false, this.sound = 'tap'});

  final Land land;
  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final double size;
  final bool filled;
  final String? sound;

  @override
  Widget build(BuildContext context) {
    final look = LandLook.of(land);
    final bg = filled ? look.accent : Colors.white;
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: sound,
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: bg,
            shape: BoxShape.circle,
            border: land == Land.city ? Border.all(color: Color.lerp(bg, Colors.black, 0.18)!, width: 2.5) : null,
            boxShadow: [BoxShadow(color: land == Land.forest ? const Color(0x335A4A30) : look.edge, offset: const Offset(0, 4), blurRadius: land == Land.forest ? 6 : 0)],
          ),
          child: Icon(icon, size: size * 0.5, color: filled ? Colors.white : Park.ink),
        ),
      ),
    );
  }
}

/// A wide button with an icon and a word.
class WideButton extends StatelessWidget {
  const WideButton({super.key, required this.label, required this.icon, this.onTap, this.color = Park.orange, this.height = 62, this.sound = 'tap'});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final Color color;
  final double height;
  final String? sound;

  @override
  Widget build(BuildContext context) {
    final light = color == Colors.white;
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: sound,
        child: Container(
          height: height,
          padding: EdgeInsets.symmetric(horizontal: height * 0.42),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(height / 2),
            border: Border.all(color: Color.lerp(color, Colors.black, 0.15)!, width: 2.5),
            boxShadow: [BoxShadow(color: Color.lerp(color, Colors.black, 0.25)!, offset: const Offset(0, 4))],
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(icon, size: height * 0.46, color: light ? Park.orange : Colors.white),
            const SizedBox(width: 10),
            Text(label, style: TextStyle(fontSize: height * 0.36, fontWeight: FontWeight.w700, color: light ? Park.ink : Colors.white)),
          ]),
        ),
      ),
    );
  }
}

/// A speech bubble with a speaker: tap to hear it again.
class SpeakBubble extends StatelessWidget {
  const SpeakBubble({super.key, required this.land, required this.text, this.onTap, this.size = 22});

  final Land land;
  final String text;
  final VoidCallback? onTap;
  final double size;

  @override
  Widget build(BuildContext context) {
    final look = LandLook.of(land);
    return Semantics(
      container: true,
      button: onTap != null,
      label: text,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        sound: null,
        child: LandCard(
          land: land,
          padding: const EdgeInsets.fromLTRB(10, 8, 18, 8),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            Container(
              width: size * 1.7,
              height: size * 1.7,
              decoration: BoxDecoration(color: look.accent, shape: land == Land.blocks ? BoxShape.rectangle : BoxShape.circle, borderRadius: land == Land.blocks ? BorderRadius.circular(8) : null),
              child: Icon(Icons.volume_up_rounded, color: Colors.white, size: size),
            ),
            const SizedBox(width: 10),
            Flexible(child: Text(text, style: TextStyle(fontSize: size, fontWeight: FontWeight.w700, color: Park.ink, height: 1.3))),
          ]),
        ),
      ),
    );
  }
}

/// Shakes its child side to side once each time [trigger] changes.
class Wiggle extends StatefulWidget {
  const Wiggle({super.key, required this.trigger, required this.child, this.amount = 0.08});

  final int trigger;
  final Widget child;
  final double amount;

  @override
  State<Wiggle> createState() => _WiggleState();
}

class _WiggleState extends State<Wiggle> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));

  @override
  void didUpdateWidget(Wiggle old) {
    super.didUpdateWidget(old);
    if (old.trigger != widget.trigger) _c.forward(from: 0);
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
          return Transform.rotate(angle: math.sin(t * math.pi * 4) * (1 - t) * widget.amount, child: child);
        },
        child: widget.child,
      );
}

/// A gentle bob up and down, for things waiting to be picked up.
class Bob extends StatefulWidget {
  const Bob({super.key, required this.child, this.phase = 0, this.amount = 4});

  final Widget child;
  final double phase;
  final double amount;

  @override
  State<Bob> createState() => _BobState();
}

class _BobState extends State<Bob> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1800))..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) => Transform.translate(offset: Offset(0, math.sin((_c.value + widget.phase) * 2 * math.pi) * widget.amount), child: child),
        child: widget.child,
      );
}

/// Dots: [done] of [count] filled, the current one wide.
class RoundDots extends StatelessWidget {
  const RoundDots({super.key, required this.count, required this.done, this.color = Park.orange});

  final int count;
  final int done;
  final Color color;

  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
        for (var i = 0; i < count; i++)
          AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            margin: const EdgeInsets.symmetric(horizontal: 3),
            width: i == done ? 24 : 11,
            height: 11,
            decoration: BoxDecoration(
              color: i < done ? color : (i == done ? Color.lerp(color, Colors.white, 0.35) : Colors.white),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: Color.lerp(color, Colors.black, 0.1)!, width: 1.5),
            ),
          ),
      ]);
}

/// A token on the block train: a flat circle, square, triangle or star.
class TokenView extends StatelessWidget {
  const TokenView(this.token, {super.key, this.size = 48});

  final Token token;
  final double size;

  static const hues = {Hue.red: Color(0xFFFF5A4E), Hue.blue: Color(0xFF3D7BFF), Hue.yellow: Color(0xFFFFC21F), Hue.green: Color(0xFF2FBF71)};

  @override
  Widget build(BuildContext context) {
    final s = size * (0.55 + 0.15 * token.size) / 1.0;
    return SizedBox(width: size, height: size, child: Center(child: CustomPaint(size: Size.square(s), painter: _TokenPainter(token.shape, hues[token.hue]!))));
  }
}

class _TokenPainter extends CustomPainter {
  _TokenPainter(this.shape, this.color);

  final Shape shape;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final p = Paint()..color = color;
    final dark = Paint()..color = Color.lerp(color, Colors.black, 0.18)!;
    switch (shape) {
      case Shape.circle:
        canvas.drawCircle(Offset(w / 2, w / 2), w / 2, p);
        canvas.drawCircle(Offset(w * 0.36, w * 0.34), w * 0.1, Paint()..color = Colors.white.withValues(alpha: 0.45));
      case Shape.square:
        canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(0, 0, w, w), Radius.circular(w * 0.14)), p);
        canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(0, w * 0.78, w, w * 0.22), Radius.circular(w * 0.1)), dark);
      case Shape.triangle:
        canvas.drawPath(Path()
          ..moveTo(w / 2, 0)
          ..lineTo(w, w * 0.92)
          ..lineTo(0, w * 0.92)
          ..close(), p);
      case Shape.star:
        final path = Path();
        for (var i = 0; i < 10; i++) {
          final r = i.isEven ? w / 2 : w * 0.22;
          final a = -math.pi / 2 + i * math.pi / 5;
          final pt = Offset(w / 2 + r * math.cos(a), w * 0.53 + r * math.sin(a));
          i == 0 ? path.moveTo(pt.dx, pt.dy) : path.lineTo(pt.dx, pt.dy);
        }
        canvas.drawPath(path..close(), p);
    }
  }

  @override
  bool shouldRepaint(_TokenPainter old) => old.shape != shape || old.color != color;
}
