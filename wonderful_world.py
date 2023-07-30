import datetime
import sqlite3
import kivy

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp


from kivy.lang import Builder
Builder.load_file('points_calculation_screen.kv')
Builder.load_file('players_rating_screen.kv')
Builder.load_file('games_history_screen.kv')

kivy.require('2.0.0')

# Window size
Window.softinput_mode = "below_target"
if Window.width > Window.height:
    # Window.size = (450, 800)
    Window.size = (370, 680)

# App background color
Window.clearcolor = (0, 0, 0, 1)
conn = sqlite3.connect("test.db")
cur = conn.cursor()

# themes_list = ["night", "day", "evening", "blue"]
theme = "night"

color_theme = {
    "night": {
        "bg_1": (0.15, 0.15, 0.15, 1),
        "bg_2": (.35, .35, .35, 1),
        "text": (1, 1, 1, 1),
        "icon": "img/night.png",
        "rating_icon": "img/rating_icon_white.png",
        "close_icon": "img/close.png",
        "back_icon": "img/left_arrow_white.png",
        "pressed_icon": "img/.png"},
    "day": {
        "bg_1": (1, 1, 1, 1),
        "bg_2": (.7, .7, .7, 1),
        "text": (0, 0, 0, 1),
        "icon": "img/day.png",
        "rating_icon": "img/rating_icon_black.png",
        "close_icon": "img/close.png",
        "back_icon": "img/left_arrow_black.png",
        "pressed_icon": "img/.png"},
    "evening": {
        "bg_1": (239/255, 222/255, 205/255, 1),
        "bg_2": (190/255, 165/255, 155/255, 1),
        "text": (0, 0, 0, 1),
        "icon": "img/evening.png",
        "rating_icon": "img/rating_icon_black.png",
        "close_icon": "img/close.png",
        "back_icon": "img/left_arrow_black.png",
        "pressed_icon": "img/.png"},
    "blue": {
        "bg_1": (10/255, 20/255, 50/255, 1),
        "bg_2": (0, .3, .35, 1),
        "text": (.3, 1, 1, 1),
        "icon": "img/blue.png",
        "rating_icon": "img/rating_icon_white.png",
        "close_icon": "img/close.png",
        "back_icon": "img/left_arrow_white.png",
        "pressed_icon": "img/.png"}
}

player_tab_counter = 1


class MyApp(App):
    def __init__(self):
        super().__init__()
        self.theme_icon = color_theme[theme]["icon"]
        self.background_color = color_theme[theme]["bg_1"]
        self.background_pressed = color_theme[theme]["bg_2"]
        self.text_color = color_theme[theme]["text"]
        self.rating_icon = color_theme[theme]["rating_icon"]
        self.close_icon = color_theme[theme]["close_icon"]
        self.back_icon = color_theme[theme]["back_icon"]

    def build(self):
        self.title = "It's a Wonderful World"
        self.icon = "img/icon_min.png"

        screen_manager = ScreenManager()
        screen_manager.add_widget(PointsCalculationScreen())
        screen_manager.add_widget(GamesHistoryScreen())
        screen_manager.add_widget(PlayersRatingScreen())
        return screen_manager


class PointsCalculationScreen(Screen):
    def __init__(self):
        super().__init__()

    def save_game_data(self):

        def get_formatted_datetime():
            def add_zero(num):
                return num if num > 9 else '0' + str(num)

            curr_datetime = datetime.datetime.now()
            return f"{add_zero(curr_datetime.hour)}:{add_zero(curr_datetime.minute)} " \
                   f"{add_zero(curr_datetime.day)}-{add_zero(curr_datetime.month)}-{add_zero(curr_datetime.year)}"

        def create_input_values_tuple():
            input_values_list = []
            for i in range(1, len(PlayerTab.number_inputs_list), 2):
                num1 = PlayerTab.number_inputs_list[i].text
                num2 = PlayerTab.number_inputs_list[i + 1].text
                input_values_list.append(int(num1) if num1.isdecimal() else 0)
                input_values_list.append(int(num2) + int(i > 8) if num2.isdecimal() else 0)
                # print(input_values_list)
                # print(tuple(input_values_list))
            return tuple(input_values_list)

        normal_points = PlayerTab.calculate_points_expression(PlayerTab.number_inputs_list[0])
        current_game_id = cur.execute("SELECT MAX(game_id) FROM games_history").fetchone()[0] + 1

        cur.execute("""INSERT INTO games_history
                   (game_id,player_name,score,empire_card,date,normal_points)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                    (current_game_id, PlayerTab.ids.player_name_input.text,
                     int(PlayerTab.results_text_list[-1].text.split(" ")[1]),
                     None, get_formatted_datetime(), normal_points))

        cur.execute("""INSERT INTO categories_multipliers 
                   (disc_1, disc_2, money_1, money_2, 
                   sci_1, sci_2, transport_1, transport_2, 
                   econ_1, econ_2, general_1, general_2) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    create_input_values_tuple())
        conn.commit()
        self.clear_player_info()
        print("saved...")

    def change_tab_name(self, player_tab, text):
        if player_tab == 1:
            self.ids.first_player_tab.text = text
        elif player_tab == 2:
            self.ids.second_player_tab.text = text
        elif player_tab == 3:
            self.ids.third_player_tab.text = text
        elif player_tab == 4:
            self.ids.fourth_player_tab.text = text
        else:
            self.ids.fifth_player_tab.text = text

    def to_games_history_screen(self):
        self.manager.current = "GamesHistoryScreen"
        self.manager.transition.direction = "left"
        games_history_screen = self.manager.get_screen("GamesHistoryScreen")
        games_history_screen.show_games_history()

    def to_players_rating_screen(self):
        self.manager.current = "PlayersRatingScreen"
        self.manager.transition.direction = "down"

    def change_color_theme(self):
        global theme
        themes_list = ["night", "day", "evening", "blue"]
        theme_index = 0 if themes_list.index(theme) + 1 >= len(themes_list) else themes_list.index(theme) + 1
        theme = themes_list[theme_index]
        self.ids.change_color_theme_button.background_normal = f"img/{themes_list[theme_index]}.png"
        print(theme)


class PlayerTab(AnchorLayout):

    def __init__(self, **kwargs):
        super(PlayerTab, self).__init__(**kwargs)

        global player_tab_counter
        self.current_player_tab = player_tab_counter
        player_tab_counter += 1

        self.categories_names_list = ["discoveries", "money", "science", "transport", "economist", "general"]
        self.number_inputs_list = []
        self.results_text_list = []
        self.current_category = -1
        # self.build_category_blocks()
        self.build_dropdown()

    def add_category_inputs(self, category_inputs_box):
        if self.current_category > 3:
            first_category_input, multiply_sign_text, second_category_input = category_inputs_box.children[0].children
            multiply_sign_text.text = "x ("
            multiply_sign_text.size_hint = (.5, .8)
            multiply_sign_text.font_size = dp(18)

            category_inputs_box.children[0].add_widget(Label(text=" + 1)",
                                                             size_hint=(.5, .8),
                                                             font_size=dp(18),
                                                             color=MyApp().text_color))

    def return_category_image(self):
        self.current_category += 1
        return f"img/{self.categories_names_list[self.current_category]}.png"

    def add_widget_to_list(self, list_name_string, widget):
        if list_name_string == "number_inputs_list":
            self.number_inputs_list.append(widget)
        elif list_name_string == "results_text_list":
            self.results_text_list.append(widget)

    def build_dropdown(self):
        pass

    def calculate_result(self):
        # Normal points
        points = self.calculate_points_expression(self.number_inputs_list[-1])
        self.results_text_list[-2].text = str(points)

        # Categories
        for i in range(0, 12, 2):
            num1 = self.calculate_points_expression(self.number_inputs_list[i])
            num2 = self.calculate_points_expression(self.number_inputs_list[i + 1])
            if i > 6:
                self.results_text_list[i // 2].text = str(num1 * (num2 + 1))
                points += num1 * (num2 + 1)
            else:
                self.results_text_list[i // 2].text = str(num1 * num2)
                points += num1 * num2
        self.results_text_list[-1].text = f"Результат: {points}"

    @staticmethod
    def calculate_points_expression(element):
        nums_in_expression = [""]
        for character in element.text:
            if character.isdecimal():
                nums_in_expression[-1] += character
            elif nums_in_expression[-1] != "":
                nums_in_expression.append("")
        return sum([int(num) for num in nums_in_expression if num.isdecimal()])

    def clear_player_info(self):
        for num_input in self.number_inputs_list:
            num_input.text = ""
        self.ids.player_name_input.text = ""
        self.ids.first_player_tab.text = "Игрок\n1"
        self.calculate_result()


class GamesHistoryScreen(Screen):
    def __init__(self):
        super().__init__()
        # self.show_games_history()

    def show_games_history(self):
        played_games_id_list = cur.execute("""SELECT DISTINCT game_id FROM games_history ORDER BY rowid DESC;""")
        self.build_table(played_games_id_list.fetchall())

    #         label = Label(text=f"{row}")
    #         # with label.canvas:
    #         #     Color(0, 1, 0, 1)
    #         #     Rectangle(pos=label.pos, size=label.size)
    #         row_main_box.add_widget(label)
    #         data_table_box.add_widget(row_main_box)

    def build_table(self, games_id_list):

        data_table_scroll_box = self.ids.data_table_scroll_box
        data_table_scroll_box.clear_widgets()

        # data_table_scroll_box.add_widget(BoxLayout())
        number_counter = 1
        for game_id in games_id_list:
            players_data = cur.execute("""SELECT rowid, player_name, score, date 
                                          FROM games_history WHERE game_id = ? 
                                          ORDER BY score DESC;""", game_id).fetchall()
            print()
            data_table_centring_box = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_y=None)
            data_table_scroll_box.add_widget(data_table_centring_box)

            data_table_box = GridLayout(cols=4, size_hint=[.9, 1])
            data_table_centring_box.add_widget(data_table_box)

            def create_label(text, size_hint=(1, 1)):
                label = Label(text=f"{text}", size_hint=size_hint)
                # with label.canvas:
                #     Color(rgba=themes_table_background_colors[theme])
                #     Rectangle(pos=label.pos, size=label.size)
                data_table_box.add_widget(label)

            for player_data in players_data:
                print(player_data)
                create_label(number_counter, [.3, 1])
                create_label(player_data[1], [.7, 1])
                create_label(player_data[2], [.5, 1])
                create_label(player_data[3])

                number_counter += 1

                # delete_button_box = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=[.1, 1])
                # data_table_box.add_widget(delete_button_box)
                # delete_button = Button(text="x", size_hint=[dp(1), .5])
                # delete_button.bind(on_press=self.delete_player_game_info)
                # delete_button_box.add_widget(delete_button)

    def to_points_calculation_screen(self):
        self.manager.current = "PointsCalculationScreen"
        self.manager.transition.direction = "right"

    def to_players_rating_screen(self):
        self.manager.current = "PlayersRatingScreen"
        self.manager.transition.direction = "down"


class PlayersRatingScreen(Screen):

    def to_points_calculation_screen(self):
        self.manager.current = "PointsCalculationScreen"
        self.manager.transition.direction = "up"


if __name__ == '__main__':
    MyApp().run()
