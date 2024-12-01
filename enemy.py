import pygame
from pygame.math import Vector2


class Enemy(pygame.sprite.Sprite):
    def __init__(self, path, speed=2, health=30, image_path=None, game = None, reward=10):
        """
        Базовый класс для врагов
        Инициализация врага:
        path: список точек пути, по которым будет двигаться врага;
        speed: скорость движения врага;
        health: здоровье врага;
        image_path: путь к изображению врага;
        game: ссылка на текущую игру (для доступа к игровым ресурсам и состоянию);
        reward: награда за уничтожение врага.
        """
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.game = game
        self.path = path
        self.path_index = 0
        self.speed = speed
        self.health = health
        self.reward = reward
        self.position = Vector2(path[0])
        self.rect.center = self.position

    def take_damage(self, amount):
        """
        Уменьшение здоровья врага при получении урона.
        Если здоровье <= 0, враг умирает
        amount: количество урона.
        """
        self.health -= amount
        if self.health <= 0:
            self.on_death()

    def on_death(self):
        """
        Действия при смерти врага. Увеличивает деньги игрока и удаляет врага.
        """
        if self.game:  # Проверяем, есть ли ссылка на игру
            self.game.settings.starting_money += self.reward  # Увеличиваем деньги игрока
            print(f"Enemy killed! Player rewarded with ${self.reward}. Total money: ${self.game.settings.starting_money}")
        self.kill()  # Удаляем врага из игры

    def update(self):
        """
        Обновление состояния врага. Обрабатывает движение по пути.
        """
        if self.path_index < len(self.path) - 1:
            start_point = Vector2(self.path[self.path_index])
            end_point = Vector2(self.path[self.path_index + 1])
            direction = (end_point - start_point).normalize()

            self.position += direction * self.speed
            self.rect.center = self.position

            if self.position.distance_to(end_point) < self.speed:
                self.path_index += 1

            if self.path_index >= len(self.path) - 1:
                self.game.game_over()
                self.kill()


class FastEnemy(Enemy):
    """
    Класс для создания врагов более быстрых, чем в базовом классе, но с низким здоровьем
    """
    def __init__(self, path, game):
        super().__init__(path=path, speed=3, health=10,
                         image_path='assets/enemies/fast_enemy.png', game=game, reward=15)


class StrongEnemy(Enemy):
    """
    Класс для создания врагов более медленных, но с высоким здоровьем
    """
    def __init__(self, path, game):
        super().__init__(path=path, speed=1, health=100,
                         image_path='assets/enemies/strong_enemy.png', game=game, reward=30)


class BossEnemy(Enemy):
    """
    Класс для создания очень медленных врагов, но с очень высоким здоровьем
    """
    def __init__(self, path, game):
        super().__init__(path=path, speed=0.5, health=300,
                         image_path='assets/enemies/boss_enemy.png', game=game, reward=100)

