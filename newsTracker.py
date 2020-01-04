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
            primatelji = ["jakovk6@jix.im", "jakovk7@jix.im", "jakovk8@jix.im", "jakovk@jix.im", "jakovk2@jix.im"]
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
                #provjeravanjej duplikata - za svaki slučaj
                GlavniAgent.listaRezultata24Sata = list(dict.fromkeys(GlavniAgent.listaRezultata24Sata)) 
                for vijest in GlavniAgent.listaRezultata24Sata:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            
            print("\nPrikaz povezanih vijesti sa stranice Večernji.hr :\n")
            if(len(GlavniAgent.listaRezultataVecernji) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                #provjeravanjej duplikata - za svaki slučaj
                GlavniAgent.listaRezultataVecernji = list(dict.fromkeys(GlavniAgent.listaRezultataVecernji)) 
                for vijest in GlavniAgent.listaRezultataVecernji:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            
            print("\nPrikaz povezanih vijesti sa stranice Jutarnji List :\n")
            if(len(GlavniAgent.listaRezultataJutarnji) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                #provjeravanjej duplikata - za svaki slučaj
                GlavniAgent.listaRezultataJutarnji = list(dict.fromkeys(GlavniAgent.listaRezultataJutarnji)) 
                for vijest in GlavniAgent.listaRezultataJutarnji:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")
            
            print("\nPrikaz povezanih vijesti sa stranice Slobodna Dalmacija :\n")
            if(len(GlavniAgent.listaRezultataSlobodnaDalmacija) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                #provjeravanjej duplikata - za svaki slučaj
                GlavniAgent.listaRezultataSlobodnaDalmacija = list(dict.fromkeys(GlavniAgent.listaRezultataSlobodnaDalmacija)) 
                for vijest in GlavniAgent.listaRezultataSlobodnaDalmacija:
                    brojac += 1
                    print(f"\t{brojac}) {vijest}")

            print("\nPrikaz povezanih vijesti sa stranice Dnevnik.Hr :\n")
            if(len(GlavniAgent.listaRezultataDnevnikHr) == 0):
                print("\tNema vijesti povezanih sa tom ključnom riječi.")
            else:
                brojac = 0
                #provjeravanjej duplikata - za svaki slučaj
                GlavniAgent.listaRezultataDnevnikHr = list(dict.fromkeys(GlavniAgent.listaRezultataDnevnikHr)) 
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
                to= "jakovk3@jix.im",
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
                to= "jakovk3@jix.im",
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
                to= "jakovk3@jix.im",
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
                to= "jakovk3@jix.im",
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
                to= "jakovk3@jix.im",
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
    normaliziranaListaKljucnihRijeci = []

    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("News Filter agent: Pokrećem se i čekam da svi scraperi završe sa dohvatom podataka.")

        async def on_end(self):
            print("News Filter agent: Filtrirao sam sve prikupljene novosti. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):

            #ovdje filtriram i saljem glavnom agentu rezultate za display
            if(NewsFilterAgent.normaliziranaListaKljucnihRijeci[0] == "sve vijesti"):
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
                for kljucnaRijec in NewsFilterAgent.normaliziranaListaKljucnihRijeci:
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
            self.set_next_state("Stanje5")   
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=100)
            if msg:
                if msg.body != '':
                    NewsFilterAgent.BrojacZavrsenihScrapera += 1
                    if(NewsFilterAgent.BrojacZavrsenihScrapera == 5):
                        print("\nNews Filter agent: Svi scraperi su mi javili da su prikupili i poslali podatke.") 
                        self.set_next_state("Stanje3")
                    else:
                        self.set_next_state("Stanje2")
            else:
                print("\tNewsFilter agent: Čekao sam, ali nema odgovora.")
    
    class Stanje3(State):
        async def run(self):

            #saljem poruku agentu za normalizaciju 
            msg = spade.message.Message(
                to= "jakovk5@jix.im",
                body= "Pronađi mi ključne riječi."
            )
            await self.send(msg)
            print("News Filter agent: Šaljem zahtjev agentu za normalizaciju da mi dobavi ključne riječi da mogu filtrirati podatke.") 
            self.set_next_state("Stanje4")
    
    class Stanje4(State):
        async def run(self):

            msg = await self.receive(timeout=100)
            if msg:
                if msg.body != '':
                    print("\nNewsFilter agent: Zaprimio sam normalizirane ključne riječi.")
                    self.set_next_state("Stanje1")
            else:
                print("\tNewsFilter agent: Čekao sam, ali nema odgovora.")

    class Stanje5(State):
        async def run(self):

            #saljem poruku glavnom agentu da sam gotov sa filtriranjem pribavljenih podataka
            msg = spade.message.Message(
                to= "jakovkglavni@jix.im",
                body= "Gotov sam sa filtriranjem podataka."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom 

    async def setup(self):

        newsAg = self.MojePonasanje()

        newsAg.add_state(name="Stanje1", state=self.Stanje1())
        newsAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        newsAg.add_state(name="Stanje3", state=self.Stanje3())
        newsAg.add_state(name="Stanje4", state=self.Stanje4())
        newsAg.add_state(name="Stanje5", state=self.Stanje5())

        newsAg.add_transition(source="Stanje2", dest="Stanje2")
        newsAg.add_transition(source="Stanje2", dest="Stanje3")
        newsAg.add_transition(source="Stanje3", dest="Stanje4")
        newsAg.add_transition(source="Stanje4", dest="Stanje1")
        newsAg.add_transition(source="Stanje1", dest="Stanje5")
        
        self.add_behaviour(newsAg)
#kraj NewsFilter agenta

class NormalizationAgent(Agent):

    stranicaUrl = "https://www.kontekst.io/hrvatski/"
    fullStranicaUrl = "" # stranicaUrl + tu ide lowercase pojam


    class MojePonasanje(FSMBehaviour):
        async def on_start(self):
            print("Normalization agent: Pokrećem se i stojim u stanju pripravnosti.")

        async def on_end(self):
            print("\nNormalization agent: Normalizirao sam ključnu riječ. Završavam sa radom.")
            await self.agent.stop()

    class Stanje1(State):
        async def run(self):
            
            kljucnaRijec = input(" ---> Unesite ključnu riječ prema kojoj želite filtrirati novosti  ('sve vijesti' za prikaz svih): ")
            print("Normalization agent: Započinjem normalizaciju.")
            kljucnaRijec = kljucnaRijec.strip()

            if(kljucnaRijec == "sve vijesti"):
                NewsFilterAgent.normaliziranaListaKljucnihRijeci.append("sve vijesti")
                self.set_next_state("Stanje3")
            else:
                #dodavanje originalne riječi
                NewsFilterAgent.normaliziranaListaKljucnihRijeci.append(kljucnaRijec)
                #dodavanje lowercase riječi
                NewsFilterAgent.normaliziranaListaKljucnihRijeci.append(kljucnaRijec.lower())
                #dodavanje uppercase riječi
                NewsFilterAgent.normaliziranaListaKljucnihRijeci.append(kljucnaRijec.upper())

                #dohvacanje sinonima
                NormalizationAgent.fullStranicaUrl = NormalizationAgent.stranicaUrl + kljucnaRijec.lower()

                page = requests.get(NormalizationAgent.fullStranicaUrl)
            
                soup = BeautifulSoup(page.content, 'html.parser')
                sinonimi = soup.find_all("a", {"class": "dictentry"})
                sinonimi = list(dict.fromkeys(sinonimi))

                for sinonim in sinonimi:
                    NewsFilterAgent.normaliziranaListaKljucnihRijeci.append(sinonim.text.strip())

                #dodaju se i lowercase i uppercase verzije sinonima
                lowerLista = []
                upperLista = []
                for rijec in NewsFilterAgent.normaliziranaListaKljucnihRijeci:
                    lowerLista.append(rijec.lower())
                    upperLista.append(rijec.upper())
                
                for lowZapis in lowerLista:
                    NewsFilterAgent.normaliziranaListaKljucnihRijeci.append(lowZapis)

                for upZapis in upperLista:
                    NewsFilterAgent.normaliziranaListaKljucnihRijeci.append(upZapis)

                #velika je šansa da ima duplikata, tako da ih izbacujemo
                NewsFilterAgent.normaliziranaListaKljucnihRijeci = list(dict.fromkeys(NewsFilterAgent.normaliziranaListaKljucnihRijeci))

                #izbacivanje prazih rezultata (nekad ta stranica ima neke skrivene prazne rezultate poput '{{ item.term}}')
                for zapis in NewsFilterAgent.normaliziranaListaKljucnihRijeci:
                    if "{" in zapis:
                        NewsFilterAgent.normaliziranaListaKljucnihRijeci.remove(zapis)

                print("\n[TEST INFO] Normalization agent: Ovo su pronađeni sinonimi.")
                brojacv2 = 0
                for rijec in NewsFilterAgent.normaliziranaListaKljucnihRijeci:
                    brojacv2 += 1
                    print(f"{brojacv2}) {rijec}")
                self.set_next_state("Stanje3")   
            
    class Stanje2(State):
        async def run(self):

            msg = await self.receive(timeout=100)
            if msg:
                if msg.body != '':
                    print("\nNormalization agent: Krećem sa radom.")
                    self.set_next_state("Stanje1")
            else:
                print("\tNormalization agent: Čekao sam, ali nema odgovora.")
    
    class Stanje3(State):
        async def run(self):

            #saljem poruku filter agentu da sam gotov sa normalizacijom
            msg = spade.message.Message(
                to= "jakovk3@jix.im",
                body= "Gotov sam sa normalizacijom."
            )
            await self.send(msg)
            #ovo je trenutak kada ja završavam sa svojim radom 

    async def setup(self):

        normAg = self.MojePonasanje()

        normAg.add_state(name="Stanje1", state=self.Stanje1())
        normAg.add_state(name="Stanje2", state=self.Stanje2(), initial=True)
        normAg.add_state(name="Stanje3", state=self.Stanje3())

        normAg.add_transition(source="Stanje2", dest="Stanje1")
        normAg.add_transition(source="Stanje1", dest="Stanje3")
        
        self.add_behaviour(normAg)
#kraj Normalization agenta

if __name__ == '__main__':

    scraperDnevnikHrAgent = ScraperDnevnikHrAgent("jakovk2@jix.im", "456789")
    scraperDnevnikHrAgent.start()

    scraperSlobodnaDalmacijaAgent = ScraperSlobodnaDalmacijaAgent("jakovk@jix.im","1234567")
    scraperSlobodnaDalmacijaAgent.start()

    scraperJutarnjiAgent = ScraperJutarnjiAgent("jakovk8@jix.im","891011")
    scraperJutarnjiAgent.start()

    scraperVecernjiAgent = ScraperVecernjiAgent("jakovk7@jix.im", "78910")
    scraperVecernjiAgent.start()

    scraper24Agent = Scraper24SataAgent("jakovk6@jix.im", "67890")
    scraper24Agent.start()

    normalizationAgent = NormalizationAgent("jakovk5@jix.im", "45678")
    normalizationAgent.start()

    newsFilterAgent = NewsFilterAgent("jakovk3@jix.im", "234567")
    newsFilterAgent.start()

    time.sleep(1.5)
    glavniAgent = GlavniAgent("jakovkglavni@jix.im", "98765")
    glavniAgent.start()