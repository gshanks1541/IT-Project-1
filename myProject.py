import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from pymongo import MongoClient
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import tweepy
import csv
import pandas as pd

kivy.require("1.10.1")

class MyGrid(GridLayout):
    numScraped = 0
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 2

        self.submit = Button(text="Web Scrape (Shallow)", font_size=40)
        self.submit.bind(on_press=self.web_scrape_shallow)
        self.add_widget(self.submit)

        self.submit = Button(text="Web Scrape (Deep)", font_size=40)
        self.submit.bind(on_press=self.web_scrape_deep)
        self.add_widget(self.submit)

        self.submit = Button(text="Twitter Scrape", font_size=40)
        self.submit.bind(on_press=self.twitter_scrape)
        self.add_widget(self.submit)

        self.submit = Button(text="Update DB", font_size=40)
        self.submit.bind(on_press=self.updatedb)
        self.add_widget(self.submit)

        self.submit = Button(text="Search Threat", font_size=40)
        self.submit.bind(on_press=self.search)
        self.add_widget(self.submit)

        self.input = TextInput(multiline=False)
        self.add_widget(self.input)

        self.submit = Button(text="Export Data to CSV", font_size=40)
        self.submit.bind(on_press=self.export_all)
        self.add_widget(self.submit)

    def scrape_mcafee_table(self, db_col, threat_type, url, is_deep):
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

            count = 0
            for td in tr.find_all("td"):
                if count == 0:
                    name = td.text
                elif count == 1:
                    description = td.text
                count += 1
            if name is None:
                continue

            if is_deep:
                data2 = requests.get(source)
                soup2 = BeautifulSoup(data2.text, "html.parser")
                for tr in soup2.find_all("tr"):
                    count = 0
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

    def scrape_mcafee(self, db_col, is_deep):
        print("Scraping McAfee...")
        feed = [["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/exploit-kits.html", "Exploit Kits"],
                ["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/campaigns.html", "Campaigns"],
                ["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/ransomware.html", "Ransomware"],
                ["https://www.mcafee.com/enterprise/en-gb/threat-center/threat-landscape-dashboard/vulnerabilities.html", "Vulnerabilities"]]
        for d in feed:
            self.scrape_mcafee_table(db_col, d[1], d[0], is_deep)
        print("Scraping McAfee Complete")

    def scrape_norton_table(self, db_col, url, is_deep):
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

            if is_deep:
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

    def scrape_norton(self, db_col, is_deep):
        print("Scraping Norton...")
        feed = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0-9-special-characters"]

        for d in feed:
            self.scrape_norton_table(db_col, "https://au.norton.com/online-threats/a-z-listing/" + d + ".html", is_deep)
        print("Scraping Norton Complete")

    def webscrape(self, is_deep):
        print("Web Scrape button pressed ")
        client = MongoClient(port=27017)
        db = client.projectdb
        db_col = db.threats
        self.numScraped = 0
        self.scrape_mcafee(db_col, is_deep)
        self.scrape_norton(db_col, is_deep)
        # self.scrape_kaspersky(db_col)
        print("All Scrapes Complete")

    def web_scrape_shallow(self, instance):
        self.webscrape(False)

    def web_scrape_deep(self, instance):
        self.webscrape(True)

    def twitter_scrape(self, instance):
        print("Twitter Scrape Started")
        client = MongoClient(port=27017)
        db = client.projectdb
        db_col = db.threats
        self.numScraped = 0
        # Personal Twitter Developer Keys and Tokens
        consumer_key = "nX7aJP4OUszK1dFgfm6BTZrXQ"
        consumer_secret = "s1C56X7kGeSrum8M6VXs8IdfTMOfKDmpQnJTDodLcCr6kbv938"
        access_token = "1128419970960936961-ocBanOhQYajRPcXQ3c1alFBf3BlanX"
        access_token_secret = "elHOFXT79tht3RmP1V90lW6bKJhHxNjHHHDolFVyfadTO"

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        name = None
        source = None
        date = datetime.now()
        threat_type = None
        description = None


        for tweet in tweepy.Cursor(api.search, q="#cyber", count=100, lang="en", since="2017-04-03").items():
            date = tweet.created_at
            description = tweet.text
            source0 = tweet.text.find('@')
            source1 = tweet.text.find(':', source0)
            if (source0 > 0 and source1 > 0):
                source = tweet.text[source0:source1]

            existing_record_matches = db_col.find({"source": source, "description": description})
            if existing_record_matches.count() > 0:
                db_col.update_one({"source": source, "description": description}, {"$set": {"date": date, "type": threat_type, "description": description}})
            else:
                new_record = {"name": name, "source": source, "date": date, "type": threat_type, "description": description}
                db_col.insert_one(new_record)
            self.numScraped += 1
            print("Twitter threats scraped {" + str(self.numScraped) + "}...")
        print("Twitter Scrape Complete")

    def updatedb(self, instance):
        print("Update Database Ran")
        client = MongoClient(port=27017)
        db = client.projectdb
        col = db.threats

        # Insert a record (below)
        # newRecord = {"name": "test123", "source": "www.newssite.com", "date": "30/01/2001", "type": "ware", "description": "test123"}
        # col.insert_one(newRecord)

        # Delete records (below)
        # col.delete_one({"type": "ware"})
        # col.delete_many({"type": "ware"})

        # Update records (below)
        # col.update_one({"name": "test123"}, {"$set": {"type": "ware"}})
        # col.update_many({"name": "test123"}, {"$set": {"type": "ware"}})

        # print document list
        # print("Result: ", db.list_collection_names())
        # for record in db.threats.find():
        #    print(record)

    def search(self, instance):
        print("Search button pressed ")
        client = MongoClient(port=27017)
        db = client.projectdb
        col = db.threats
        myquery = {"type": "Ransomware"}
        # {"name": "test123", "source": "www.test123.com", "date": "30/01/2001", "type": "ware", "description": "test123"}

        mydoc = col.find(myquery)
        for record in mydoc:
            print(record)

    def export_all(self, instance):
        self.numScraped = 0
        print("Exporting all records")
        db_col = MongoClient(port=27017).projectdb.threats

        csv_file = open("threats_export.csv", "a")
        csv_writer = csv.writer(csv_file)
        docs = db_col.find()
        for record in docs:
            self.numScraped += 1
            print('Writing record ' + str(self.numScraped) + ' to CSV')
            name = record['name']
            if name is None:
                name = ''
            source = record['source']
            if source is None:
                source = ''
            date = str(record['date'])
            if date is None:
                date = ''
            type = record['type']
            if type is None:
                type = ''
            description = record['description']
            if description is None:
                description = ''
            csv_writer.writerow([name.encode("utf-8"), source.encode("utf-8"), date.encode("utf-8"), type.encode("utf-8"), description.encode("utf-8")])
        print("Exporting all records complete")


class dip(App):
    def build(self):
        return MyGrid()

dip = dip()
dip.run()

print("Application has ended")
