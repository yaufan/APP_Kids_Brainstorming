import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/content.dart';
import '../../core/rounds.dart';
import 'play_screen.dart';

/// 哪個不一樣？: three or four block cards; tap the one that does not fit.
class OddGame extends StatefulWidget {
  const OddGame({super.key, required this.round, required this.hooks});

  final OddRound round;
  final PlayHooks hooks;

  @override
  State<OddGame> createState() => _OddGameState();
}

class _OddGameState extends State<OddGame> {
  final _shake = <Block, int>{};
  var _found = false;

  void _tap(Block b) {
    if (_found) return;
    if (b == widget.round.odd) {
      setState(() => _found = true);
      widget.hooks.sfx('sparkle');
      widget.hooks.done(widget.round.why);
      return;
    }
    setState(() => _shake[b] = (_shake[b] ?? 0) + 1);
    widget.hooks.sfx('bounce');
    widget.hooks.miss('${b.zh}和大家一樣喔，再找找看！');
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final cards = widget.round.cards;
        final cols = cards.length == 3 && box.maxWidth > box.maxHeight ? 3 : 2;
        final rows = (cards.length / cols).ceil();
        final size = math.min((box.maxWidth - 32) / cols - 16, (box.maxHeight - 16) / rows - 20).clamp(60.0, 300.0);
        return Center(
          child: SizedBox(
            width: cols * (size + 20),
            child: Wrap(alignment: WrapAlignment.center, spacing: 20, runSpacing: 20, children: [
              for (final b in cards)
                Semantics(
                  container: true,
                  button: true,
                  label: b.zh,
                  excludeSemantics: true,
                  onTap: () => _tap(b),
                  child: Pressable(
                    onTap: () => _tap(b),
                    sound: null,
                    child: Wiggle(
                      trigger: _shake[b] ?? 0,
                      child: AnimatedScale(
                        scale: _found && b == widget.round.odd ? 1.08 : 1,
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeOutBack,
                        child: SizedBox(
                          width: size,
                          height: size,
                          child: LandCard(
                            land: Land.blocks,
                            ring: _found && b == widget.round.odd ? Park.gold : null,
                            padding: EdgeInsets.all(size * 0.1),
                            child: Art(Land.blocks, b.id),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
            ]),
          ),
        );
      });
}
