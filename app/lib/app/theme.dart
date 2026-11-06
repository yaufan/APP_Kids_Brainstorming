import 'package:flutter/material.dart';

import '../core/content.dart';

/// The park's shared colours (the map, parent mode, words).
abstract final class Park {
  static const ink = Color(0xFF3B2F55);
  static const inkSoft = Color(0xFF8A7FA3);
  static const sky = Color(0xFFDDF1FF);
  static const cream = Color(0xFFFFF7EC);
  static const orange = Color(0xFFFF8A3D);
  static const gold = Color(0xFFFFC53D);
  static const go = Color(0xFF4CC38A);
  static const parentBg = Color(0xFFF3F2F7);
}

/// How each land looks (docs/design.md "三個園區"): its colours and the kind
/// of card it draws (A outlined with a hard edge under it, B paper, C flat
/// blocks).
class LandLook {
  const LandLook({required this.top, required this.bottom, required this.accent, required this.card, required this.edge});

  final Color top;
  final Color bottom;
  final Color accent;
  final Color card;
  final Color edge;

  static const city = LandLook(top: Color(0xFFDDF1FF), bottom: Color(0xFFFFF6E5), accent: Color(0xFFFF7A45), card: Colors.white, edge: Color(0xFFB9A6E0));
  static const forest = LandLook(top: Color(0xFFEFE3CB), bottom: Color(0xFFE4D3B4), accent: Color(0xFF6E9E5A), card: Color(0xFFFFF8EC), edge: Color(0xFFC9B48E));
  static const blocks = LandLook(top: Color(0xFFEEF0FA), bottom: Color(0xFFE6E9F7), accent: Color(0xFF3D7BFF), card: Colors.white, edge: Color(0xFFD5DAF0));

  static LandLook of(Land land) => switch (land) { Land.city => city, Land.forest => forest, Land.blocks => blocks };
}

abstract final class ParkTheme {
  /// jf open 粉圓 (OFL): a rounded typeface made in Taiwan.
  static const font = 'Huninn';

  static ThemeData light() {
    final base = ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: Park.orange, surface: Park.cream),
      scaffoldBackgroundColor: Park.cream,
      fontFamily: font,
      materialTapTargetSize: MaterialTapTargetSize.padded,
    );
    return base.copyWith(textTheme: base.textTheme.apply(bodyColor: Park.ink, displayColor: Park.ink, fontFamily: font));
  }
}
