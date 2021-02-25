"""

Tile Map Editor/Creator

Use to create tilemaps from preveously created artwork of any tilesize (not recommended for smaller than 9x9).
Very simple 2 layer program with some basic paint functions.
Functions in brackets have not been included yet.

Python 3.9 program by AanasSchaf

features:

- Menu Options:
    - New map, with specifications
    - Load a previously created map with its specifications
    - Save map as info.txt and image.png
    (- Create a random map)
    - Autofill function to complete maps (only works if the requirements of the tiles have been fulfilled and the map is not filled with other tiles)
    - 2 layers, background and foreground that can be adapted individually or togehter
    (- Configuration menu for defining options)
    - Exit button

- Tool Options:
    - Pen tool for regular drawing
    - Eraser tool for removing tiles
    - Line tool, to be conbined with Pen or eraser tool for drawing or removing a line
    - Empty rectangle tool, to be conbined with Pen or eraser tool for drawing or removing an empty rectangle
    - Filled rectangle tool, to be conbined with Pen or eraser tool for drawing or removing a filled rectangle
    - Empty cirlce tool, to be conbined with Pen or eraser tool for drawing or removing an empty circle
    - Filled circle tool, to be conbined with Pen or eraser tool for drawing or removing a filled circle
    - Sphere tool, to be conbined with Pen or eraser tool for drawing or removing a whacky thing
    - Fill tool, to be conbined with Pen or eraser tool for drawing or removing tiles of the same type in an area
    - Grid tool to visualize (or not) a grid, (currently only works with included grid art)
    - Mini map tool to fit the map to the screen

-Tile Optiions:
    - Tilesets of any size (Tilesize as well as amount of tiles) can be used if saved correctly
        - sizes/#tilesize/Tile_Sets/#tilesetname/*.png
        - only individual tiles will work, the program can not split an image into usable tiles
    - personal artwork may not work with the autofill function if the format of the images does not match the intended system
    - The tiles of the selected folder are shown in groups of 18 as well as the first tiles of all folders

- Interaction: (should be adapted with the config option)
    - general interaction is with the left mousebutton
    - scrolling is done with wasd or arrow kes, right mousebutton drag or right mousebutton scrollbar use
    - hotkeys:
        - Fullscreen: f
        - Tileselection: 1,2,...,0, shift+1, ... shift+8
        - Exit: Escape


"""

import pygame
import os
import glob
from pathlib import Path
import math

# import itertools
# import time

white = (255, 255, 255)
gray = (128, 128, 128)
black = (0, 0, 0)


class Start:
    def __init__(self, screen_width=1280, screen_height=720, map_tiles_x=50, map_tiles_y=50):
        pygame.init()

        self.run = True

        self.map_x = map_tiles_x
        self.map_y = map_tiles_y
        self.SCREEN_X = screen_width
        self.SCREEN_Y = screen_height
        self.clock = pygame.time.Clock()
        self.fullscreen = True
        self.screen = pygame.display.set_mode((self.SCREEN_X, self.SCREEN_Y))  # , pygame.FULLSCREEN)
        self.tile_size = 32
        self.grid_img = pygame.image.load(os.path.join("images/sizes", str(self.tile_size), "grid.png"))
        self.Tile_path = os.path.join("images/sizes", str(self.tile_size), "TileSets")
        self.tool_path = "images/buttons"
        self.map_save_path = "Saves/Maps"
        self.tile_key_dict = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
                              pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8, pygame.K_0: 9}

        # map screen
        self.screen_rect = pygame.Rect(self.SCREEN_X // 8, 64, self.SCREEN_X * 6 // 8, self.SCREEN_Y - 64)

        # scroll bar rects
        self.sb_width, self.sb_length = 16, 64

        self.x_move_rect_top = pygame.Rect(0, 0, self.sb_length, self.sb_width)
        self.x_move_rect_top.center = (self.SCREEN_X // 2, 64 + self.sb_width // 2)
        self.y_move_rect_left = pygame.Rect(self.SCREEN_X // 8, self.screen_rect.height // 2 + 64, self.sb_width,
                                            self.sb_length)

        self.x_move_rect_bottom = pygame.Rect(0, 0, self.sb_length, self.sb_width)
        self.x_move_rect_bottom.center = (self.SCREEN_X // 2, self.SCREEN_Y - self.sb_width // 2)
        self.y_move_rect_right = pygame.Rect(self.SCREEN_X // 8 * 7 - 16, self.screen_rect.height // 2 + 64,
                                             self.sb_width, self.sb_length)

        # toolmenu info
        self.tools = [pygame.image.load(filename).convert() for filename in
                      glob.glob(os.path.join(self.tool_path, "*.png"))]

        # load tile info
        self.tile_set_dict = {}
        self.tile_set_counter = {}
        self.tile_set_names = []
        self.tile_sets = []
        self.empty_list = []

        # go through folders ans subfolders in a path
        # root = main path, dir = subfolder, file = file
        for root, dirs, files in os.walk(self.Tile_path):
            for folder in dirs:
                self.tile_set_names.append(folder)
            for name in files:
                path = os.path.join(root, name)
                self.tile_sets.append(path)

        # load sizes into tile dictionary to call with the specified name :)
        # add the amount of empty lists to the dictionary to replace with the actual list
        for i in range(len(self.tile_set_names)):
            self.empty_list.append([])
            self.tile_set_dict = dict(zip(self.tile_set_names, self.empty_list))
            a = 0
            for item in self.tile_sets:
                if self.tile_set_names[i] in item:
                    a += 1
                    self.tile_set_dict[self.tile_set_names[i]].append(pygame.image.load(item))
                    self.tile_set_counter.update({self.tile_set_names[i]: a})

        # print(self.tile_set_counter)

        # state for menu changes
        self.state = "map"
        # version for save file name generation
        self.version = 0

        # text input
        self.forbidden_characters = [":", "\"", "<", ">", "\\", "/", "|", "?", "*"]
        self.input_action = False
        self.new_text = "40x40"
        self.save_text = str(self.tile_size) + "_" + str(self.map_x) + "x" + str(self.map_y) + "_"
        self.box_color_inactive = (50, 100, 150)
        self.box_color_active = black
        self.box_color = self.box_color_inactive

    # for loading saved and new maps of different sizes
    def reset_values(self):
        # map menu
        map_menu_left.tile_rect_dict = {}
        map_menu_left.tile_rect_list = []
        map_menu_left.tile_rect_keys = []
        map_menu_left.map_menu_left_list = []

        map_menu_left.tile_set_index = 0
        map_menu_left.tile_index = 0

        # map
        map1.map_tiles_interaction = []
        map1.map_tile_value = []
        map1.map_tile_index = []
        map1.map_tile_surfaces = []
        map1.interact = ["key", 0, 0]

        map1.map_dict = {}
        map1.bg_dict = {}

        # load tile info
        self.tile_set_dict = {}
        self.tile_set_counter = {}
        self.tile_set_names = []
        self.tile_sets = []
        self.empty_list = []

    # for renewing important values after loading info
    def reload_values(self):

        # images path update according to tilesize
        self.grid_img = pygame.image.load(os.path.join("images/sizes", str(self.tile_size), "grid.png"))
        self.Tile_path = os.path.join("images/sizes", str(self.tile_size), "TileSets")

        # create map surface
        map1.overlay_org = pygame.Surface(
            ((self.map_x + 2) * self.tile_size, (self.map_y + 2) * self.tile_size)).convert()
        map1.overlay_org.fill(map1.bg)
        map1.overlay_rect = map1.overlay_org.get_rect()
        map1.overlay_rect.center = self.screen_rect.center
        map1.overlay = map1.overlay_org

        # map interaction info
        map1.cursor_rect = pygame.Rect(0, 0, self.tile_size, self.tile_size)
        map1.menu_width = self.SCREEN_X // 8
        map1.scroll_dv_left = map1.menu_width
        map1.scroll_dv_right = - map1.menu_width + self.SCREEN_X - map1.overlay_rect.width
        map1.scroll_dv_top = 64
        map1.scroll_dv_bottom = self.SCREEN_Y - map1.overlay_rect.height
        map1.scroll_dv_x = map1.overlay_rect.width // 2 - self.screen_rect.width // 2
        map1.scroll_dv_y = map1.overlay_rect.height // 2 - self.screen_rect.height // 2
        map1.scroll_v = [0, 0]
        map1.scroll_dv = [0, 0]

        # go through folders ans subfolders in a path
        # root = main path, dir = subfolder, file = file
        for root, dirs, files in os.walk(self.Tile_path):
            for folder in dirs:
                self.tile_set_names.append(folder)
            for name in files:
                path = os.path.join(root, name)
                self.tile_sets.append(path)

        # load sizes into tile dictionary to call with the specified name :)
        # add the amount of empty lists to the dictionary to replace with the actual list
        for i in range(len(self.tile_set_names)):
            self.empty_list.append([])
            self.tile_set_dict = dict(zip(self.tile_set_names, self.empty_list))
            a = 0
            for item in self.tile_sets:
                if self.tile_set_names[i] in item:
                    a += 1
                    self.tile_set_dict[self.tile_set_names[i]].append(pygame.image.load(item))
                    self.tile_set_counter.update({self.tile_set_names[i]: a})

        map_menu_left.menu_index = 0
        map_menu_left.menu_index_top = 0
        map_menu_left.menu_index_bottom = 0
        map_menu_left.index_top, map_menu_left.index_bottom = 0, 0
        map_menu_left.number_top = len(self.tile_set_dict.get(self.tile_set_names[0])) - 1
        map_menu_left.number_bottom = len(self.tile_set_names) - 1
        map_menu_left.selected_rect = None

        # map tool menu stuff

        map_menu_top.pen_tool = True
        map_menu_top.eraser_tool = False
        map_menu_top.line_tool = False
        map_menu_top.empty_rect_tool = False
        map_menu_top.full_rect_tool = False
        map_menu_top.empty_circle_tool = False
        map_menu_top.full_circle_tool = False
        map_menu_top.sphere_tool = False
        map_menu_top.fill_tool = False
        map_menu_top.mini_map_tool = False

    def menu_interaction_states(self):

        # menu interaction states
        # new
        if self.state == map_menu.options_list[0].lower():
            map1.cursor_change = False
            self.run = False
            map_menu.new_loop()

        # load
        elif self.state == map_menu.options_list[1].lower():
            map1.cursor_change = False
            self.run = False
            map_menu.load_loop()

        # save
        elif self.state == map_menu.options_list[2].lower():
            map1.cursor_change = False
            self.run = False
            map_menu.save_loop()

        # random
        elif self.state == map_menu.options_list[3].lower():
            print("random")

        # autofill
        elif self.state == map_menu.options_list[4].lower():
            if map1.autofill:
                map1.autofill = False
                map_menu.auto_counter = 0
            else:
                map1.autofill = True

        # background
        elif self.state == map_menu.options_list[5].lower():
            if map1.background:
                map1.background = False
            else:
                map1.background = True
                map1.background_visible = True

        # foreground
        elif self.state == map_menu.options_list[6].lower():
            if map1.foreground:
                map1.foreground = False
            else:
                map1.foreground = True
                map1.foreground_visible = True

        # config
        elif self.state == map_menu.options_list[7].lower():
            print("config")

        # exit
        elif self.state == map_menu.options_list[8].lower():
            self.run = False


# map menu: initialize before Map, for there is info in here for the map class
class MapMenu:
    def __init__(self, menu_width, menu_height, pos_x=0, bg_color=(50, 100, 150), bg_image=None):

        # save and load info
        if not bg_image:
            self.bg = bg_color
        else:
            self.bg = bg_image

        # set up graphics menu
        self.font = pygame.font.SysFont(pygame.font.get_fonts()[-6], 24)
        self.x = menu_width
        self.y = menu_height
        self.SURF = pygame.Surface((self.x, self.y)).convert()
        self.SURF.fill(self.bg)
        self.SURF_rect = self.SURF.get_rect()
        self.SURF_rect.x = pos_x

        # set up menu lists
        self.map_menu_left_list = []
        self.menu_grid_list = []
        self.options_list = ["New", "Load", "Save", "Random", "Autofill", "Background", "Foreground", "Config",
                             "Exit"]
        self.change_rect_list = []

        self.tile_rect_dict = {}
        self.tile_rect_list = []
        self.tile_rect_keys = []

        self.tile_set_index = 0
        self.tile_index = 0

        self.menu_tile_size = 32
        self.tile_menu_grid = pygame.image.load(os.path.join("images/sizes", str(self.menu_tile_size), "grid.png"))

        # menu changing
        self.menu_index = 0
        self.menu_index_top = 0
        self.menu_index_bottom = 0
        self.index_top, self.index_bottom = 0, 0
        self.number_top = len(start.tile_set_dict.get(start.tile_set_names[0])) - 1
        self.number_bottom = len(start.tile_set_names) - 1
        self.menu_state = start.tile_set_names[self.menu_index]

        self.selected_rect = None
        self.selected_pen_rect = None
        self.grid_rect = None
        self.mini_map_rect = None
        # print(self.menu_state)

        # right menu functions
        # save
        self.directories = os.listdir(start.map_save_path)
        self.menu_interaction_rect = pygame.Rect(0, 0, self.x * 8, self.y)

        # load
        self.menu_buttons = []
        self.load_files = []

        # new
        self.new_menu_options = ["Tile Size", "Map Size (Width x Height)", "Create"]
        self.tile_size_list = os.listdir("images/sizes")
        self.tile_size_select = 1

        # autofill
        self.auto_counter = 0

        # tool menu initialization
        self.pen_tool = True
        self.eraser_tool = False
        self.line_tool = False
        self.empty_rect_tool = False
        self.full_rect_tool = False
        self.empty_circle_tool = False
        self.full_circle_tool = False
        self.sphere_tool = False
        self.fill_tool = False
        self.mini_map_tool = False

        # tool menu objects
        self.start = [0, 0]
        self.end = [0, 0]
        self.rectangle = pygame.Rect(self.start, self.end)
        self.radius = 0

    # tile menu
    def menu_grid_left(self):
        pygame.draw.rect(self.SURF, white, [0, 0, self.SURF.get_width(), self.SURF.get_height() // 2], 1)
        pygame.draw.rect(self.SURF, white,
                         [0, self.SURF.get_height() // 2, self.SURF.get_width(), self.SURF.get_height() // 2], 1)

        spacing = self.menu_tile_size // 2
        columns = self.x // (self.menu_tile_size + spacing)
        rows = (self.y // 2 - self.menu_tile_size * 2) // (self.menu_tile_size + spacing)

        for j in range(2):
            x_pos, y_pos, i = spacing, self.menu_tile_size, 0
            for i in range(columns * rows):
                # here
                rect = pygame.Rect(0, 0, self.menu_tile_size, self.menu_tile_size)
                rect.x = x_pos
                rect.y = y_pos + j * self.SURF.get_height() // 2
                # subsurface = self.SURF.subsurface(rect)
                # # subsurface.blit(start.grid_img, [0, 0])
                x_pos += self.menu_tile_size + spacing
                if x_pos >= self.SURF.get_width() // 5 * 4:
                    x_pos = spacing
                    y_pos += self.menu_tile_size + spacing

                self.menu_grid_list.append([rect, [j, i]])

        for i in range(2):
            for j in range(2):
                change_rect = pygame.Rect(int(self.SURF.get_width() // 5 * 3) * i,
                                          self.SURF.get_height() // 2 * (j + 1) - 32,
                                          int(self.SURF.get_width() // 5 * 2), 32)
                pygame.draw.rect(self.SURF, white, change_rect, 1)

                self.change_rect_list.append(change_rect)

    def define_menu_grid_left(self):
        # tile selection
        self.SURF.fill(self.bg)
        for rect in self.menu_grid_list:
            if rect[1][0] == 0:
                self.index_top = int(rect[1][1] + self.menu_index_top * len(
                    self.menu_grid_list) / 2)

                subsurface = self.SURF.subsurface(rect[0])
                subsurface.fill(self.bg)
                if self.number_top >= self.index_top >= 0:
                    subsurface.blit(start.tile_set_dict.get(
                        start.tile_set_names[self.tile_set_index])[self.index_top], [0, 0])
                pygame.draw.rect(self.SURF, black, rect[0], 1)

            # tileset selection
            elif rect[1][0] == 1:
                self.index_bottom = int(rect[1][1] + self.menu_index_bottom * len(
                    map_menu_left.menu_grid_list) / 2)

                subsurface = self.SURF.subsurface(rect[0])
                subsurface.fill(self.bg)
                if self.number_bottom >= self.index_bottom >= 0:
                    subsurface.blit(start.tile_set_dict.get(start.tile_set_names[self.index_bottom])[0], [0, 0])
                pygame.draw.rect(self.SURF, black, rect[0], 1)

        if self.selected_rect:
            pygame.draw.rect(self.SURF, white, self.selected_rect, 1)

        # change menu
        arrows_white = [self.font.render("<<<", True, white),
                        self.font.render(">>>", True, white)]
        arrows_grey = [self.font.render("<<<", True, gray),
                       self.font.render(">>>", True, gray)]

        for rect in self.change_rect_list:
            arrow_rect = arrows_white[0].get_rect(center=rect.center)
            subsurface = self.SURF.subsurface(arrow_rect)
            subsurface.fill(self.bg)

            if self.change_rect_list.index(rect) == 0:
                if 0 < self.menu_index_top:
                    pygame.draw.rect(self.SURF, white, rect, 1)
                    subsurface.blit(arrows_white[0], [0, 0])
                else:
                    pygame.draw.rect(self.SURF, gray, rect, 1)
                    subsurface.blit(arrows_grey[0], [0, 0])

            elif self.change_rect_list.index(rect) == 1:
                if 0 < self.menu_index_bottom:
                    pygame.draw.rect(self.SURF, white, rect, 1)
                    subsurface.blit(arrows_white[0], [0, 0])
                else:
                    pygame.draw.rect(self.SURF, gray, rect, 1)
                    subsurface.blit(arrows_grey[0], [0, 0])
            elif self.change_rect_list.index(rect) == 2:
                if self.number_top > self.index_top:
                    pygame.draw.rect(self.SURF, white, rect, 1)
                    subsurface.blit(arrows_white[1], [0, 0])
                else:
                    pygame.draw.rect(self.SURF, gray, rect, 1)
                    subsurface.blit(arrows_grey[1], [0, 0])
            else:
                if self.number_bottom > self.index_bottom:
                    pygame.draw.rect(self.SURF, white, rect, 1)
                    subsurface.blit(arrows_white[1], [0, 0])
                else:
                    pygame.draw.rect(self.SURF, gray, rect, 1)
                    subsurface.blit(arrows_grey[1], [0, 0])

        pygame.draw.rect(self.SURF, white, self.SURF_rect, 1)
        pygame.draw.line(self.SURF, white, (0, self.SURF_rect.height // 2),
                         (self.SURF_rect.width, self.SURF_rect.height // 2), 1)

    def tile_menu_interaction(self, event):

        if self.SURF_rect.collidepoint(event.pos):
            for rect in self.menu_grid_list:
                if rect[0].collidepoint(event.pos):
                    if map_menu_top.menu_grid_list.index(map_menu_top.selected_pen_rect) == 1:
                        map_menu_top.selected_pen_rect = map_menu_top.menu_grid_list[0]
                    if map_menu_top.menu_grid_list.index(map_menu_top.selected_rect) == 1:
                        map_menu_top.selected_rect = map_menu_top.menu_grid_list[0]

                    if rect[1][0] == 0:
                        a = int(rect[1][1] + self.menu_index_top * len(
                            self.menu_grid_list) / 2)
                        if self.number_top >= a:

                            # show selected tile
                            self.selected_rect = rect[0]
                            map1.interact = [start.tile_set_names[self.tile_set_index],
                                             a, 0]
                            map1.rotation = 0
                            if map_menu_top.menu_grid_list.index(map_menu_top.selected_pen_rect) == 0:
                                map1.cursor_change = True
                            if map1.interact[0] == "key":
                                map1.interact = [start.tile_set_names[0], a, 0]

                            print(map1.interact)
                    if rect[1][0] == 1:
                        if self.number_bottom >= int(rect[1][1] +
                                                     self.menu_index_bottom * len(self.menu_grid_list) / 2):
                            # choose top menu tileset
                            self.tile_set_index = int(
                                rect[1][1] + self.menu_index_bottom * len(self.menu_grid_list) / 2)

                            self.number_top = len(
                                start.tile_set_dict.get(start.tile_set_names[self.tile_set_index])) - 1
                            self.menu_index_top = 0
                            # show selected tile
                            self.selected_rect = self.menu_grid_list[0][0]

                            map1.rotation = 0
                            map1.interact = [start.tile_set_names[self.tile_set_index],
                                             0, 0]

                            print(map1.interact)
                            print(self.tile_set_index, self.number_bottom)

                            # change menu interaction window
                            for c_rect in self.change_rect_list:
                                if c_rect.collidepoint(event.pos):
                                    if self.change_rect_list.index(c_rect) == 0:
                                        if 0 < self.menu_index_top:
                                            self.menu_index_top -= 1
                                            self.selected_rect = None
                                        else:
                                            pass
                                    elif self.change_rect_list.index(c_rect) == 2:
                                        if self.number_top > self.index_top:
                                            self.menu_index_top += 1
                                            self.selected_rect = None
                                        else:
                                            pass
                                    elif self.change_rect_list.index(c_rect) == 1:
                                        if 0 < self.menu_index_bottom:
                                            self.menu_index_bottom -= 1
                                            self.selected_rect = None
                                        else:
                                            pass
                                    elif self.change_rect_list.index(c_rect) == 3:
                                        if self.number_bottom > self.index_bottom:
                                            self.menu_index_bottom += 1
                                            self.selected_rect = None
                                        else:
                                            pass

                                    print("side", self.menu_index_top, self.menu_index_bottom)

    # options menu
    def menu_grid_right(self):
        pygame.draw.rect(self.SURF, white, [0, 0, self.SURF.get_width(), self.SURF.get_height()], 1)

        spacing = 32 // 2
        x_pos, y_pos, i, index = spacing, 64, 0, 0
        for _ in self.options_list:
            rect = pygame.Rect(
                (x_pos, i * (y_pos + spacing) + spacing // 2, int(self.SURF.get_width() // 5 * 4), 64))
            check_rect = pygame.Rect(rect.right - 16, rect.bottom - 16, 16, 16)
            self.menu_grid_list.append([i, rect, check_rect])
            i += 1

    def define_menu_grid_right(self):
        for rect in self.menu_grid_list:
            i = self.menu_grid_list.index(rect)
            text = self.font.render(self.options_list[i], True, white)
            text_rect = text.get_rect(center=rect[1].center)
            subsurface_main = self.SURF.subsurface(text_rect)
            subsurface_main.fill(self.bg)
            subsurface_main.blit(text, [0, 0])

            pygame.draw.rect(self.SURF, white, rect[1], 1)

            # create checkboxes for recognition of what is turned on or not
            # this shows visibility and workability
            subsurface_check = self.SURF.subsurface(rect[2])

            if map1.background and self.options_list[i].lower() == "background":
                pygame.draw.rect(self.SURF, (0, 255, 0), rect[1], 1)
                if map1.background_visible:
                    subsurface_check.fill((0, 255, 0))
                else:
                    subsurface_check.fill(self.bg)
                    pygame.draw.rect(self.SURF, (255, 0, 0), rect[1], 1)
                    pygame.draw.rect(self.SURF, white, rect[2], 1)
            elif not map1.background and self.options_list[i].lower() == "background":
                pygame.draw.rect(self.SURF, (255, 0, 0), rect[1], 1)
                if map1.background_visible:
                    subsurface_check.fill((0, 255, 0))
                else:
                    subsurface_check.fill(self.bg)
                    pygame.draw.rect(self.SURF, (255, 0, 0), rect[1], 1)
                    pygame.draw.rect(self.SURF, white, rect[2], 1)

            elif map1.foreground and self.options_list[i].lower() == "foreground":
                pygame.draw.rect(self.SURF, (0, 255, 0), rect[1], 1)
                if map1.foreground_visible:
                    subsurface_check.fill((0, 255, 0))
                else:
                    subsurface_check.fill(self.bg)
                    pygame.draw.rect(self.SURF, (255, 0, 0), rect[1], 1)
                    pygame.draw.rect(self.SURF, white, rect[2], 1)
            elif not map1.foreground and self.options_list[i].lower() == "foreground":
                pygame.draw.rect(self.SURF, (255, 0, 0), rect[1], 1)
                if map1.foreground_visible:
                    subsurface_check.fill((0, 255, 0))
                else:
                    subsurface_check.fill(self.bg)
                    pygame.draw.rect(self.SURF, (255, 0, 0), rect[1], 1)
                    pygame.draw.rect(self.SURF, white, rect[2], 1)

            elif self.options_list[i].lower() == "autofill":
                pygame.draw.rect(self.SURF, white, rect[2], 1)

    def options_menu_interaction(self, event):
        if self.SURF_rect.collidepoint(event.pos):
            position = tuple(
                map(lambda i, j: i - j, pygame.mouse.get_pos(), (start.SCREEN_X // 8 * 7, 0)))
            for rect in self.menu_grid_list:
                if rect[2].collidepoint(position):
                    # visibility of fore and background
                    if rect[0] == 5:
                        if map1.background_visible:
                            map1.background_visible = False
                        else:
                            map1.background_visible = True
                    if rect[0] == 6:
                        if map1.foreground_visible:
                            map1.foreground_visible = False
                        else:
                            map1.foreground_visible = True

                elif rect[1].collidepoint(position):
                    start.state = self.options_list[rect[0]].lower()

                    if rect[0] == 2:
                        map1.grid = False

    # tool menu
    def menu_grid_top(self):
        pygame.draw.rect(self.SURF, white, [0, 0, self.SURF.get_width(), self.SURF.get_height()], 1)
        x_pos, y_pos, i, index = self.y, 0, 0, 0
        for i in range(start.SCREEN_X // 8 * 6 // self.y - 2):
            rect = pygame.Rect(((i + 1) * x_pos, y_pos, self.y, self.y))
            pygame.draw.rect(self.SURF, white, rect, 1)
            self.menu_grid_list.append(rect)
        for i in range(2):
            change_rect = pygame.Rect((i * (start.SCREEN_X // 8 * 6 - x_pos), y_pos, self.y, self.y))
            pygame.draw.rect(self.SURF, black, change_rect, 1)
            self.change_rect_list.append(change_rect)

    def define_menu_grid_top(self):
        # tool selection
        self.number_top = len(start.tools) - 1
        for rect in self.menu_grid_list:
            self.index_top = self.menu_grid_list.index(rect)

            subsurface = self.SURF.subsurface(rect)
            subsurface.fill(self.bg)
            if map1.cursor_change and self.index_top == 0:
                surface = pygame.transform.rotozoom(map1.cursor_image, map1.interact[2], 64 // start.tile_size)
                subsurface.blit(surface, [0, 0])

            if self.number_top >= self.index_top >= 0:
                subsurface.blit(start.tools[self.index_top], [0, 0])

            pygame.draw.rect(self.SURF, black, rect, 2)

        if not self.selected_rect:
            self.selected_rect = self.menu_grid_list[0]
            self.selected_pen_rect = self.menu_grid_list[0]

        if map1.grid:
            self.grid_rect = self.menu_grid_list[9]
            pygame.draw.rect(self.SURF, white, self.grid_rect, 3)

        if self.mini_map_tool:
            self.mini_map_rect = self.menu_grid_list[10]
            pygame.draw.rect(self.SURF, white, self.mini_map_rect, 3)

        pygame.draw.rect(self.SURF, white, self.selected_rect, 3)
        pygame.draw.rect(self.SURF, white, self.selected_pen_rect, 3)

        arrows_white = [self.font.render("<<<", True, white),
                        self.font.render(">>>", True, white)]
        arrows_grey = [self.font.render("<<<", True, (128, 128, 128)),
                       self.font.render(">>>", True, (128, 128, 128))]

        for rect in self.change_rect_list:
            arrow_rect = arrows_white[0].get_rect(center=rect.center)
            subsurface = self.SURF.subsurface(arrow_rect)
            subsurface.fill(self.bg)

            if self.change_rect_list.index(rect) == 0:
                if 0 < self.menu_index_top:
                    pygame.draw.rect(self.SURF, white, rect, 1)
                    subsurface.blit(arrows_white[0], [0, 0])
                else:
                    pygame.draw.rect(self.SURF, gray, rect, 1)
                    subsurface.blit(arrows_grey[0], [0, 0])

            elif self.change_rect_list.index(rect) == 1:
                if self.number_top > self.index_top:
                    pygame.draw.rect(self.SURF, white, rect, 1)
                    subsurface.blit(arrows_white[1], [0, 0])
                else:
                    pygame.draw.rect(self.SURF, gray, rect, 1)
                    subsurface.blit(arrows_grey[1], [0, 0])

    def tool_line_draw(self):
        # line from 2 points
        steps = 0
        try:
            m = (self.end[1] - self.start[1]) / (self.end[0] - self.start[0])
            b = self.start[1] - m * self.start[0]
        except ZeroDivisionError:
            m = 1
            b = 0

        # coordinates in the interval
        if self.end[1] - self.start[1] > start.tile_size // 2:
            steps = 1
        elif self.end[1] - self.start[1] < - start.tile_size // 2:
            steps = - 1
        if steps != 0:
            for y in range(int(self.start[1]), int(self.end[1]), steps):
                x = (y - b) / m

                for coordinates in map1.map_tile_index:
                    # see if (x,y) is in the rect + 1 because of room from overlay edge
                    if (coordinates[0] + 1) * start.tile_size <= x <= (coordinates[0] + 2) * start.tile_size:
                        if (coordinates[1] + 1) * start.tile_size <= y <= (coordinates[1] + 2) * start.tile_size:
                            if map1.foreground:
                                map1.map_dict[coordinates] = map1.interact
                            if map1.background:
                                map1.bg_dict[coordinates] = map1.interact

        else:
            if self.end[0] - self.start[0] > 0:
                steps = 1
            elif self.end[0] - self.start[0] < 0:
                steps = - 1
            else:
                steps = 1

            for x in range(int(self.start[0]), int(self.end[0]), steps):
                y = self.start[1]

                for coordinates in map1.map_tile_index:
                    # see if (x,y) is in the rect + 1 because of room from overlay edge
                    if (coordinates[1] + 1) * start.tile_size <= y <= (coordinates[1] + 2) * start.tile_size:
                        if (coordinates[0] + 1) * start.tile_size <= x <= (coordinates[0] + 2) * start.tile_size:
                            if map1.foreground:
                                map1.map_dict[coordinates] = map1.interact
                            if map1.background:
                                map1.bg_dict[coordinates] = map1.interact

    def tool_rect_update(self):
        size = abs(self.end[0] - self.start[0]), \
               abs(self.end[1] - self.start[1])

        # draw the rectangle in all directions
        # start = top left
        if self.end[0] - self.start[0] >= 0 and self.end[1] - self.start[1] >= 0:
            self.rectangle = pygame.Rect([self.start[0], self.start[1]], size)
        # start = bottom left
        elif self.end[0] - self.start[0] >= 0 > self.end[1] - self.start[1]:
            self.rectangle = pygame.Rect([self.start[0], self.end[1]], size)
        # start = top right
        elif self.end[0] - self.start[0] < 0 <= self.end[1] - self.start[1]:
            self.rectangle = pygame.Rect([self.end[0], self.start[1]], size)
        # start = bottom right
        elif self.end[0] - self.start[0] < 0 and self.end[1] - self.start[1] < 0:
            self.rectangle = pygame.Rect([self.end[0], self.end[1]], size)

    def tool_empty_rect_draw(self):
        for rect in map1.map_tiles_interaction:
            # left side from top to bottom
            if rect.right >= self.rectangle.left >= rect.left:
                if rect.bottom >= self.rectangle.top and rect.top <= self.rectangle.bottom:
                    coordinates = map1.map_tile_index[map1.map_tiles_interaction.index(rect)]
                    if map1.foreground:
                        map1.map_dict[coordinates] = map1.interact
                    if map1.background:
                        map1.bg_dict[coordinates] = map1.interact
            # right side from top to bottom
            elif rect.right >= self.rectangle.right >= rect.left:
                if rect.bottom >= self.rectangle.top and rect.top <= self.rectangle.bottom:
                    coordinates = map1.map_tile_index[map1.map_tiles_interaction.index(rect)]
                    if map1.foreground:
                        map1.map_dict[coordinates] = map1.interact
                    if map1.background:
                        map1.bg_dict[coordinates] = map1.interact
            # top side from left to right
            elif rect.top <= self.rectangle.top <= rect.bottom:
                if rect.right <= self.rectangle.right and rect.left >= self.rectangle.left:
                    coordinates = map1.map_tile_index[map1.map_tiles_interaction.index(rect)]
                    if map1.foreground:
                        map1.map_dict[coordinates] = map1.interact
                    if map1.background:
                        map1.bg_dict[coordinates] = map1.interact
            # bottom side from left to right
            elif rect.top <= self.rectangle.bottom <= rect.bottom:
                if rect.right <= self.rectangle.right and rect.left >= self.rectangle.left:
                    coordinates = map1.map_tile_index[map1.map_tiles_interaction.index(rect)]
                    if map1.foreground:
                        map1.map_dict[coordinates] = map1.interact
                    if map1.background:
                        map1.bg_dict[coordinates] = map1.interact

    def tool_full_rect_draw(self):
        for rect in map1.map_tiles_interaction:
            if rect.right >= self.rectangle.left and rect.left <= self.rectangle.right:
                if rect.bottom >= self.rectangle.top and rect.top <= self.rectangle.bottom:
                    coordinates = map1.map_tile_index[map1.map_tiles_interaction.index(rect)]
                    if map1.foreground:
                        map1.map_dict[coordinates] = map1.interact
                    if map1.background:
                        map1.bg_dict[coordinates] = map1.interact

    def tool_circ_update(self):
        # cirlce radius
        self.radius = math.sqrt((self.end[0] - self.start[0]) ** 2 + (
                self.end[1] - self.start[1]) ** 2)

    def tool_empty_circ_draw(self):
        for i in range(360):
            y = self.start[1] + math.sin(i) * self.radius
            x = self.start[0] + math.cos(i) * self.radius

            for coordinates in map1.map_tile_index:
                # see if (x,y) is in the rect + 1 because of room from overlay edge
                if (coordinates[1] + 1) * start.tile_size <= y <= (coordinates[1] + 2) * start.tile_size:
                    if (coordinates[0] + 1) * start.tile_size <= x <= (coordinates[0] + 2) * start.tile_size:
                        if map1.foreground:
                            map1.map_dict[coordinates] = map1.interact
                        if map1.background:
                            map1.bg_dict[coordinates] = map1.interact

    def tool_full_circ_draw(self):
        for j in range(int(self.radius // (start.tile_size // 2))):
            if j >= 1:
                self.radius -= start.tile_size // 2
            for i in range(0, 360, 2):
                y = self.start[1] + math.sin(i) * self.radius
                x = self.start[0] + math.cos(i) * self.radius

                for coordinates in map1.map_tile_index:
                    # see if (x,y) is in the rect + 1 because of room from overlay edge
                    if (coordinates[1] + 1) * start.tile_size <= y <= (coordinates[1] + 2) * start.tile_size:
                        if (coordinates[0] + 1) * start.tile_size <= x <= (coordinates[0] + 2) * start.tile_size:
                            if map1.foreground:
                                map1.map_dict[coordinates] = map1.interact
                            if map1.background:
                                map1.bg_dict[coordinates] = map1.interact

    def tool_sphere(self):
        for j in range(int(self.radius // 10)):
            self.radius -= (j * 10)
            for i in range(360):
                y = self.start[1] + math.sin(i) * self.radius
                x = self.start[0] + math.cos(i) * self.radius

                for coordinates in map1.map_tile_index:
                    # see if (x,y) is in the rect + 1 because of room from overlay edge
                    if (coordinates[1] + 1) * start.tile_size <= y <= (coordinates[1] + 2) * start.tile_size:
                        if (coordinates[0] + 1) * start.tile_size <= x <= (coordinates[0] + 2) * start.tile_size:
                            if map1.foreground:
                                map1.map_dict[coordinates] = map1.interact
                            if map1.background:
                                map1.bg_dict[coordinates] = map1.interact

    # quality of life stuff with the tool menu/ selected tile show/ automatic selection/ etc
    def tool_start(self):
        if map1.interact[0] == "key" and not map_menu_left.selected_rect:
            map1.interact = [start.tile_set_names[0], 0, 0]
            map_menu_left.selected_rect = map_menu_left.menu_grid_list[
                map1.interact[1] - map_menu_left.menu_index_top * len(
                    map_menu_left.menu_grid_list) // 2][0]

    def tool_menu_map_interaction(self, event, map_position):

        # drawing tool values use left click for start and end
        # the biggest part is the rectangle tool, as it always defines the top left corner as starting point
        # if, elif variation is used to make it work

        if self.line_tool or self.empty_rect_tool or self.full_rect_tool \
                or self.empty_circle_tool or self.full_circle_tool or self.sphere_tool:
            if event.type == pygame.MOUSEBUTTONDOWN and not map1.drawing:
                if start.screen_rect.collidepoint(event.pos):
                    if event.button == 1:
                        self.start = [map_position[0], map_position[1]]
                        map1.drawing = True

            elif event.type == pygame.MOUSEMOTION and map1.drawing:
                self.end = [map_position[0], map_position[1]]
                self.tool_rect_update()
                self.tool_circ_update()

            elif event.type == pygame.MOUSEBUTTONDOWN and map1.drawing:
                if event.button == 1:
                    self.end = [map_position[0], map_position[1]]
                    self.tool_rect_update()
                    self.tool_circ_update()

                    # line creation
                    if self.line_tool:
                        self.tool_line_draw()

                    # rectangle creation
                    elif self.empty_rect_tool:
                        self.tool_empty_rect_draw()

                    elif self.full_rect_tool:
                        self.tool_full_rect_draw()

                    # circle creation
                    elif self.empty_circle_tool:
                        self.tool_empty_circ_draw()

                    elif self.full_circle_tool:
                        self.tool_full_circ_draw()

                    elif self.sphere_tool:
                        self.tool_sphere()

                    map1.drawing = False
                    self.start = [0, 0]
                    self.end = [0, 0]
                    self.rectangle = pygame.Rect(0, 0, 0, 0)

    def tool_menu_interaction(self, event):

        if self.SURF_rect.collidepoint(event.pos):
            position = tuple(map(lambda i, j: i - j, pygame.mouse.get_pos(), (start.SCREEN_X // 8, 0)))
            for rect in self.change_rect_list:
                if rect.collidepoint(position):
                    if self.change_rect_list.index(rect) == 0:
                        if 0 < self.menu_index_top:
                            self.menu_index -= 1
                        else:
                            pass
                    elif self.change_rect_list.index(rect) == 1:
                        if self.menu_index_top > self.index_top:
                            self.menu_index += 1
                        else:
                            pass

                    print("top", self.menu_index)

            for rect in self.menu_grid_list:
                if rect.collidepoint(position):
                    if self.number_top >= self.menu_grid_list.index(rect) * (
                            self.menu_index + 1):

                        if self.menu_grid_list.index(rect) * (self.menu_index + 1) == 0:
                            if self.selected_pen_rect == rect:
                                self.selected_rect = rect
                            elif self.menu_grid_list.index(self.selected_rect) == 1:
                                self.selected_rect = rect

                        elif self.menu_grid_list.index(rect) * (
                                self.menu_index + 1) == 1:
                            if self.selected_pen_rect == rect:
                                self.selected_rect = rect
                            elif self.menu_grid_list.index(self.selected_rect) == 0:
                                self.selected_rect = rect

                        elif self.menu_grid_list.index(rect) <= 8:
                            self.selected_rect = rect

                        # grid tool
                        elif self.menu_grid_list.index(rect) == 9:
                            if map1.grid:
                                map1.grid = False
                            else:
                                map1.grid = True

                        elif self.menu_grid_list.index(rect) == 10:
                            if self.mini_map_tool:
                                self.mini_map_tool = False
                            else:
                                self.mini_map_tool = True

                        if self.menu_grid_list.index(rect) <= 1:
                            self.selected_pen_rect = rect

                        print(self.selected_rect)

                        self.tool_start()
                        self.pen_tool = False
                        self.eraser_tool = False
                        self.line_tool = False
                        self.empty_rect_tool = False
                        self.full_rect_tool = False
                        self.empty_circle_tool = False
                        self.full_circle_tool = False
                        self.sphere_tool = False
                        self.fill_tool = False
                        map1.cursor_change = True

                        # combine pen with the other tools
                        if self.menu_grid_list.index(self.selected_pen_rect) == 0:
                            if map1.interact != map1.interact_temp and map1.interact_temp != ["key", 0,
                                                                                              0]:
                                map1.interact = map1.interact_temp
                                map1.interact_temp = ["key", 0, 0]
                            if self.menu_grid_list.index(self.selected_rect) == 0:
                                self.pen_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 2:
                                self.line_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 3:
                                self.empty_rect_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 4:
                                self.full_rect_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 5:
                                self.empty_circle_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 6:
                                self.full_circle_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 7:
                                self.sphere_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 8:
                                self.fill_tool = True

                        # combine eraser with the other tools
                        elif self.menu_grid_list.index(self.selected_pen_rect) == 1:
                            # map_menu_left.selected_rect = None
                            map1.cursor_change = False
                            if map1.interact != ["key", 0, 0]:
                                map1.interact_temp = map1.interact
                            map1.interact = ["key", 0, 0]
                            if self.menu_grid_list.index(self.selected_rect) == 1:
                                self.eraser_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 2:
                                self.line_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 3:
                                self.empty_rect_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 4:
                                self.full_rect_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 5:
                                self.empty_circle_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 6:
                                self.full_circle_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 7:
                                self.sphere_tool = True
                            elif self.menu_grid_list.index(self.selected_rect) == 8:
                                self.fill_tool = True

    def render_tool_stuff(self, map_scale):

        # tool stuff
        if self.line_tool:
            pygame.draw.line(map1.overlay, black, self.start, self.end, 4)
        elif self.empty_rect_tool or self.full_rect_tool:
            pygame.draw.rect(map1.overlay, black, self.rectangle, 4)
        elif self.empty_circle_tool or self.full_circle_tool or self.sphere_tool:
            pygame.draw.circle(map1.overlay, black, self.start, self.radius, 4)

        # mini map
        if self.mini_map_tool:
            # transform the map to the size of the screen_recet
            copy = pygame.transform.rotozoom(map1.overlay, 0, map_scale)
            copy_rect = copy.get_rect()
            copy_rect.center = start.screen_rect.center
            pygame.draw.rect(start.screen, self.bg, start.screen_rect)
            pygame.draw.rect(start.screen, black, copy_rect, 3)
            start.screen.blit(copy, copy_rect)

    def autofill_method(self):
        if self.auto_counter == 0:
            for coordinates in map1.map_tile_index:
                # foreground
                if map1.foreground:
                    if map1.map_dict.get(coordinates)[0] != "key":
                        if map1.map_dict.get(coordinates)[1] == 0:

                            # 3x3 coordinate field
                            coordinates11 = (coordinates[0] - 1, coordinates[1] - 1)
                            coordinates12 = (coordinates[0], coordinates[1] - 1)
                            coordinates13 = (coordinates[0] + 1, coordinates[1] - 1)
                            coordinates21 = (coordinates[0] - 1, coordinates[1])
                            # coordinates22 = (coordinates[0], coordinates[1])
                            coordinates23 = (coordinates[0] + 1, coordinates[1])
                            coordinates31 = (coordinates[0] - 1, coordinates[1] + 1)
                            coordinates32 = (coordinates[0], coordinates[1] + 1)
                            coordinates33 = (coordinates[0] + 1, coordinates[1] + 1)

                            # coordinate field info
                            square11 = map1.map_dict.get(coordinates11)
                            square12 = map1.map_dict.get(coordinates12)
                            square13 = map1.map_dict.get(coordinates13)
                            square21 = map1.map_dict.get(coordinates21)
                            # square22 = map1.map_dict.get(coordinates22)
                            square23 = map1.map_dict.get(coordinates23)
                            square31 = map1.map_dict.get(coordinates31)
                            square32 = map1.map_dict.get(coordinates32)
                            square33 = map1.map_dict.get(coordinates33)

                            # print(square11, " | ", square12, " | ", square13)
                            # print(square21, " | ", square22, " | ", square23)
                            # print(square31, " | ", square32, " | ", square33)

                            # straights
                            if square12 and square12[0] == "key":
                                map1.map_dict[coordinates12] = [map1.map_dict.get(coordinates)[0], 1, 0]
                            if square21 and square21[0] == "key":
                                map1.map_dict[coordinates21] = [map1.map_dict.get(coordinates)[0], 1, 90]
                            if square23 and square23[0] == "key":
                                map1.map_dict[coordinates23] = [map1.map_dict.get(coordinates)[0], 1, 270]
                            if square32 and square32[0] == "key":
                                map1.map_dict[coordinates32] = [map1.map_dict.get(coordinates)[0], 1, 180]

                            # corner (outside)
                            if square11 and square11[0] == "key":
                                map1.map_dict[coordinates11] = [map1.map_dict.get(coordinates)[0], 2, 0]
                            if square13 and square13[0] == "key" and square23 != map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates13] = [map1.map_dict.get(coordinates)[0], 2, 270]
                            if square31 and square31[0] == "key" and square32 != map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates31] = [map1.map_dict.get(coordinates)[0], 2, 90]
                            if square33 and square33[0] == "key" and square32 != map1.map_dict.get(
                                    coordinates) and square23 != map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates33] = [map1.map_dict.get(coordinates)[0], 2, 180]

                            # corner (inside)
                            if square11 != map1.map_dict.get(coordinates) and square21 == map1.map_dict.get(
                                    coordinates) and square12 == map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates11] = [map1.map_dict.get(coordinates)[0], 3, 0]
                            if square13 != map1.map_dict.get(coordinates) and square23 == map1.map_dict.get(
                                    coordinates) and square12 == map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates13] = [map1.map_dict.get(coordinates)[0], 3, 270]
                            if square31 != map1.map_dict.get(coordinates) and square21 == map1.map_dict.get(
                                    coordinates) and square32 == map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates31] = [map1.map_dict.get(coordinates)[0], 3, 90]
                            if square33 != map1.map_dict.get(coordinates) and square23 == map1.map_dict.get(
                                    coordinates) and square32 == map1.map_dict.get(coordinates):
                                map1.map_dict[coordinates33] = [map1.map_dict.get(coordinates)[0], 3, 180]

                            # since the map dict works from top left down, the order of the code is really important
                            if square12 != map1.map_dict.get(coordinates) and square11 == map1.map_dict.get(
                                    coordinates):
                                map1.map_dict[coordinates12] = [map1.map_dict.get(coordinates)[0], 3, 270]
                            if square21 != map1.map_dict.get(coordinates) and square11 == map1.map_dict.get(
                                    coordinates):
                                map1.map_dict[coordinates21] = [map1.map_dict.get(coordinates)[0], 3, 90]
                            if square21 != map1.map_dict.get(coordinates) and square31 == map1.map_dict.get(
                                    coordinates):
                                map1.map_dict[coordinates21] = [map1.map_dict.get(coordinates)[0], 3, 0]
                            if square32 != map1.map_dict.get(coordinates) and square31 == map1.map_dict.get(
                                    coordinates):
                                map1.map_dict[coordinates32] = [map1.map_dict.get(coordinates)[0], 3, 180]

                # background
                if map1.background:
                    if map1.bg_dict.get(coordinates)[0] != "key":
                        if map1.bg_dict.get(coordinates)[1] == 0:

                            # 3x3 coordinate field
                            coordinates11 = (coordinates[0] - 1, coordinates[1] - 1)
                            coordinates12 = (coordinates[0], coordinates[1] - 1)
                            coordinates13 = (coordinates[0] + 1, coordinates[1] - 1)
                            coordinates21 = (coordinates[0] - 1, coordinates[1])
                            # coordinates22 = (coordinates[0], coordinates[1])
                            coordinates23 = (coordinates[0] + 1, coordinates[1])
                            coordinates31 = (coordinates[0] - 1, coordinates[1] + 1)
                            coordinates32 = (coordinates[0], coordinates[1] + 1)
                            coordinates33 = (coordinates[0] + 1, coordinates[1] + 1)

                            # coordinate field info
                            square11 = map1.bg_dict.get(coordinates11)
                            square12 = map1.bg_dict.get(coordinates12)
                            square13 = map1.bg_dict.get(coordinates13)
                            square21 = map1.bg_dict.get(coordinates21)
                            # square22 = map1.bg_dict.get(coordinates22)
                            square23 = map1.bg_dict.get(coordinates23)
                            square31 = map1.bg_dict.get(coordinates31)
                            square32 = map1.bg_dict.get(coordinates32)
                            square33 = map1.bg_dict.get(coordinates33)

                            # print(square11, " | ", square12, " | ", square13)
                            # print(square21, " | ", square22, " | ", square23)
                            # print(square31, " | ", square32, " | ", square33)

                            # straights
                            if square12 and square12[0] == "key":
                                map1.bg_dict[coordinates12] = [map1.bg_dict.get(coordinates)[0], 1, 0]
                            if square21 and square21[0] == "key":
                                map1.bg_dict[coordinates21] = [map1.bg_dict.get(coordinates)[0], 1, 90]
                            if square23 and square23[0] == "key":
                                map1.bg_dict[coordinates23] = [map1.bg_dict.get(coordinates)[0], 1, 270]
                            if square32 and square32[0] == "key":
                                map1.bg_dict[coordinates32] = [map1.bg_dict.get(coordinates)[0], 1, 180]

                            # corner (outside)
                            if square11 and square11[0] == "key":
                                map1.bg_dict[coordinates11] = [map1.bg_dict.get(coordinates)[0], 2, 0]
                            if square13 and square13[0] == "key" and square23 != map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates13] = [map1.bg_dict.get(coordinates)[0], 2, 270]
                            if square31 and square31[0] == "key" and square32 != map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates31] = [map1.bg_dict.get(coordinates)[0], 2, 90]
                            if square33 and square33[0] == "key" and square32 != map1.bg_dict.get(
                                    coordinates) and square23 != map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates33] = [map1.bg_dict.get(coordinates)[0], 2, 180]

                            # corner (inside)
                            if square11 != map1.bg_dict.get(coordinates) and square21 == map1.bg_dict.get(
                                    coordinates) and square12 == map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates11] = [map1.bg_dict.get(coordinates)[0], 3, 0]
                            if square13 != map1.bg_dict.get(coordinates) and square23 == map1.bg_dict.get(
                                    coordinates) and square12 == map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates13] = [map1.bg_dict.get(coordinates)[0], 3, 270]
                            if square31 != map1.bg_dict.get(coordinates) and square21 == map1.bg_dict.get(
                                    coordinates) and square32 == map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates31] = [map1.bg_dict.get(coordinates)[0], 3, 90]
                            if square33 != map1.bg_dict.get(coordinates) and square23 == map1.bg_dict.get(
                                    coordinates) and square32 == map1.bg_dict.get(coordinates):
                                map1.bg_dict[coordinates33] = [map1.bg_dict.get(coordinates)[0], 3, 180]

                            # since the map dict works from top left down, the order of the code is really important
                            if square12 != map1.bg_dict.get(coordinates) and square11 == map1.bg_dict.get(
                                    coordinates):
                                map1.bg_dict[coordinates12] = [map1.bg_dict.get(coordinates)[0], 3, 270]
                            if square21 != map1.bg_dict.get(coordinates) and square11 == map1.bg_dict.get(
                                    coordinates):
                                map1.bg_dict[coordinates21] = [map1.bg_dict.get(coordinates)[0], 3, 90]
                            if square21 != map1.bg_dict.get(coordinates) and square31 == map1.bg_dict.get(
                                    coordinates):
                                map1.bg_dict[coordinates21] = [map1.bg_dict.get(coordinates)[0], 3, 0]
                            if square32 != map1.bg_dict.get(coordinates) and square31 == map1.bg_dict.get(
                                    coordinates):
                                map1.bg_dict[coordinates32] = [map1.bg_dict.get(coordinates)[0], 3, 180]
                        # # fix gaps
                        #
                        # if map1.map_dict[coordinates11] != [map1.map_dict.get(coordinates)[0], 3, 0] and \
                        #         map1.map_dict[coordinates11] != [map1.map_dict.get(coordinates)[0], 2, 0] and \
                        #         map1.map_dict[coordinates21] != [map1.map_dict.get(coordinates)[0], 1, 90] and \
                        #         map1.map_dict[coordinates21] != map1.map_dict.get(coordinates):
                        #     map1.map_dict[coordinates11] = [map1.map_dict.get(coordinates)[0], 1, 0]

            # may be used for drawing and autofill at the same time
            # self.auto_counter = 1

    def fill_tool_method(self, event, map_position):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # calculated the relative map_position of the mouse to the original tile map
            if start.screen_rect.collidepoint(event.pos):
                for rect in map1.map_tiles_interaction:
                    if rect.collidepoint(map_position):

                        if event.button == 1:
                            coordinates = map1.map_tile_index[map1.map_tiles_interaction.index(rect)]
                            if map1.foreground and map1.map_dict.get(coordinates) != map1.interact:
                                # create a list for the tiles to be changed
                                fill_list = []

                                fill_info_fg = map1.map_dict.get(coordinates)
                                fill_list.append(coordinates)

                                map1.map_dict[coordinates] = map1.interact
                                for fill_coordinates in fill_list:

                                    # + coordinate field
                                    coordinates12 = (fill_coordinates[0], fill_coordinates[1] - 1)
                                    coordinates21 = (fill_coordinates[0] - 1, fill_coordinates[1])
                                    coordinates23 = (fill_coordinates[0] + 1, fill_coordinates[1])
                                    coordinates32 = (fill_coordinates[0], fill_coordinates[1] + 1)

                                    # coordinate field info
                                    square12 = map1.map_dict.get(coordinates12)
                                    square21 = map1.map_dict.get(coordinates21)
                                    square23 = map1.map_dict.get(coordinates23)
                                    square32 = map1.map_dict.get(coordinates32)

                                    if square12 == fill_info_fg:
                                        map1.map_dict[coordinates12] = map1.interact
                                        fill_list.append(coordinates12)
                                    if square21 == fill_info_fg:
                                        map1.map_dict[coordinates21] = map1.interact
                                        fill_list.append(coordinates21)
                                    if square23 == fill_info_fg:
                                        map1.map_dict[coordinates23] = map1.interact
                                        fill_list.append(coordinates23)
                                    if square32 == fill_info_fg:
                                        map1.map_dict[coordinates32] = map1.interact
                                        fill_list.append(coordinates32)

                            if map1.background and map1.bg_dict.get(coordinates) != map1.interact:
                                # create a list for the tiles to be changed
                                fill_list = []

                                fill_info_fg = map1.bg_dict.get(coordinates)

                                fill_list.append(coordinates)
                                map1.bg_dict[coordinates] = map1.interact

                                for fill_coordinates in fill_list:

                                    # + coordinate field
                                    coordinates12 = (fill_coordinates[0], fill_coordinates[1] - 1)
                                    coordinates21 = (fill_coordinates[0] - 1, fill_coordinates[1])
                                    coordinates23 = (fill_coordinates[0] + 1, fill_coordinates[1])
                                    coordinates32 = (fill_coordinates[0], fill_coordinates[1] + 1)

                                    # coordinate field info
                                    square12 = map1.bg_dict.get(coordinates12)
                                    square21 = map1.bg_dict.get(coordinates21)
                                    square23 = map1.bg_dict.get(coordinates23)
                                    square32 = map1.bg_dict.get(coordinates32)

                                    if square12 == fill_info_fg:
                                        map1.bg_dict[coordinates12] = map1.interact
                                        fill_list.append(coordinates12)
                                    if square21 == fill_info_fg:
                                        map1.bg_dict[coordinates21] = map1.interact
                                        fill_list.append(coordinates21)
                                    if square23 == fill_info_fg:
                                        map1.bg_dict[coordinates23] = map1.interact
                                        fill_list.append(coordinates23)
                                    if square32 == fill_info_fg:
                                        map1.bg_dict[coordinates32] = map1.interact
                                        fill_list.append(coordinates32)

    def save_name_method(self):

        subsurface = start.screen.subsurface(self.menu_interaction_rect)
        pygame.draw.rect(subsurface, map1.bg, self.menu_interaction_rect)
        pygame.draw.rect(subsurface, white, self.menu_interaction_rect, 1)

        input_rect = pygame.Rect(self.x, self.menu_interaction_rect.height // 2,
                                 self.menu_interaction_rect.width - self.x, 30)

        pygame.draw.rect(subsurface, start.box_color, input_rect)
        pygame.draw.rect(subsurface, white, input_rect, 1)
        txt_surface = self.font.render(start.save_text, True, white)
        subsurface.blit(txt_surface, (input_rect.x + 10, input_rect.y))

        if ":" in start.save_text:
            print("no")

    # save all relevant map info in a text file
    # save the matching surface into an png
    def save_map_method(self):
        i = 0
        for _ in self.directories:
            i += 1
        print("number of files in directory: " + str(i))

        filename = os.path.join(start.map_save_path, start.save_text)
        filename_txt = os.path.join(filename + ".txt")
        filename_png = os.path.join(filename + ".png")

        pygame.image.save(map1.overlay, filename_png)

        Path(filename_txt).touch()

        with open(filename_txt, mode='w') as file_object:
            file_object.write("start.version = " + str(start.version) + "\n")
            file_object.write("start.map_x, start.map_y = map1.x, map1.y = " + str((start.map_x, start.map_y)) + "\n")
            file_object.write("start.tile_size = " + str(start.tile_size) + "\n")
            file_object.write("start.tilepath = \"" + str(start.Tile_path) + "\"\n")
            file_object.write("map1.bg_dict = " + str(map1.bg_dict) + "\n")
            file_object.write("map1.map_dict = " + str(map1.map_dict) + "\n")

        file_object.close()
        print("saved")

    def save_loop(self):

        start.run = True
        while start.run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start.run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        start.run = False

                start.box_color = start.box_color_active
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print(start.save_text)
                        # save the map
                        map_menu.save_map_method()
                        start.state = "map"

                    elif event.key == pygame.K_BACKSPACE:
                        start.save_text = start.save_text[:-1]
                    else:
                        start.save_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = tuple(
                        map(lambda i, j: i - j, pygame.mouse.get_pos(), (start.SCREEN_X // 8 * 7, 0)))
                    if event.button == 1:
                        for rect in map_menu.menu_grid_list:
                            if rect[1].collidepoint(position):
                                if map_menu.options_list[rect[0]].lower() == "save":
                                    print(start.save_text)
                                    # save the map
                                    map_menu.save_map_method()
                                    start.state = "map"

            if start.state == "map":
                start.run = False
                map1.map_loop()

            self.save_name_method()

            start.screen.blit(map_menu_top.SURF, map_menu_top.SURF_rect)
            start.screen.blit(map_menu_left.SURF, map_menu_left.SURF_rect)
            start.screen.blit(map_menu.SURF, map_menu.SURF_rect)

            map_menu.define_menu_grid_right()
            map_menu_left.define_menu_grid_left()
            map_menu_top.define_menu_grid_top()

            pygame.display.update(start.screen_rect)

    def load_file_grid(self):
        self.menu_buttons = []
        self.load_files = []
        for names in os.listdir(start.map_save_path):
            if names.endswith(".txt"):
                name = names.replace(".txt", "")
                self.load_files.append(name)

        for i in range(20):
            load_rect = pygame.Rect(self.x + 64, 84 + (self.y - 84) // 20 * i, self.x * 6 - 128, (self.y - 84) // 20)
            self.menu_buttons.append(load_rect)
            i += 1

        # save files flip page
        for i in range(2):
            change_rect = pygame.Rect((self.x + i * (self.x * 6 - 64), 0, 64, self.y))
            self.change_rect_list.append(change_rect)

    def load_map_method(self):
        # set the load screen
        subsurface = start.screen.subsurface(self.menu_interaction_rect)
        pygame.draw.rect(subsurface, self.bg, self.menu_interaction_rect)
        pygame.draw.rect(subsurface, white, self.menu_interaction_rect, 1)

        # tool selection
        self.number_top = len(self.load_files) - 1
        for rect in self.menu_buttons:
            self.index_top = self.menu_buttons.index(rect)

            # if the amount of files is smaller than the max index of that page
            if self.number_top >= self.index_top + self.menu_index * 20 >= 0:
                load_text = self.font.render(self.load_files[self.index_top + self.menu_index * 20], True, white)
                load_rect = load_text.get_rect()
                # position the file to one of the 20 rects
                load_rect.center = self.menu_buttons[self.index_top].center
                subsurface.blit(load_text, load_rect)

        # flip the page for save files
        arrows_white = [self.font.render("<<<", True, white),
                        self.font.render(">>>", True, white)]
        arrows_grey = [self.font.render("<<<", True, (128, 128, 128)),
                       self.font.render(">>>", True, (128, 128, 128))]

        for rect in self.change_rect_list:
            arrow_rect = arrows_white[0].get_rect()

            if self.change_rect_list.index(rect) == 0:
                arrow_rect.center = rect.center
                if 0 < self.menu_index:
                    pygame.draw.rect(subsurface, white, rect, 1)
                    subsurface.blit(arrows_white[0], arrow_rect)
                else:
                    pygame.draw.rect(subsurface, gray, rect, 1)
                    subsurface.blit(arrows_grey[0], arrow_rect)

            elif self.change_rect_list.index(rect) == 1:
                arrow_rect.center = rect.center
                if self.number_top > self.index_top + self.menu_index * 20:
                    pygame.draw.rect(subsurface, white, rect, 1)
                    subsurface.blit(arrows_white[1], arrow_rect)
                else:
                    pygame.draw.rect(subsurface, gray, rect, 1)
                    subsurface.blit(arrows_grey[1], arrow_rect)

    def load_loop(self):

        self.load_file_grid()

        start.run = True
        while start.run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start.run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        start.run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # change rect
                        for rect in self.change_rect_list:
                            if rect.collidepoint(event.pos):
                                if self.change_rect_list.index(rect) == 0:
                                    if 0 < self.menu_index:
                                        self.menu_index -= 1
                                    else:
                                        pass
                                elif self.change_rect_list.index(rect) == 1:
                                    if self.number_top > self.index_top + self.menu_index * 20:
                                        self.menu_index += 1
                                    else:
                                        pass

                                print(self.menu_index)

                        for rect in self.menu_buttons:
                            if rect.collidepoint(event.pos):

                                a = self.menu_buttons.index(rect) + self.menu_index * 20
                                # reset values, that will be replaced by loading information
                                if a <= len(self.load_files) - 1:
                                    start.reset_values()

                                    load_data = self.load_files[a]

                                    filename = os.path.join(start.map_save_path, load_data + ".txt")
                                    data = open(filename, mode='r')
                                    info = data.readlines()
                                    for line in info:
                                        exec(line)

                                    # this overwrites the loaded map_dict
                                    map1.create_tiled_map(x_pos_start=start.tile_size, y_pos_start=start.tile_size)
                                    exec(info[-2])
                                    exec(info[-1])

                                    # update the version number of the save file and create the name reference
                                    start.version += 1

                                    if start.version == 1:
                                        start.save_text = load_data + "_V0" + str(start.version)
                                    elif start.version < 10:
                                        start.save_text = load_data[:-4] + "_V0" + str(start.version)
                                    else:
                                        start.save_text = load_data[:-4] + "_V" + str(start.version)

                                    # reload values that are influenced by the loaded info
                                    start.reload_values()

                                start.state = "map"

            self.load_map_method()

            start.screen.blit(map_menu_top.SURF, map_menu_top.SURF_rect)
            start.screen.blit(map_menu_left.SURF, map_menu_left.SURF_rect)
            start.screen.blit(map_menu.SURF, map_menu.SURF_rect)

            map_menu.define_menu_grid_right()
            map_menu_left.define_menu_grid_left()
            map_menu_top.define_menu_grid_top()

            if start.state == "map":
                start.run = False
                map1.map_loop()

            pygame.display.update(start.screen_rect)

    def new_grid(self):
        self.menu_buttons = []
        # self.font = pygame.font.SysFont(pygame.font.get_fonts()[-6], 28)

        i = 0

        # selection options

        for option in self.new_menu_options:
            text = self.font.render(option, True, white)
            rect = text.get_rect()
            size = rect.size
            rect.center = (start.SCREEN_X // 2, 84 + (size[1] * 3 + 5) * i)

            self.menu_buttons.append(rect)

            i += 1

        # tile size options

        for tile_size in self.tile_size_list:
            text = self.font.render(tile_size, True, white)
            rect = text.get_rect()
            size = rect.size
            rect.center = (start.SCREEN_X // 2 - size[0] * 2 + size[0] * 2 * self.tile_size_list.index(tile_size),
                           84 + (size[1] + 5))

            self.menu_buttons.append(rect)

        # map size input
        for i in range(1):
            text = self.font.render(self.new_menu_options[i + 1], True, white)
            rect = text.get_rect()
            size = rect.size
            rect.center = (start.SCREEN_X // 2, 84 + size[1] + (size[1] * 3 + 5) * (i + 1))

            self.menu_buttons.append(rect)

    def new_map_method(self):
        # new_font = pygame.font.SysFont(pygame.font.get_fonts()[-6], 40)

        subsurface = start.screen.subsurface(self.menu_interaction_rect)
        pygame.draw.rect(subsurface, self.bg, self.menu_interaction_rect)
        pygame.draw.rect(subsurface, white, self.menu_interaction_rect, 1)

        pygame.draw.rect(subsurface, black, self.menu_buttons[self.new_menu_options.index("Create")])
        pygame.draw.rect(subsurface, white, self.menu_buttons[len(self.new_menu_options) + self.tile_size_select], 1)

        i = 0
        for option in self.new_menu_options:
            text = self.font.render(option, True, white)
            subsurface.blit(text, self.menu_buttons[i])
            i += 1

        for option in self.tile_size_list:
            text = self.font.render(option, True, white)
            subsurface.blit(text, self.menu_buttons[i])
            i += 1

        # input box
        pygame.draw.rect(subsurface, start.box_color, self.menu_buttons[-1])
        pygame.draw.rect(subsurface, white, self.menu_buttons[-1], 1)
        txt_surface = self.font.render(start.new_text, True, white)
        subsurface.blit(txt_surface, (self.menu_buttons[-1].x + 10, self.menu_buttons[-1].y))

    def new_loop(self):

        self.new_grid()
        start.run = True
        while start.run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start.run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        start.run = False

                start.box_color = start.box_color_active if start.input_action else start.box_color_inactive
                if event.type == pygame.KEYDOWN:
                    if start.input_action:
                        if event.key == pygame.K_RETURN:
                            print(start.new_text)
                        elif event.key == pygame.K_BACKSPACE:
                            start.new_text = start.new_text[:-1]
                        else:
                            start.new_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    start.input_action = False
                    if event.button == 1:
                        for rect in self.menu_buttons:
                            if rect.collidepoint(event.pos):

                                if rect == self.menu_buttons[-1]:
                                    # Toggle the active variable.
                                    start.input_action = True

                                elif len(self.new_menu_options) <= self.menu_buttons.index(rect) < len(
                                        self.menu_buttons) - 1:
                                    self.tile_size_select = self.menu_buttons.index(rect) - len(self.new_menu_options)
                                    print(self.tile_size_list[self.tile_size_select])

                                elif rect == self.menu_buttons[self.new_menu_options.index("Create")]:
                                    # redraw the overlay in case the map is too small

                                    # reset values, that will be replaced by loading information
                                    start.reset_values()

                                    # new map info
                                    start.tile_size = int(self.tile_size_list[self.tile_size_select])
                                    map_size = start.new_text.split("x")
                                    start.map_x = int(map_size[0])
                                    start.map_y = int(map_size[1])

                                    # save file name help
                                    start.save_text = str(start.tile_size) + "_" + str(start.map_x) + "x" + str(
                                        start.map_y) + "_"
                                    print(start.save_text)

                                    # this overwrites the loaded map_dict
                                    map1.create_tiled_map(x_pos_start=start.tile_size, y_pos_start=start.tile_size)

                                    # reload values that are influenced by the loaded info
                                    start.reload_values()

                                    start.state = "map"

                                    subsurface = start.screen.subsurface(self.menu_interaction_rect)
                                    subsurface.fill(map1.bg)

            if start.state == "map":
                start.run = False
                map1.map_loop()

            self.new_map_method()

            start.screen.blit(map_menu_top.SURF, map_menu_top.SURF_rect)
            start.screen.blit(map_menu_left.SURF, map_menu_left.SURF_rect)
            start.screen.blit(map_menu.SURF, map_menu.SURF_rect)

            map_menu.define_menu_grid_right()
            map_menu_left.define_menu_grid_left()
            map_menu_top.define_menu_grid_top()

            pygame.display.update(start.screen_rect)

    def config_menu(self):
        # hotkeys (rotation, tile selection, fullscreen)
        # colors (color scale for menu, background)
        # view (show tiles as xx by yy pixels)
        # savepaths
        pass


# create Map class
class Map:
    def __init__(self, bg_color=(128, 212, 255), bg_image=None, grid=1, top_border=64, fps=30):

        # FPS
        self.fps = fps
        self.speed = 8
        self.key_dir = {pygame.K_LEFT: (-self.speed, 0), pygame.K_RIGHT: (self.speed, 0), pygame.K_UP: (0, -self.speed),
                        pygame.K_DOWN: (0, self.speed), pygame.K_a: (-self.speed, 0), pygame.K_d: (self.speed, 0),
                        pygame.K_w: (0, -self.speed),
                        pygame.K_s: (0, self.speed)}

        self.grid = grid
        self.screen_x = start.SCREEN_X
        self.screen_y = start.SCREEN_Y

        if not bg_image:
            self.bg = bg_color
        else:
            self.bg = bg_image

        # create map surface
        self.overlay_org = pygame.Surface(
            ((start.map_x + 2) * start.tile_size, (start.map_y + 2) * start.tile_size)).convert()
        self.overlay_org.fill(self.bg)
        self.overlay_rect = self.overlay_org.get_rect()
        self.overlay_rect.center = start.screen_rect.center
        self.overlay = self.overlay_org

        # map interaction info
        self.menu_width = map_menu_left.x
        self.scroll_dv_left = self.menu_width
        self.scroll_dv_right = - self.menu_width + start.SCREEN_X - self.overlay_rect.width
        self.scroll_dv_top = top_border
        self.scroll_dv_bottom = start.SCREEN_Y - self.overlay_rect.height
        self.scroll_dv_x = self.overlay_rect.width // 2 - start.screen_rect.width // 2
        self.scroll_dv_y = self.overlay_rect.height // 2 - start.screen_rect.height // 2
        self.scroll_v = [0, 0]
        self.scroll_dv = [0, 0]
        self.scale = 1
        self.rotation = 0
        self.zoom_state = "1"
        self.drawing = False
        self.erasing = False

        # cursor setup
        self.cursor_image = pygame.image.load("images/sizes/32/TileSets/Grass/Grass_Tileset_32_01.png")
        self.cursor_rect = pygame.Rect(0, 0, start.tile_size, start.tile_size)
        self.cursor_change = False
        self.cursor = None

        # initialize matrices
        self.map_tiles_interaction = []
        self.map_tile_value = []
        self.map_tile_index = []
        self.map_tile_surfaces = []
        self.interact = ["key", 0, 0]
        self.interact_temp = ["key", 0, 0]

        self.map_dict = {}
        self.bg_dict = {}

        # matrices 2
        self.map_rect_list = []

        # menu stuff
        self.background = True
        self.background_visible = True
        self.foreground = True
        self.foreground_visible = True
        self.autofill = False

    def rotation_method(self):
        self.rotation += 90
        if self.rotation >= 360:
            self.rotation = 0

    def create_tiled_map(self, x_pos_start=0, y_pos_start=0):
        x_pos = x_pos_start
        y_pos = y_pos_start
        i = 0
        for x in range(start.map_x):
            for y in range(start.map_y):
                rect = pygame.Rect(x_pos, y_pos, start.tile_size, start.tile_size)
                self.map_tiles_interaction.append(rect)
                self.map_tile_index.append((x, y))
                self.map_tile_value.append(self.interact)

                y_pos += start.tile_size
                i += 1

            x_pos += start.tile_size
            y_pos = y_pos_start
            self.map_dict = dict(zip(self.map_tile_index, self.map_tile_value))
            self.bg_dict = dict(zip(self.map_tile_index, self.map_tile_value))

        # print(self.map_dict)

    def blit_map(self):
        self.overlay.fill(self.bg)
        i = 0
        for rect in self.map_tiles_interaction:
            subsurface = self.overlay.subsurface(rect)
            try:
                if map1.background_visible:
                    if self.bg_dict.get(self.map_tile_index[i]) != ["key", 0, 0]:
                        a, b, c = self.bg_dict.get(self.map_tile_index[i])[0], self.bg_dict.get(self.map_tile_index[i])[
                            1], \
                                  self.bg_dict.get(self.map_tile_index[i])[2]
                        map_tile = start.tile_set_dict.get(a)[b]
                        map_tile = pygame.transform.rotate(map_tile, c)
                        subsurface.blit(map_tile, [0, 0])
                if map1.foreground_visible:
                    if self.map_dict.get(self.map_tile_index[i]) != ["key", 0, 0]:
                        a, b, c = self.map_dict.get(self.map_tile_index[i])[0], \
                                  self.map_dict.get(self.map_tile_index[i])[
                                      1], \
                                  self.map_dict.get(self.map_tile_index[i])[2]
                        map_tile = start.tile_set_dict.get(a)[b]
                        map_tile = pygame.transform.rotate(map_tile, c)
                        subsurface.blit(map_tile, [0, 0])
            except IndexError:
                self.map_dict[self.map_tile_index[i]] = ["key", 0, 0]
            if self.grid:
                # pygame.draw.rect(subsurface, black, rect, 1)
                subsurface.blit(start.grid_img, [0, 0])
            i += 1

    def scroll_update(self):
        if self.scroll_v != [0, 0]:
            if self.overlay_rect.width > start.screen_rect.width:
                self.scroll_dv[0] += self.scroll_v[0]
            if self.overlay_rect.height > start.screen_rect.height:
                self.scroll_dv[1] += self.scroll_v[1]

    def on_screen_center(self):
        if self.scroll_v != [0, 0]:
            if self.overlay_rect.width > start.screen_rect.width:
                # scroll left
                if self.overlay_rect.left > self.menu_width:
                    self.overlay_rect.left = self.menu_width - 1
                    self.scroll_v = [0, 0]
                    self.scroll_dv[0] = self.scroll_dv_x
                # scroll right
                if self.overlay_rect.right < self.screen_x - self.menu_width:
                    self.overlay_rect.right = self.screen_x - self.menu_width + 1
                    self.scroll_v = [0, 0]
                    self.scroll_dv[0] = - self.scroll_dv_x

            if self.overlay_rect.height > start.screen_rect.height:
                # scroll up
                if self.overlay_rect.top > self.scroll_dv_top:
                    self.overlay_rect.top = - 1
                    self.scroll_v = [0, 0]
                    self.scroll_dv[1] = self.scroll_dv_y
                # scroll down
                if self.overlay_rect.bottom < self.screen_y:
                    self.overlay_rect.bottom = self.screen_y + 1
                    self.scroll_v = [0, 0]
                    self.scroll_dv[1] = - self.scroll_dv_y

    def scroll_method(self, event):
        # scroll function
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_dir:
                self.scroll_v = self.key_dir[event.key]

        elif event.type == pygame.KEYUP:
            if event.key in self.key_dir:
                self.scroll_v = [0, 0]

    def draw_cursor(self, map_scale):

        # draw the cursor
        if self.foreground or self.background:
            if self.cursor_change:
                self.cursor_image = start.tile_set_dict.get(self.interact[0])[self.interact[1]]
                self.cursor = pygame.transform.rotate(self.cursor_image, self.interact[2])
                self.cursor_rect = self.cursor.get_rect()
                self.cursor_rect.center = pygame.mouse.get_pos()

                if map_menu_top.mini_map_tool:
                    self.cursor = pygame.transform.rotozoom(self.cursor, 0, map_scale)
                    self.cursor_rect = self.cursor.get_rect()
                    self.cursor_rect.center = pygame.mouse.get_pos()

            if self.cursor_change and start.screen_rect.contains(self.cursor_rect):
                start.screen.blit(self.cursor, self.cursor_rect)

    def general_map_interaction(self, event, map_position):

        # map interaction
        # pen and eraser
        if map_menu_top.pen_tool or map_menu_top.eraser_tool:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # calculated the relative map_position of the mouse to the original tile map
                if start.screen_rect.collidepoint(event.pos):
                    for rect in self.map_tiles_interaction:
                        if rect.collidepoint(map_position):

                            if event.button == 1:
                                coordinates = self.map_tile_index[self.map_tiles_interaction.index(rect)]
                                if self.foreground:
                                    self.map_dict[coordinates] = self.interact
                                    self.drawing = True
                                if self.background:
                                    self.bg_dict[coordinates] = self.interact
                                    self.drawing = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False

            if self.drawing:
                if event.type == pygame.MOUSEMOTION:
                    if start.screen_rect.collidepoint(event.pos):
                        for rect in self.map_tiles_interaction:
                            if rect.collidepoint(map_position):
                                coordinates = self.map_tile_index[self.map_tiles_interaction.index(rect)]
                                if self.foreground:
                                    self.map_dict[coordinates] = self.interact
                                if self.background:
                                    self.bg_dict[coordinates] = self.interact

    def map_loop(self):

        # how to scale the map mini_map
        screen_scale = start.screen_rect.width / start.screen_rect.height
        overlay_scale = self.overlay_rect.width / self.overlay_rect.height
        if overlay_scale >= screen_scale:
            map_scale = start.screen_rect.width / self.overlay_rect.width
        else:
            map_scale = start.screen_rect.height / self.overlay_rect.height

        # relative cursor map_position to the original sizes
        map_position = tuple(map(lambda i, j: i - j, pygame.mouse.get_pos(),
                                 (self.scroll_dv[0] + (start.screen_rect.centerx - self.overlay_rect.width // 2),
                                  self.scroll_dv[1] + (start.screen_rect.centery - self.overlay_rect.height // 2))))

        moving = False
        moving_bar_x = False
        moving_bar_y = False
        start.run = True
        while start.run:

            start.clock.tick(self.fps)

            # layer interaction
            if not self.background_visible:
                self.background = False
            if not self.foreground_visible:
                self.foreground = False

            # cursor + image position
            if map_menu_top.mini_map_tool:
                # mini map cursor position
                # transform the map to the size of the screen_recet
                copy = pygame.transform.rotozoom(self.overlay, 0, map_scale)
                copy_rect = copy.get_rect()
                copy_rect.center = start.screen_rect.center

                top_left_x = copy_rect.centerx - copy_rect.width // 2
                top_left_y = copy_rect.centery - copy_rect.height // 2

                # adapt the cursor position
                map_position = tuple(map(lambda i, j: i - j, (pygame.mouse.get_pos()[0] // map_scale,
                                                              pygame.mouse.get_pos()[1] // map_scale),
                                         (top_left_x // map_scale, top_left_y // map_scale)))

            elif not map_menu_top.mini_map_tool:
                # relative cursor map_position to the original sizes
                map_position = tuple(map(lambda i, j: i - j, pygame.mouse.get_pos(),
                                         (
                                             self.scroll_dv[0] + (
                                                     start.screen_rect.centerx - self.overlay_rect.width // 2),
                                             self.scroll_dv[1] + (
                                                     start.screen_rect.centery - self.overlay_rect.height // 2))))

            # event loop for pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start.run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        start.run = False
                    # grid on off
                    if event.key == pygame.K_g:
                        if self.grid:
                            self.grid = False
                        else:
                            self.grid = True
                    # fullscreen toggle
                    if event.key == pygame.K_f:
                        if start.fullscreen:
                            start.screen = pygame.display.set_mode((start.SCREEN_X, start.SCREEN_Y))
                            start.fullscreen = False
                        else:
                            start.screen = pygame.display.set_mode((start.SCREEN_X, start.SCREEN_Y), pygame.FULLSCREEN)
                            start.fullscreen = True

                    # tile rotation
                    if event.key == pygame.K_r:
                        self.rotation_method()
                        self.interact = [self.interact[0], self.interact[1], self.rotation]

                    # tile selection from 1 to 18 + the modifier for the next page(s)
                    if event.key in start.tile_key_dict and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        try:
                            if start.tile_key_dict.get(event.key) + 10 in range(len(start.tile_set_dict.get(
                                    self.interact[0]))) and start.tile_key_dict.get(event.key) + 10 <= 18 + (
                                    map_menu_left.menu_index_top * len(map_menu_left.menu_grid_list) / 2):
                                self.interact = [self.interact[0], start.tile_key_dict.get(event.key) + 10 + (
                                        map_menu_left.menu_index_top * len(map_menu_left.menu_grid_list) // 2), 0]
                                map_menu_left.selected_rect = \
                                    map_menu_left.menu_grid_list[start.tile_key_dict.get(event.key) + 10][0]
                        except TypeError:
                            pass
                    elif event.key in start.tile_key_dict:
                        try:
                            if start.tile_key_dict.get(event.key) in range(
                                    len(start.tile_set_dict.get(self.interact[0]))):
                                self.interact = [self.interact[0], start.tile_key_dict.get(event.key) + (
                                        map_menu_left.menu_index_top * len(map_menu_left.menu_grid_list) // 2), 0]
                                map_menu_left.selected_rect = \
                                    map_menu_left.menu_grid_list[start.tile_key_dict.get(event.key)][0]
                        except TypeError:
                            pass

                # mouse scroll (right button + scroll bar)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        if start.x_move_rect_top.collidepoint(event.pos) or start.x_move_rect_bottom.collidepoint(
                                event.pos):
                            moving_bar_x = True
                        elif start.y_move_rect_left.collidepoint(event.pos) or start.y_move_rect_right.collidepoint(
                                event.pos):
                            moving_bar_y = True
                        else:
                            moving = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.scroll_v = [0, 0]
                    moving = False
                    moving_bar_x = False
                    moving_bar_y = False
                elif event.type == pygame.MOUSEMOTION:
                    if moving:
                        self.scroll_v = list(event.rel)
                    elif moving_bar_x:
                        start.x_move_rect_top.centerx = event.pos[0]
                        start.x_move_rect_bottom.centerx = event.pos[0]
                        self.scroll_dv[0] = (start.screen_rect.centerx - start.x_move_rect_top.centerx) / (
                                start.screen_rect.width / self.overlay_rect.width)
                    elif moving_bar_y:
                        start.y_move_rect_left.centery = event.pos[1]
                        start.y_move_rect_right.centery = event.pos[1]
                        self.scroll_dv[1] = (start.screen_rect.centery - start.y_move_rect_left.centery) / (
                                start.screen_rect.height / self.overlay_rect.height)

                # map menu interaction
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # tile menu (left menu)
                        map_menu_left.tile_menu_interaction(event)
                        # tool menu
                        map_menu_top.tool_menu_interaction(event)
                        # options menu
                        map_menu.options_menu_interaction(event)

                # draw and erase stuff on the map with tools or without
                self.general_map_interaction(event, map_position)
                map_menu_top.tool_menu_map_interaction(event, map_position)

                # scrolling
                self.scroll_method(event)

                # fill tool
                if map_menu_top.fill_tool:
                    map_menu_top.fill_tool_method(event, map_position)

            # autofill function
            if self.autofill:
                map_menu.autofill_method()
                self.autofill = False

            # scrolling and testing if the screen shows correctly
            self.scroll_update()
            self.overlay_rect.centerx = self.scroll_dv[0] + start.screen_rect.centerx
            self.overlay_rect.centery = self.scroll_dv[1] + start.screen_rect.centery
            self.on_screen_center()

            # create the objects on screen
            start.screen.fill(map_menu.bg)
            start.screen.blit(self.overlay, self.overlay_rect)

            # show the map
            self.blit_map()

            # show the menus
            start.screen.blit(map_menu_top.SURF, map_menu_top.SURF_rect)
            start.screen.blit(map_menu_left.SURF, map_menu_left.SURF_rect)
            start.screen.blit(map_menu.SURF, map_menu.SURF_rect)

            # draw the tool shapes + mini map funciton
            map_menu_top.render_tool_stuff(map_scale)

            # draw the menus
            map_menu.define_menu_grid_right()
            map_menu_left.define_menu_grid_left()
            map_menu_top.define_menu_grid_top()

            # draw the cursor
            self.draw_cursor(map_scale)

            # draw the scroll rectangles
            pygame.draw.rect(start.screen, white, start.x_move_rect_top)
            pygame.draw.rect(start.screen, white, start.y_move_rect_left)
            pygame.draw.rect(start.screen, white, start.x_move_rect_bottom)
            pygame.draw.rect(start.screen, white, start.y_move_rect_right)

            # change start.state according to the definitions
            start.menu_interaction_states()

            start.state = "map"
            pygame.display.update(start.screen_rect)


# use classes
start = Start()
map_menu = MapMenu(start.SCREEN_X // 8, start.SCREEN_Y, pos_x=start.SCREEN_X * 7 // 8)
map_menu_left = MapMenu(start.SCREEN_X // 8, start.SCREEN_Y)
map_menu_top = MapMenu(start.SCREEN_X // 8 * 6, 64, pos_x=start.SCREEN_X * 1 // 8)

map1 = Map(grid=1, top_border=64, fps=60)

map_menu.menu_grid_right()
map_menu_left.menu_grid_left()
map_menu_top.menu_grid_top()

map1.create_tiled_map(x_pos_start=start.tile_size, y_pos_start=start.tile_size)

# print(map_menu_top.change_rect_list)
map1.map_loop()

pygame.quit()
