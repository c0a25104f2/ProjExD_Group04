import pygame as pg
import random  # ランダム機能を使うために使用
import os  # ファイルやフォルダを操作するためのライブラリ
import sys  # Python自体を操作するためのライブラリ

WIDTH = 800
HEIGHT = 600
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# スクリプトの場所にカレントディレクトリを移動（環境によってエラーになるのを防ぐため、例外処理を追加）
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except Exception:
    pass


class Card:  # カード1枚を表す
    def __init__(self, rank, suit):
        self.rank = rank  # 数字部分
        self.suit = suit  # マーク部分

    def draw(self, screen, font, x, y):  # カードを表示するための関数
        pg.draw.rect(screen, WHITE, (x, y, 70, 100))  # 白い長方形を描く
        pg.draw.rect(screen, BLACK, (x, y, 70, 100), 2)  # カードの枠線
        text = font.render(f"{self.rank}{self.suit}", True, BLACK)  # カードの文字を作る
        screen.blit(text, (x + 10, y + 35))  # 作った文字を画面に貼り付け


class Deck:  # 山札を管理する(52枚)
    def __init__(self):
        suits = ["H", "D", "C", "S"]  # カードのマーク
        ranks = [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"]  # カードの数字
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(rank, suit))

        random.shuffle(self.cards)  # 山札をランダムに混ぜる

    def draw(self):  # 山札からカードを引く処理
        if len(self.cards) == 0:
            raise Exception("Deck is empty")
        return self.cards.pop()  # カードを1枚取り出す


class Hand:  # 手札を管理する部分
    def __init__(self):
        self.cards = []  # 手札を入れるための空リストを作る

    def add(self, card):  # 手札にカードを追加する関数
        self.cards.append(card)

    def total(self):  # 手札の合計点を計算する
        value = 0
        aces = 0
        for card in self.cards:
            if card.rank in ["J", "Q", "K"]:
                value += 10
            elif card.rank == "A":
                value += 11
                aces += 1
            else:
                value += int(card.rank)

        while value > 21 and aces:  # Aを1点に変更する処理
            value -= 10
            aces -= 1

        return value

    def draw(self, screen, font, x, y):  # 手札を画面に表示する部分
        for i, card in enumerate(self.cards):
            card.draw(screen, font, x + i * 90, y)  # カードを表示、横にずらす

        total = font.render(f"Player Total : {self.total()}", True, WHITE)
        screen.blit(total, (x, y + 120))

    def draw_dealer(self, screen, font, x, y, hide=True):  # ディーラーの手札表示
        for i, card in enumerate(self.cards):
            if i == 0 and hide:
                pg.draw.rect(screen, BLACK, (x + i * 90, y, 70, 100))  # カードの裏側
                pg.draw.rect(screen, WHITE, (x + i * 90, y, 70, 100), 2)
            else:
                card.draw(screen, font, x + i * 90, y)

        if not hide:
            total = font.render(f"Dealer Total : {self.total()}", True, WHITE)
            screen.blit(total, (x, y + 120))


class Chips:
    def __init__(self):
        self.total_chips = 1000  # 初期所持金
        self.current_bet = 10  # デフォルトの賭け金
        self.min_bet = 10  # 最低賭け金

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
        if outcome == "blackjack":
            payout = int(self.current_bet * 2.5)
        elif outcome == "win":
            payout = self.current_bet * 2
            
        elif outcome == "draw":
            payout = self.current_bet
        else:
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
        self.font = None
        self.text = ""

    def update(self, screen):
        if self.font is None:
            self.font = pg.font.SysFont("msgothic", 30)
        img = self.font.render(self.text, True, WHITE)
        screen.blit(img, (50, 520))


class Gmo:  # ゲームオーバー画面＆コンティニューボタン
    def __init__(self):
        self.gm = pg.Surface((WIDTH, HEIGHT))
        self.fonto = pg.font.SysFont("msgothic", 50)  # Game Overのフォント
        self.txt = self.fonto.render("♧ゲームオーバー♦", True, (255, 255, 255))
        self.txt_sub = self.fonto.render("右シフトキーで復活！", True, (255, 215, 0))

    def gamen(self, screen):
        self.gm.fill((0, 0, 0))
        self.gm.set_alpha(190)
        self.gm.blit(self.txt, [200, 230])
        self.gm.blit(self.txt_sub, [180, 310])
        screen.blit(self.gm, [0, 0])


class Burakkujakku_gamen:
    def burakkujakku_gamen(self, screen: pg.Surface) -> None:
        go_img = pg.Surface((WIDTH, HEIGHT))
        go_img.fill((0, 0, 0))
        go_img.set_alpha(180)

        fonto = pg.font.SysFont("msgothic", 80)
        txt = fonto.render("Black Jack", True, (255, 255, 255))
        go_img.blit(txt, [WIDTH // 2 - 150, HEIGHT // 2 - 40])
        screen.blit(go_img, [0, 0])


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

    # ベット額が所持力を上回っていたら自動調整
    if chips.current_bet > chips.total_chips:
        chips.current_bet = chips.total_chips

    # 初期ブラックジャック（ナチュラル21）判定
    if player.total() == 21:
        if dealer.total() == 21:
            message.text = "Both Blackjack! Draw!"
            outcome = "draw"
        else:
            message.text = "BlackJack! You Win!"
            outcome = "blackjack"
        game_over = True

    return deck, player, dealer, message, game_over, outcome


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Pygame ブラックジャック")

    # 日本語表示対応のフォント指定
    font = pg.font.SysFont("msgothic", 25)
    main_menu_font = pg.font.SysFont("msgothic", 60)
    msg_font = pg.font.SysFont("msgothic", 30)
    clock = pg.time.Clock()
    scene = "TITLE"
    chips = Chips()
    gmo = Gmo()

    # 最初のゲームの初期化
    deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)

    betting_phase = True
    is_gameover_screen = False  # 破産（所持金0）フラグ
    result_timer = 0
    payout_settled = False  # チップ精算を1度だけ行うためのフラグ
    is_double_down = False  # ダブルダウンしたか記憶するフラグ

    while True:
        # --- 1. イベント処理 ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN:
                # 破産状態でのゲームオーバー画面表示中のキー受付
                if is_gameover_screen:
                    if event.key == pg.K_RSHIFT:  # 右シフトで復活
                        chips.total_chips = 1000
                        chips.current_bet = 10
                        deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)
                        betting_phase = True
                        is_gameover_screen = False
                        payout_settled = False
                    continue  # 他のキーは無視

                # タイトル画面でのキー受付
                if scene == "TITLE":
                    if event.key == pg.K_e:
                        deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)
                        betting_phase = True
                        payout_settled = False
                        if game_over:
                            result_timer = pg.time.get_ticks()
                        else:
                            result_timer = 0
                        scene = "GAME"

                # ゲーム画面でのキー受付
                elif scene == "GAME":
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

                            # 初期配られたカードで勝負がついていた（ナチュラルBJなど）場合の即座の精算処理
                            if game_over:
                                payout = chips.settle_payout(outcome)
                                payout_settled = True
                                if outcome == "blackjack" or outcome == "win":
                                    message.text += f" (+{payout} chips)"
                                elif outcome == "draw":
                                    message.text += " (Push)"
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
                            # ディーラーが17以上になるまで引き続ける
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

                            # 勝負がついたので、ゲームオーバーとタイマーをセット
                            game_over = True
                            result_timer = pg.time.get_ticks()
                        elif event.key == pg.K_d:# DOUBLE DOWN
                            # ダブルダウンは最初の2枚（手札が2枚）のときのみ可能
                            if len(player.cards) == 2 and chips.total_chips >= chips.current_bet:
                                chips.total_chips -= chips.current_bet  # 追加で同額を支払う
                                chips.current_bet *= 2  # このゲームの賭け金を2倍にする
                                is_double_down = True  # ダブルダウンフラグをON

                                player.add(deck.draw())
                                
                                
                                # カードを1枚引いた時点でバーストした場合
                                if player.total() > 21:
                                    message.text = "Bust! You Lose!"
                                    outcome = "lose"
                                    game_over = True
                                    result_timer = pg.time.get_ticks()
                                # バーストしなかった場合は、そのままスタンド（ディーラーのターン）へ移行
                                else:
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
        if scene == "GAME" and game_over and not betting_phase and not payout_settled:
            payout = chips.settle_payout(outcome)
            payout_settled = True
            if outcome == "lose":
                message.text += f" (-{chips.current_bet} chips)"
            elif outcome == "draw":
                pass  # 引き分け時はそのまま
            else:
                message.text += f" (+{payout} chips)"

        # --- 3. 画面の描画処理（シーンごとに完全に切り分け） ---
        if scene == "TITLE":
            screen.fill(WHITE)
            title_text = main_menu_font.render("Blackjack", True, BLACK)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            screen.blit(title_text, title_rect)

            start_text = font.render("E ボタンでスタート", True, BLACK)
            start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 * 2))
            screen.blit(start_text, start_rect)

                
        elif scene == "GAME":
            screen.fill(GREEN)
            chips.draw_ui(screen, font)

            if betting_phase:
                # ベット選択画面のテキスト表示
                guide_text1 = msg_font.render("ベット額を決めてください", True, WHITE)
                guide_text2 = font.render("↑/↓ : ±10  |  ←/→ : ±100  |  Enter : 決定", True, WHITE)
                screen.blit(guide_text1, (50, 250))
                screen.blit(guide_text2, (50, 300))
            else:
                # ゲーム画面の表示（手札や点数）
                # ゲーム進行中（not game_over）はディーラーの1枚目を隠し、ゲームオーバーになったらオープン
                dealer.draw_dealer(screen, font, 50, 80, not game_over)
                player.draw(screen, font, 50, 320)
                message.update(screen)

                if not game_over:
                    guide = font.render("[H]: Hit (もう1枚) [S]: Stand (勝負)", True, WHITE)
                    guide2 = font.render("[D]: double down(2倍で勝負)", True, WHITE)
                    screen.blit(guide, (50, 20))
                    screen.blit(guide2,(50, 45))

            # 初期ブラックジャック演出（手札2枚かつ合計21点）
            if player.total() == 21 and len(player.cards) == 2 and not betting_phase:
                bg = Burakkujakku_gamen()
                bg.burakkujakku_gamen(screen)

            # 破産ゲームオーバー画面の重ね合わせ描画
            if is_gameover_screen:
                gmo.gamen(screen)

        # --- 4. 画面の更新 ---
        pg.display.update()

        # --- 5. ゲームの自動進行リセット & 破産チェック ---
        if scene == "GAME" and game_over and not betting_phase and not is_gameover_screen:
            # 勝敗表示後、2.5秒（2500ミリ秒）経過したら次へ
            if pg.time.get_ticks() - result_timer > 2500:
                if chips.total_chips <= 0:
                    # チップが0になったらゲームオーバー画面へ
                    is_gameover_screen = True
                else:
                    if is_double_down:
                        chips.current_bet //= 2
                        is_double_down = False
                    # チップがあれば次のゲームを自動開始
                    deck, player, dealer, message, game_over, outcome = new_game(msg_font, chips)
                    betting_phase = True

        # フレームレートを60に固定
        clock.tick(60)


if __name__ == "__main__":
    pg.init()  # pygameを初期化
    main()  # ゲーム本体の開始
    pg.quit()  # pygameの終了
    sys.exit()  # pythonプログラム自体の終了