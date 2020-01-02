#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datetime
import spade
import time
import requests
import requests_html
import bs4
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
from spade.agent import Agent
from spade.behaviour import TimeoutBehaviour, CyclicBehaviour
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
  
class GlavniAgent(Agent):
    
    listaRezultata24Sata = []
    listaRezultataVecernji = []
    listaRezultataJutarnji = []
    listaRezultataSlobodnaDalmacija = []
    listaRezultataDnevnikHr = []

    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("\nGlavni agent: Pokrećem se i započinjem dobavljanje današnjih novosti za Vas!")

        async def on_end(self):
            print("\nGlavni agent: Završavam sa radom.")
            print("\n ------------------------------- \n")
            #print("Izvorni kod dostupan i na GitHub-u: https://github.com/TheJakov/newsTracker")
            await self.agent.stop()
            time.sleep(300)
            sys.exit(0)


    class Stanje1(State):
        async def run(self):
            
            print(f"Glavni agent: Saljem dostupnim scraper agentima zahtjev za prikupljanje vijesti.\n")
            primatelji = ["username@jix.im", "username2@jix.im", "username3@jix.im", "username4@jix.im", "username5@jix.im"]
            for primatelj in primatelji:
                msg = spade.message.Message(
                    to=primatelj,
                    body="Kreni !"
                )
                await self.send(msg)
            self.set_next_state("Stanje2")        
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=300)
            if msg:
                if msg.body != '':
                    print("\nGlavni agent: Primio sam poruku da su novosti spremne za prikazivanje. Slijedi prikaz novosti.\n\n")
                    self.set_next_state("Stanje3")
            else:
                print("\tGlavni agent: Čekao sam, ali nema odgovora.")
    
    class Stanje3(State):
        async def run(self):

            print("Prikaz povezanih vijesti sa stranice 24Sata :\n")
            if(len(GlavniAgent.listaRezultata24Sata) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                for vijest in GlavniAgent.listaRezultata24Sata:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            
            print("\nPrikaz povezanih vijesti sa stranice Večernji.hr :\n")
            if(len(GlavniAgent.listaRezultataVecernji) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                for vijest in GlavniAgent.listaRezultataVecernji:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            
            print("\nPrikaz povezanih vijesti sa stranice Jutarnji List :\n")
            if(len(GlavniAgent.listaRezultataJutarnji) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                for vijest in GlavniAgent.listaRezultataJutarnji:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            
            print("\nPrikaz povezanih vijesti sa stranice Slobodna Dalmacija :\n")
            if(len(GlavniAgent.listaRezultataSlobodnaDalmacija) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                for vijest in GlavniAgent.listaRezultataSlobodnaDalmacija:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")

            print("\nPrikaz povezanih vijesti sa stranice Dnevnik.Hr :\n")
            if(len(GlavniAgent.listaRezultataDnevnikHr) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                for vijest in GlavniAgent.listaRezultataDnevnikHr:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            #ovo je trenutak kada ja završavam sa svojim radom 

    async def setup(self):

        glavniAg = self.MojePonasanje()

        glavniAg.add_state(name="Stanje1", state=self.Stanje1(), initial=True)
        glavniAg.add_state(name="Stanje2", state=self.Stanje2())
        glavniAg.add_state(name="Stanje3", state=self.Stanje3())

        glavniAg.add_transition(source="Stanje1", dest="Stanje2")
        glavniAg.add_transition(source="Stanje2", dest="Stanje3")
        
        self.add_behaviour(glavniAg)
#kraj glavnog agenta

class Scraper24SataAgent(Agent):
    stranicaUrl = "https://www.24sata.hr"
    
    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("Scraper 24sata: Pokrećem se i  postavljam u stanje pripravnosti!")

        async def on_end(self):
            print("\nScraper 24sata: Prikupio sam novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            page = requests.get(Scraper24SataAgent.stranicaUrl)
            
            soup = BeautifulSoup(page.content, 'html.parser')
            stories = soup.find_all("h3", {"class": "card__title"})
            stories = list(dict.fromkeys(stories))

            for story in stories:
                tekst = story.find("span")
                NewsFilterAgent.listaNovosti24Sata.append(tekst.text)
            self.set_next_state("Stanje3")   
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=75)
            if msg:
                if msg.body != '':
                    print(f"Scraper 24sata: Primio sam poruku Glavnog agenta. Krecem s radom.")
            else:
                print("\tScraper 24Sata: Čekao sam, ali nema odgovora.")
            self.set_next_state("Stanje1")
    
    class Stanje3(State):
        async def run(self):

            #saljem poruku filter agentu da sam gotov sa pribavljanjem svojih podataka
            msg = spade.message.Message(
                to= "username_filter@jix.im",
                body= "Gotov sam."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom 
  
    async def setup(self):

        scraperAg = self.MojePonasanje()

        scraperAg.add_state(name="Stanje1", state=self.Stanje1())
        scraperAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        scraperAg.add_state(name="Stanje3", state=self.Stanje3())

        scraperAg.add_transition(source="Stanje2", dest="Stanje1")
        scraperAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(scraperAg)
#kraj 24 sata scraper agenta

class ScraperVecernjiAgent(Agent):
    stranicaUrl = "https://www.vecernji.hr"
    
    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("Scraper Vecernji: Pokrećem se i  postavljam u stanje pripravnosti!")

        async def on_end(self):
            print("\nScraper Vecernji: Prikupio sam novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            page = requests.get(ScraperVecernjiAgent.stranicaUrl)
            
            soup = BeautifulSoup(page.content, 'html.parser')
            stories = soup.find_all("h2", {"class": "card__title"})
            stories = list(dict.fromkeys(stories))

            for story in stories:
                NewsFilterAgent.listaNovostiVecernji.append(story.text)
            self.set_next_state("Stanje3")

    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=75)
            if msg:
                if msg.body != '':
                    print(f"Scraper Vecernji: Primio sam poruku Glavnog agenta. Krecem s radom.")
            else:
                print("\tScraper Vecernji: Čekao sam, ali nema odgovora.")
            self.set_next_state("Stanje1")

    class Stanje3(State):
        async def run(self):

            #saljem poruku filter agentu da sam gotov sa pribavljanjem svojih podataka
            msg = spade.message.Message(
                to= "username_filter@jix.im",
                body= "Gotov sam."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom    
            
    async def setup(self):

        scraperAg = self.MojePonasanje()

        scraperAg.add_state(name="Stanje1", state=self.Stanje1())
        scraperAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        scraperAg.add_state(name="Stanje3", state=self.Stanje3())

        scraperAg.add_transition(source="Stanje2", dest="Stanje1")
        scraperAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(scraperAg)
#kraj Vecernji scraper agenta

class ScraperJutarnjiAgent(Agent):
    stranicaUrl = "https://www.jutarnji.hr"
    
    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("Scraper Jutarnji: Pokrećem se i  postavljam u stanje pripravnosti!")

        async def on_end(self):
            print("\nScraper Jutarnji: Prikupio sam novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            page = requests.get(ScraperJutarnjiAgent.stranicaUrl)
            
            soup = BeautifulSoup(page.content, 'html.parser')
            stories = soup.find_all("h4", {"class": "title"})
            stories = list(dict.fromkeys(stories))

            for story in stories:
                NewsFilterAgent.listaNovostiJutarnji.append(story.text.strip())
            self.set_next_state("Stanje3")    
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=75)
            if msg:
                if msg.body != '':
                    print(f"Scraper Jutarnji: Primio sam poruku Glavnog agenta. Krecem s radom.")
            else:
                print("\tScraper Jutarnji: Čekao sam, ali nema odgovora.")
            self.set_next_state("Stanje1")
    
    class Stanje3(State):
        async def run(self):
            
            #saljem poruku filter agentu da sam gotov sa pribavljanjem svojih podataka
            msg = spade.message.Message(
                to= "username_filter@jix.im",
                body= "Gotov sam."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom
  
    async def setup(self):

        scraperAg = self.MojePonasanje()

        scraperAg.add_state(name="Stanje1", state=self.Stanje1())
        scraperAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        scraperAg.add_state(name="Stanje3", state=self.Stanje3())

        scraperAg.add_transition(source="Stanje2", dest="Stanje1")
        scraperAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(scraperAg)
#kraj Jutarnji scraper agenta

class ScraperSlobodnaDalmacijaAgent(Agent):
    stranicaUrl = "https://www.slobodnadalmacija.hr"
    
    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("Scraper SlobodnaDalmacija: Pokrećem se i  postavljam u stanje pripravnosti!")

        async def on_end(self):
            print("\nScraper SlobodnaDalmacija: Prikupio sam novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            page = requests.get(ScraperSlobodnaDalmacijaAgent.stranicaUrl)
            
            soup = BeautifulSoup(page.content, 'html.parser')
            stories = soup.find_all("h2", {"class": "story__title"})
            stories = list(dict.fromkeys(stories))

            for story in stories:
                NewsFilterAgent.listaNovostiSlobodnaDalmacija.append(story.text.strip())
            self.set_next_state("Stanje3")
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=75)
            if msg:
                if msg.body != '':
                    print(f"Scraper SlobodnaDalmacija: Primio sam poruku Glavnog agenta. Krecem s radom.")
            else:
                print("\tScraper SlobodnaDalmacija: Čekao sam, ali nema odgovora.")
            self.set_next_state("Stanje1")
    
    class Stanje3(State):
        async def run(self):

            #saljem poruku filter agentu da sam gotov sa pribavljanjem svojih podataka
            msg = spade.message.Message(
                to= "username_filter@jix.im",
                body= "Gotov sam."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom

    async def setup(self):

        scraperAg = self.MojePonasanje()

        scraperAg.add_state(name="Stanje1", state=self.Stanje1())
        scraperAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        scraperAg.add_state(name="Stanje3", state=self.Stanje3())

        scraperAg.add_transition(source="Stanje2", dest="Stanje1")
        scraperAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(scraperAg)
#kraj SlobodnaDalmacija scraper agenta

class ScraperDnevnikHrAgent(Agent):
    stranicaUrl = "https://www.dnevnik.hr"
    
    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("Scraper DnevnikHr: Pokrećem se i  postavljam u stanje pripravnosti!")

        async def on_end(self):
            print("\nScraper DnevnikHr: Prikupio sam novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            page = requests.get(ScraperDnevnikHrAgent.stranicaUrl)
            
            soup = BeautifulSoup(page.content, 'html.parser')
            stories = soup.find_all("h3", {"class": "title"})
            stories = list(dict.fromkeys(stories))

            for story in stories:
                NewsFilterAgent.listaNovostiDnevnikHr.append(story.text.strip())
            self.set_next_state("Stanje3")
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=75)
            if msg:
                if msg.body != '':
                    print(f"Scraper DnevnikHr: Primio sam poruku Glavnog agenta. Krecem s radom.")
            else:
                print("\tScraper DnevnikHr: Čekao sam, ali nema odgovora.")
            self.set_next_state("Stanje1")

    class Stanje3(State):
        async def run(self):

            #saljem poruku filter agentu da sam gotov sa pribavljanjem svojih podataka
            msg = spade.message.Message(
                to= "username_filter@jix.im",
                body= "Gotov sam."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom

  
    async def setup(self):

        scraperAg = self.MojePonasanje()

        scraperAg.add_state(name="Stanje1", state=self.Stanje1())
        scraperAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        scraperAg.add_state(name="Stanje3", state=self.Stanje3())

        scraperAg.add_transition(source="Stanje2", dest="Stanje1")
        scraperAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(scraperAg)
#kraj DnevnikHr scraper agenta

class NewsFilterAgent(Agent):
    
    listaNovosti24Sata = []
    listaNovostiVecernji = []
    listaNovostiJutarnji = []
    listaNovostiSlobodnaDalmacija = []
    listaNovostiDnevnikHr = []
    BrojacZavrsenihScrapera = 0

    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("News Filter agent: Pokrećem se i čekam da svi scraperi završe sa dohvatom podataka.")

        async def on_end(self):
            print("\nNews Filter agent: Filtrirao sam sve prikupljene novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            print("\nNews Filter agent: Svi scraperi su mi javili da su prikupili i poslali podatke.") 
            #ovdje filtriram i saljem glavnom agentu rezultate za display
            kljucnaRijec = input(" ----> Unesite ključnu riječ prema kojoj želite filtrirati novosti  ('sve vijesti' za prikaz svih): ")
            print("News Filter agent: Započinjem pregled i filtiranje prikupljenih novosti.")
            kljucnaRijec = kljucnaRijec.strip()

            if(kljucnaRijec == "sve vijesti"):
                for zapis in NewsFilterAgent.listaNovosti24Sata:
                    GlavniAgent.listaRezultata24Sata.append(zapis)

                for zapis in NewsFilterAgent.listaNovostiVecernji:
                    GlavniAgent.listaRezultataVecernji.append(zapis)

                for zapis in NewsFilterAgent.listaNovostiJutarnji:
                    GlavniAgent.listaRezultataJutarnji.append(zapis)

                for zapis in NewsFilterAgent.listaNovostiSlobodnaDalmacija:
                    GlavniAgent.listaRezultataSlobodnaDalmacija.append(zapis)
                
                for zapis in NewsFilterAgent.listaNovostiDnevnikHr:
                    GlavniAgent.listaRezultataDnevnikHr.append(zapis)
            else:
                for zapis in NewsFilterAgent.listaNovosti24Sata:
                    if(kljucnaRijec in zapis):
                        GlavniAgent.listaRezultata24Sata.append(zapis)

                for zapis in NewsFilterAgent.listaNovostiVecernji:
                    if(kljucnaRijec in zapis):
                        GlavniAgent.listaRezultataVecernji.append(zapis)

                for zapis in NewsFilterAgent.listaNovostiJutarnji:
                    if(kljucnaRijec in zapis):
                        GlavniAgent.listaRezultataJutarnji.append(zapis)

                for zapis in NewsFilterAgent.listaNovostiSlobodnaDalmacija:
                    if(kljucnaRijec in zapis):
                        GlavniAgent.listaRezultataSlobodnaDalmacija.append(zapis)
                
                for zapis in NewsFilterAgent.listaNovostiDnevnikHr:
                    if(kljucnaRijec in zapis):
                        GlavniAgent.listaRezultataDnevnikHr.append(zapis)
            self.set_next_state("Stanje3")   
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=100)
            if msg:
                if msg.body != '':
                    NewsFilterAgent.BrojacZavrsenihScrapera += 1
                    if(NewsFilterAgent.BrojacZavrsenihScrapera == 5):
                        self.set_next_state("Stanje1")
                    else:
                        self.set_next_state("Stanje2")
            else:
                print("\tNewsFilter agent: Čekao sam, ali nema odgovora.")
    
    class Stanje3(State):
        async def run(self):

            #saljem poruku glavnom agentu da sam gotov sa filtriranjem pribavljenih podataka
            msg = spade.message.Message(
                to= "username_main@jix.im",
                body= "Gotov sam sa pribavljanjem podataka."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom 

    async def setup(self):

        newsAg = self.MojePonasanje()

        newsAg.add_state(name="Stanje1", state=self.Stanje1())
        newsAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        newsAg.add_state(name="Stanje3", state=self.Stanje3())

        newsAg.add_transition(source="Stanje2", dest="Stanje1")
        newsAg.add_transition(source="Stanje2", dest="Stanje2")
        newsAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(newsAg)
#kraj NewsFilter agenta

if __name__ == '__main__':

    scraperDnevnikHrAgent = ScraperDnevnikHrAgent("username@jix.im", "password")
    scraperDnevnikHrAgent.start()

    scraperSlobodnaDalmacijaAgent = ScraperSlobodnaDalmacijaAgent("username2@jix.im","password2")
    scraperSlobodnaDalmacijaAgent.start()

    scraperJutarnjiAgent = ScraperJutarnjiAgent("username3@jix.im","password3")
    scraperJutarnjiAgent.start()

    scraperVecernjiAgent = ScraperVecernjiAgent("username4@jix.im", "password4")
    scraperVecernjiAgent.start()

    scraper24Agent = Scraper24SataAgent("username5@jix.im", "password5")
    scraper24Agent.start()

    newsFilterAgent = NewsFilterAgent("username_filter@jix.im", "password6")
    newsFilterAgent.start()

    time.sleep(1.5)
    glavniAgent = GlavniAgent("username_main@jix.im", "password7")
    glavniAgent.start()