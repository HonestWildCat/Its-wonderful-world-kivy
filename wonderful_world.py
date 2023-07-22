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
# from kivy.uix.button import Button
# from kivy.graphics import Color, Rectangle
# from kivy.metrics import dp

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


class MyApp(App):
    def build(self):
        self.title = "It's a Wonderful World"
        self.icon = "img/icon_min.png"

        screen_manager = ScreenManager()
        screen_manager.add_widget(PointsCalculationScreen())
        screen_manager.add_widget(GamesHistoryScreen())
        screen_manager.add_widget(PlayersRatingScreen())
        return screen_manager


class PointsCalculationScreen(Screen):
    categories_names_list = ["discoveries", "money", "science", "transport", "economist", "general"]
    number_inputs_list = []
    results_text_list = []

    def __init__(self):
        super().__init__()
        self.build_category_blocks()
        self.build_dropdown()

    def build_category_blocks(self):
        self.number_inputs_list.append(self.ids.normal_points_input)
        self.results_text_list.append(self.ids.normal_points_result_text)

        category_grid_box = self.ids.category_grid_box
        for i in range(6):
            category_centring_box = AnchorLayout(anchor_x="center", anchor_y="center")
            category_grid_box.add_widget(category_centring_box)
            category_main_box = BoxLayout(orientation='vertical', size_hint=[.9, .9])
            category_centring_box.add_widget(category_main_box)

            category_image_box = AnchorLayout(anchor_x="center", anchor_y="center")
            category_main_box.add_widget(category_image_box)
            category_image = Image(source=f'img/{self.categories_names_list[i]}.png')
            category_image_box.add_widget(category_image)

            category_inputs_box = BoxLayout(orientation='horizontal')
            category_main_box.add_widget(category_inputs_box)
            first_category_input = TextInput(hint_text="0", halign="center", multiline=False,
                                             size_hint=[.8, .7], font_size=20)
            category_inputs_box.add_widget(first_category_input)
            self.number_inputs_list.append(first_category_input)
            first_category_input.bind(text=self.calculate_result)

            multiply_sign_text = Label(text="x",  size_hint=[.5, .9], font_size=20)
            category_inputs_box.add_widget(multiply_sign_text)

            second_category_input = TextInput(hint_text="0", halign="center", multiline=False,
                                              size_hint=[.8, .7], font_size=20)
            category_inputs_box.add_widget(second_category_input)
            self.number_inputs_list.append(second_category_input)
            second_category_input.bind(text=self.calculate_result)

            category_result_text = Label(text="0", size_hint=[1, .3])
            category_main_box.add_widget(category_result_text)
            self.results_text_list.append(category_result_text)

            if i > 3:
                multiply_sign_text.text = "x ("
                multiply_sign_text.size_hint = [.6, .9]
                category_inputs_box.add_widget(Label(text=" + 1)",  size_hint=[.5, .9], font_size=20))
                category_result_text.size_hint = [.8, .5]

        self.results_text_list.append(self.ids.final_result_text)

    def build_dropdown(self):
        pass

    def calculate_result(self, *args, **kwargs):
        print(args)
        print(kwargs)
        points = self.calculate_points_expression(self.number_inputs_list[0])
        self.results_text_list[0].text = str(points)
        for i in range(2, 14, 2):
            num1 = self.calculate_points_expression(self.number_inputs_list[i - 1])
            num2 = self.calculate_points_expression(self.number_inputs_list[i])
            if i > 8:
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

    def change_tab_name(self, text):
        self.ids.first_player_tab.text = text

    def save_game_data(self):

        def get_formatted_datetime():
            def add_zero(num):
                return num if num > 9 else '0' + str(num)

            curr_datetime = datetime.datetime.now()
            return f"{add_zero(curr_datetime.hour)}:{add_zero(curr_datetime.minute)} " \
                   f"{add_zero(curr_datetime.day)}-{add_zero(curr_datetime.month)}-{add_zero(curr_datetime.year)}"

        def create_input_values_tuple():
            input_values_list = []
            for i in range(1, len(self.number_inputs_list), 2):
                num1 = self.number_inputs_list[i].text
                num2 = self.number_inputs_list[i + 1].text
                input_values_list.append(int(num1) if num1.isdecimal() else 0)
                input_values_list.append(int(num2) + int(i > 8) if num2.isdecimal() else 0)
                print(input_values_list)
                print(tuple(input_values_list))
            return tuple(input_values_list)

        normal_points = self.calculate_points_expression(self.number_inputs_list[0])
        current_game_id = cur.execute("SELECT MAX(game_id) FROM games_history").fetchone()[0] + 1

        cur.execute("""INSERT INTO games_history
                   (game_id,player_name,score,empire_card,date,normal_points)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                    (current_game_id, self.ids.player_name_input.text,
                     int(self.results_text_list[-1].text.split(" ")[1]),
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

    def to_games_history_screen(self):
        self.manager.current = "GamesHistoryScreen"
        self.manager.transition.direction = "left"
        games_history_screen = self.manager.get_screen("GamesHistoryScreen")
        games_history_screen.show_games_history()

    def to_players_rating_screen(self):
        self.manager.current = "PlayersRatingScreen"
        self.manager.transition.direction = "right"


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

            for player_data in players_data:
                print(player_data)
                rowid = Label(text=f"{number_counter}", size_hint=[.3, 1])
                data_table_box.add_widget(rowid)
                player_name = Label(text=f"{player_data[1]}", size_hint=[.7, 1])
                data_table_box.add_widget(player_name)
                score = Label(text=f"{player_data[2]}", size_hint=[.5, 1])
                data_table_box.add_widget(score)
                date = Label(text=f"{player_data[3]}")
                data_table_box.add_widget(date)

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
        self.manager.transition.direction = "left"


class PlayersRatingScreen(Screen):

    def to_points_calculation_screen(self):
        self.manager.current = "PointsCalculationScreen"
        self.manager.transition.direction = "left"


if __name__ == '__main__':
    MyApp().run()
