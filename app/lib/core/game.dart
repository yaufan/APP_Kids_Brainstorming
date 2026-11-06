import 'dart:math' as math;

import 'content.dart';

/// What a parent set.
class Settings {
  const Settings({
    this.level = Level.mid,
    this.minutes = 15,
    this.off = const {},
    this.english = false,
    this.music = true,
    this.sounds = true,
    this.voice = true,
    this.full = true,
  });

  /// The child's age, which sets how hard the puzzles are.
  final Level level;

  /// How long one sitting may be before a rest.
  final int minutes;

  /// Games the parent turned off.
  final Set<GameKind> off;
  final bool english;
  final bool music;
  final bool sounds;
  final bool voice;
  final bool full;

  static const minuteChoices = [5, 10, 15, 20, 30];

  /// A game shows on the map when it is on and suits the age.
  bool shows(GameKind g) => !off.contains(g) && g.from.index <= level.index;

  Settings copyWith({Level? level, int? minutes, Set<GameKind>? off, bool? english, bool? music, bool? sounds, bool? voice, bool? full}) => Settings(
        level: level ?? this.level,
        minutes: minutes ?? this.minutes,
        off: off ?? this.off,
        english: english ?? this.english,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
      );

  Map<String, dynamic> toJson() => {
        'level': level.name,
        'minutes': minutes,
        'off': [for (final g in off) g.name],
        'english': english,
        'music': music,
        'sounds': sounds,
        'voice': voice,
        'full': full,
      };

  factory Settings.fromJson(Map<String, dynamic> j) {
    final m = j['minutes'];
    final off = j['off'];
    return Settings(
      level: Level.values.where((l) => l.name == j['level']).firstOrNull ?? Level.mid,
      minutes: m is int && minuteChoices.contains(m) ? m : 15,
      off: {if (off is List) for (final g in GameKind.values) if (off.contains(g.name)) g},
      english: j['english'] as bool? ?? false,
      music: j['music'] as bool? ?? true,
      sounds: j['sounds'] as bool? ?? true,
      voice: j['voice'] as bool? ?? true,
      full: j['full'] as bool? ?? true,
    );
  }
}

/// How a skill is going: answers tried and answers right first time.
class Tally {
  const Tally({this.tried = 0, this.right = 0});

  final int tried;
  final int right;

  Tally add({required bool right}) => Tally(tried: tried + 1, right: this.right + (right ? 1 : 0));
}

/// Everything kept: cases solved, stickers, how each skill is going, the
/// rest, the settings. One small file (store.dart).
class Game {
  const Game({
    this.cases = const {},
    this.slips = const {},
    this.skills = const {},
    this.stickers = const {},
    this.restSince,
    this.settings = const Settings(),
  });

  /// Cases solved in each game.
  final Map<GameKind, int> cases;

  /// Wrong tries in each game's last round (lots of them make the next
  /// round a level easier).
  final Map<GameKind, int> slips;
  final Map<Skill, Tally> skills;

  /// Stickers in the detective book: 'land/id' of the pictures collected.
  final Set<String> stickers;

  /// When the play time ran out (null: playing).
  final DateTime? restSince;
  final Settings settings;

  /// A rest lasts until a parent lets play go on, or an hour has passed.
  static const restLength = Duration(hours: 1);

  /// Three wrong tries in a round and the next round is a level easier.
  static const tooHard = 3;

  bool resting(DateTime now) => restSince != null && now.difference(restSince!) < restLength;

  /// Stars on a game on the map: one a case, three at most.
  int starsOf(GameKind g) => math.min(3, cases[g] ?? 0);

  /// The level the next round of [g] is dealt at.
  Level levelFor(GameKind g) {
    final level = settings.level;
    if ((slips[g] ?? 0) < tooHard || level == Level.small) return level;
    final easier = Level.values[level.index - 1];
    return easier.index >= g.from.index ? easier : level;
  }

  Game copyWith({
    Map<GameKind, int>? cases,
    Map<GameKind, int>? slips,
    Map<Skill, Tally>? skills,
    Set<String>? stickers,
    DateTime? restSince,
    bool clearRest = false,
    Settings? settings,
  }) =>
      Game(
        cases: cases ?? this.cases,
        slips: slips ?? this.slips,
        skills: skills ?? this.skills,
        stickers: stickers ?? this.stickers,
        restSince: clearRest ? null : (restSince ?? this.restSince),
        settings: settings ?? this.settings,
      );

  /// A round of [g] done, with [wrong] wrong tries on the way.
  Game round(GameKind g, {required int wrong}) => copyWith(
        slips: {...slips, g: wrong},
        skills: {...skills, g.skill: (skills[g.skill] ?? const Tally()).add(right: wrong == 0)},
      );

  /// A case of [g] solved: a star and [sticker] for the book.
  Game solved(GameKind g, {String? sticker}) => copyWith(
        cases: {...cases, g: (cases[g] ?? 0) + 1},
        stickers: sticker == null ? stickers : {...stickers, sticker},
      );

  Game rest(DateTime now) => copyWith(restSince: now);

  Game playOn() => copyWith(clearRest: true);

  Map<String, dynamic> toJson() => {
        'version': 1,
        'cases': {for (final e in cases.entries) e.key.name: e.value},
        'slips': {for (final e in slips.entries) e.key.name: e.value},
        'skills': {for (final e in skills.entries) e.key.name: [e.value.tried, e.value.right]},
        'stickers': stickers.toList()..sort(),
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
        'settings': settings.toJson(),
      };

  factory Game.fromJson(Map<String, dynamic>? j) {
    if (j == null) return const Game();
    Map<GameKind, int> perGame(Object? o) => {
          if (o is Map)
            for (final g in GameKind.values)
              if (o[g.name] is int && (o[g.name] as int) >= 0) g: o[g.name] as int,
        };
    final skills = j['skills'];
    final stickers = j['stickers'];
    final rest = j['restSince'];
    return Game(
      cases: perGame(j['cases']),
      slips: perGame(j['slips']),
      skills: {
        if (skills is Map)
          for (final s in Skill.values)
            if (skills[s.name] case [final int tried, final int right] when tried >= right && right >= 0) s: Tally(tried: tried, right: right),
      },
      stickers: {if (stickers is List) for (final s in stickers) if (s is String) s},
      restSince: rest is String ? DateTime.tryParse(rest) : null,
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
    );
  }
}

/// The pictures a case in [g] can give as a sticker (the things, not the
/// scenes or the places).
List<String> stickersFor(GameKind g) => switch (g) {
      GameKind.sort => [for (final s in sortScenes) for (final t in s.things) 'city/${t.id}'],
      GameKind.owner => [for (final o in owners) 'city/${o.id}'],
      GameKind.pairs => [for (final p in pairs) ...['forest/${p.a}', 'forest/${p.b}']],
      GameKind.detective => [for (final m in mysteries) 'forest/${m.thing}'],
      GameKind.odd => [for (final b in blockThings) 'blocks/${b.id}'],
      GameKind.next => [for (final s in sequences) 'blocks/${s.steps.last}'],
    }.toSet().toList();

/// A sticker for solving a case in [g]: one the child does not have yet if
/// there is one.
String stickerFor(GameKind g, Set<String> have, math.Random r) {
  final all = stickersFor(g);
  final fresh = [for (final s in all) if (!have.contains(s)) s];
  final pool = fresh.isEmpty ? all : fresh;
  return pool[r.nextInt(pool.length)];
}
