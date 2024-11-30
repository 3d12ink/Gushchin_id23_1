import json
import pygame
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QSpinBox
import math

def create_default_json():
    data = {
        "sun": {
            "mass": 999,  # масса солнца в кг
        },
        "planets": [
            {"name": "planet_1", "density": 5.5, "orbit_radius": 50, "speed": 3.123},
            {"name": "planet_2", "density": 5, "orbit_radius": 80, "speed": 4.312},
            {"name": "planet_3", "density": 4, "orbit_radius": 110, "speed": 5.321},
            {"name": "planet_4", "density": 3.5, "orbit_radius": 140, "speed": 6.123},
            {"name": "planet_5", "density": 3, "orbit_radius": 170, "speed": 7.912},
            {"name": "planet_6", "density": 2, "orbit_radius": 200, "speed": 8.129},
            {"name": "planet_7", "density": 1, "orbit_radius": 230, "speed": 9.192}
        ]
    }

    with open("planetary_system.json", "w") as f:
        json.dump(data, f, indent=4)


create_default_json()

class Asteroid:
    def __init__(self, x, y, direction, speed, mass):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.mass = mass
        self.color = (255, 0, 0)  # астероид всегда красный

    def move(self):
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

    def check_collision(self, sun_position, sun_radius, planets):
        # Проверка на столкновение с Солнцем
        distance_to_sun = math.sqrt((self.x - sun_position[0]) ** 2 + (self.y - sun_position[1]) ** 2)
        if distance_to_sun < sun_radius:
            return "sun"

        # Проверка на столкновение с планетами
        for planet in planets:
            distance_to_planet = math.sqrt((self.x - planet['position'][0]) ** 2 + (self.y - planet['position'][1]) ** 2)
            if distance_to_planet < planet['radius']:
                return planet['name']
        return None

class PlanetarySystem:
    def __init__(self):
        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Planetary System")

        self.planets = []
        self.sun_position = (400, 400)
        self.sun_radius = 30
        self.asteroids = []
        self.sun_mass = 999
        self.orbit_radius = []
        self.speeds = []
        self.densities = []
        self.paused = False
        self.mouse_drag_start = None
        self.planet_radius = 10  # Радиус планеты для проверки столкновений

        self.load_system()

    def load_system(self):
        # Загружаем данные из JSON
        with open("planetary_system.json", "r") as f:
            data = json.load(f)

        self.sun = data["sun"]

        self.planets = []
        for planet in data["planets"]:
            self.planets.append({
                'name': planet['name'],
                'density': planet['density'],
                'orbit_radius': planet['orbit_radius'],
                'speed': planet['speed'],
                'position': (self.sun_position[0] + planet['orbit_radius'], self.sun_position[1]),  # Начальная позиция планеты
                'radius': self.planet_radius
            })

    def calculate_color(self, density):
        # Цвет планеты зависит от плотности
        max_density = 5.5  # Максимальная плотность (для нормализации)
        color_value = int(255 * (density / max_density))
        return (color_value, 0, 255 - color_value)

    def update(self):
        self.screen.fill((0, 0, 0))  # Очистить экран

        def calculate_color(self, density):
            # Цвет планеты зависит от плотности
            max_density = 5.5  # Максимальная плотность (для нормализации)
            color_value = int(255 * (density / max_density))
            return (color_value, 0, 255 - color_value)

        # Отображение солнца
        pygame.draw.circle(self.screen, (255, 255, 0), self.sun_position, self.sun_radius)

        for i, planet in enumerate(self.planets):
            angle = pygame.time.get_ticks() * planet['speed'] / 1400
            x = self.sun_position[0] + planet['orbit_radius'] * math.cos(angle)
            y = self.sun_position[1] + planet['orbit_radius'] * math.sin(angle)

            planet['position'] = (x, y)  # Обновляем позицию планеты
            planet_color = self.calculate_color(planet['density'])
            pygame.draw.circle(self.screen, planet_color, (int(x), int(y)), planet['radius'])

        # Обновление астероидов
        for asteroid in self.asteroids:
            asteroid.move()
            pygame.draw.circle(self.screen, asteroid.color, (int(asteroid.x), int(asteroid.y)), 5)

            # Проверка на столкновение с планетами или Солнцем
            collision_result = asteroid.check_collision(self.sun_position, self.sun_radius, self.planets)
            if collision_result:
                if collision_result == "sun":
                    self.sun_mass += asteroid.mass
                else:
                    planet = next(p for p in self.planets if p['name'] == collision_result)
                    planet['density'] += asteroid.mass  # Увеличиваем плотность планеты
                self.asteroids.remove(asteroid)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_drag_start = event.pos  # Начало зажатия

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.mouse_drag_start:
                            end_pos = event.pos
                            direction = math.atan2(end_pos[1] - self.mouse_drag_start[1], end_pos[0] - self.mouse_drag_start[0])
                            # Создаем астероид
                            asteroid = Asteroid(self.mouse_drag_start[0], self.mouse_drag_start[1], direction, 5, 10)
                            self.asteroids.append(asteroid)
                            self.mouse_drag_start = None

            if not self.paused:
                self.update()
            clock.tick(60)

    def toggle_pause(self):
        self.paused = not self.paused


# Запуск программы
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Planetary System Controls")

layout = QVBoxLayout()

btn_pause = QPushButton("Pause / Resume")
layout.addWidget(btn_pause)

# Слайдер для массы астероида
mass_slider_label = QLabel("Asteroid Mass:")
mass_slider = QSlider(Qt.Horizontal)
mass_slider.setMinimum(1)
mass_slider.setMaximum(100)
mass_slider.setValue(10)
layout.addWidget(mass_slider_label)
layout.addWidget(mass_slider)

# Слайдер для скорости астероида
speed_slider_label = QLabel("Asteroid Speed:")
speed_slider = QSlider(Qt.Horizontal)
speed_slider.setMinimum(1)
speed_slider.setMaximum(20)
speed_slider.setValue(5)
layout.addWidget(speed_slider_label)
layout.addWidget(speed_slider)

window.setLayout(layout)

window.show()

planetary_system = PlanetarySystem()


# Обработчик для кнопки паузы
def toggle_pause():
    planetary_system.toggle_pause()


btn_pause.clicked.connect(toggle_pause)

planetary_system.run()
