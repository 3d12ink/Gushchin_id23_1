import json
import pygame
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel
import math

def create_default_json():
    data = {
        "sun": {
            "mass": 999,
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


class PlanetarySystem:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Planetary System")

        self.planets = []
        self.sun_position = (400, 400)
        self.orbit_radius = []  #список радиусов планет
        self.speeds = []  #список скоростей планет
        self.densities = []  #список плотностей планет
        self.paused = False

        #список для астероидов
        self.asteroids = []
        #параметры астероидов
        self.asteroid_mass = 10
        self.asteroid_speed = 5
        self.asteroid_direction = (1, 0)  #направление  по X

        self.load_system()

    def load_system(self):
        #данные о системе
        with open("planetary_system.json", "r") as f:
            data = json.load(f)

        self.sun = data["sun"]

        for planet in data["planets"]:#данные о планетах
            self.planets.append(planet["name"])  #имя планеты
            self.densities.append(planet["density"])  #плотность
            self.orbit_radius.append(planet["orbit_radius"])  #радиус
            self.speeds.append(planet["speed"])  #скорость

    def calculate_color(self, density):# функция для вычисления цвета планеты
        max_density = 10.5
        color_value = int(255 * (density / max_density))
        return (color_value, 0, 255 - color_value)

    def update(self):
        # обновление экрана
        self.screen.fill((0, 0, 0))  # очищаем экран черным цветом

        # отображение Солнца
        pygame.draw.circle(self.screen, (255, 255, 0), self.sun_position, 30)

        # отображение планет
        for i in range(len(self.planets)):
            # вычисление текущего угола орбиты планеты
            angle = pygame.time.get_ticks() * self.speeds[i] / 14000
            # вычисление новые координаты планеты
            x = self.sun_position[0] + self.orbit_radius[i] * math.cos(angle)
            y = self.sun_position[1] + self.orbit_radius[i] * math.sin(angle)

            # Вычисление цвет планеты
            planet_color = self.calculate_color(self.densities[i])
            # Отображаем планету
            pygame.draw.circle(self.screen, planet_color, (int(x), int(y)), 10)

        # Отображение астероидов
        for asteroid in self.asteroids:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(asteroid['x']), int(asteroid['y'])), 5)

            # обновление координат астероида
            asteroid['x'] += asteroid['vx']
            asteroid['y'] += asteroid['vy']

            # проверка на столкновение с солнцем
            if math.sqrt((asteroid['x'] - self.sun_position[0]) ** 2 + (asteroid['y'] - self.sun_position[1]) ** 2) < 30:
                #добавляем массы астероид к массе солнцу
                self.sun['mass'] += asteroid['mass']
                self.asteroids.remove(asteroid)  # Удаление астероида

            # Проверка на столкновение с планетами
            for i in range(len(self.planets)):
                # позиция планеты
                planet_pos = (self.sun_position[0] + self.orbit_radius[i] * math.cos(pygame.time.get_ticks() * self.speeds[i] / 1400),
                              self.sun_position[1] + self.orbit_radius[i] * math.sin(pygame.time.get_ticks() * self.speeds[i] / 1400))
                # Проверка, столкнулся ли астероид с планетой
                if math.sqrt((asteroid['x'] - planet_pos[0]) ** 2 + (asteroid['y'] - planet_pos[1]) ** 2) < 10:
                    # Увеличиваем плотность планеты в зависимости от массы астероида
                    self.densities[i] += asteroid['mass'] / 10
                    self.asteroids.remove(asteroid)  # Удаляем астероид

        # Обновление экрана
        pygame.display.flip()

    def run(self):
        # Основной цикл
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()  # Завершение
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левый клик мыши (создание астероида)
                        self.create_asteroid(event.pos)
                    elif event.button == 3:  # Правая кнопка мыши (выбор направления)
                        self.start_direction(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:  # Завершение выбора направления
                        self.end_direction(event.pos)

            if not self.paused:
                self.update()  # Обновляем симуляцию
            clock.tick(60)

    def create_asteroid(self, position):
        #Функция для создания астероида в заданной позиции
        asteroid = {
            'x': position[0],
            'y': position[1],
            'vx': self.asteroid_direction[0] * self.asteroid_speed,  # Скорость по оси X
            'vy': self.asteroid_direction[1] * self.asteroid_speed,  # Скорость по оси Y
            'mass': self.asteroid_mass  #Масса астероида
        }
        self.asteroids.append(asteroid)  #Добавляем астероид в список

    def start_direction(self, position):
        #Запоминаем начальную точку для вычисления направления
        self.asteroid_start_pos = position

    def end_direction(self, position):
        # Вычисляем направление астероида
        dx = position[0] - self.asteroid_start_pos[0]
        dy = position[1] - self.asteroid_start_pos[1]
        length = math.sqrt(dx**2 + dy**2)  #длина вектора
        self.asteroid_direction = (dx / length, dy / length)  # Нормализуем вектор направления

    def toggle_pause(self):
        #переключение состояния паузы
        self.paused = not self.paused


#интерфейс
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Planetary System Controls")

layout = QVBoxLayout()

# кнопка для паузы
btn_pause = QPushButton("Pause / Resume")
layout.addWidget(btn_pause)

#масса астероида (слайдер)
label_mass = QLabel("Asteroid Mass")
layout.addWidget(label_mass)
mass_slider = QSlider(Qt.Horizontal)
mass_slider.setRange(1, 10)
mass_slider.setValue(1)  #начальное значение массы
layout.addWidget(mass_slider)

# Скорость астероида
label_speed = QLabel("Asteroid Speed")
layout.addWidget(label_speed)
speed_slider = QSlider(Qt.Horizontal)
speed_slider.setRange(1, 20)
speed_slider.setValue(5)  #начальное значение скорости
layout.addWidget(speed_slider)

window.setLayout(layout)

window.show()

planetary_system = PlanetarySystem()  #создаем окно солнечной системы

#обработчик для кнопки паузы
def toggle_pause():
    planetary_system.toggle_pause()

#обработчик для изменения массы и скорости астероида
def update_asteroid_properties():
    planetary_system.asteroid_mass = mass_slider.value()  #обновление массы
    planetary_system.asteroid_speed = speed_slider.value()  #обновление скорости

#подключение обработчики к событиям
btn_pause.clicked.connect(toggle_pause)
mass_slider.valueChanged.connect(update_asteroid_properties)
speed_slider.valueChanged.connect(update_asteroid_properties)

planetary_system.run()
