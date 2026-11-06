import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/version.dart';
import '../../core/content.dart';
import '../../core/game.dart';
import '../../core/providers.dart';

/// Parent mode (after the gate): the child's age, the games, play time,
/// sounds, how each skill is going and ideas for playing together.
class ParentScreen extends ConsumerWidget {
  const ParentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final s = g.settings;
    final game = ref.read(gameProvider.notifier);
    final now = ref.read(clockProvider)();

    Widget section(String title, List<Widget> children) => Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 14, 18, 12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: const TextStyle(fontSize: 15, color: Park.inkSoft, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                ...children,
              ]),
            ),
          ),
        );

    Widget toggle(String label, bool value, void Function(bool)? set, {Key? key, String? note}) => SwitchListTile(
          key: key,
          contentPadding: EdgeInsets.zero,
          title: Text(label, style: const TextStyle(fontSize: 17)),
          subtitle: note == null ? null : Text(note, style: const TextStyle(fontSize: 13, color: Park.inkSoft)),
          value: value,
          onChanged: set,
        );

    const note = TextStyle(fontSize: 14, height: 1.5, color: Park.inkSoft);

    return Scaffold(
      backgroundColor: Park.parentBg,
      appBar: AppBar(
        backgroundColor: Park.parentBg,
        title: const Text(Strings.parentTitle),
        leading: IconButton(icon: const Icon(Icons.close_rounded), tooltip: Strings.back, onPressed: () => context.canPop() ? context.pop() : context.go('/')),
      ),
      body: ListView(padding: const EdgeInsets.fromLTRB(16, 8, 16, 32), children: [
        section(Strings.age, [
          RadioGroup<Level>(
            groupValue: s.level,
            onChanged: (v) => game.settings((x) => x.copyWith(level: v)),
            child: Column(children: [
              for (final l in Level.values)
                RadioListTile<Level>(
                  key: ValueKey('level-${l.name}'),
                  contentPadding: EdgeInsets.zero,
                  value: l,
                  title: Text(Strings.levelLine(l), style: const TextStyle(fontSize: 16)),
                ),
            ]),
          ),
          const Text(Strings.ageNote, style: note),
        ]),
        section(Strings.games, [
          for (final k in GameKind.values)
            toggle(
              '${k.land.zh}：${k.zh}',
              !s.off.contains(k),
              (v) => game.settings((x) => x.copyWith(off: v ? ({...x.off}..remove(k)) : {...x.off, k})),
              key: ValueKey('game-${k.name}'),
              note: k == GameKind.detective ? Strings.detectiveNote : null,
            ),
        ]),
        section(Strings.playTime, [
          Wrap(spacing: 8, runSpacing: 8, children: [
            for (final m in Settings.minuteChoices)
              ChoiceChip(
                key: ValueKey('minutes-$m'),
                label: Text(Strings.minutes(m), style: const TextStyle(fontSize: 16)),
                selected: m == s.minutes,
                onSelected: (_) => game.settings((x) => x.copyWith(minutes: m)),
                selectedColor: const Color(0xFFFFE2CC),
                showCheckmark: false,
              ),
          ]),
          const SizedBox(height: 10),
          const Text(Strings.playTimeNote, style: note),
          if (g.resting(now)) ...[
            const SizedBox(height: 10),
            const Text(Strings.resting, style: TextStyle(fontSize: 16)),
            const SizedBox(height: 6),
            FilledButton(
              key: const ValueKey('play-on'),
              onPressed: () {
                game.change((g) => g.playOn());
                ref.read(sessionStartProvider.notifier).restart();
                context.go('/');
              },
              child: const Text(Strings.playOn),
            ),
          ],
        ]),
        section(Strings.sound, [
          toggle(Strings.music, s.music, (v) => game.settings((x) => x.copyWith(music: v)), key: const ValueKey('music')),
          toggle(Strings.effects, s.sounds, (v) => game.settings((x) => x.copyWith(sounds: v)), key: const ValueKey('effects')),
          toggle(Strings.voice, s.voice, (v) => game.settings((x) => x.copyWith(voice: v)), key: const ValueKey('voice')),
          toggle(Strings.english, s.english, (v) => game.settings((x) => x.copyWith(english: v)), key: const ValueKey('english')),
        ]),
        section(Strings.progress, [
          for (final k in Skill.values) _SkillBar(skill: k, tally: g.skills[k] ?? const Tally()),
          const SizedBox(height: 4),
          const Text(Strings.progressNote, style: note),
        ]),
        section(Strings.together, [
          for (final t in Strings.tips)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Padding(padding: EdgeInsets.only(top: 3), child: Icon(Icons.favorite_rounded, size: 16, color: Park.orange)),
                const SizedBox(width: 8),
                Expanded(child: Text(t, style: const TextStyle(fontSize: 16, height: 1.45))),
              ]),
            ),
        ]),
        section(Strings.fullVersion, [
          const Text(Strings.fullNote, style: note),
          toggle(Strings.fullSwitch, s.full, (v) => game.settings((x) => x.copyWith(full: v)), key: const ValueKey('full')),
        ]),
        section(Strings.about, [
          const Text(Strings.privacy, style: TextStyle(fontSize: 15, height: 1.5)),
          const SizedBox(height: 6),
          Text(Strings.version(appVersion), style: note),
        ]),
      ]),
    );
  }
}

class _SkillBar extends StatelessWidget {
  const _SkillBar({required this.skill, required this.tally});

  final Skill skill;
  final Tally tally;

  static const colors = {Skill.classify: Color(0xFFFF8A3D), Skill.match: Color(0xFF3D9BFF), Skill.pattern: Color(0xFF9B6BFF), Skill.reason: Color(0xFF2FBF71)};

  @override
  Widget build(BuildContext context) {
    final part = tally.tried == 0 ? 0.0 : tally.right / tally.tried;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(children: [
        SizedBox(width: 44, child: Text(skill.zh, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700))),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(value: part, minHeight: 10, color: colors[skill], backgroundColor: const Color(0xFFECEAF2)),
            ),
            const SizedBox(height: 3),
            Text(Strings.skillLine(tally.right, tally.tried), style: const TextStyle(fontSize: 13, color: Park.inkSoft)),
          ]),
        ),
      ]),
    );
  }
}
