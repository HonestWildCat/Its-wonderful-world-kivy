import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Window size
from kivy.core.window import Window
Window.size = (450, 800)

# Window.clearcolor = (0.09, 0.09, 0.12, 1.0)


class MyApp(App):
    image_list = ["discoveries", "money", "science", "transport", "economist", "general"]
    inputs_list = []
    intermediate_results_list = []

    def build_structure(self):
        # Main box
        outer_box = AnchorLayout(anchor_x="center", anchor_y="center")
        main_box = BoxLayout(orientation='vertical', size_hint=(0.9, 1))
        outer_box.add_widget(main_box)
        
        # Header
        header_box = BoxLayout(orientation='vertical',
                               size_hint=(1, 0.7))
        main_box.add_widget(header_box)        
        header = Label(text="∆ Подсчёт очков ∆", font_size="30sp")
        header_box.add_widget(header)
 
        # Normal points
        points_box = BoxLayout(orientation='vertical')
        main_box.add_widget(points_box)
                
        desc = Label(text="Обычные очки:", font_size="20sp")
        points_box.add_widget(desc)

        input_and_button_box = BoxLayout(orientation='horizontal',
                                         size_hint=(1, 0.7))
        points_box.add_widget(input_and_button_box)

        self.points_input = TextInput(hint_text="0", halign="center", multiline=False, font_size="20sp",
                                      size_hint=(0.8, 1))
        input_and_button_box.add_widget(self.points_input)
        self.points_input.bind(text=self.on_input_change)

        erase_button = Button(text="x", font_size="20sp",
                              size_hint=(0.2, 1),
                              background_color=[0.95, 0.3, 0.3, 1])
        input_and_button_box.add_widget(erase_button)
        erase_button.bind(on_press=self.erase_input_values)
        
        self.normal_points_result = Label(text="0", font_size="15sp",
                                          size_hint=(1, 0.5))
        points_box.add_widget(self.normal_points_result)

        # Points with multipliers
        self.points_with_multipliers_builder(main_box)

        # Result
        result_box = BoxLayout(orientation='vertical')
        main_box.add_widget(result_box)
        self.result = Label(text="Результат: 0", font_size="20sp")
        result_box.add_widget(self.result)
        
        return outer_box

    def points_with_multipliers_builder(self, main_box):
        for i in range(1, 4):
            outerbox = BoxLayout(orientation='horizontal')
            main_box.add_widget(outerbox)
            for o in range(2):
                # Inner section
                innerbox = BoxLayout(orientation='vertical')
                outerbox.add_widget(innerbox)

                # Image
                img = Image(source=f'img/{self.image_list[i * 2 + o - 2]}.jpg')
                innerbox.add_widget(img)

                # Inputs
                input_box = BoxLayout(orientation='horizontal',
                                      size_hint=(1, 0.6))
                innerbox.add_widget(input_box)
                self.inputs_list.append([])

                input1 = TextInput(hint_text="0", halign="center", multiline=False, font_size="18sp")
                input1.bind(text=self.on_input_change)
                input_box.add_widget(input1)
                self.inputs_list[-1].append(input1)

                multiply_sign = Label(text="x", font_size="20sp",
                                      size_hint=(0.3, 1))
                input_box.add_widget(multiply_sign)

                input2 = TextInput(hint_text="0" if i * 2 + o - 1 < 5 else "1",
                                   halign="center", multiline=False, font_size="20sp")
                input2.bind(text=self.on_input_change)
                input_box.add_widget(input2)
                self.inputs_list[-1].append(input2)

                # Intermediate result
                intermediate_result = Label(text="0",
                                            size_hint=(1, 0.5))
                innerbox.add_widget(intermediate_result)
                self.intermediate_results_list.append(intermediate_result)

                if not o:
                    invisible_separator_box = BoxLayout(size_hint=(0.3, 1))
                    outerbox.add_widget(invisible_separator_box)

    def on_input_change(self, instance, value):
        self.calculate_result()
        # Input properties:
        # hint_text hint_text_color keyboard background_color
        # border center focused font_family font_size ids input_filter
        # input_type keyboard_mode line_height line_spacing opacity padding padding_x padding_y
        # selection_color selection_text size size_hint text

    def calculate_result(self):
        points = self.calculate_points_expression()
        for input_block in self.inputs_list:
            num1 = int(input_block[0].text) if input_block[0].text.isdecimal() else 0
            num2 = int(input_block[1].text) if input_block[1].text.isdecimal() else 0
            if input_block != self.inputs_list[-1] and input_block != self.inputs_list[-2]:
                points += num1 * num2
            else:
                points += num1 * (num2 + 1)
        self.result.text = f"Результат: {points}"

    def calculate_points_expression(self):
        nums_in_expression = [""]
        for i in self.points_input.text:
            if i.isdecimal():
                nums_in_expression[len(nums_in_expression) - 1] += i
            elif nums_in_expression[len(nums_in_expression) - 1] != "":
                nums_in_expression.append("")
        return sum([int(j) for j in nums_in_expression if j.isdecimal()])

    def erase_input_values(self, instance):
        self.points_input.text = ""
        for input_block in self.inputs_list:
            input_block[0].text = ""
            input_block[1].text = ""

    def build(self):
        return self.build_structure()


if __name__ == '__main__':
    MyApp().run()
