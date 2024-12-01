"""
Модуль tower.py содержит классы для реализации башен в игре жанра "Tower Defense".
Он включает базовый класс Tower и его наследников для различных типов башен, таких как BasicTower и SniperTower.
Класс Tower отвечает за логику стрельбы, поиска целей, улучшения башен и визуализации информации об уровне и стоимости улучшения.

Каждая башня имеет следующие характеристики:
- Позиция: координаты расположения на игровом поле.
- Урон: величина урона, наносимого врагам.
- Дальность: максимальное расстояние, на которое башня может атаковать.
- Скорострельность: время между выстрелами.

Модуль также загружает звуковые эффекты для выстрелов, которые воспроизводятся при атаке на врагов.
******************

Импортируемые модули:
- pygame: библиотека для разработки игр, обеспечивающая функционал для работы с графикой, звуком и событиями.
- bullet: класс для реализации пуль.
- math: для математических вычислений, таких как определение углов.
"""
import pygame
from bullet import Bullet
import math

class Tower(pygame.sprite.Sprite):
    """
    Базовый класс для башен. Обеспечивает базовую функциональность, включая:
    - нанесение урона врагам;
    - улучшение башни с повышением характеристик;
    - отображение информации о башне.
    """

    def __init__(self, position, game):
        """
        Инициализация башни.
        :param position: Позиция башни на игровом поле (tuple или Vector2).
        :param game: Ссылка на основной объект игры для доступа к ресурсам.
        """
        super().__init__()

        # Основные параметры
        self.position = pygame.math.Vector2(position)
        self.game = game

        # Характеристики башни
        self.tower_range = 120  # Радиус действия башни
        self.damage = 50  # Урон
        self.rate_of_fire = 1000  # Скорострельность в миллисекундах (интервал между выстрелами)
        self.last_shot_time = pygame.time.get_ticks()  # Время последнего выстрела
        self.level = 1  # Уровень башни

        # Визуальные элементы
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)  # Заготовка для башни
        self.image.fill((0, 255, 0))  # Цвет башни
        self.rect = self.image.get_rect(center=self.position)

        # Для вращения башни к цели
        self.original_image = self.image
        self.rotation_angle = 0

        # Звук выстрела
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/shoot.wav")

    def upgrade_cost(self):
        """
        Рассчитывает стоимость улучшения башни.
        :return: Стоимость улучшения (50 × текущий уровень башни).
        """
        return 50 * self.level

    def upgrade(self):
        """
        Улучшение уровня башни. Увеличивает урон и скорострельность на 20%.
        """
        # Проверяем, достаточно ли денег для улучшения
        if self.game.settings.starting_money >= self.upgrade_cost():
            # Списываем деньги
            self.game.settings.starting_money -= self.upgrade_cost()

            # Увеличиваем уровень башни
            self.level += 1

            # Увеличиваем характеристики башни
            self.damage = int(self.damage * 1.2)  # Увеличиваем урон на 20%
            self.rate_of_fire = int(self.rate_of_fire * 0.8)  # Увеличиваем скорострельность (уменьшение интервала)

            print(f"Башня улучшена до уровня {self.level}. Новый урон: {self.damage}, "
                  f"новая скорострельность: {self.rate_of_fire} мс.")
        else:
            print("Недостаточно денег для улучшения башни.")

    def is_hovered(self, mouse_pos):
        """
        Проверяет, находится ли курсор мыши над башней.
        :param mouse_pos: Позиция мыши.
        :return: True, если курсор над башней, иначе False.
        """
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """
        Отображение информации о башне на экране.
        :param screen: Экран, на который производится отрисовка.
        """
        screen.blit(self.image, self.rect.topleft)

        # Если мышь наведена на башню, отобразить информацию
        mouse_pos = pygame.mouse.get_pos()
        if self.is_hovered(mouse_pos):
            level_text = self.game.font.render(f"Level: {self.level}", True, (255, 255, 255))
            upgrade_cost_text = self.game.font.render(f"Upgrade: ${self.upgrade_cost()}", True, (255, 255, 255))

            # Располагаем текст рядом с башней
            level_text_pos = (self.rect.centerx, self.rect.top - 20)
            upgrade_cost_text_pos = (self.rect.centerx, self.rect.top - 40)

            # Отрисовка текста
            screen.blit(level_text, level_text_pos)
            screen.blit(upgrade_cost_text, upgrade_cost_text_pos)

    def rotate_towards(self, target_position):
        """
        Поворачивает башню в направлении заданной цели.
        :param target_position: Позиция цели.
        """
        dx = target_position[0] - self.position.x
        dy = target_position[1] - self.position.y
        self.rotation_angle = (180 / math.pi) * -math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.position)

    def shoot(self, target):
        """
        Стреляет по цели.
        :param target: Объект цели (например, враг).
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.rate_of_fire:
            self.last_shot_time = current_time
            target.take_damage(self.damage)
            self.shoot_sound.play()

    def find_target(self, enemies):
        """
        Находит ближайшую цель среди врагов, находящихся в радиусе действия башни.
        :param enemies: Список врагов.
        :return: Ближайший враг или None, если врагов нет в радиусе действия.
        """
        closest_enemy = None
        closest_distance = float('inf')

        for enemy in enemies:
            distance = self.position.distance_to(enemy.position)
            if distance <= self.tower_range and distance < closest_distance:
                closest_enemy = enemy
                closest_distance = distance

        return closest_enemy

    def update(self, enemies, current_time, bullets):
        """
        Обновляет состояние башни: поиск цели, стрельба и создание пуль.
        :param enemies: Список врагов.
        :param current_time: Текущее игровое время.
        :param bullets: Список пуль, чтобы добавлять новые.
        """
        # Ищем ближайшую цель
        target = self.find_target(enemies)
        if target:
            # Поворачиваем башню к цели
            self.rotate_towards(target.position)

            # Проверяем, может ли башня стрелять
            if current_time - self.last_shot_time >= self.rate_of_fire:
                self.last_shot_time = current_time  # Обновляем время последнего выстрела

                # Создаем пулю, добавляем ее в список пуль
                bullet = Bullet(self.position, target.position, self.damage, self.game)
                bullets.add(bullet)

                # Воспроизводим звук выстрела
                self.shoot_sound.play()


class BasicTower(Tower):
    """
    Класс BasicTower ("Базовая башня")- дочерний от класса Tower.
    Определяет свойства и поведение базовой башни, включая урон, дальность и скорость стрельбы.
    """
    def __init__(self, position, game):
        """
        Инициализация базовой башни.
        :param position: Позиция башни на игровом поле.
        :param game: Ссылка на текущую игру.
        """
        super().__init__(position, game)
        self.image = pygame.image.load('assets/towers/basic_tower.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.tower_range = 150
        self.damage = 20
        self.rate_of_fire = 1000

    def shoot(self, target, bullets_group):
        """
        Логика стрельбы для базовой башни.
        :param target: Цель, на которую производится выстрел.
        :param bullets_group: Группа пуль, в которую будут добавлены новые пули.
        """
        self.shoot_sound.play()
        new_bullet = Bullet(self.position, target.position, self.damage, self.game)
        bullets_group.add(new_bullet)


class SniperTower(Tower):
    """
    Класс SniperTower ("Снайперская башня") также является наследником от класса Tower.
    Определяет свойства и поведение базовой башни, включая урон, дальность и скорость стрельбы.
    """
    def __init__(self, position, game):
        """
        Инициализация снайперской башни.
        :param position: Позиция башни на игровом поле.
        :param game: Ссылка на текущую игру.
        """
        super().__init__(position, game)
        self.image = pygame.image.load('assets/towers/sniper_tower.png').convert_alpha()
        self.image = pygame.transform.rotate(self.image, 90)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.tower_range = 300
        self.damage = 40
        self.rate_of_fire = 2000

    def find_target(self, enemies):
        """
        Поиск самой здоровой цели среди врагов.
        :param enemies: Список врагов на игровом поле.
        :return: Враг с наибольшим здоровьем, находящийся в пределах досягаемости.
        """
        healthiest_enemy = None
        max_health = 0
        for enemy in enemies:
            if self.position.distance_to(enemy.position) <= self.tower_range and enemy.health > max_health:
                healthiest_enemy = enemy
                max_health = enemy.health
        return healthiest_enemy

    def shoot(self, target, bullets_group):
        """
        Логика стрельбы для снайперской башни.
        :param target: Цель, на которую производится выстрел.
        :param bullets_group: Группа пуль, в которую будут добавлены новые пули.
        """
        self.shoot_sound.play()
        new_bullet = Bullet(self.position, target.position, self.damage, self.game)
        bullets_group.add(new_bullet)


class MoneyTower(Tower):
    """
    Класс, представляющий денежную башню в игре Tower Defense.
    Эта башня генерирует деньги для игрока с заданной скоростью.
    Описание:
    position: Позиция башни на игровом поле.
    game: Ссылка на текущую игру, позволяющая доступ к её ресурсам.
    image: Изображение башни.
    original_image: Оригинальное изображение для возможной трансформации.
    rect: Прямоугольник, определяющий размеры и положение башни.
    money_generation_rate: Количество денег, генерируемое за один интервал.
    generation_interval: Интервал времени (в миллисекундах) для генерации денег.
    last_generation_time: Время последней генерации денег.
    """
    def __init__(self, position, game):
        """
        Инициализация денежной башни
        """
        super().__init__(position, game)
        self.image = pygame.image.load('assets/towers/money_tower.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=self.position)
        self.money_generation_rate = 10  # Сколько денег генерируется
        self.generation_interval = 1000  # Интервал генерации в миллисекундах
        self.last_generation_time = pygame.time.get_ticks()

    def update(self, enemies, current_time, bullets_group):
        """
        Обновляет состояние башни, проверяя, должно ли произойти новое генерирование денег на основе текущего времени.
        Описание:
        enemies (Group): Группа врагов, с которыми взаимодействует башня.
        current_time (int): Текущее время в миллисекундах.
        bullets_group (Group): Группа пуль, выстреленных башней.
        """
        # Генерация денег с заданным интервалом
        if current_time - self.last_generation_time > self.generation_interval:
            self.generate_money()
            self.last_generation_time = current_time

    def generate_money(self):
        """
        Генерирует деньги для игрока, увеличивая его текущую сумму денег.
        """
        self.game.settings.starting_money += self.money_generation_rate
