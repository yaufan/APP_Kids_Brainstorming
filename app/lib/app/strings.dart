import '../core/content.dart';

/// Everything the app says, in Traditional Chinese (Taiwan).
abstract final class Strings {
  static const appName = '想一想樂園';

  // The park.
  static const welcome = '歡迎來到想一想樂園！今天想玩哪一個？';
  static const parent = '家長';
  static const book = '偵探手冊';
  static const home = '回樂園';
  static const back = '回去';
  static String enter(Land land) => '我們去${land.zh}！';
  static const abuLines = ['我是小偵探阿布！', '想一想，再想一想！', '你好聰明喔！', '我們一起破案吧！'];

  // Playing.
  static const ask = {
    GameKind.sort: '把東西放回家！',
    GameKind.owner: '這是誰的？拿給需要它的人。',
    GameKind.pairs: '誰和誰是一對？用手指連起來！',
    GameKind.detective: '看看線索，找出是誰！',
    GameKind.odd: '哪個不一樣？',
    GameKind.next: '接下來是什麼？',
  };
  static String whereGoes(String thing) => '$thing要放哪裡呢？';
  static String whose(String thing) => '$thing是誰的呢？';
  static String notHere(String thing, String place) => '$thing不放$place喔，再想一想！';
  static String notTheirs(String thing, String who) => '$who不需要$thing喔，再想一想！';
  static const notPair = '它們不是一對喔，再想一想！';
  static const notOdd = '它和大家一樣喔，再找找看！';
  static const notNext = '再看一次火車，想一想！';
  static const notNextStep = '想一想，接下來會怎樣？';
  static const lookAtClues = '先看看線索喔！點一下線索。';
  static String notThem(String who) => '不是$who喔，看看線索！';
  static const nextRound = '下一題';
  static const right = ['答對了！', '好棒！', '你真厲害！', '沒錯！'];
  static const solved = '破案了！';
  static String gotSticker(String thing) => '得到一張$thing貼紙！';
  static const again = '再玩一次';
  static const toPark = '回樂園';
  static const train = '下一個是什麼？';
  static const steps = '接下來會怎樣？';
  static String clue(int n) => '線索$n';

  // The book.
  static String bookCount(int have, int all) => '收集了 $have／$all 張';

  // Resting.
  static const restTitle = '樂園要休息了';
  static const restLine = '樂園要休息了，眼睛也休息一下。\n我們去把家裡的玩具放回家吧！';

  // Parent gate (as in the sibling apps).
  static const callParent = '請爸爸媽媽來幫忙喔！';
  static const parentGateTitle = '家長確認';
  static String gateQuestion(String a, String b) => '$a 加 $b 等於多少？';
  static const gateRules = '答錯三次要等一分鐘。';
  static const wrongAnswer = '不對喔，換一題。';
  static String gateWait(int s) => '請等 $s 秒再試';
  static const backspace = '刪掉';
  static const cancel = '取消';

  // Parent mode.
  static const parentTitle = '家長模式';
  static const age = '年齡（難度）';
  static String levelLine(Level l) => '${l.zh}（${l.ages}）';
  static const ageNote = '答錯好幾次時，下一題會自動變簡單一點；答對了再變回來。';
  static const games = '要玩哪些遊戲';
  static const detectiveNote = '小偵探從「中」開始才會出現。';
  static const playTime = '每次可以玩多久';
  static String minutes(int m) => '$m 分鐘';
  static const playTimeNote = '時間到了，樂園會天黑休息，請小朋友去把家裡的玩具放回家。要家長解開，或等一個小時，才能再玩。';
  static const playOn = '讓小朋友再玩一次（重新計時）';
  static const resting = '現在是休息時間。';
  static const sound = '聲音';
  static const music = '背景音樂';
  static const effects = '音效';
  static const voice = '念出題目和原因';
  static const english = '東西的名字後面加英文（apple）';
  static const progress = '能力進度';
  static String skillLine(int right, int tried) => tried == 0 ? '還沒玩過' : '玩了 $tried 題，一次就答對 $right 題';
  static const progressNote = '「一次就答對」：這一題沒有放錯或選錯。常常放錯的能力，可以在生活中多一起玩。';
  static const together = '生活中一起玩';
  static const tips = [
    '收玩具的時候一起分類：積木放這籃、車子放那籃。',
    '逛超市時找找看：水果區在哪裡？冷凍櫃在哪裡？',
    '倒垃圾時一起資源回收：這是紙、這是寶特瓶。',
    '吃飯前排碗筷：一個碗配一雙筷子。',
    '多問一句「為什麼？」，讓小朋友說說看「因為……」。',
  ];
  static const fullVersion = '完整版';
  static const fullNote = '免費版有卡通城的兩個遊戲；完整版有三個園區的全部遊戲。（測試版先全部打開。）';
  static const fullSwitch = '打開完整版（測試用）';
  static const about = '關於';
  static const privacy = '不連網、不定位、沒有廣告、沒有帳號；玩的紀錄只存在這支手機裡。';
  static String version(String v) => '版本 $v';
}
