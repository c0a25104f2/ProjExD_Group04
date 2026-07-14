import pygame as pg
import random #ランダム機能を使うために使用
import os #ファイルやフォルダを操作するためのライブラリ
import sys #Python事態を操作するためのライブラリ

WIDTH = 800 #以下2行色
HEIGHT = 600
GREEN = (34, 139, 34) #以下3行色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Card: #カード1枚を表す
    def __init__(self, rank, suit):
        self.rank = rank #数字部分
        self.suit = suit #マーク部分

    def draw(self, screen, font, x, y): #カードを表示するための関数(画面、文字、横位置、縦位置)
        pg.draw.rect(screen, WHITE, (x, y, 70, 100)) # 白い長方形を描く(x座標、y座標、幅、高さ)
        pg.draw.rect(screen, BLACK, (x, y, 70, 100), 2) # カードの枠線(・・・、太さ)
        text = font.render(f"{self.rank}{self.suit}", True, BLACK) # カードの文字を作る
        screen.blit(text, (x+10, y+35)) # 作った文字を画面に貼り付け (カード左から10、カード上から35)


class Deck: # 山札を管理する(52枚)
    def __init__(self):
        suits = ["H", "D", "C", "S"] # カードのマークを作っている
        ranks = [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"] # カードの数字を作っている["1","2",・・・,"K","A"]
        self.cards = [] # 空のカード置き場
        for suit in suits: # マークで繰り返し
            for rank in ranks: # 数字で繰り返し
                self.cards.append(Card(rank, suit)) # Cardクラスに入れて対応するカードを作成

        random.shuffle(self.cards) # 山札をランダムに混ぜる


    def draw(self): # 山札からカードを引く処理
        if len(self.cards) == 0: # 山札の枚数を確認
            raise Exception("Deck is empty") # エラーを発生させる/山札が空の場合に文を出力
        return self.cards.pop() # カードを1枚取り出す


class Hand: # 手札を管理する部分
    def __init__(self):
        self.cards = [] # 手札を入れるための空リストを作る

    def add(self, card): # 手札にカードを追加する関数
        self.cards.append(card) # カードをリストの最後に追加

    def total(self): # 手札の合計点を計算する
        value = 0 # 現在の合格点を保存する変数
        aces = 0 # A(エース)の枚数を数える変数
        for card in self.cards: # 手札のカードを順番に調べる
            if card.rank in ["J", "Q", "K"]: # これらの時+10
                value += 10
            elif card.rank == "A": # これらの時　+1 or + 11
                value += 11
                aces += 1
            else:
                value += int(card.rank) # 数字を点数に加える

        while value > 21 and aces: # Aを1点に変更する処理
            value -= 10 # 10点減らす
            aces -= 1 # Aを1枚処理済みにする

        return value # 計算した合計点をかえす


    def draw(self, screen, font, x, y): # 手札を画面に表示する部分
        for i, card in enumerate(self.cards): # 手札のカードを順番に取り出す
            card.draw(screen, font, x+i*90, y) # カードを表示させる、i*90で横にずらす

        total = font.render( f"Player Total : {self.total()}", True, WHITE) # 合計点を文字にする
        screen.blit(total, (x, y+120)) # 合計点をカードの下に表示する


    def draw_dealer(self, screen, font, x, y, hide=True): # ディーラーのカードを表示する関数(ディーラーの手札、ゲーム画面、文字の種類、表示開始位置、表示開始位置、１枚目を隠すかどうか)
        for i, card in enumerate(self.cards): # カードを1枚ずつ取り出す
            if i == 0 and hide: # 条件を確認(1枚目を隠すかどうか判定)
                pg.draw.rect(screen, BLACK, (x+i*90, y, 70, 100)) # 黒い長方形を書く(カードの裏側)
                pg.draw.rect(screen, WHITE, (x+i*90, y, 70,100), 2) # 黒いカードに白い枠線をつける
            else:
                card.draw(screen, font, x+i*90, y) # カードを表示

        if not hide: # カードを隠さない場合(ゲームの終了時)
            total = font.render(f"Dealer Total : {self.total()}", True, WHITE) # ディーラーの合計点を文字にする
            screen.blit(total,(x,y+120)) #合計点をカードの下に表示する

class Chips:
    def __init__(self):
        self.total_chips = 1000  # 初期所持金
        self.current_bet = 10    # デフォルトの賭け金
        self.min_bet = 10        # 最低賭け金

    def adjust_bet(self, amount):
        """ 十字キーでベット額を増減。所持チップを越えないように制御 """
        self.current_bet += amount
        if self.current_bet < self.min_bet:
            self.current_bet = self.min_bet
        if self.current_bet > self.total_chips:
            self.current_bet = self.total_chips

    def place_bet(self):
        """ ベット確定時に所持金から引く """
        self.total_chips -= self.current_bet

    def settle_payout(self, outcome):
        """ 勝敗に応じて配当金を計算し、所持金に加算する """
        # outcomeの種類: "win", "blackjack", "draw", "lose"
        if outcome == "blackjack":
            # ブラックジャックは2.5倍払い戻し（1.5倍の利益）
            payout = int(self.current_bet * 2.5)
        elif outcome == "win":
            # 通常勝利は2倍払い戻し
            payout = self.current_bet * 2
        elif outcome == "draw":
            # 引き分けはベット額の払い戻し
            payout = self.current_bet
        else:
            # 負けは0
            payout = 0
            
        self.total_chips += payout
        return payout

    def draw_ui(self, screen, font):
        """ 画面右上に現在の所持金と現在のベット額を常時表示 """
        chips_text = font.render(f"Total Chips: {self.total_chips}", True, GOLD)
        bet_text = font.render(f"Current Bet: {self.current_bet}", True, GOLD)
        screen.blit(chips_text, (WIDTH - 250, 20))
        screen.blit(bet_text, (WIDTH - 250, 50))

class Message:
    def __init__(self, font):
        self.font = pg.font.SysFont("msgothic", 30)
        self.text = "" # 表示する文字を空にする

    def update(self,screen): # 画面にメッセージを表示する
        img = self.font.render(self.text, True, WHITE) # 文字を画像に変換
        screen.blit(img,(50,520)) # 画面へ貼り付ける

class Gmo:# ゲームオーバー画面＆コンティニューボタン
    def __init__(self):
        self.gm = pg.Surface((WIDTH, HEIGHT)) 
        self.fonto = pg.font.SysFont("msgothic", 50)#Game Overのフォントづくり
        self.txt = self.fonto.render("♧ゲームオーバー♦", True, (255, 255, 255))
    def gamen(self, screen):
        pg.draw.rect(self.gm, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
        self.gm.set_alpha(190)
        self.gm.blit(self.txt,[200, 260])
        screen.blit(self.gm, [0, 0])
    # def rebotan(self):

def new_game(msg_font, chips):
    deck = Deck()
    player = Hand()
    dealer = Hand()
    player.add(deck.draw())
    player.add(deck.draw())
    dealer.add(deck.draw())
    dealer.add(deck.draw())
    message = Message(msg_font)
    game_over = False
    outcome = None  # 配当計算用の勝敗ステータス

    # 破産チェック：次のゲーム開始時にチップが0なら1000に戻す
    if chips.total_chips <= 0:
        chips.total_chips = 1000
        chips.current_bet = 10

    # ベット額が所持金を上回っていたら自動調整
    if chips.current_bet > chips.total_chips:
        chips.current_bet = chips.total_chips

    return deck, player, dealer, message, game_over, outcome

    if player.total() == 21:# 初期ブラックジャック判定
        if dealer.total() == 21:# ディーラーもブラックジャックの場合
            message.text = "Both Blackjack! Draw!"
        else:
            message.text = "BlackJack! You Win!"

        game_over = True
    


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Pygame ブラックジャック")
    
    # 日本語表示対応のため、標準のゴシック体フォントを指定（無い場合はデフォルトにフォールバック）
    font = pg.font.SysFont("msgothic", 24)
    msg_font = pg.font.SysFont("msgothic", 30)
    clock = pg.time.Clock()
    
    chips = Chips()
    gmo = Gmo()
    
    # 最初のゲームの初期化
    deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)

    betting_phase = True
    is_gameover_screen = False  # 破産（所持金0）フラグ
    result_timer = 0
    payout_settled = False      # チップ精算を1度だけ行うためのフラグ

    while True:
        # --- 1. イベント処理 ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN:
                # 破産ゲームオーバー画面の時
                if is_gameover_screen:
                    if event.key == pg.K_RSHIFT:  # 右シフトで復活
                        chips.total_chips = 1000
                        chips.current_bet = 10
                        deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)
                        betting_phase = True
                        is_gameover_screen = False
                        payout_settled = False
                    continue

                # ベットフェーズ（金額決め）の時
                if betting_phase:
                    if event.key == pg.K_UP:
                        chips.adjust_bet(10)
                    elif event.key == pg.K_DOWN:
                        chips.adjust_bet(-10)
                    elif event.key == pg.K_RIGHT:
                        chips.adjust_bet(100)
                    elif event.key == pg.K_LEFT:
                        chips.adjust_bet(-100)
                    elif event.key == pg.K_RETURN:
                        chips.place_bet()
                        betting_phase = False
                        payout_settled = False
                        
                        # 初期配られたカードで勝負がついていた（BJなど）場合の処理
                        if game_over:
                            payout = chips.settle_payout(outcome)
                            payout_settled = True
                            if payout > 0:
                                message.text += f" (+{payout} chips)"
                            else:
                                message.text += f" (Lose {chips.current_bet} chips)"
                            result_timer = pg.time.get_ticks()
                
                # プレイ中（ヒット・スタンド選択）の時
                elif not game_over:
                    if event.key == pg.K_h:
                        player.add(deck.draw())
                        if player.total() > 21:
                            message.text = "Bust! You Lose!"
                            outcome = "lose"
                            game_over = True
                            result_timer = pg.time.get_ticks()

                    elif event.key == pg.K_s:
                        while dealer.total() < 17:
                            dealer.add(deck.draw())
                        p = player.total()
                        d = dealer.total()

                        if d > 21:
                            message.text = "Dealer Bust! You Win!"
                            outcome = "win"
                        elif p > d:
                            message.text = "You Win!"
                            outcome = "win"
                        elif p < d:
                            message.text = "You Lose!"
                            outcome = "lose"
                        else:
                            message.text = "Draw!"
                            outcome = "draw"

                        game_over = True
                        result_timer = pg.time.get_ticks()

        # --- 2. 精算処理 (勝負が決まった瞬間に1回だけ実行) ---
        if game_over and not betting_phase and not payout_settled:
            payout = chips.settle_payout(outcome)
            payout_settled = True
            if outcome == "lose":
                message.text += f" (-{chips.current_bet} chips)"
            else:
                message.text += f" (+{payout} chips)"

        # --- 3. 画面の描画 ---
        screen.fill(GREEN)
        chips.draw_ui(screen, font)

        if betting_phase:
            # ベット選択画面のテキスト表示
            guide_text1 = msg_font.render("ベット額を決めてください", True, WHITE)
            guide_text2 = font.render("↑/↓ : ±10  |  ←/→ : ±100  |  Enter : 決定", True, WHITE)
            screen.blit(guide_text1, (50, 250))
            screen.blit(guide_text2, (50, 300))
        else:
            # 試合画面の表示
            dealer.draw_dealer(screen, font, 50, 80, not game_over)
            player.draw(screen, font, 50, 320)
            message.update(screen)
            
            if not game_over:
                guide = font.render("[H]: Hit (もう1枚)   [S]: Stand (勝負)", True, WHITE)
                screen.blit(guide, (50, 20))

        # 破産ゲームオーバー画面の重ね合わせ描画
        if is_gameover_screen:
            gmo.gamen(screen)

        # --- 4. 画面の更新 ---
        pg.display.update()

        # --- 5. ゲームの自動進行リセット & 破産チェック ---
        if game_over and not betting_phase and not is_gameover_screen:
            # 勝敗表示後、2.5秒経過したら次へ
            if pg.time.get_ticks() - result_timer > 2500:
                if chips.total_chips <= 0:
                    # チップが0になったらゲームオーバー画面へ
                    is_gameover_screen = True
                else:
                    # チップがあれば次のゲームを自動開始
                    deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)
                    betting_phase = True

        # フレームレートを60に固定
        clock.tick(60)

if __name__ == "__main__":
    pg.init() # pygameを初期化
    main() # ゲーム本体の開始
    pg.quit() # pygameの終了
    sys.exit() # pythonプログラム自体の終了