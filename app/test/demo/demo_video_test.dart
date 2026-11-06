// Records a demo video of 想一想樂園 being played: a scripted child (a white
// dot where the finger is) with a caption under the phone screen; the music
// and sounds the app asked for are written down and mixed in afterwards by
// tools/demo_audio.py.
//
//   flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true
//   python3 ../tools/demo_audio.py
//
// Needs ffmpeg; writes build/demo/demo.mp4, chapters.txt and sounds.txt.
// Skipped in normal test runs.
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:think_park/app/app.dart';
import 'package:think_park/app/strings.dart';
import 'package:think_park/core/content.dart';
import 'package:think_park/core/providers.dart';
import 'package:think_park/core/rounds.dart';
import 'package:think_park/core/sounds.dart';
import 'package:think_park/core/store.dart';
import 'package:think_park/core/voice.dart';
import 'package:think_park/features/play/play_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers.dart' show loadFonts;

const _phone = Size(390, 844);
const _captionHeight = 84.0;
const _fps = 10;
const _demo = bool.fromEnvironment('DEMO');

/// The music and sounds asked for, with the frame they were asked at.
class _Track implements Sounds {
  _Track(this.frame);

  final int Function() frame;
  final lines = <String>[];
  final _holders = MusicHolders();
  Music? _playing;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => lines.add('${frame()} sfx $sfx');

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _changed();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _changed();
  }

  void _changed() {
    final now = _holders.current;
    if (now == _playing) return;
    _playing = now;
    lines.add('${frame()} music ${now?.file ?? '-'}');
  }
}

void main() {
  testWidgets('demo video', skip: !_demo, (tester) async {
    await tester.runAsync(loadFonts);
    tester.view.physicalSize = Size(_phone.width * 3, (_phone.height + _captionHeight) * 3);
    tester.view.devicePixelRatio = 3;
    addTearDown(tester.view.reset);

    var frameCount = 0;
    var now = DateTime(2026, 11, 6, 10);
    final track = _Track(() => frameCount);
    final finger = ValueNotifier<Offset?>(null);
    final caption = ValueNotifier<String>('');
    final key = GlobalKey();
    await tester.pumpWidget(RepaintBoundary(
      key: key,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(children: [
          SizedBox.fromSize(
            size: _phone,
            child: MediaQuery(
              data: const MediaQueryData(size: _phone, devicePixelRatio: 3, padding: EdgeInsets.only(top: 24)),
              child: Stack(children: [
                ProviderScope(
                  overrides: [
                    storeProvider.overrideWithValue(MemoryStore()),
                    soundsProvider.overrideWithValue(track),
                    voiceProvider.overrideWithValue(const SilentVoice()),
                    randomProvider.overrideWithValue(math.Random(8)),
                    clockProvider.overrideWithValue(() => now),
                  ],
                  child: const ParkApp(),
                ),
                IgnorePointer(child: ValueListenableBuilder(valueListenable: finger, builder: (_, at, _) => _Finger(at))),
              ]),
            ),
          ),
          SizedBox(
            width: _phone.width,
            height: _captionHeight,
            child: ColoredBox(
              color: const Color(0xFFFF7A45),
              child: Center(
                child: ValueListenableBuilder(
                  valueListenable: caption,
                  builder: (_, text, _) => Text(text,
                      textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Huninn', color: Colors.white, fontSize: 17, height: 1.35)),
                ),
              ),
            ),
          ),
        ]),
      ),
    ));

    final rec = (await tester.runAsync(() => _Recorder.start(key)))!;
    final marks = <String>[];
    void mark(String name) => marks.add('$name $frameCount');
    Future<void> frames(int n) async {
      for (var i = 0; i < n; i++) {
        frameCount++;
        await tester.runAsync(() async {
          await rec.capture();
          await Future<void>.delayed(const Duration(milliseconds: 15));
        });
        await tester.pump(const Duration(milliseconds: 1000 ~/ _fps));
      }
    }

    Future<void> seconds(double s) => frames((s * _fps).round());
    Future<void> touch(Offset at) async {
      finger.value = at;
      await frames(2);
      await tester.tapAt(at);
      await frames(2);
      finger.value = null;
    }

    Offset at(String l) => tester.getCenter(find.bySemanticsLabel(l).last);
    Future<void> label(String l) => touch(at(l));
    Future<void> drag(Offset from, Offset to) async {
      finger.value = from;
      final g = await tester.startGesture(from);
      await frames(2);
      for (var i = 1; i <= 7; i++) {
        final p = Offset.lerp(from, to, Curves.easeInOut.transform(i / 7))!;
        await g.moveTo(p);
        finger.value = p;
        await frames(1);
      }
      await g.up();
      finger.value = null;
      await frames(2);
    }

    Object round() => (tester.state(find.byType(PlayScreen)) as dynamic).debugRound as Object;
    Future<void> open(GameKind g) async {
      await label(g.zh);
      await seconds(2.2);
    }

    Future<void> home() async {
      await label(Strings.home);
      await seconds(1.2);
    }

    // The park.
    mark('park');
    caption.value = '想一想樂園：跟著小狐狸偵探阿布\n練分類、配對、規律和推理';
    await seconds(3.5);
    caption.value = '三個園區、三種卡通畫風\n卡通城、紙片森林、積木王國';
    await seconds(3);

    // 卡通城：放哪裡？
    mark('sort');
    caption.value = '卡通城「放哪裡？」：把東西放回家\n阿布走進哪裡，就變成那裡的樣子';
    await open(GameKind.sort);
    final sort = round() as SortRound;
    for (final (i, t) in sort.things.indexed) {
      final name = sortThings[t.id]!.zh;
      if (i == 0) {
        caption.value = '放錯了只會彈回去，阿布給提示\n不扣分、不催促';
        final wrong = sort.places.firstWhere((p) => p.id != t.place);
        await drag(at(name), at(wrong.zh));
        await seconds(2.4);
        caption.value = '放對了，阿布會說出「為什麼」';
      }
      await drag(at(name), at(sort.scene.place(t.place).zh));
      await seconds(i == 0 ? 2.8 : 1.4);
    }
    await seconds(3.5);
    await home();

    // 卡通城：是誰的？
    mark('owner');
    caption.value = '「是誰的？」：把東西拿給需要的人';
    await open(GameKind.owner);
    final owner = round() as OwnerRound;
    for (final o in owner.people) {
      await drag(at(ownerThings[o.wants]!.zh), at(o.zh));
      await seconds(2.2);
    }
    await seconds(2.5);
    await home();

    // 紙片森林：連連看
    mark('pairs');
    caption.value = '紙片森林「連連看」：用手指畫線\n把一對連起來（剪紙畫風）';
    await open(GameKind.pairs);
    final pairs = round() as PairsRound;
    for (final p in pairs.left) {
      await drag(at(pairThings[p.a]!.zh), at(pairThings[p.b]!.zh));
      await seconds(2.2);
    }
    await seconds(2.5);
    await home();

    // 紙片森林：小偵探
    mark('detective');
    caption.value = '「小偵探」：看線索，找出是誰\n（3 歲半以上）';
    await open(GameKind.detective);
    final d = round() as DetectiveRound;
    await seconds(1);
    for (final (i, c) in d.clues.indexed) {
      await label('${Strings.clue(i + 1)}：${c.zh}');
      await seconds(2.2);
    }
    await label(d.culprit.zh);
    caption.value = '找到了！說說看「因為……所以……」';
    await seconds(5);
    await home();

    // 積木王國：哪個不一樣？ A whole case, to the sticker.
    mark('odd');
    caption.value = '積木王國「哪個不一樣？」\n全部用圓形、方形、三角形拼出來';
    await open(GameKind.odd);
    for (var r = 0; r < GameKind.odd.rounds; r++) {
      final odd = round() as OddRound;
      if (r == 0) {
        await label(odd.cards.firstWhere((c) => c != odd.odd).zh);
        await seconds(2);
      }
      await label(odd.odd.zh);
      await seconds(r == 0 ? 3.5 : 2.6);
      if (r == 1) caption.value = '五題破一個案，得到貼紙和星星';
    }
    await seconds(3.5);
    await label(Strings.toPark);
    await seconds(1.5);

    // 積木王國：接下來是什麼？
    mark('next');
    caption.value = '「接下來是什麼？」：積木火車的規律\n和事情的順序';
    await open(GameKind.next);
    for (var r = 0; r < 3; r++) {
      final n = round() as NextRound;
      await seconds(1.5);
      switch (n) {
        case PatternRound():
          await label(n.answer.zh);
        case SequenceRound():
          await label(sequenceThings[n.answer]!.zh);
      }
      await seconds(3.2);
    }
    await home();

    // The book.
    mark('book');
    caption.value = '偵探手冊：每破一個案得到一張貼紙';
    await label(Strings.book);
    await seconds(2.5);
    await label(Land.blocks.zh);
    await seconds(2);
    await label(Strings.home);
    await seconds(1);

    // Time for a rest.
    mark('rest');
    now = now.add(const Duration(minutes: 15, seconds: 1));
    caption.value = '家長設定的時間到了（預設 15 分鐘）\n樂園天黑休息，要家長解開才能再玩';
    await seconds(5.5);

    // Parent mode.
    mark('parent');
    caption.value = '家長答對題目，才能再玩或進家長模式';
    const digits = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9};
    Future<void> gate() async {
      final parts = (find.textContaining('加').evaluate().first.widget as Text).data!.split(' ');
      for (final d in '${digits[parts[0]]! + digits[parts[2]]!}'.split('')) {
        await touch(tester.getCenter(find.byKey(ValueKey('gate-key-$d'))));
        await frames(3);
      }
    }

    await label(Strings.parent);
    await seconds(1.2);
    await gate();
    await seconds(1.5);
    await label(Strings.parent);
    await seconds(1);
    await gate();
    await seconds(1);
    caption.value = '家長模式：年齡（三個難度）、要玩哪些遊戲\n每次玩多久、看分類、配對、規律、推理的進度';
    await seconds(3);
    await tester.drag(find.byType(ListView), const Offset(0, -900));
    await seconds(3);
    caption.value = '';
    mark('end');
    await seconds(0.5);

    await tester.runAsync(() async {
      await rec.finish();
      File('build/demo/chapters.txt').writeAsStringSync('${marks.join('\n')}\n');
      File('build/demo/sounds.txt').writeAsStringSync('fps $_fps\nframes $frameCount\n${track.lines.join('\n')}\n');
    });
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }, timeout: const Timeout(Duration(minutes: 40)));
}

class _Finger extends StatelessWidget {
  const _Finger(this.at);

  final Offset? at;

  @override
  Widget build(BuildContext context) {
    final p = at;
    if (p == null) return const SizedBox.expand();
    return Stack(children: [
      Positioned(
        left: p.dx - 22,
        top: p.dy - 22,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.55),
            border: Border.all(color: const Color(0xFF3B2F55).withValues(alpha: 0.5), width: 3),
          ),
        ),
      ),
    ]);
  }
}

/// Streams frames of [key]'s boundary into ffmpeg.
class _Recorder {
  _Recorder(this._key, this._ffmpeg);

  final GlobalKey _key;
  final Process _ffmpeg;

  static Future<_Recorder> start(GlobalKey key) async {
    Directory('build/demo').createSync(recursive: true);
    final size = Size(_phone.width * 2, (_phone.height + _captionHeight) * 2);
    final ffmpeg = await Process.start('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '${size.width.toInt()}x${size.height.toInt()}', '-r', '$_fps', '-i', '-',
      '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', 'build/demo/demo_silent.mp4',
    ]);
    ffmpeg.stderr.listen(stderr.add);
    return _Recorder(key, ffmpeg);
  }

  Future<void> capture() async {
    final boundary = _key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    image.dispose();
    _ffmpeg.stdin.add(bytes!.buffer.asUint8List());
    await _ffmpeg.stdin.flush();
  }

  Future<void> finish() async {
    await _ffmpeg.stdin.flush();
    await _ffmpeg.stdin.close();
    final code = await _ffmpeg.exitCode;
    if (code != 0) throw StateError('ffmpeg failed ($code)');
  }
}
