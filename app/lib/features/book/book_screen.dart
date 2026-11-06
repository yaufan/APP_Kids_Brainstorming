import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/game.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';

/// 偵探手冊: a page for each land with the stickers earned by solving cases;
/// the ones still to find are pale shadows.
class BookScreen extends ConsumerStatefulWidget {
  const BookScreen({super.key});

  /// Every sticker of a land, in the order of its games.
  static List<String> stickersOf(Land land) => {
        for (final g in GameKind.values)
          if (g.land == land) ...stickersFor(g),
      }.toList();

  @override
  ConsumerState<BookScreen> createState() => _BookScreenState();
}

class _BookScreenState extends ConsumerState<BookScreen> {
  late final Sounds _sounds;
  var _land = Land.city;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.park);
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  void _say(Land land, String id) {
    final s = ref.read(gameProvider).settings;
    final name = nameOf(land, id);
    if (name != null && s.voice) ref.read(voiceProvider).say(name, en: s.english ? _en(land, id) : null);
  }

  String? _en(Land land, String id) => switch (land) {
        Land.city => (sortThings[id] ?? ownerThings[id])?.en,
        Land.forest => (pairThings[id] ?? mysteryThings[id])?.en,
        Land.blocks => blockThings.where((b) => b.id == id).firstOrNull?.en ?? sequenceThings[id]?.en,
      };

  @override
  Widget build(BuildContext context) {
    final have = ref.watch(gameProvider.select((g) => g.stickers));
    final look = LandLook.of(_land);
    final all = BookScreen.stickersOf(_land);
    final got = all.where(have.contains).length;
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [look.top, look.bottom])),
        child: SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 10, 14, 4),
              child: Row(children: [
                LandButton(land: _land, label: Strings.home, icon: Icons.home_rounded, onTap: () => context.canPop() ? context.pop() : context.go('/')),
                const SizedBox(width: 12),
                const Text(Strings.book, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700)),
                const Spacer(),
                Text(Strings.bookCount(got, all.length), style: const TextStyle(fontSize: 16, color: Park.inkSoft)),
              ]),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              child: Row(children: [
                for (final l in Land.values)
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: Semantics(
                        container: true,
                        button: true,
                        selected: l == _land,
                        label: l.zh,
                        excludeSemantics: true,
                        onTap: () => setState(() => _land = l),
                        child: Pressable(
                          onTap: () => setState(() => _land = l),
                          child: LandCard(
                            land: l,
                            color: l == _land ? LandLook.of(l).accent : null,
                            padding: const EdgeInsets.symmetric(vertical: 10),
                            child: Center(
                              child: Text(l.zh, style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: l == _land ? Colors.white : Park.ink)),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
              ]),
            ),
            Expanded(
              child: GridView.count(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                crossAxisCount: MediaQuery.sizeOf(context).width > 700 ? 6 : 4,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                children: [
                  for (final (i, sticker) in all.indexed)
                    _Sticker(
                      land: _land,
                      id: sticker.split('/').last,
                      have: have.contains(sticker),
                      seed: i,
                      onTap: have.contains(sticker) ? () => _say(_land, sticker.split('/').last) : null,
                    ),
                ],
              ),
            ),
          ]),
        ),
      ),
    );
  }
}

class _Sticker extends StatelessWidget {
  const _Sticker({required this.land, required this.id, required this.have, required this.seed, this.onTap});

  final Land land;
  final String id;
  final bool have;
  final int seed;
  final VoidCallback? onTap;

  static const _shadow = ColorFilter.matrix([0, 0, 0, 0, 120, 0, 0, 0, 0, 110, 0, 0, 0, 0, 150, 0, 0, 0, 0.22, 0]);

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: have,
        label: have ? (nameOf(land, id) ?? id) : '？',
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          sound: 'sticker',
          child: LandCard(
            land: land,
            seed: seed,
            padding: const EdgeInsets.all(8),
            child: have ? Art(land, id) : ColorFiltered(colorFilter: _shadow, child: Art(land, id)),
          ),
        ),
      );
}
