import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests
from bs4 import BeautifulSoup

kivy.require("1.10.1")

class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)  
        self.cols = 2

        self.count = 0
        self.submit = Button(text="Scrape", font_size=40)
        self.submit.bind(on_press=self.scrape)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Search", font_size=40)
        self.submit.bind(on_press=self.search)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Export Data", font_size=40)
        self.submit.bind(on_press=self.export)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Add New Feed", font_size=40)
        self.submit.bind(on_press=self.addfeed)
        self.add_widget(self.submit)

    def scrape(self, instance):
        self.count += 1
        upcount = self.count
        print("Scrape button pressed ", upcount)
        data = requests.get('https://au.norton.com/online-threats/threats.html')

        soup = BeautifulSoup(data.text, 'html.parser')

        for tr in soup.find_all('tr'):
            for td in tr.find_all('td'):
                print(td.text)
        data = requests.get(
            'https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/exploit-kits.html')

        soup = BeautifulSoup(data.text, 'html.parser')

        for tr in soup.find_all('tr'):
            for td in tr.find_all('td'):
                print(td.text)

    def search(self, instance):
        self.count += 1
        upcount = self.count
        print("Search button pressed ", upcount)

    def export(self, instance):
        self.count += 1
        upcount = self.count
        print("Export button pressed ", upcount)

    def addfeed(self, instance):
        self.count += 1
        upcount = self.count
        print("Add Feed button pressed ", upcount)

class MyApp(App):
    def build(self):
        return MyGrid()


myApp = MyApp()
myApp.run()

print("Application has ended")
