import pygame as pg
import random
import os
import sys #Python事態を操作するためのライブラリ

WIDTH = 800 #以下2行色
HEIGHT = 600
GREEN = (34, 139, 34) #以下3行色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
os.chdir(os.path.dirname(os.path.abspath(__file__)))


class Card: #カード1枚を表す
    def __init__(self, rank, suit):
        self.rank = rank #数字部分
        self.suit = suit #マーク部分

    def draw(self, screen, font, x, y):
        pg.draw.rect(screen, WHITE, (x, y, 70, 100))
        pg.draw.rect(screen, BLACK, (x, y, 70, 100), 2)

        text = font.render(f"{self.rank}{self.suit}", True, BLACK)
        screen.blit(text, (x+10, y+35))


class Deck:

    def __init__(self):

        suits = ["H", "D", "C", "S"]
        ranks = [str(i) for i in range(2, 11)] + ["J", "Q", "K", "A"]
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(rank, suit))

        random.shuffle(self.cards)


    def draw(self):

        # 山札切れ防止
        if len(self.cards) == 0:
            raise Exception("Deck is empty")
        return self.cards.pop()


class Hand:

    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def total(self):
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

        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value


    def draw(self, screen, font, x, y):
        for i, card in enumerate(self.cards):
            card.draw(screen, font, x+i*90, y)

        total = font.render( f"Player Total : {self.total()}", True, WHITE)
        screen.blit(total, (x, y+120))


    def draw_dealer(self, screen, font, x, y, hide=True):
        for i, card in enumerate(self.cards):
            if i == 0 and hide:
                pg.draw.rect(screen, BLACK, (x+i*90, y, 70, 100))
                pg.draw.rect(screen, WHITE, (x+i*90, y, 70,100), 2)
            else:
                card.draw(screen, font, x+i*90, y)

        if not hide:
            total = font.render(f"Dealer Total : {self.total()}", True, WHITE)
            screen.blit(total,(x,y+120))


class Message:
    def __init__(self):
        self.font = pg.font.SysFont("msgothic", 30)
        self.text = ""

    def update(self,screen):
        img = self.font.render(self.text, True, WHITE)
        screen.blit(img,(50,520))



def new_game():
    deck = Deck()
    player = Hand()
    dealer = Hand()
    player.add(deck.draw())
    player.add(deck.draw())
    dealer.add(deck.draw())
    dealer.add(deck.draw())
    message = Message()
    game_over = False
    if player.total() == 21:# 初期ブラックジャック判定
        if dealer.total() == 21:# ディーラーもブラックジャックの場合
            message.text = "Both Blackjack! Draw!"
        else:
            message.text = "BlackJack! You Win!"

        game_over = True
    return deck, player, dealer, message, game_over


def main():
    screen = pg.display.set_mode((WIDTH,HEIGHT))
    pg.display.set_caption("Pygame ブラックジャック")
    font = pg.font.SysFont("msgothic", 25)
    clock = pg.time.Clock()
    deck, player, dealer, message, game_over = new_game()

    if game_over:
        result_timer = pg.time.get_ticks()
    else:
        result_timer = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN and not game_over:
                if event.key == pg.K_h:# HIT
                    player.add(deck.draw())
                    if player.total() > 21:
                        message.text = "Bust! You Lose!"
                        game_over = True
                        result_timer = pg.time.get_ticks()
                elif event.key == pg.K_s:# STAND
                    while dealer.total() < 17:
                        dealer.add(deck.draw())
                    p = player.total()
                    d = dealer.total()

                    if d > 21:
                        message.text = "Dealer Bust! You Win!"
                    elif p > d:
                        message.text = "You Win!"
                    elif p < d:
                        message.text = "You Lose!"
                    else:
                        message.text = "Draw!"

                    game_over = True
                    result_timer = pg.time.get_ticks()

                    #ダブルダウンの追加処理
                elif event.key == pg.K_d:# DOUBLE DOWN
                    # ダブルダウンは最初の2枚（手札が2枚）のときのみ可能
                    if len(player.cards) == 2:
                        player.add(deck.draw())
                        
                        # カードを1枚引いた時点でバーストした場合
                        if player.total() > 21:
                            message.text = "Bust! You Lose!"
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
                            elif p > d:
                                message.text = "You Win!"
                            elif p < d:
                                message.text = "You Lose!"
                            else:
                                message.text = "Draw!"

                            game_over = True
                            result_timer = pg.time.get_ticks()

        screen.fill(GREEN)
        dealer.draw_dealer(screen, font, 50, 80, not game_over)
        player.draw(screen, font, 50, 320)
        message.update(screen)
        pg.display.update()
        if game_over:# 2秒後に新しいゲーム開始
            if pg.time.get_ticks() - result_timer > 2000:
                deck, player, dealer, message, game_over = new_game()

        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()