import pygame
import sys
import random

# 游戏参数
ROWS, COLS = 10, 10
MINES = 10
CELL_SIZE = 50
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

# 颜色
BG_COLOR = (200, 200, 200)
GRID_COLOR = (100, 100, 100)
OPEN_COLOR = (230, 230, 230)
FLAG_COLOR = (255, 0, 0)
MINE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 255)

pygame.init()
FONT = pygame.font.Font(r"E:\code\GameDemo\resource\font\MiSans\MiSans-Demibold.ttf",36)
SMALL_FONT = pygame.font.Font(r"E:\code\GameDemo\resource\font\MiSans\MiSans-Regular.ttf",24)

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_open = False
        self.is_flag = False
        self.adjacent = 0

class Minesweeper:
    def __init__(self):
        self.board = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]
        self.mines = set()
        self.flags = set()
        self.opened = 0
        self.game_over = False
        self.win = False
        self.first_click = True

    def _place_mines(self, safe_r, safe_c):
        # 以(safe_r, safe_c)为中心的3x3区域不能有雷
        safe_zone = set()
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                nr, nc = safe_r+dr, safe_c+dc
                if 0<=nr<ROWS and 0<=nc<COLS:
                    safe_zone.add((nr, nc))
        while len(self.mines) < MINES:
            r = random.randint(0, ROWS-1)
            c = random.randint(0, COLS-1)
            if (r, c) in safe_zone or self.board[r][c].is_mine:
                continue
            self.board[r][c].is_mine = True
            self.mines.add((r, c))

    def _calc_adjacent(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c].is_mine:
                    continue
                count = 0
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        nr, nc = r+dr, c+dc
                        if 0<=nr<ROWS and 0<=nc<COLS and self.board[nr][nc].is_mine:
                            count += 1
                self.board[r][c].adjacent = count

    def open_cell(self, r, c):
        if self.board[r][c].is_open or self.board[r][c].is_flag or self.game_over:
            return
        if self.first_click:
            self._place_mines(r, c)
            self._calc_adjacent()
            self.first_click = False
        self._open_cell_impl(r, c)

    def _open_cell_impl(self, r, c):
        if self.board[r][c].is_open or self.board[r][c].is_flag:
            return
        self.board[r][c].is_open = True
        self.opened += 1
        if self.board[r][c].is_mine:
            self.game_over = True
            self.win = False
            return
        if self.board[r][c].adjacent == 0:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr, nc = r+dr, c+dc
                    if 0<=nr<ROWS and 0<=nc<COLS and not self.board[nr][nc].is_open:
                        self._open_cell_impl(nr, nc)
        self._check_win()

    def flag_cell(self, r, c):
        if self.board[r][c].is_open or self.game_over:
            return
        self.board[r][c].is_flag = not self.board[r][c].is_flag
        if self.board[r][c].is_flag:
            self.flags.add((r, c))
        else:
            self.flags.discard((r, c))

    def _check_win(self):
        if self.opened == ROWS*COLS - MINES and not self.game_over:
            self.game_over = True
            self.win = True

    def draw(self, screen):
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c*CELL_SIZE, r*CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if self.board[r][c].is_open:
                    pygame.draw.rect(screen, OPEN_COLOR, rect)
                    if self.board[r][c].is_mine:
                        pygame.draw.circle(screen, MINE_COLOR, rect.center, CELL_SIZE//4)
                    elif self.board[r][c].adjacent > 0:
                        txt = FONT.render(str(self.board[r][c].adjacent), True, TEXT_COLOR)
                        screen.blit(txt, txt.get_rect(center=rect.center))
                else:
                    pygame.draw.rect(screen, BG_COLOR, rect)
                    if self.board[r][c].is_flag:
                        pygame.draw.polygon(screen, FLAG_COLOR, [rect.topleft, (x+CELL_SIZE//2, y+10), (x+10, y+CELL_SIZE//2)])
                pygame.draw.rect(screen, GRID_COLOR, rect, 2)

def draw_popup(screen, msg):
    # 半透明遮罩
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    # 弹窗矩形
    popup_w, popup_h = 320, 180
    popup_x = (WIDTH - popup_w) // 2
    popup_y = (HEIGHT - popup_h) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
    pygame.draw.rect(screen, (255, 255, 255), popup_rect, border_radius=12)
    pygame.draw.rect(screen, (100, 100, 100), popup_rect, 3, border_radius=12)
    # 提示文字
    txt = FONT.render(msg, True, (0,0,0))
    screen.blit(txt, txt.get_rect(center=(WIDTH//2, popup_y+50)))
    # 按钮
    yes_rect = pygame.Rect(popup_x+40, popup_y+110, 90, 40)
    no_rect = pygame.Rect(popup_x+popup_w-130, popup_y+110, 90, 40)
    pygame.draw.rect(screen, (0,200,0), yes_rect, border_radius=8)
    pygame.draw.rect(screen, (200,0,0), no_rect, border_radius=8)
    yes_txt = SMALL_FONT.render("是", True, (255,255,255))
    no_txt = SMALL_FONT.render("否", True, (255,255,255))
    screen.blit(yes_txt, yes_txt.get_rect(center=yes_rect.center))
    screen.blit(no_txt, no_txt.get_rect(center=no_rect.center))
    return yes_rect, no_rect

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("扫雷 - 10x10 10雷")
    clock = pygame.time.Clock()
    game = Minesweeper()
    popup_active = False
    popup_result = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not popup_active:
                if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                    x, y = event.pos
                    r, c = y//CELL_SIZE, x//CELL_SIZE
                    if event.button == 1:
                        game.open_cell(r, c)
                    elif event.button == 3:
                        game.flag_cell(r, c)
                if event.type == pygame.KEYDOWN and game.game_over:
                    if event.key == pygame.K_r:
                        game = Minesweeper()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if yes_rect.collidepoint(x, y):
                        game = Minesweeper()
                        popup_active = False
                    elif no_rect.collidepoint(x, y):
                        pygame.quit()
                        sys.exit()
        screen.fill(BG_COLOR)
        game.draw(screen)
        if game.game_over and not popup_active:
            popup_active = True
        if popup_active:
            msg = "你赢了！是否重新开始？" if game.win else "游戏结束！是否重新开始？"
            yes_rect, no_rect = draw_popup(screen, msg)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
