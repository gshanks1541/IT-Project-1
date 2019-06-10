import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from pymongo import MongoClient
import requests
from datetime import datetime
from bs4 import BeautifulSoup

kivy.require("1.10.1")

class MyGrid(GridLayout):
    numScraped = 0;
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 2

        self.count = 0
        self.submit = Button(text="Web Scrape", font_size=40)
        self.submit.bind(on_press=self.webscrape)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Twitter Scrape", font_size=40)
        self.submit.bind(on_press=self.twitterscrape)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="News Scrape", font_size=40)
        self.submit.bind(on_press=self.newsscrape)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Update DB", font_size=40)
        self.submit.bind(on_press=self.updatedb)
        self.add_widget(self.submit)

        self.count = 0
        self.submit = Button(text="Search Threat:", font_size=40)
        self.submit.bind(on_press=self.search)
        self.add_widget(self.submit)

        self.input = TextInput(multiline=False)
        self.add_widget(self.input)

    def scrape_mcafee_table(self, db_col, threat_type, url):
        data = requests.get(url)
        soup = BeautifulSoup(data.text, "html.parser")

        for tr in soup.find_all("tr"):
            name = None
            source = None
            date = datetime.now()
            description = None
            for l in tr.find_all('a', class_="tldThreatName"):
                source = "https://www.mcafee.com" + l["href"]
                break

            count = 0;
            for td in tr.find_all("td"):
                if count == 0:
                    name = td.text
                elif count == 1:
                    description = td.text
                count += 1
            if name is None:
                continue

            data2 = requests.get(source)
            soup2 = BeautifulSoup(data2.text, "html.parser")
            for tr in soup2.find_all("tr"):
                count = 0;
                for td in tr.find_all("td"):
                    if count == 1:
                        date = datetime.strptime(td.text, "%Y-%m-%d")
                    count += 1

            existing_record_matches = db_col.find({"name": name, "source": source})
            if existing_record_matches.count() > 0:
                db_col.update_one({"name": name, "source": source}, {"$set": {"date": date, "type": threat_type, "description": description}})
            else:
                new_record = {"name": name, "source": source, "date": date, "type": threat_type, "description": description}
                db_col.insert_one(new_record)
            self.numScraped += 1
            print("McAfee threats scraped {" + str(self.numScraped) + "}...")

    def scrape_mcafee(self, db_col):
        print("Scraping McAfee...")
        feed = [["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/exploit-kits.html", "Exploit Kits"],
                ["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/campaigns.html", "Campaigns"],
                ["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/ransomware.html", "Ransomware"],
                ["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/vulnerabilities.html", "Vulnerabilities"]]
        for d in feed:
            self.scrape_mcafee_table(db_col, d[1], d[0])
        print("Scraping McAfee Complete")

    def scrape_norton_table(self, db_col, url):
        data = requests.get(url)
        soup = BeautifulSoup(data.text, "html.parser")

        for tr in soup.find_all("tr"):
            name = None
            source = None
            date = datetime.now()
            threat_type = None
            description = None
            for l in tr.find_all("a"):
                source = "https://au.norton.com" + l["href"]
                break
            if source is None:
                continue
            count = 0

            for td in tr.find_all("td"):
                if count == 0:
                    name = td.text.lstrip().rstrip()
                elif count == 1:
                    threat_type = td.text.lstrip().rstrip()
                elif count == 2:
                    if len(td.text) > 7:
                        try:
                            date = datetime.strptime(td.text.strip(), "%d/%m/%Y")
                        except:
                            print("Bad date")
                count += 1

            data2 = requests.get(source)
            soup2 = BeautifulSoup(data2.text, "html.parser")
            for td in soup2.find_all("div", class_="technical-description"):
                description = td.text.strip("\n").strip("\t")

            existing_record_matches = db_col.find({"name": name, "source": source})
            if existing_record_matches.count() > 0:
                db_col.update_one({"name": name, "source": source}, {"$set": {"date": date, "type": threat_type, "description": description}})
            else:
                new_record = {"name": name, "source": source, "date": date, "type": threat_type, "description": description}
                db_col.insert_one(new_record)
            self.numScraped += 1
            print("Norton threats scraped {" + str(self.numScraped) + "}...")

    def scrape_norton(self, db_col):
        print("Scraping Norton...")
        feed = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0-9-special-characters"]

        for d in feed:
            self.scrape_norton_table(db_col, "https://au.norton.com/online-threats/a-z-listing/" + d + ".html")
        print("Scraping Norton Complete")

    def webscrape(self, instance):
        print("Web Scrape button pressed ")
        client = MongoClient(port=27017)
        db = client.projectdb
        db_col = db.threats
        self.numScraped = 0
        self.scrape_mcafee(db_col)
        # self.scrape_norton(db_col)
        print("All Scrapes Complete")

    def twitterscrape(self, instance):
        self.count += 1
        upcount = self.count
        print("Twitter Scrape button pressed ", upcount)
        client = MongoClient(port=27017)
        db = client.projectdb
        col = db.threats
        serverStatusResult = db.command("serverStatus")

        # Insert a record (below)
        # newRecord = {"name": "test123", "source": "Twitter @test", "date": "30/01/2001", "type": "ware", "description": "test123"}
        # col.insert_one(newRecord)

    def newsscrape(self, instance):
        self.count += 1
        upcount = self.count
        print("News Scrape button pressed ", upcount)
        client = MongoClient(port=27017)
        db = client.projectdb
        col = db.threats
        serverStatusResult = db.command("serverStatus")

        # Insert a record (below)
        # newRecord = {"name": "test123", "source": "www.newssite.com", "date": "30/01/2001", "type": "ware", "description": "test123"}
        # col.insert_one(newRecord)

    def updatedb(self, instance):
        self.count += 1
        upcount = self.count
        print("Update DB button pressed ", upcount)
        client = MongoClient(port=27017)
        db = client.projectdb
        col = db.threats
        serverStatusResult = db.command("serverStatus")

        # Insert a record (below)
        # newRecord = {"name": "test123", "source": "www.test123.com", "date": "30/01/2001", "type": "ware", "description": "test123"}
        # col.insert_one(newRecord)
        # col.insert_many(newRecord)

        # Delete records (below)
        # col.delete_one({"type": "ware"})
        # col.delete_many({"type": "ware"})

        # Update records (below)
        # col.update_one({"name": "test123"}, {"$set": {"type": "ware"}})
        # col.update_many({"name": "test123"}, {"$set": {"type": "ware"}})

        print("Result: ", db.list_collection_names())
        for record in db.threats.find():
            print(record)
        #print(serverStatusResult)

    def search(self, instance):
        self.count += 1
        upcount = self.count
        print("Search button pressed ", upcount)
        client = MongoClient(port=27017)
        db = client.projectdb
        col = db.threats
        myquery = {"type": "Ransomware"}
        # {"name": "test123", "source": "www.test123.com", "date": "30/01/2001", "type": "ware", "description": "test123"}

        mydoc = col.find(myquery)
        for record in mydoc:
            print(record)

class dip(App):
    def build(self):
        return MyGrid()

dip = dip()
dip.run()

print("Application has ended")
