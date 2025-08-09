# This is an Advanced Galaxy Runner Desktop Kivy/Python App written in Python 3.8
import random
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '600')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle, Ellipse, Rectangle
from kivy.graphics import InstructionGroup
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 8
    V_LINES_SPACING = .4  # percentage' in screen width
    vertical_lines = []

    H_NB_LINES = 15
    H_LINES_SPACING = .1  # percentage' in screen height
    horizontal_lines = []

    SPEED = .8
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 2.0
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    NB_OBSTACLES = 10
    obstacles = []
    obstacles_coordinates = []

    SPEED_LASER = 6.0
    lasers = []

    explosions = []

    shield_active = BooleanProperty(False)
    shield_instruction_group = None

    ship_invincible = BooleanProperty(False)
    ship_invincible_time = NumericProperty(0)

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_has_started = False

    menu_title = StringProperty("G A L A X Y   R U N N E R ")
    menu_button_title = StringProperty("START")
    distance_txt = StringProperty()
    score_txt = StringProperty()
    score = NumericProperty(0)
    lives_txt = StringProperty()
    lives = NumericProperty(4)
    shield_count_txt = StringProperty()
    shield_count = NumericProperty(3)
    last_life_award_score = NumericProperty(0)

    sound_begin = None
    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W:" + str(self.width) + " H:" + str(self.height))
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_obstacles()
        self.init_ship()

        self.shield_instruction_group = InstructionGroup()
        self.shield_graphic = Ellipse()
        self.shield_instruction_group.add(Color(0, 0, 1, 0.5))
        self.shield_instruction_group.add(self.shield_graphic)

        self.reset_game()

        Window.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_key_up=self._on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")
        self.sound_laser = SoundLoader.load("audio/laser.wav")
        self.sound_explosion = SoundLoader.load("audio/boom.wav")
        self.sound_shield = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_laser.volume = .25
        self.sound_explosion.volume = .25
        self.sound_shield.volume = .25
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume =.6

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.tiles_coordinates = []
        self.obstacles_coordinates = []
        self.lasers = []
        self.explosions = []
        self.lives = 4
        self.lives_txt = "LIVES: " + str(self.lives)
        self.shield_count = 3
        self.shield_count_txt = "SHIELDS: " + str(self.shield_count)
        self.score = 0
        self.last_life_award_score = 0
        self.score_txt = "SCORE: " + str(self.score)
        self.distance_txt = "DISTANCE: 0.0 KM"
        self.ship_invincible = False
        self.ship_invincible_time = 0
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux', 'windows', 'macosx'):
            return True
        return False

    def _on_keyboard_down(self, window, key, *args):
        if key == 276:  # left
            self.current_speed_x = self.SPEED_X
        elif key == 275:  # right
            self.current_speed_x = -self.SPEED_X
        elif key == 13:  # enter
            self.on_menu_button_pressed()
        elif key == 32: # spacebar
            self.fire_laser()
        elif key == 273: # up arrow
            self.activate_shield()
        return True

    def _on_keyboard_up(self, window, key, *args):
        self.current_speed_x = 0
        return True

    def on_touch_down(self, touch):
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)

    def transform(self, x, y):
        #return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(self, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y / self.perspective_point_y
        factor_y = pow(factor_y, 4)
        tr_x = self.perspective_point_x + diff_x * factor_y
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y

        return int(tr_x), int(tr_y)

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 2)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def init_obstacles(self):
        with self.canvas:
            Color(1, 0, 0)
            for i in range(0, self.NB_OBSTACLES):
                self.obstacles.append(Ellipse())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 15):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0

        # clean the coordinates that are out of the screen
        # ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        print("foo1")

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

        print("foo2")

        # Generate obstacles
        for i in range(len(self.obstacles_coordinates) - 1, -1, -1):
            if self.obstacles_coordinates[i][1] < self.current_y_loop:
                del self.obstacles_coordinates[i]

        if len(self.obstacles_coordinates) == 0:
            # Place obstacles on the newly generated tiles
            # This is just a simple way to generate some obstacles for now
            for i in range(10, len(self.tiles_coordinates), 20):
                if len(self.obstacles_coordinates) < self.NB_OBSTACLES:
                    self.obstacles_coordinates.append(self.tiles_coordinates[i])

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, len(self.tiles_coordinates)):
            if i >= self.NB_TILES:
                break
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_obstacles(self):
        for i in range(0, len(self.obstacles_coordinates)):
            if i >= self.NB_OBSTACLES:
                break
            obstacle = self.obstacles[i]
            obstacle_coordinates = self.obstacles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(obstacle_coordinates[0], obstacle_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(obstacle_coordinates[0] + 1, obstacle_coordinates[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            # The quad is not a rectangle in perspective, so we approximate
            # by taking the min/max of the transformed coordinates.
            min_x = min(x1, x2, x3, x4)
            max_x = max(x1, x2, x3, x4)
            min_y = min(y1, y2, y3, y4)
            max_y = max(y1, y2, y3, y4)

            screen_width = max_x - min_x
            screen_height = max_y - min_y

            # Make the obstacle a circle with 50% of the smaller dimension of the tile
            diameter = min(screen_width, screen_height) * 0.5
            obstacle.size = (diameter, diameter)
            obstacle.pos = (min_x + (screen_width - diameter) / 2, min_y + (screen_height - diameter) / 2)

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[100, 0, 100])
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update_lasers(self):
        for laser in self.lasers[:]:
            points = laser.points
            points[1] += self.SPEED_LASER
            points[3] += self.SPEED_LASER
            laser.points = points

            if laser.points[1] > self.height:
                self.lasers.remove(laser)
                self.canvas.remove(laser)
                continue

            # Collision detection
            laser_x = laser.points[0]
            laser_y = laser.points[3]
            for i, obstacle_coord in enumerate(self.obstacles_coordinates[:]):
                obstacle_widget = self.obstacles[i]
                if obstacle_widget.size == [0, 0]: # already hit
                    continue

                min_x = obstacle_widget.pos[0]
                max_x = obstacle_widget.pos[0] + obstacle_widget.size[0]
                min_y = obstacle_widget.pos[1]
                max_y = obstacle_widget.pos[1] + obstacle_widget.size[1]

                if min_x < laser_x < max_x and min_y < laser_y < max_y:
                    # Collision
                    self.sound_explosion.play()
                    self.lasers.remove(laser)
                    self.canvas.remove(laser)
                    self.obstacles_coordinates.remove(obstacle_coord)
                    self.on_obstacle_destroyed()

                    # Add explosion
                    explosion = Rectangle(
                        source="images/explosion.jpg",
                        pos=(obstacle_widget.pos[0] - obstacle_widget.size[0] / 2, obstacle_widget.pos[1] - obstacle_widget.size[1] / 2),
                        size=(obstacle_widget.size[0] * 2, obstacle_widget.size[1] * 2)
                    )
                    self.explosions.append(explosion)
                    self.canvas.add(explosion)

                    # "Remove" obstacle by making it size 0
                    obstacle_widget.size = (0, 0)

                    Clock.schedule_once(lambda dt: self.remove_explosion(explosion), 0.5)

                    break

    def update_shield(self):
        if self.shield_active:
            shield_diameter = self.width * self.SHIP_WIDTH * 1.2
            self.shield_graphic.size = (shield_diameter, shield_diameter)
            center_x = self.ship.points[2]
            y_nose = self.ship.points[3]
            y_base = self.ship.points[1]
            center_y = y_base + (y_nose - y_base) / 2
            self.shield_graphic.pos = (center_x - shield_diameter / 2, center_y - shield_diameter / 2)

            for i, obstacle_coord in enumerate(self.obstacles_coordinates[:]):
                obstacle_widget = self.obstacles[i]
                if obstacle_widget.size == [0, 0]:
                    continue
                dx = self.shield_graphic.pos[0] + shield_diameter/2 - (obstacle_widget.pos[0] + obstacle_widget.size[0]/2)
                dy = self.shield_graphic.pos[1] + shield_diameter/2 - (obstacle_widget.pos[1] + obstacle_widget.size[1]/2)
                distance = (dx**2 + dy**2)**0.5
                if distance < shield_diameter/2 + obstacle_widget.size[0]/2:
                    self.obstacles_coordinates.remove(obstacle_coord)
                    self.on_obstacle_destroyed()

                    # Add explosion
                    explosion = Rectangle(
                        source="images/explosion.jpg",
                        pos=(obstacle_widget.pos[0] - obstacle_widget.size[0] / 2, obstacle_widget.pos[1] - obstacle_widget.size[1] / 2),
                        size=(obstacle_widget.size[0] * 2, obstacle_widget.size[1] * 2)
                    )
                    self.explosions.append(explosion)
                    self.canvas.add(explosion)

                    obstacle_widget.size = (0, 0)
                    if self.sound_explosion:
                        self.sound_explosion.play()
                    Clock.schedule_once(lambda dt: self.remove_explosion(explosion), 0.5)

    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_obstacles()
        self.update_lasers()
        self.update_ship()
        self.update_shield()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                distance_in_km = self.current_y_loop / 100.0
                self.distance_txt = f"DISTANCE: {distance_in_km:.2f} KM"
                self.generate_tiles_coordinates()
                print("loop : " + str(self.current_y_loop))

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.state_game_over:
            if self.ship_invincible:
                self.ship_invincible_time -= dt
                if self.ship_invincible_time <= 0:
                    self.ship_invincible = False

            if not self.check_ship_collision() and not self.ship_invincible:
                self.lives -= 1
                self.lives_txt = "LIVES: " + str(self.lives)
                self.ship_invincible = True
                self.ship_invincible_time = 1.5
                self.current_offset_x = 0

                # Add explosion on ship
                ship_center_x = self.ship.points[2]
                ship_center_y = (self.ship.points[1] + self.ship.points[3]) / 2
                explosion_size = self.width * self.SHIP_WIDTH * 1.5
                explosion = Rectangle(
                    source="images/explosion.jpg",
                    pos=(ship_center_x - explosion_size/2, ship_center_y - explosion_size/2),
                    size=(explosion_size, explosion_size)
                )
                self.explosions.append(explosion)
                self.canvas.add(explosion)
                Clock.schedule_once(lambda dt: self.remove_explosion(explosion), 0.5)

                if self.lives == 0:
                    self.trigger_game_over()
                    return
                else:
                    if self.sound_gameover_impact:
                        self.sound_gameover_impact.play()

            for i, obstacle_coord in enumerate(self.obstacles_coordinates[:]):
                if self.check_ship_collision_with_tile(obstacle_coord[0], obstacle_coord[1]):
                    if not self.ship_invincible:
                        self.lives -= 1
                        self.lives_txt = "LIVES: " + str(self.lives)
                        self.ship_invincible = True
                        self.ship_invincible_time = 1.5

                        # Add explosion on ship
                        ship_center_x = self.ship.points[2]
                        ship_center_y = (self.ship.points[1] + self.ship.points[3]) / 2
                        explosion_size = self.width * self.SHIP_WIDTH * 1.5
                        explosion = Rectangle(
                            source="images/explosion.jpg",
                            pos=(ship_center_x - explosion_size/2, ship_center_y - explosion_size/2),
                            size=(explosion_size, explosion_size)
                        )
                        self.explosions.append(explosion)
                        self.canvas.add(explosion)
                        Clock.schedule_once(lambda dt: self.remove_explosion(explosion), 0.5)

                        if self.lives == 0:
                            self.trigger_game_over()
                        else:
                            if self.sound_explosion:
                                self.sound_explosion.play()
                    self.obstacles_coordinates.remove(obstacle_coord)
                    self.obstacles[i].size = (0, 0)
                    break

    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def trigger_game_over(self):
        self.state_game_over = True
        self.menu_title = "G  A  M  E    O  V  E  R"
        self.menu_button_title = "RESTART"
        self.menu_widget.opacity = 1
        self.sound_music1.stop()
        self.sound_gameover_impact.play()
        Clock.schedule_once(self.play_game_over_voice_sound, 3)
        print("GAME OVER")

    def on_obstacle_destroyed(self):
        self.score += 25
        self.score_txt = "SCORE: " + str(self.score)
        if self.score >= self.last_life_award_score + 120:
            self.last_life_award_score += 120
            self.lives += 1
            self.lives_txt = "LIVES: " + str(self.lives)

    def remove_explosion(self, explosion):
        if explosion in self.explosions:
            self.explosions.remove(explosion)
            self.canvas.remove(explosion)

    def fire_laser(self):
        if not self.state_game_over and self.state_game_has_started:
            self.sound_laser.play()
            with self.canvas:
                Color(0, 0, 1)
                x = self.ship.points[2]
                y = self.ship.points[3]
                laser = Line(points=[x, y, x, y + 10], width=2)
                self.lasers.append(laser)

    def activate_shield(self):
        if not self.shield_active and not self.state_game_over and self.shield_count > 0:
            self.shield_active = True
            self.shield_count -= 1
            self.shield_count_txt = "SHIELDS: " + str(self.shield_count)
            if self.sound_shield:
                self.sound_shield.play()
            self.canvas.add(self.shield_instruction_group)
            Clock.schedule_once(self.deactivate_shield, 5)

    def deactivate_shield(self, dt):
        self.shield_active = False
        self.canvas.remove(self.shield_instruction_group)

    def on_menu_button_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass

GalaxyApp().run()

#Final Commit!#