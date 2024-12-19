# ライブラリのインポート
import pygame
import time
import random
import asyncio

# 各種設定
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
orange = (255, 165, 0)
gray = (50, 50, 50)

size_block = 30

num_block_width = 30
num_block_height = 20

dis_width = size_block * num_block_width
dis_height = size_block * num_block_height

food_size = 0.5

snake_speed = 8
step = 8
move = 1/step

font = "./CP Font.otf"

# 各種関数

# スコアの表示
def show_scores(dis, font, score1, score2):
    # プレイヤー1のスコア（左上）
    player1_text = font.render("プレイヤー1", True, blue)
    score1_text = font.render(f"{score1//8}", True, blue)
    
    player1_rect = player1_text.get_rect(topleft=(10, 10))
    score1_rect = score1_text.get_rect(midtop=(player1_rect.centerx, player1_rect.bottom + 5))
    
    dis.blit(player1_text, player1_rect.topleft)
    dis.blit(score1_text, score1_rect.topleft)
    
    # プレイヤー2のスコア（右上）
    player2_text = font.render("プレイヤー2", True, orange)
    score2_text = font.render(f"{score2//8}", True, orange)
    
    player2_rect = player2_text.get_rect(topright=(dis_width - 10, 10))
    score2_rect = score2_text.get_rect(midtop=(player2_rect.centerx, player2_rect.bottom + 5))
    
    dis.blit(player2_text, player2_rect.topleft)
    dis.blit(score2_text, score2_rect.topleft)
    
def show_remaining_time(dis, font, remaining_time, color, ):
    # 1行目: "残り時間"
    time_label = font.render("残り時間", True, color)
    label_rect = time_label.get_rect(center=(dis_width // 2, dis_height // 2 - 20))  # 中央より少し上に配置

    # 2行目: 秒数
    time_value = font.render(f"{remaining_time // 1000:02d}", True, color)  # 秒数（ゼロ埋め付き）
    value_rect = time_value.get_rect(center=(dis_width // 2, dis_height // 2 + 20))  # 中央より少し下に配置

    # 描画
    dis.blit(time_label, label_rect)
    dis.blit(time_value, value_rect)



# 蛇の描画
def draw_snake(dis, snake_list, color):
    for i, (x, y) in enumerate(snake_list):
        # セグメントの中心座標
        center_x = x * size_block + size_block // 2
        center_y = y * size_block + size_block // 2
        pygame.draw.circle(dis, color, (center_x, center_y), size_block // 2)
        
# 餌の描画
def draw_food(dis, food_x, food_y):
    
    # ブロックの中心を計算
    food_center_x = food_x * size_block + size_block // 2
    food_center_y = food_y * size_block + size_block // 2

    # 食べ物の左上座標を計算
    food_top_left_x = food_center_x - (size_block * food_size) // 2
    food_top_left_y = food_center_y - (size_block * food_size) // 2

    # 食べ物を描画
    pygame.draw.rect(dis, green, [food_top_left_x, food_top_left_y, size_block * food_size, size_block * food_size])


# メッセージの表示
def message(dis, font, msg, color):
    mesg = font.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(dis_width / 2, dis_height / 2))
    dis.blit(mesg, mesg_rect)


# 新しい餌の位置を決める
def make_food():
    food_x = random.randrange(1, num_block_width-1)
    food_y = random.randrange(1, num_block_height-1)
    return food_x, food_y


def reset_snake(is_wall_collision, snake_list, initial_x, initial_y, wall_flag, player, x_change, y_change):
    
    if is_wall_collision:
        # 壁に衝突した場合、スネークを初期位置に戻す
        snake_list = [(initial_x, initial_y)]
        wall_flag = False
        x_change, y_change = 0, 0
        x, y = initial_x, initial_y
    else:
        # 自分自身や相手に衝突した場合、スネークの長さを1にする
        snake_list = [snake_list[-1]]
        x, y = snake_list[-1]
            

    length = 1
    return snake_list, length, wall_flag, x_change, y_change, x, y

async def main():
    game_init = True
    game_close = False
    game_over_1 = False
    game_over_2 = False
    wall1 = False
    wall2 = False
    end_game = False
    
    # pygameの初期化
    pygame.init()
    pygame.mixer.init()
    dis = pygame.display.set_mode((dis_width, dis_height))
    pygame.display.set_caption("2人で対戦！スネークゲーム")

    clock = pygame.time.Clock()
    font_message = pygame.font.Font(font, 35)
    font_score = pygame.font.Font(font, 30)
    
    # タイマー関連の設定
    game_duration = 60_000  # 60秒 (ミリ秒)
    game_duration = 10_000
#     start_time = pygame.time.get_ticks()  # ゲーム開始時刻を記録

    # 効果音
    eat_sound = pygame.mixer.Sound("sfx/8bit取得1_えさ.ogg")
    wall_sound = pygame.mixer.Sound("sfx/Crash-Beer-Bottle-On-Cinder-Block-Smash-02.ogg")
    you_sound = pygame.mixer.Sound("sfx/8bit爆発2_あいて.ogg")
    start_sound = pygame.mixer.Sound("sfx/Countdown06-1.ogg")
    eat_sound.set_volume(0.3)
    


    while True:
        if game_init:
            # 初期化
            x1, y1 = num_block_width // 4, num_block_height // 2
            x2, y2 = 3 * num_block_width // 4, num_block_height // 2
            x_change1, y_change1 = 0, 0
            x_change2, y_change2 = 0, 0
            snake_list1, snake_list2 = [], []
            length1, length2 = 1, 1
            food_x, food_y = make_food()
            game_init = False
            # タイマー関連の設定
            game_duration = 60_000  # 60秒 (ミリ秒)
            game_init_2 = True
            remaining_time = 60_000
            


        elif game_close:
            pygame.quit()
            break
            
        elif game_over_1:
            snake_list1, length1, wall1, x_change1, y_change1, x1, y1 = reset_snake(
                wall1, snake_list1, num_block_width // 4, num_block_height // 2, wall1, 1, x_change1, y_change1
            )
            game_over_1 = False

        elif game_over_2:
            snake_list2, length2, wall2, x_change2, y_change2, x2, y2 = reset_snake(
                wall2, snake_list2, 3 * num_block_width // 4, num_block_height // 2, wall2, 2, x_change2, y_change2
            )
            game_over_2 = False
        
        elif end_game:
            # ゲームオーバー

            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_close = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        end_game = False
                        game_init = True
                        
                        
            dis.fill(black)        
            message(dis, font_message, "時間切れ！C:もう一度", red)
            show_scores(dis, font_score, length1 - 1, length2 - 1)
            pygame.display.update()

                        
                        
                        
        else:     

            if game_init_2 is False:
                # 残り時間を計算
                elapsed_time = pygame.time.get_ticks() - start_time
                remaining_time = max(0, game_duration - elapsed_time)

                if remaining_time == 0:  # 60秒経過でゲーム終了
                    end_game = True


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_close = True
                if event.type == pygame.KEYDOWN:
                        if game_init_2:
                            if event.key == pygame.K_SPACE:
                                start_sound.play()
                                wait_start_time = pygame.time.get_ticks()  # 待機の開始時刻を記録
                                while pygame.time.get_ticks() - wait_start_time < 3000:  # 3秒経過を待機
                                    for wait_event in pygame.event.get():
                                        if wait_event.type == pygame.QUIT:
                                            game_close = True
                                            break
                                    if game_close:
                                        break
                                if not game_close:
                                    start_time = pygame.time.get_ticks()
                                    game_init_2 = False


                        else:
                            # プレイヤー1の操作
                            if event.key == pygame.K_a:
                                x_change1, y_change1 = -1*move, 0
                            elif event.key == pygame.K_d:
                                x_change1, y_change1 = move, 0
                            elif event.key == pygame.K_w:
                                x_change1, y_change1 = 0, -1*move
                            elif event.key == pygame.K_s:
                                x_change1, y_change1 = 0, move
                            # プレイヤー2の操作
                            elif event.key == pygame.K_LEFT:
                                x_change2, y_change2 = -1*move, 0
                            elif event.key == pygame.K_RIGHT:
                                x_change2, y_change2 = move, 0
                            elif event.key == pygame.K_UP:
                                x_change2, y_change2 = 0, -1*move
                            elif event.key == pygame.K_DOWN:
                                x_change2, y_change2 = 0, move


            for i in range(step):

                # 蛇の移動
                x1 += x_change1
                y1 += y_change1
                x2 += x_change2
                y2 += y_change2



                # 壁との衝突判定
                if x1 >= num_block_width or x1 < 0 or y1 >= num_block_height or y1 < 0:
                    game_over_1 = True
                    wall1 = True
                    # wall_sound.play()
                    break
                if x2 >= num_block_width or x2 < 0 or y2 >= num_block_height or y2 < 0:
                    game_over_2 = True
                    wall2 = True
                    # wall_sound.play()
                    break

                # 自分自身や他プレイヤーとの衝突判定
                head1, head2 = (x1, y1), (x2, y2)
                snake_list1.append(head1)
                snake_list2.append(head2)

                if len(snake_list1) > length1:
                    del snake_list1[0]
                if len(snake_list2) > length2:
                    del snake_list2[0]
                if head1 in snake_list1[:-1] or head1 in snake_list2:
                    game_over_1 = True
                    you_sound.play()
                    break
                if head2 in snake_list2[:-1] or head2 in snake_list1:
                    game_over_2 = True
                    you_sound.play()
                    break

                easy = 0
                if ((food_x-easy) <= head1[0] <= (food_x+easy)) and ((food_y-easy) <= head1[1] <= (food_y+easy)):  
                    food_x, food_y = make_food()
                    length1 += step 
                    eat_sound.play()

                if ((food_x-easy) <= head2[0] <= (food_x+easy)) and ((food_y-easy) <= head2[1] <= (food_y+easy)):  
                    food_x, food_y = make_food()
                    length2 += step

                    eat_sound.play()

                dis.fill(black)    

                # 残り時間を中央に表示

                if game_init_2:
                    time_value = font_score.render("SPASEキーでスタート", True, gray)  # 秒数（ゼロ埋め付き）
                    value_rect = time_value.get_rect(center=(dis_width // 2, dis_height // 2 + 10))  # 中央より少し下に配置
                    dis.blit(time_value, value_rect)

                else:
                    show_remaining_time(dis, font_score, remaining_time, gray)
                draw_food(dis, food_x, food_y)
                draw_snake(dis, snake_list1, blue)
                draw_snake(dis, snake_list2, orange)
                show_scores(dis, font_score, length1 - 1, length2 - 1)


                pygame.display.update()
                clock.tick(snake_speed*step)
        await asyncio.sleep(0) 

# メインループの実行
asyncio.run(main())
