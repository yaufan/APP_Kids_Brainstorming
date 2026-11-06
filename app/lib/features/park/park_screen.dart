import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';

/// Where things sit on the park map, as fractions of its 390×844 picture
/// (design/art/park_spots.json, from design/art/park_art.py).
abstract final class Spots {
  static const title = Offset(0.500, 0.103);
  static const games = {
    GameKind.odd: Offset(0.272, 0.306),
    GameKind.next: Offset(0.749, 0.436),
    GameKind.pairs: Offset(0.195, 0.626),
    GameKind.detective: Offset(0.810, 0.574),
    GameKind.sort: Offset(0.185, 0.881),
    GameKind.owner: Offset(0.815, 0.936),
  };
  static const lands = {Land.blocks: Offset(0.290, 0.455), Land.forest: Offset(0.385, 0.699), Land.city: Offset(0.526, 0.853)};
  static const abu = Offset(0.526, 0.938);
}

/// The home screen: the park map with three lands and their six games.
/// Tapping a game sign sends 阿布 in, changing into that land's style.
class ParkScreen extends ConsumerStatefulWidget {
  const ParkScreen({super.key});

  /// The free version opens 卡通城 (docs/design.md "以後上架和收費").
  static const free = {Land.city};

  @override
  ConsumerState<ParkScreen> createState() => _ParkScreenState();
}

class _ParkScreenState extends ConsumerState<ParkScreen> with SingleTickerProviderStateMixin {
  static var _welcomed = false;

  late final Sounds _sounds;
  late final _poof = AnimationController(vsync: this, duration: const Duration(milliseconds: 1100));
  Land? _going;
  var _line = 0;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.park);
    if (!_welcomed) {
      _welcomed = true;
      WidgetsBinding.instance.addPostFrameCallback((_) => _say(Strings.welcome));
    }
  }

  @override
  void dispose() {
    _poof.dispose();
    _sounds.release(this);
    super.dispose();
  }

  void _say(String zh) {
    if (mounted && ref.read(gameProvider).settings.voice) ref.read(voiceProvider).say(zh);
  }

  Future<void> _open(GameKind g) async {
    if (_going != null) return;
    setState(() => _going = g.land);
    _sounds.play('poof');
    _say(Strings.enter(g.land));
    await _poof.forward(from: 0);
    if (!mounted) return;
    await context.push('/play/${g.name}');
    if (mounted) setState(() => _going = null);
    _poof.reset();
  }

  void _abu() {
    _sounds.play('abu_yay');
    _say(Strings.abuLines[_line++ % Strings.abuLines.length]);
  }

  Future<void> _openParent() async {
    if (await showParentGate(context) && mounted) await context.push('/parent');
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final s = g.settings;
    return Scaffold(
      backgroundColor: const Color(0xFFCDEBFF),
      body: LayoutBuilder(builder: (context, box) {
        // The map keeps its shape; on wide screens the sky fills the sides.
        final scale = math.min(box.maxWidth / 390, box.maxHeight / 844);
        final mw = 390 * scale, mh = 844 * scale;
        final ox = (box.maxWidth - mw) / 2, oy = (box.maxHeight - mh) / 2;
        Offset at(Offset f) => Offset(ox + f.dx * mw, oy + f.dy * mh);
        final pad = MediaQuery.paddingOf(context);
        return Stack(children: [
          Positioned(left: ox, top: oy, width: mw, height: mh, child: const ParkArt('map', fit: BoxFit.fill)),
          _place(at(Spots.title), mw * 0.57, child: _Title(width: mw * 0.57)),
          for (final MapEntry(key: land, value: spot) in Spots.lands.entries)
            _place(at(spot), mw * 0.26, child: _LandTag(land: land, stars: [for (final k in GameKind.values) if (k.land == land) g.starsOf(k)].fold(0, (a, b) => a + b))),
          for (final MapEntry(key: game, value: spot) in Spots.games.entries)
            if (s.shows(game))
              _place(
                at(spot),
                mw * 0.3,
                child: _Sign(
                  game: game,
                  stars: g.starsOf(game),
                  locked: !s.full && !ParkScreen.free.contains(game.land),
                  onTap: () => _open(game),
                ),
              ),
          _place(
            at(Spots.abu),
            mw * 0.26,
            child: Semantics(
              container: true,
              button: true,
              label: '阿布',
              excludeSemantics: true,
              onTap: _abu,
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: _abu,
                child: AnimatedBuilder(
                  animation: _poof,
                  builder: (_, _) {
                    final t = _poof.value;
                    final land = t > 0.45 && _going != null ? _going! : Land.city;
                    final puff = math.sin(t * math.pi);
                    return SizedBox(
                      width: mw * 0.26,
                      height: mw * 0.26,
                      child: Stack(clipBehavior: Clip.none, children: [
                        Positioned.fill(child: Transform.scale(scale: 1 + 0.25 * puff, child: Bob(child: Abu(land: land, pose: t > 0.45 ? 'cheer' : 'wave')))),
                        if (t > 0 && t < 0.9) Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _Puff(puff)))),
                      ]),
                    );
                  },
                ),
              ),
            ),
          ),
          Positioned(
            left: 14,
            bottom: 14 + pad.bottom,
            child: WideButton(label: Strings.book, icon: Icons.menu_book_rounded, color: Colors.white, height: 54, onTap: () => context.push('/book')),
          ),
          Positioned(
            right: 12,
            top: 10 + pad.top,
            child: Semantics(
              container: true,
              button: true,
              label: Strings.parent,
              excludeSemantics: true,
              onTap: _openParent,
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: _openParent,
                child: Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.8), shape: BoxShape.circle),
                  child: const Icon(Icons.lock_outline_rounded, color: Park.inkSoft, size: 22),
                ),
              ),
            ),
          ),
        ]);
      }),
    );
  }

  /// [child] centred on [center], [width] wide.
  Widget _place(Offset center, double width, {required Widget child}) => Positioned(
        left: center.dx - width / 2,
        top: center.dy,
        width: width,
        child: FractionalTranslation(translation: const Offset(0, -0.5), child: Center(child: child)),
      );
}

/// The park's name on the plank under the rainbow.
class _Title extends StatelessWidget {
  const _Title({required this.width});

  final double width;

  @override
  Widget build(BuildContext context) => Stack(children: [
        Text(
          Strings.appName,
          style: TextStyle(
            fontSize: width * 0.15,
            fontWeight: FontWeight.w700,
            foreground: Paint()
              ..style = PaintingStyle.stroke
              ..strokeWidth = width * 0.025
              ..color = Colors.white,
          ),
        ),
        Text(Strings.appName, style: TextStyle(fontSize: width * 0.15, fontWeight: FontWeight.w700, color: const Color(0xFFE8503A))),
      ]);
}

/// A game's sign on the map, in its land's style, with its stars.
class _Sign extends StatelessWidget {
  const _Sign({required this.game, required this.stars, required this.locked, required this.onTap});

  final GameKind game;
  final int stars;
  final bool locked;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: !locked,
        label: game.zh,
        excludeSemantics: true,
        onTap: locked ? null : onTap,
        child: Pressable(
          onTap: locked ? null : onTap,
          child: Opacity(
            opacity: locked ? 0.55 : 1,
            child: LandCard(
              land: game.land,
              seed: game.index,
              padding: const EdgeInsets.fromLTRB(10, 6, 10, 6),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Row(mainAxisSize: MainAxisSize.min, children: [
                  if (locked) const Padding(padding: EdgeInsets.only(right: 4), child: Icon(Icons.lock_rounded, size: 16, color: Park.inkSoft)),
                  Flexible(child: FittedBox(child: Text(game.zh, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)))),
                ]),
                Row(mainAxisSize: MainAxisSize.min, children: [
                  for (var i = 0; i < 3; i++) Icon(Icons.star_rounded, size: 16, color: i < stars ? Park.gold : const Color(0xFFD9D4E6)),
                ]),
              ]),
            ),
          ),
        ),
      );
}

/// A land's name at its gate.
class _LandTag extends StatelessWidget {
  const _LandTag({required this.land, required this.stars});

  final Land land;
  final int stars;

  @override
  Widget build(BuildContext context) => LandCard(
        land: land,
        color: LandLook.of(land).accent,
        seed: 20 + land.index,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        child: FittedBox(child: Text(land.zh, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white))),
      );
}

/// The puff of smoke when 阿布 changes style.
class _Puff extends CustomPainter {
  _Puff(this.t);

  final double t;

  @override
  void paint(Canvas canvas, Size size) {
    final c = size.center(Offset.zero);
    final p = Paint()..color = Colors.white.withValues(alpha: 0.85 * t);
    for (var i = 0; i < 8; i++) {
      final a = i * math.pi / 4;
      canvas.drawCircle(c + Offset(math.cos(a), math.sin(a)) * size.width * 0.42 * t, size.width * 0.16 * t, p);
    }
    canvas.drawCircle(c, size.width * 0.3 * t, p);
  }

  @override
  bool shouldRepaint(_Puff old) => old.t != t;
}
