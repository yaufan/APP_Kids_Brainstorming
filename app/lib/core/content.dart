/// Everything the six games ask about (docs/design.md): the three lands, the
/// things drawn in each, and the puzzles made from them. The pictures are
/// `assets/art/<land>/<id>.svg` (design/art/ draws them).
library;

/// The three lands of the park, each drawn in its own cartoon style.
enum Land {
  city('卡通城'),
  forest('紙片森林'),
  blocks('積木王國');

  const Land(this.zh);

  final String zh;
}

/// What a game trains (parent mode shows how each is going).
enum Skill {
  classify('分類'),
  match('配對'),
  pattern('規律'),
  reason('推理');

  const Skill(this.zh);

  final String zh;
}

/// The parent's choice of age; the puzzles grow with it.
enum Level {
  small('小小', '2 歲半～3 歲半'),
  mid('中', '3 歲半～4 歲半'),
  big('大', '4 歲半～5 歲');

  const Level(this.zh, this.ages);

  final String zh;
  final String ages;

  /// Pick by level: [s] for 小小, [m] for 中, [b] for 大.
  T pick<T>(T s, T m, T b) => switch (this) { Level.small => s, Level.mid => m, Level.big => b };
}

/// The six games, two in each land.
enum GameKind {
  sort('放哪裡？', Land.city, Skill.classify, Level.small),
  owner('是誰的？', Land.city, Skill.match, Level.small),
  pairs('連連看', Land.forest, Skill.match, Level.small),
  detective('小偵探', Land.forest, Skill.reason, Level.mid),
  odd('哪個不一樣？', Land.blocks, Skill.classify, Level.small),
  next('接下來是什麼？', Land.blocks, Skill.pattern, Level.small);

  const GameKind(this.zh, this.land, this.skill, this.from);

  final String zh;
  final Land land;
  final Skill skill;

  /// The youngest level it is offered at (小偵探 starts at 中).
  final Level from;

  /// Rounds in one case; finishing them earns a star and a sticker.
  int get rounds => switch (this) { GameKind.sort => 3, GameKind.detective => 3, _ => 5 };
}

/// Something drawn in a land.
class Thing {
  const Thing(this.id, this.zh, this.en);

  final String id;
  final String zh;
  final String en;
}

String art(Land land, String id) => 'assets/art/${land.name}/$id.svg';

// ---------------------------------------------------------------- 卡通城：放哪裡？

/// A place in a scene things go to; [x], [y], [w] are fractions of the scene
/// (its centre and width).
class Place {
  const Place(this.id, this.zh, {required this.x, required this.y, required this.w, this.from = Level.small});

  final String id;
  final String zh;
  final double x;
  final double y;
  final double w;

  /// The youngest level it is used at (冷凍庫 next to 冰箱 only for 大).
  final Level from;
}

/// A thing to put away, the place it belongs, and why (said when it lands).
class Stray {
  const Stray(this.id, this.place, this.why);

  final String id;
  final String place;
  final String why;
}

class SortScene {
  const SortScene(this.id, this.zh, this.from, this.places, this.things);

  final String id;
  final String zh;
  final Level from;
  final List<Place> places;
  final List<Stray> things;

  Place place(String id) => places.firstWhere((p) => p.id == id);
}

const sortScenes = [
  SortScene('room', '房間', Level.small, [
    Place('toy_box', '玩具箱', x: 0.24, y: 0.62, w: 0.36),
    Place('bookshelf', '書架', x: 0.2, y: 0.3, w: 0.32),
    Place('laundry', '洗衣籃', x: 0.78, y: 0.62, w: 0.32),
    Place('bed', '床', x: 0.72, y: 0.32, w: 0.46),
  ], [
    Stray('ball', 'toy_box', '球是玩具，玩好了放進玩具箱。'),
    Stray('blocks', 'toy_box', '積木是玩具，玩好了放進玩具箱。'),
    Stray('toy_car', 'toy_box', '玩具車是玩具，玩好了放進玩具箱。'),
    Stray('book', 'bookshelf', '書看完了，放回書架上。'),
    Stray('sock', 'laundry', '穿過的襪子要洗，放進洗衣籃。'),
    Stray('tshirt', 'laundry', '穿過的衣服要洗，放進洗衣籃。'),
    Stray('pillow', 'bed', '枕頭放在床上，睡覺的時候用。'),
  ]),
  SortScene('bathroom', '浴室', Level.small, [
    Place('brush_cup', '牙刷杯', x: 0.24, y: 0.3, w: 0.26),
    Place('towel_rack', '毛巾架', x: 0.76, y: 0.28, w: 0.34),
    Place('bathtub', '浴缸', x: 0.66, y: 0.64, w: 0.56),
    Place('soap_dish', '肥皂盒', x: 0.22, y: 0.62, w: 0.26),
  ], [
    Stray('toothbrush', 'brush_cup', '牙刷放在牙刷杯裡，我們在浴室刷牙。'),
    Stray('toothpaste', 'brush_cup', '牙膏和牙刷放在一起，刷牙的時候用。'),
    Stray('towel', 'towel_rack', '毛巾掛在毛巾架上，才會乾乾的。'),
    Stray('rubber_duck', 'bathtub', '小鴨子在浴缸裡陪我們洗澡。'),
    Stray('soap', 'soap_dish', '肥皂放在肥皂盒，洗手的時候用。'),
  ]),
  SortScene('kitchen', '廚房', Level.small, [
    Place('fridge', '冰箱', x: 0.22, y: 0.42, w: 0.36),
    Place('cupboard', '碗櫃', x: 0.72, y: 0.26, w: 0.44),
    Place('sink', '水槽', x: 0.72, y: 0.62, w: 0.42),
    Place('freezer', '冷凍庫', x: 0.22, y: 0.12, w: 0.36, from: Level.big),
  ], [
    Stray('milk', 'fridge', '牛奶要冰在冰箱裡，才不會壞掉。'),
    Stray('vegetables', 'fridge', '青菜放冰箱，才會新鮮。'),
    Stray('bowl', 'cupboard', '乾淨的碗放回碗櫃。'),
    Stray('plate', 'cupboard', '乾淨的盤子放回碗櫃。'),
    Stray('dirty_cup', 'sink', '用過的杯子放進水槽，洗乾淨。'),
    Stray('ice_cream', 'freezer', '冰淇淋要放冷凍庫，才不會融化。'),
  ]),
  SortScene('nature', '大自然', Level.mid, [
    Place('sky', '天空', x: 0.5, y: 0.12, w: 0.9),
    Place('tree', '大樹', x: 0.2, y: 0.4, w: 0.36),
    Place('grass', '草地', x: 0.72, y: 0.58, w: 0.5),
    Place('sea', '海裡', x: 0.5, y: 0.86, w: 0.9),
  ], [
    Stray('bird', 'sky', '小鳥有翅膀，在天空飛。'),
    Stray('squirrel', 'tree', '松鼠住在樹上。'),
    Stray('monkey', 'tree', '猴子喜歡爬樹。'),
    Stray('cow', 'grass', '牛在草地上吃草。'),
    Stray('sheep', 'grass', '羊在草地上吃草。'),
    Stray('fish', 'sea', '魚要住在水裡。'),
    Stray('octopus', 'sea', '章魚住在海裡。'),
  ]),
  SortScene('market', '超市', Level.mid, [
    Place('fruit_stand', '水果區', x: 0.26, y: 0.34, w: 0.42),
    Place('bakery', '麵包區', x: 0.74, y: 0.34, w: 0.42),
    Place('veggie_stand', '蔬菜區', x: 0.26, y: 0.66, w: 0.42),
    Place('frozen_case', '冷凍櫃', x: 0.74, y: 0.66, w: 0.42),
  ], [
    Stray('apple', 'fruit_stand', '蘋果是水果，放水果區。'),
    Stray('banana', 'fruit_stand', '香蕉是水果，放水果區。'),
    Stray('bread', 'bakery', '麵包放麵包區。'),
    Stray('carrot', 'veggie_stand', '紅蘿蔔是蔬菜，放蔬菜區。'),
    Stray('cabbage', 'veggie_stand', '高麗菜是蔬菜，放蔬菜區。'),
    Stray('frozen_dumplings', 'frozen_case', '冷凍水餃要放冷凍櫃，才不會壞掉。'),
  ]),
  SortScene('recycling', '資源回收', Level.big, [
    Place('bin_paper', '紙類', x: 0.14, y: 0.62, w: 0.24),
    Place('bin_bottle', '寶特瓶', x: 0.38, y: 0.62, w: 0.24),
    Place('bin_can', '鐵鋁罐', x: 0.62, y: 0.62, w: 0.24),
    Place('bin_food', '廚餘', x: 0.86, y: 0.62, w: 0.24),
    Place('bin_trash', '一般垃圾', x: 0.5, y: 0.26, w: 0.24),
  ], [
    Stray('newspaper', 'bin_paper', '報紙是紙做的，放紙類回收。'),
    Stray('cardboard', 'bin_paper', '紙箱是紙做的，放紙類回收。'),
    Stray('pet_bottle', 'bin_bottle', '喝完的寶特瓶，放寶特瓶回收。'),
    Stray('soda_can', 'bin_can', '鋁罐放鐵鋁罐回收。'),
    Stray('banana_peel', 'bin_food', '香蕉皮是吃剩的，放廚餘。'),
    Stray('tissue', 'bin_trash', '用過的衛生紙不能回收，丟一般垃圾。'),
  ]),
];

/// Names of the things put away (卡通城).
const sortThings = {
  'ball': Thing('ball', '球', 'ball'),
  'blocks': Thing('blocks', '積木', 'blocks'),
  'toy_car': Thing('toy_car', '玩具車', 'toy car'),
  'book': Thing('book', '書', 'book'),
  'sock': Thing('sock', '襪子', 'sock'),
  'tshirt': Thing('tshirt', '衣服', 'T-shirt'),
  'pillow': Thing('pillow', '枕頭', 'pillow'),
  'toothbrush': Thing('toothbrush', '牙刷', 'toothbrush'),
  'toothpaste': Thing('toothpaste', '牙膏', 'toothpaste'),
  'towel': Thing('towel', '毛巾', 'towel'),
  'rubber_duck': Thing('rubber_duck', '小鴨子', 'rubber duck'),
  'soap': Thing('soap', '肥皂', 'soap'),
  'milk': Thing('milk', '牛奶', 'milk'),
  'vegetables': Thing('vegetables', '青菜', 'vegetables'),
  'bowl': Thing('bowl', '碗', 'bowl'),
  'plate': Thing('plate', '盤子', 'plate'),
  'dirty_cup': Thing('dirty_cup', '杯子', 'cup'),
  'ice_cream': Thing('ice_cream', '冰淇淋', 'ice cream'),
  'bird': Thing('bird', '小鳥', 'bird'),
  'squirrel': Thing('squirrel', '松鼠', 'squirrel'),
  'monkey': Thing('monkey', '猴子', 'monkey'),
  'cow': Thing('cow', '牛', 'cow'),
  'sheep': Thing('sheep', '羊', 'sheep'),
  'fish': Thing('fish', '魚', 'fish'),
  'octopus': Thing('octopus', '章魚', 'octopus'),
  'apple': Thing('apple', '蘋果', 'apple'),
  'banana': Thing('banana', '香蕉', 'banana'),
  'bread': Thing('bread', '麵包', 'bread'),
  'carrot': Thing('carrot', '紅蘿蔔', 'carrot'),
  'cabbage': Thing('cabbage', '高麗菜', 'cabbage'),
  'frozen_dumplings': Thing('frozen_dumplings', '冷凍水餃', 'frozen dumplings'),
  'newspaper': Thing('newspaper', '報紙', 'newspaper'),
  'cardboard': Thing('cardboard', '紙箱', 'cardboard box'),
  'pet_bottle': Thing('pet_bottle', '寶特瓶', 'plastic bottle'),
  'soda_can': Thing('soda_can', '鋁罐', 'can'),
  'banana_peel': Thing('banana_peel', '香蕉皮', 'banana peel'),
  'tissue': Thing('tissue', '衛生紙', 'tissue'),
};

// ---------------------------------------------------------------- 卡通城：是誰的？

/// Someone who needs something; [why] is said when they get it.
class Owner {
  const Owner(this.id, this.zh, this.wants, this.why, {this.from = Level.small});

  final String id;
  final String zh;
  final String wants;
  final String why;
  final Level from;
}

const owners = [
  Owner('firefighter', '消防員', 'hose', '水管是消防員的，消防員用水管噴水滅火。'),
  Owner('doctor', '醫生', 'stethoscope', '聽診器是醫生的，醫生用它聽心跳。'),
  Owner('chef', '廚師', 'spatula', '鍋鏟是廚師的，廚師用它炒菜。'),
  Owner('baby', '寶寶', 'baby_bottle', '奶瓶是寶寶的，寶寶用奶瓶喝奶。'),
  Owner('dog', '小狗', 'bone', '骨頭是小狗的，小狗最喜歡啃骨頭。'),
  Owner('rabbit', '兔子', 'carrot', '紅蘿蔔是兔子的，兔子愛吃紅蘿蔔。'),
  Owner('cat', '小貓', 'fish', '魚是小貓的，小貓愛吃魚。'),
  Owner('police', '警察', 'whistle', '哨子是警察的，警察吹哨子指揮交通。', from: Level.mid),
  Owner('mail_carrier', '郵差', 'letter', '信是郵差的，郵差把信送到大家家裡。', from: Level.mid),
  Owner('farmer', '農夫', 'hoe', '鋤頭是農夫的，農夫用鋤頭種菜。', from: Level.mid),
  Owner('grandpa', '阿公', 'glasses', '眼鏡是阿公的，阿公戴眼鏡看報紙。', from: Level.mid),
  Owner('sister', '姊姊', 'schoolbag', '書包是姊姊的，姊姊背書包去上學。', from: Level.mid),
  Owner('hairdresser', '理髮師', 'scissors', '剪刀是理髮師的，理髮師幫我們剪頭髮。', from: Level.big),
  Owner('painter', '畫家', 'paintbrush', '畫筆是畫家的，畫家用畫筆畫圖。', from: Level.big),
];

const ownerThings = {
  'hose': Thing('hose', '水管', 'hose'),
  'stethoscope': Thing('stethoscope', '聽診器', 'stethoscope'),
  'spatula': Thing('spatula', '鍋鏟', 'spatula'),
  'baby_bottle': Thing('baby_bottle', '奶瓶', 'baby bottle'),
  'bone': Thing('bone', '骨頭', 'bone'),
  'carrot': Thing('carrot', '紅蘿蔔', 'carrot'),
  'fish': Thing('fish', '魚', 'fish'),
  'whistle': Thing('whistle', '哨子', 'whistle'),
  'letter': Thing('letter', '信', 'letter'),
  'hoe': Thing('hoe', '鋤頭', 'hoe'),
  'glasses': Thing('glasses', '眼鏡', 'glasses'),
  'schoolbag': Thing('schoolbag', '書包', 'schoolbag'),
  'scissors': Thing('scissors', '剪刀', 'scissors'),
  'paintbrush': Thing('paintbrush', '畫筆', 'paintbrush'),
};

// ---------------------------------------------------------------- 紙片森林：連連看

/// Two things that belong together, and why.
class Pair {
  const Pair(this.a, this.b, this.why, {this.from = Level.small});

  final String a;
  final String b;
  final String why;
  final Level from;
}

const pairs = [
  Pair('bee', 'flower', '蜜蜂喜歡花，牠在花裡採花蜜。'),
  Pair('hen', 'egg', '雞蛋是母雞生的。'),
  Pair('cow', 'milk', '牛奶是從乳牛來的。'),
  Pair('rain_cloud', 'umbrella', '下雨了，要撐雨傘。'),
  Pair('bird', 'nest', '小鳥住在鳥巢裡。'),
  Pair('toothbrush', 'toothpaste', '牙刷和牙膏一起用來刷牙。'),
  Pair('key', 'lock', '鑰匙可以打開鎖。'),
  Pair('sock', 'shoe', '先穿襪子，再穿鞋子。'),
  Pair('bowl', 'chopsticks', '用筷子吃碗裡的飯。'),
  Pair('dirty_hands', 'soap', '手髒髒的，要用肥皂洗乾淨。', from: Level.mid),
  Pair('snow', 'gloves', '下雪好冷，要戴手套。', from: Level.mid),
  Pair('sun', 'sun_hat', '大太陽好曬，要戴帽子。', from: Level.mid),
  Pair('squirrel', 'pinecone', '松鼠喜歡吃松果裡的種子。', from: Level.mid),
  Pair('caterpillar', 'butterfly', '毛毛蟲長大會變成蝴蝶。', from: Level.big),
  Pair('tadpole', 'frog', '蝌蚪長大會變成青蛙。', from: Level.big),
];

const pairThings = {
  'bee': Thing('bee', '蜜蜂', 'bee'),
  'flower': Thing('flower', '花', 'flower'),
  'hen': Thing('hen', '母雞', 'hen'),
  'egg': Thing('egg', '雞蛋', 'egg'),
  'cow': Thing('cow', '乳牛', 'cow'),
  'milk': Thing('milk', '牛奶', 'milk'),
  'rain_cloud': Thing('rain_cloud', '下雨', 'rain'),
  'umbrella': Thing('umbrella', '雨傘', 'umbrella'),
  'bird': Thing('bird', '小鳥', 'bird'),
  'nest': Thing('nest', '鳥巢', 'nest'),
  'toothbrush': Thing('toothbrush', '牙刷', 'toothbrush'),
  'toothpaste': Thing('toothpaste', '牙膏', 'toothpaste'),
  'key': Thing('key', '鑰匙', 'key'),
  'lock': Thing('lock', '鎖', 'lock'),
  'sock': Thing('sock', '襪子', 'sock'),
  'shoe': Thing('shoe', '鞋子', 'shoe'),
  'bowl': Thing('bowl', '碗', 'bowl'),
  'chopsticks': Thing('chopsticks', '筷子', 'chopsticks'),
  'dirty_hands': Thing('dirty_hands', '髒手', 'dirty hands'),
  'soap': Thing('soap', '肥皂', 'soap'),
  'snow': Thing('snow', '下雪', 'snow'),
  'gloves': Thing('gloves', '手套', 'gloves'),
  'sun': Thing('sun', '大太陽', 'sun'),
  'sun_hat': Thing('sun_hat', '帽子', 'hat'),
  'squirrel': Thing('squirrel', '松鼠', 'squirrel'),
  'pinecone': Thing('pinecone', '松果', 'pinecone'),
  'caterpillar': Thing('caterpillar', '毛毛蟲', 'caterpillar'),
  'butterfly': Thing('butterfly', '蝴蝶', 'butterfly'),
  'tadpole': Thing('tadpole', '蝌蚪', 'tadpole'),
  'frog': Thing('frog', '青蛙', 'frog'),
};

// ---------------------------------------------------------------- 紙片森林：小偵探

/// The forest animals that can be suspects, with what tells them apart.
enum Species {
  rabbit('小兔子', '長耳朵'),
  squirrel('小松鼠', '大尾巴'),
  hedgehog('小刺蝟', '刺刺的背'),
  bear('小熊', '圓圓的耳朵');

  const Species(this.zh, this.feature);

  final String zh;

  /// The look a clue can point at ("牠有長耳朵").
  final String feature;
}

/// What a suspect wears (one thing at most).
enum Wear {
  none('', '', ''),
  scarf('圍巾', '圍著圍巾', '沒有圍巾'),
  hat('帽子', '戴著帽子', '沒有戴帽子'),
  glasses('眼鏡', '戴著眼鏡', '沒有戴眼鏡');

  const Wear(this.zh, this.on, this.off);

  final String zh;
  final String on;
  final String off;
}

class Suspect {
  const Suspect(this.species, this.wear);

  final Species species;
  final Wear wear;

  String get id => 'suspect_${species.name}_${wear.name}';

  String get zh => wear == Wear.none ? species.zh : '${wear.on}的${species.zh}';

  @override
  bool operator ==(Object other) => other is Suspect && other.species == species && other.wear == wear;

  @override
  int get hashCode => Object.hash(species, wear);
}

/// A case in the forest: what went missing, and what the one who took it says.
class Mystery {
  const Mystery(this.id, this.zh, this.thing, this.sorry);

  final String id;
  final String zh;

  /// The picture of what went missing (in the culprit's hands at the end).
  final String thing;
  final String sorry;
}

const mysteries = [
  Mystery('strawberries', '誰吃掉了草莓？', 'strawberries', '對不起，草莓太好吃了！下次我們一起分享。'),
  Mystery('honey', '誰拿走了蜂蜜？', 'honey', '對不起，我好想吃甜甜的蜂蜜！我拿回來了。'),
  Mystery('pinecones', '誰拿走了松果？', 'pinecones', '對不起，我想收集松果！還給你。'),
];

const mysteryThings = {
  'strawberries': Thing('strawberries', '草莓', 'strawberries'),
  'honey': Thing('honey', '蜂蜜', 'honey'),
  'pinecones': Thing('pinecones', '松果', 'pinecones'),
};

// ---------------------------------------------------------------- 積木王國：哪個不一樣？

/// A thing in the block kingdom and what is true of it.
class Block {
  const Block(this.id, this.zh, this.en, this.tags);

  final String id;
  final String zh;
  final String en;
  final Set<String> tags;
}

const blockThings = [
  Block('apple', '蘋果', 'apple', {'fruit', 'food', 'red', 'round'}),
  Block('banana', '香蕉', 'banana', {'fruit', 'food', 'yellow'}),
  Block('grapes', '葡萄', 'grapes', {'fruit', 'food', 'purple'}),
  Block('orange', '橘子', 'orange', {'fruit', 'food', 'round'}),
  Block('strawberry', '草莓', 'strawberry', {'fruit', 'food', 'red'}),
  Block('watermelon', '西瓜', 'watermelon', {'fruit', 'food', 'round'}),
  Block('tomato', '番茄', 'tomato', {'vegetable', 'food', 'red', 'round'}),
  Block('carrot', '紅蘿蔔', 'carrot', {'vegetable', 'food'}),
  Block('broccoli', '花椰菜', 'broccoli', {'vegetable', 'food'}),
  Block('car', '汽車', 'car', {'vehicle', 'road'}),
  Block('bus', '公車', 'bus', {'vehicle', 'road'}),
  Block('bicycle', '腳踏車', 'bicycle', {'vehicle', 'road'}),
  Block('fire_truck', '消防車', 'fire truck', {'vehicle', 'road', 'red'}),
  Block('airplane', '飛機', 'airplane', {'vehicle', 'flies'}),
  Block('boat', '船', 'boat', {'vehicle', 'water'}),
  Block('dog', '小狗', 'dog', {'animal', 'legs'}),
  Block('cat', '小貓', 'cat', {'animal', 'legs'}),
  Block('rabbit', '兔子', 'rabbit', {'animal', 'legs'}),
  Block('elephant', '大象', 'elephant', {'animal', 'legs'}),
  Block('fish', '魚', 'fish', {'animal', 'swims'}),
  Block('bird', '小鳥', 'bird', {'animal', 'flies'}),
  Block('butterfly', '蝴蝶', 'butterfly', {'animal', 'flies'}),
  Block('bee', '蜜蜂', 'bee', {'animal', 'flies'}),
  Block('ball', '球', 'ball', {'toy', 'round', 'red'}),
  Block('cube', '積木', 'block', {'toy', 'square'}),
  Block('clock', '時鐘', 'clock', {'round'}),
  Block('sock', '襪子', 'sock', {'clothes'}),
  Block('hat', '帽子', 'hat', {'clothes'}),
  Block('tshirt', '衣服', 'T-shirt', {'clothes'}),
];

Block blockThing(String id) => blockThings.firstWhere((b) => b.id == id);

/// A rule for 哪個不一樣: the group has every one of [tags]; the odd one has
/// every one of [outside] but not all of [tags]. [why] names the odd one's
/// difference ("汽車不是水果").
class OddRule {
  const OddRule(this.tags, this.outside, this.why, {this.from = Level.small, this.to = Level.big});

  final Set<String> tags;
  final Set<String> outside;
  final String Function(String odd) why;
  final Level from;
  final Level to;

  bool fits(Block b) => b.tags.containsAll(tags);

  bool odd(Block b) => b.tags.containsAll(outside) && !fits(b);
}

final oddRules = [
  OddRule({'fruit'}, {'vehicle'}, (o) => '$o不是水果。', to: Level.mid),
  OddRule({'animal'}, {'fruit'}, (o) => '$o不是動物。', to: Level.mid),
  OddRule({'vehicle'}, {'animal'}, (o) => '$o不是車子。', to: Level.mid),
  OddRule({'clothes'}, {'fruit'}, (o) => '$o不是衣服，不能穿。', to: Level.mid),
  OddRule({'flies'}, {'legs'}, (o) => '$o不會飛。', from: Level.mid),
  OddRule({'road'}, {'flies'}, (o) => '$o在天上飛，不在馬路上跑。', from: Level.mid),
  OddRule({'fruit'}, {'vegetable'}, (o) => '$o是蔬菜，不是水果。', from: Level.mid),
  OddRule({'round'}, {'square'}, (o) => '$o是方方的，不是圓的。', from: Level.mid),
  OddRule({'legs'}, {'swims'}, (o) => '$o沒有腳，在水裡游。', from: Level.big),
  OddRule({'food', 'red'}, {'red'}, (o) => '大家都是紅色的，可是$o不能吃。', from: Level.big),
];

// ---------------------------------------------------------------- 積木王國：接下來是什麼？

/// Things that happen in order; the last is asked for.
class Sequence {
  const Sequence(this.id, this.steps, this.why, {this.from = Level.mid});

  final String id;
  final List<String> steps;
  final String why;
  final Level from;
}

const sequences = [
  Sequence('chicken', ['egg', 'chick', 'hen'], '蛋裡孵出小雞，小雞長大變母雞。'),
  Sequence('flower', ['seed', 'sprout', 'flower'], '種子發芽，長大就開花了。'),
  Sequence('dressing', ['bare_foot', 'sock_on', 'shoe_on'], '光腳丫先穿襪子，再穿鞋子。'),
  Sequence('morning', ['wake_up', 'brushing', 'breakfast'], '起床、刷牙，再吃早餐。'),
  Sequence('rain', ['cloud', 'rain', 'rainbow'], '烏雲下雨，雨停了出彩虹。', from: Level.big),
  Sequence('butterfly', ['caterpillar', 'cocoon', 'butterfly'], '毛毛蟲結成蛹，再變成蝴蝶。', from: Level.big),
];

const sequenceThings = {
  'egg': Thing('egg', '蛋', 'egg'),
  'chick': Thing('chick', '小雞', 'chick'),
  'hen': Thing('hen', '母雞', 'hen'),
  'seed': Thing('seed', '種子', 'seed'),
  'sprout': Thing('sprout', '發芽', 'sprout'),
  'flower': Thing('flower', '花', 'flower'),
  'bare_foot': Thing('bare_foot', '光腳丫', 'bare foot'),
  'sock_on': Thing('sock_on', '穿襪子', 'socks on'),
  'shoe_on': Thing('shoe_on', '穿鞋子', 'shoes on'),
  'wake_up': Thing('wake_up', '起床', 'wake up'),
  'brushing': Thing('brushing', '刷牙', 'brush teeth'),
  'breakfast': Thing('breakfast', '吃早餐', 'breakfast'),
  'cloud': Thing('cloud', '烏雲', 'cloud'),
  'rain': Thing('rain', '下雨', 'rain'),
  'rainbow': Thing('rainbow', '彩虹', 'rainbow'),
  'caterpillar': Thing('caterpillar', '毛毛蟲', 'caterpillar'),
  'cocoon': Thing('cocoon', '蛹', 'cocoon'),
  'butterfly': Thing('butterfly', '蝴蝶', 'butterfly'),
};

/// The shapes and colours the block train carries (painted by the app in
/// the block style, no pictures needed).
enum Shape { circle, square, triangle, star }

enum Hue { red, blue, yellow, green }

class Token {
  const Token(this.shape, this.hue, {this.size = 1});

  final Shape shape;
  final Hue hue;

  /// 1 small, 2 middle, 3 big (for "getting bigger").
  final int size;

  static const shapeZh = {Shape.circle: '圓形', Shape.square: '方形', Shape.triangle: '三角形', Shape.star: '星星'};
  static const hueZh = {Hue.red: '紅色', Hue.blue: '藍色', Hue.yellow: '黃色', Hue.green: '綠色'};

  String get zh => '${hueZh[hue]}的${shapeZh[shape]}';

  @override
  bool operator ==(Object other) => other is Token && other.shape == shape && other.hue == hue && other.size == size;

  @override
  int get hashCode => Object.hash(shape, hue, size);
}

// ---------------------------------------------------------------- every picture

/// Every picture each land needs (rules_test checks they all exist).
Map<Land, Set<String>> get pictures => {
      Land.city: {
        for (final s in sortScenes) ...['scene_${s.id}', for (final p in s.places) p.id, for (final t in s.things) t.id],
        for (final o in owners) ...[o.id, o.wants],
        'scene_street',
      },
      Land.forest: {
        for (final p in pairs) ...[p.a, p.b],
        for (final s in Species.values)
          for (final w in Wear.values) Suspect(s, w).id,
        for (final m in mysteries) m.thing,
        'scene_meadow',
        'scene_woods',
      },
      Land.blocks: {
        for (final b in blockThings) b.id,
        for (final s in sequences) ...s.steps,
        'scene_kingdom',
      },
    };

/// The name of a picture's thing, in whichever table has it.
String? nameOf(Land land, String id) => switch (land) {
      Land.city => (sortThings[id] ?? ownerThings[id])?.zh ?? owners.where((o) => o.id == id).firstOrNull?.zh,
      Land.forest => (pairThings[id] ?? mysteryThings[id])?.zh,
      Land.blocks => blockThings.where((b) => b.id == id).firstOrNull?.zh ?? sequenceThings[id]?.zh,
    };
