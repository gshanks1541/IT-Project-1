import kivy
from kivy.app import App
from kivy.uix.button import Label, Button
from kivy.uix.gridlayout import GridLayout

kivy.require("1.10.1")


class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)  # Use **kwargs because we don't know how many arguments we may receive.
        self.cols = 2

        self.count = 0
        self.submit = Button(text="Scrape", font_size=40)
        self.submit.bind(on_press=self.pressed)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Search", font_size=40)
        self.submit.bind(on_press=self.pressed)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Export Data", font_size=40)
        self.submit.bind(on_press=self.pressed)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Add New Feed", font_size=40)
        self.submit.bind(on_press=self.pressed)
        self.add_widget(self.submit)

    def pressed(self, instance):
        self.count += 1
        upcount = self.count
        print("Go button pressed ", upcount)


class MyApp(App):
    def build(self):
        return MyGrid()


myApp = MyApp()
myApp.run()

print("Application has ended")
