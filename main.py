"""
Проект является реализацией игры в жанре "Tower Defense", где игроку предстоит защищать базу от волн врагов,
расставляя башни.
Реализован базовый функционал: можно выиграть если пережить три волны, или проиграть если хотя бы один враг дойдёт.
Также есть два типа башен, переключение между ними по клавишам 1 и 2.

Это главный модуль, он содержит основной игровой цикл, обработку событий, обновление состояний игры и отрисовку элементов игры.
"""
import pygame
import sys
from settings import Settings
from level import Level1, Level2, Level3
from grid import Grid


class TowerDefenseGame:
    """
    Главный класс игры, управляющий основным циклом игры, событиями, обновлениями состояний и отрисовкой.
    """
    def __init__(self):
        """
        Конструктор класса. Инициализирует основные параметры игры, загружает ресурсы и создаёт объекты уровня и сетки.
        """
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Tower Defense Game")
        self.clock = pygame.time.Clock()

        self.background = pygame.image.load(self.settings.background_image).convert()
        self.background = pygame.transform.scale(
            self.background, (self.settings.screen_width, self.settings.screen_height)
        )

        # Инициализация уровней
        self.levels = [Level1(self), Level2(self), Level3(self)]  # Список уровней
        self.current_level_index = 0  # Индекс текущего уровня
        self.level = self.levels[self.current_level_index]  # Текущий уровень
        self.grid = Grid(self)

        self.font = pygame.font.SysFont("Arial", 24)

        self.shoot_sound = pygame.mixer.Sound(self.settings.shoot_sound)
        self.selected_tower_type = 'basic'
        self.is_game_over = False
        self.is_game_won = False  # Флаг для проверки победы

        # Переменная для отслеживания состояния отображения сетки
        self.show_grid = False

    def game_over(self):
        """
        Обрабатывает условия окончания игры.
        """
        self.is_game_over = True

    def is_position_inside(self, pos):
        """
        Функция проверяет, находится ли позиция в пределах игрового поля.
        """
        return 0 <= pos.x <= self.settings.screen_width and 0 <= pos.y <= self.settings.screen_height

    def _check_events(self):
        """
        Обрабатывает игровые события, такие как нажатие клавиш и клики мыши.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_tower_type = 'basic'
                    print("Selected basic tower.")
                elif event.key == pygame.K_2:
                    self.selected_tower_type = 'sniper'
                    print("Selected sniper tower.")
                elif event.key == pygame.K_3:
                    self.selected_tower_type = 'money'
                    print("Selected money tower.")

                # Обработка нажатия пробела и переключение состояния отображения сетки
                elif event.key == pygame.K_SPACE:
                    self.show_grid = not self.show_grid

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Левая кнопка мыши — размещение башни
                if event.button == 1:
                    if self.selected_tower_type:
                        self.level.attempt_place_tower(mouse_pos, self.selected_tower_type)
                    else:
                        print("No tower type selected.")

                # Правая кнопка мыши — улучшение башни
                elif event.button == 3:
                    for tower in self.level.towers:
                        if tower.rect.collidepoint(mouse_pos):
                            tower.upgrade()
                            break

    def _update_game(self):
        """
        Обновляет состояние игры, вызывая обновления уровня и сетки.
        """
        if not self.is_game_over and not self.is_game_won:
            self.level.update()
            self.grid.update()
            # Проверка уничтожения врагов и добавление награды
            for enemy in list(self.level.enemies):  # Преобразуем группу врагов в список для безопасного удаления
                if enemy.health <= 0:  # Если здоровье врага <= 0
                    self.settings.starting_money += enemy.reward  # Добавляем деньги за уничтожение
                    self.level.enemies.remove(enemy)  # Удаляем врага из группы
                    print(f"Enemy defeated! Reward: {enemy.reward}. Total Money: {self.settings.starting_money}")

            # Проверка на завершение уровня
            if self.level.all_waves_complete and len(self.level.enemies) == 0:
                self._next_level()

    def _next_level(self):
        """
        Переход к следующему уровню или завершение игры при прохождении всех уровней.
        """
        if self.current_level_index < len(self.levels) - 1:
            self.current_level_index += 1
            self.level = self.levels[self.current_level_index]
            print(f"Starting Level {self.current_level_index + 1}")
        else:
            self.is_game_won = True
            print("You have completed all levels! You win!")

    def _draw_win_screen(self):
        """
        Отображает экран победы.
        """
        self.screen.fill((0, 0, 0))
        win_text = "You Win!"
        win_render = self.font.render(win_text, True, (255, 215, 0))
        win_rect = win_render.get_rect(center=(self.settings.screen_width / 2, self.settings.screen_height / 2))
        self.screen.blit(win_render, win_rect)

    def _draw_game_over_screen(self):
        """
        Отображает экран проигрыша.
        """
        self.screen.fill((0, 0, 0))
        game_over_text = "Game Over!"
        game_over_render = self.font.render(game_over_text, True, (255, 0, 0))
        game_over_rect = game_over_render.get_rect(center=(self.settings.screen_width / 2, self.settings.screen_height / 2))
        self.screen.blit(game_over_render, game_over_rect)

    def _draw(self):
        """
        Управляет отрисовкой всех элементов игры.
        """
        if self.is_game_over:
            self._draw_game_over_screen()
        elif self.is_game_won:
            self._draw_win_screen()
        else:
            self.screen.blit(self.background, (0, 0))
            self.level.draw(self.screen)
            if self.show_grid:  # Отображаем сетку только если show_grid True
                self.grid.draw()

            # Отображение информации о деньгах, башнях, волнах и врагах
            money_text = self.font.render(f"Money: ${self.settings.starting_money}", True, (255, 255, 255))
            tower_text = self.font.render(
                f"Selected Tower: {self.selected_tower_type if self.selected_tower_type else 'None'}", True,
                (255, 255, 255))
            waves_text = self.font.render(f"Waves Left: {len(self.level.waves) - self.level.current_wave}", True,
                                          (255, 255, 255))
            enemies_text = self.font.render(f"Enemies Left: {len(self.level.enemies)}", True, (255, 255, 255))

            self.screen.blit(money_text, (10, 10))
            self.screen.blit(tower_text, (10, 40))
            self.screen.blit(waves_text, (10, 70))
            self.screen.blit(enemies_text, (10, 100))

            # Отображение информации об улучшении башен
            mouse_pos = pygame.mouse.get_pos()
            for tower in self.level.towers:
                if tower.is_hovered(mouse_pos):
                    tower.draw(self.screen)

        pygame.display.flip()

    def run_game(self):
        """
        Запускает основной игровой цикл.
        """
        while True:
            self._check_events()
            self._update_game()

            if len(self.level.enemies) == 0 and not self.level.all_waves_complete:
                self.level.start_next_wave()

            self._draw()
            self.clock.tick(60)


if __name__ == '__main__':
    td_game = TowerDefenseGame()
    td_game.run_game()
