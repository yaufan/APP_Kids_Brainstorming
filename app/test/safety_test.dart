import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:think_park/core/content.dart';
import 'package:think_park/features/parent/parent_gate.dart';

import 'helpers.dart';

/// Privacy and the parent gate (docs/design.md: no network, nothing leaves
/// the phone, parent mode only through the gate).
void main() {
  test('the app asks for no permissions and takes no links from other apps', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
    expect(manifest, isNot(contains('uses-permission')), reason: 'no internet, camera, location…');
    expect(manifest, contains('android:name="flutter_deeplinking_enabled" android:value="false"'));
    expect(File('ios/Runner/Info.plist').readAsStringSync(), contains('<key>FlutterDeepLinkingEnabled</key>\n\t<false/>'));
  });

  testWidgets('parent mode and unknown pages cannot be opened without the gate', (tester) async {
    final app = await TestApp.start(tester);
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'no pass from the gate');
    ParentPass.grant();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/parent', reason: 'right after the gate');
    app.go('/');
    await app.settle();
    app.go('/parent');
    await app.settle();
    expect(app.location, '/', reason: 'the pass is used up');
    app.go('/play/nothing');
    await app.settle();
    expect(app.location, '/');
    app.go('/play/${GameKind.odd.name}');
    await app.settle(800);
    expect(app.location, '/play/odd');
    await app.end();
  });
}
