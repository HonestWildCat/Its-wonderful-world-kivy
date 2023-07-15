import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Window size
from kivy.core.window import Window
if Window.width > Window.height:
    Window.size = (450, 800)

# App background color
# Window.clearcolor = (0.09, 0.09, 0.12, 1.0)


class MyApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(PointsCalculationScreen())
        screen_manager.add_widget(GamesHistoryScreen())
        screen_manager.add_widget(PlayersRatingScreen())
        return screen_manager


class PointsCalculationScreen(Screen):
    image_names_list = ["discoveries", "money", "science", "transport", "economist", "general"]
    number_inputs_list = []
    intermediate_results_id_list = ["normal_points_result_text"]

    def __init__(self):
        super().__init__()
        self.build_category_blocks()

    def build_category_blocks(self):
        self.number_inputs_list.append(self.ids.normal_points_input)
        category_grid_box = self.ids.category_grid_box
        for i in range(6):
            category_centring_box = AnchorLayout(anchor_x="center", anchor_y="center")
            category_grid_box.add_widget(category_centring_box)
            category_main_box = BoxLayout(orientation='vertical')
            category_centring_box.add_widget(category_main_box)

            category_image_box = AnchorLayout(anchor_x="center", anchor_y="center")
            category_main_box.add_widget(category_image_box)
            category_image = Image(source=f'img/{self.image_names_list[i]}.jpg')
            category_image_box.add_widget(category_image)

            category_inputs_box = BoxLayout(orientation='horizontal')
            category_main_box.add_widget(category_inputs_box)
            first_category_input = TextInput(hint_text="0")
            category_inputs_box.add_widget(first_category_input)
            self.number_inputs_list.append(first_category_input)

            multiply_sign_text = Label(text="x")
            category_inputs_box.add_widget(multiply_sign_text)

            second_category_input = TextInput(hint_text="0")
            category_inputs_box.add_widget(second_category_input)
            self.number_inputs_list.append(second_category_input)
            if i > 3:
                multiply_sign_text.text = "x ("
                category_inputs_box.add_widget(Label(text=" + 1)"))

            category_result_text = Label(text="x")
            category_main_box.add_widget(category_result_text)


class GamesHistoryScreen(Screen):
    pass


class PlayersRatingScreen(Screen):
    pass


if __name__ == '__main__':
    MyApp().run()
