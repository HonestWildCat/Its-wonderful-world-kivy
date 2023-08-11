import datetime
import sqlite3
import kivy

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.graphics import Rectangle, Color

# Loading kv files
from kivy.lang import Builder
Builder.load_file('points_calculation_screen.kv')
Builder.load_file('players_rating_screen.kv')
Builder.load_file('games_history_screen.kv')
Builder.load_file('games_full_info_screen.kv')

kivy.require('2.0.0')

# Window size
Window.softinput_mode = "below_target"
if Window.width > Window.height:
    Window.size = (370, 680)

# App background color
Window.clearcolor = (0, 0, 0, 1)

# Connection to database || Creating database if not exist
conn = sqlite3.connect("players_data.db")
cur = conn.cursor()

# Creating tables if not exist
cur.execute("""CREATE TABLE IF NOT EXISTS games_history(
               rowid INTEGER PRIMARY KEY AUTOINCREMENT,
               game_id INT,
               player_name TEXT,
               score INT,
               empire_card INT,
               date TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS categories_multipliers(
               rowid INTEGER PRIMARY KEY AUTOINCREMENT,
               normal_points INT,
               disc_1 INT,
               disc_2 INT,
               money_1 INT,
               money_2 INT,
               sci_1 INT,
               sci_2 INT,
               transport_1 INT,
               transport_2 INT,
               econ_1 INT,
               econ_2 INT,
               general_1 INT,
               general_2 INT)""")

# Color themes
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
# Needed to give each player tab its own id
player_tab_counter = 1


class MyApp(App):
    def __init__(self):
        super().__init__()
        # Setting style/color of elements according to color theme
        self.theme_icon = color_theme[theme]["icon"]
        self.background_color = color_theme[theme]["bg_1"]
        self.background_pressed = color_theme[theme]["bg_2"]
        self.text_color = color_theme[theme]["text"]
        self.rating_icon = color_theme[theme]["rating_icon"]
        self.close_icon = color_theme[theme]["close_icon"]
        self.back_icon = color_theme[theme]["back_icon"]

        self.screen_manager = ScreenManager()

    def build(self):
        # Setting title and icon of the app
        self.title = "It's a Wonderful World"
        self.icon = "img/icon.png"

        # Adding screens to screen manager
        self.screen_manager.add_widget(PointsCalculationScreen())
        self.screen_manager.add_widget(GamesHistoryScreen())
        self.screen_manager.add_widget(PlayersRatingScreen())
        self.screen_manager.add_widget(GamesFullInfoScreen())
        return self.screen_manager


class PointsCalculationScreen(Screen):
    def __init__(self):
        super().__init__()
        self.player_tabs_list = [self.ids.first_player_tab_box,
                                 self.ids.second_player_tab_box,
                                 self.ids.third_player_tab_box,
                                 self.ids.fourth_player_tab_box,
                                 self.ids.fifth_player_tab_box]
        self.tabs_prefix = ["first", "second", "third", "fourth", "fifth"]

    def save_game_data(self):
        def main():
            no_tab_filled = True

            max_game_id_in_database = cur.execute("SELECT MAX(game_id) FROM games_history").fetchone()[0]
            curr_game_id = max_game_id_in_database + 1 if max_game_id_in_database is not None else 0

            for player_tab in self.player_tabs_list:
                # Preventing saving blank player tabs
                if check_fields_filling(player_tab):
                    no_tab_filled = False

                    current_tab = self.ids[f"{self.tabs_prefix[player_tab.current_player_tab - 1]}_player_tab"]
                    player_name = current_tab.text.replace("\n", " ")
                    score = int(player_tab.results_text_list[-1].text.split()[2])
                    empire_card = player_tab.empire_card

                    normal_points_result = int(player_tab.results_text_list[-2].text)

                    insert_values_to_database(curr_game_id, player_name, score, empire_card,
                                              normal_points_result, player_tab.number_inputs_list)

            self.clear_all_players_info()
            print("No values" if no_tab_filled else "saved...")

        def check_fields_filling(tab):
            tab_score = int(tab.ids.final_result_text.text.split()[2])
            return True if tab_score > 0 else False

        def get_formatted_datetime():
            def add_zero(num):
                return num if num > 9 else '0' + str(num)

            curr_datetime = datetime.datetime.now()
            return f"{add_zero(curr_datetime.hour)}:{add_zero(curr_datetime.minute)} " \
                   f"{add_zero(curr_datetime.day)}-{add_zero(curr_datetime.month)}-{add_zero(curr_datetime.year)}"

        def create_input_values_tuple(normal_points, number_inputs_list):
            input_values_list = [normal_points]
            for i in range(0, len(number_inputs_list)-1):
                num = number_inputs_list[i].text
                if i in (9, 11):
                    input_values_list.append(int(num) + 1 if num.isdecimal() else 0)
                else:
                    input_values_list.append(int(num) + 1 if num.isdecimal() else 0)
            return tuple(input_values_list)

        def insert_values_to_database(game_id, player_name, score, empire_card, normal_points, number_inputs_list):
            print(game_id, player_name, score, empire_card, get_formatted_datetime())
            print(create_input_values_tuple(normal_points, number_inputs_list))
            cur.execute("""INSERT INTO games_history (game_id, player_name, score, empire_card, date) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (game_id, player_name, score, empire_card, get_formatted_datetime()))

            cur.execute("""INSERT INTO categories_multipliers 
                               (normal_points,
                               disc_1, disc_2, money_1, money_2, 
                               sci_1, sci_2, transport_1, transport_2, 
                               econ_1, econ_2, general_1, general_2) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        create_input_values_tuple(normal_points, number_inputs_list))

            conn.commit()

        main()

    def change_tab_name(self, player_tab, text):
        current_tab_header = self.ids[f"{self.tabs_prefix[player_tab - 1]}_player_tab"]
        current_tab_header.text = text if (not text.isspace() and text != "") else f"Игрок\n{player_tab}"

    def clear_all_players_info(self):
        for player_tab in self.player_tabs_list:
            player_tab.clear_player_info()

    def to_games_history_screen(self):
        self.manager.current = "GamesHistoryScreen"
        self.manager.transition.direction = "left"
        games_history_screen = self.manager.get_screen("GamesHistoryScreen")
        games_history_screen.show_games_history()

    def to_players_rating_screen(self):
        self.manager.current = "PlayersRatingScreen"
        self.manager.transition.direction = "down"
        players_rating_screen = self.manager.get_screen("PlayersRatingScreen")
        players_rating_screen.show_players_rating()

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

        self.empire_cards_list = ["Unknown", "Panafrican_union", "Noram_states",
                                  "Asian_federation", "Aztec_empire", "European_republic",
                                  "Side_B", "5_crystal"]
        self.empire_card = 0

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

    def build_dropdown(self, empire_cards_dropdown):
        print(empire_cards_dropdown)
        pass

    def change_empire_card(self, empire_cards_select_button):
        self.empire_card = self.empire_card + 1 if self.empire_card < len(self.empire_cards_list) - 1 else 0
        empire_cards_select_button.background_normal = f"img/empire_cards/" \
                                                       f"{self.empire_cards_list[self.empire_card]}.png"
        # print(self.empire_cards_list[self.empire_card])

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
        self.results_text_list[-1].text = f"[b] Результат: {points} [/b]"

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
        self.calculate_result()
        self.empire_card = -1
        self.change_empire_card(self.ids.empire_cards_select_button)


class GamesHistoryScreen(Screen):
    def __init__(self):
        super().__init__()

    def show_games_history(self, query=""):
        query = "%" + query + "%"
        played_games_id_list = cur.execute("""SELECT DISTINCT game_id FROM games_history ORDER BY rowid DESC;""")
        self.build_table(played_games_id_list.fetchall(), searched_player_name=query)

    @staticmethod
    def draw_table_horizontal_lines(data_table_scroll_box, players_in_games):
        data_table_scroll_box.canvas.remove_group(u"table rows")
        players_in_games.reverse()

        line_height = dp(13)
        row_height = dp(31.5)

        lines_sum_height = line_height
        row_sum_height = row_height

        for game in players_in_games:
            for player in range(game):
                if player == game - 1:
                    lines_sum_height += line_height
                with data_table_scroll_box.canvas:
                    Color(rgba=(MyApp().text_color[0], MyApp().text_color[1], MyApp().text_color[2], 0.1))
                    Rectangle(pos=(data_table_scroll_box.x,
                                   data_table_scroll_box.y + lines_sum_height + row_sum_height),
                              size=(Window.width, dp(2)),
                              group=u"table rows")
                row_sum_height += row_height
            lines_sum_height += line_height

    def build_table(self, games_id_list, searched_player_name=""):
        def create_label(text, size_hint=(1, 1)):
            label = Label(text=f"{text}", size_hint=size_hint)
            data_table_box.add_widget(label)

        data_table_scroll_box = self.ids.data_table_scroll_box
        data_table_scroll_box.clear_widgets()

        number_counter = 1
        players_in_game = []

        data_table_scroll_box.add_widget(Button(background_color=(0, 0, 0, 0)))

        for game_id in games_id_list:
            game_id = game_id[0], searched_player_name
            players_data = cur.execute("""SELECT rowid, player_name, score, date 
                                          FROM games_history WHERE game_id = ? AND player_name LIKE ?
                                          ORDER BY score DESC;""", game_id).fetchall()

            for player_data in players_data:

                data_table_box = GridLayout(cols=5, size_hint=[.9, 1])
                data_table_scroll_box.add_widget(data_table_box)

                create_label(number_counter, [.3, 1])
                create_label(player_data[1], [.7, 1])
                create_label(player_data[2], [.35, 1])
                create_label(player_data[3], [.85, 1])

                # delete_button_box = AnchorLayout(anchor_x="left", anchor_y="center", size_hint=[.1, 1])
                # data_table_box.add_widget(delete_button_box)
                # delete_button = Button(text="x", size_hint=[.2, .3])
                # delete_button.bind(on_press=self.delete_player_game_info)
                # delete_button_box.add_widget(delete_button)

                number_counter += 1
            players_in_game.append(len(players_data))

            if players_data:
                data_table_scroll_box.add_widget(Button(background_normal='img/line_separator_white.png',
                                                        background_down='img/line_separator_white.png'))

        self.draw_table_horizontal_lines(data_table_scroll_box, players_in_game)

    def color_table_rows(self):
        for row in self.ids.data_table_scroll_box.children:
            with row.canvas:
                Color(rgba=(0, .5, .7, 1))
                Rectangle(pos=row.pos, size=row.size)

    def delete_player_game_info(self):
        print("delete_player_game_info")

    def to_points_calculation_screen(self):
        self.manager.current = "PointsCalculationScreen"
        self.manager.transition.direction = "right"

    def to_players_rating_screen(self):
        self.manager.current = "PlayersRatingScreen"
        self.manager.transition.direction = "down"


class PlayersRatingScreen(Screen):
    def __init__(self, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.empire_cards_list = ["Unknown", "Panafrican_union", "Noram_states",
                                  "Asian_federation", "Aztec_empire", "European_republic",
                                  "Side_B", "5_crystal"]

    def show_players_rating(self):
        best_players = self.get_first_5_players()
        self.build_rank_table(best_players)

    def get_first_5_players(self):
        best_players_list = []
        player_rank = 1
        best_players = cur.execute("""SELECT game_id, player_name, score, empire_card, date FROM games_history
                                      ORDER BY score DESC LIMIT 5;""").fetchall()
        for player in best_players:
            players_in_game = cur.execute("""SELECT COUNT(rowid) FROM games_history 
                                             WHERE game_id = ?;""", (player[0],)).fetchone()
            best_players_list.append((player_rank, player[1], player[2], self.empire_cards_list[player[3]],
                                      players_in_game[0], player[4]))
            player_rank += 1
        return best_players_list

    def build_rank_table(self, best_players):
        table_main_box = self.ids.table_main_box
        table_main_box.clear_widgets()

        for player in best_players:
            player_main_centring_box = AnchorLayout(anchor_x="center", anchor_y="center")
            table_main_box.add_widget(player_main_centring_box)
            player_main_box = BoxLayout(orientation="horizontal", size_hint=[.9, 1])
            player_main_centring_box.add_widget(player_main_box)

            player_rating = Label(text=str(player[0]), size_hint=[.15, 1])
            player_main_box.add_widget(player_rating)

            player_info_box = BoxLayout(orientation="vertical")
            player_main_box.add_widget(player_info_box)

            player_name_and_score = Label(text=f"{player[1]} - {player[2]}")
            player_info_box.add_widget(player_name_and_score)

            player_empire_card_and_players_box = BoxLayout(orientation="horizontal")
            player_info_box.add_widget(player_empire_card_and_players_box)
            player_empire_card_box = AnchorLayout(anchor_x="center", anchor_y="center")
            player_empire_card_and_players_box.add_widget(player_empire_card_box)
            empire_card_image = Image(source=f'img/empire_cards/{player[3]}.png')
            player_empire_card_box.add_widget(empire_card_image)

            player_players_count_box = AnchorLayout(anchor_x="center", anchor_y="center")
            player_empire_card_and_players_box.add_widget(player_players_count_box)
            players_count_image = Image(source=f'img/players.png')
            player_players_count_box.add_widget(players_count_image)
            players_count = Label(text=f"{player[4]}")
            player_players_count_box.add_widget(players_count)

            player_game_time = Label(text=f"{player[5]}")
            player_info_box.add_widget(player_game_time)

            right_place_holder = Label(size_hint=[.15, 1])
            player_main_box.add_widget(right_place_holder)
        print(best_players)

    def to_points_calculation_screen(self):
        self.manager.current = "PointsCalculationScreen"
        self.manager.transition.direction = "up"

    def to_games_full_info_screen(self):
        self.manager.current = "GamesFullInfoScreen"
        self.manager.transition.direction = "down"
        games_full_info_screen = self.manager.get_screen("GamesFullInfoScreen")
        games_full_info_screen.show_full_games_info()


class GamesFullInfoScreen(Screen):
    def show_full_games_info(self):
        full_games_info = self.get_full_games_info()
        self.build_table(full_games_info)

    @staticmethod
    def get_full_games_info():
        return cur.execute("""SELECT game_id, player_name,empire_card, score,  
                              normal_points, disc_1, disc_2, money_1, money_2, sci_1, sci_2, transport_1, transport_2,
                              econ_1, econ_2, general_1, general_2, date 
                              FROM games_history JOIN categories_multipliers 
                              ON games_history.rowid = categories_multipliers.rowid""").fetchall()

    def build_table(self, full_games_info):
        data_table_scroll_box = self.ids.data_table_scroll_box
        data_table_scroll_box.clear_widgets()
        data_table_scroll_box.add_widget(Label())
        data_table_scroll_box.add_widget(Label(text="     game_id, player_name,empire_card, score,"
                                                    "normal_points, disc_1, disc_2, money_1, money_2, sci_1,"
                                                    "sci_2, transport_1, transport_2,"
                                                    "econ_2, general_1, general_2, date     "))
        for player in full_games_info:
            data_table_scroll_box.add_widget(Label(text=f"{player}"))

    def to_points_calculation_screen(self):
        self.manager.current = "PointsCalculationScreen"
        self.manager.transition.direction = "up"

    def to_players_rating_screen(self):
        self.manager.current = "PlayersRatingScreen"
        self.manager.transition.direction = "up"


if __name__ == '__main__':
    MyApp().run()

# Close connection with database
conn.close()
