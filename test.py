import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class RoomMapApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical")
        button = Button(text="Save Map")
        layout.add_widget(button)
        button.bind(on_press=self.save_map)
        return layout

    def save_map(self, instance):
        # ...
        pass

if __name__ == "__main__":
    kivy.require("2.0.0")
    RoomMapApp().run()