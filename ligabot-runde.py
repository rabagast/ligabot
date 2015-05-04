#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup as bs
try:
    import syslog
    uselog = True
    log = syslog.syslog
except ImportError:
    uselog = False
import requests
import time
from datetime import datetime
import html.parser
html_parser = html.parser.HTMLParser()
import praw
import os.path
import re
import twython
Twython = twython.Twython
import os
from random import randint
from ligabot import twitter, reddit

username = reddit['username']
password = reddit['password']
useragent = reddit['useragent']
subreddit = "tippeligaensandbox"
reddit_post_title = ""

consumer_key = twitter['consumer_key']
consumer_secret = twitter['consumer_secret']
access_token_key = twitter['access_token_key']
access_token_secret = twitter['access_token_secret']

tw = Twython(consumer_key, consumer_secret, access_token_key, access_token_secret)

def main():
    createNecessaryFiles()
    reddit = praw.Reddit(user_agent=useragent)
    reddit.login(username, password)
    #subreddit = reddit.get_subreddit(subreddit)

    forkortelse = {
        'Aalesund': 'AaFK',
        'Bodø/Glimt': 'B/G',
        'Haugesund': 'FKH',
        'Lillestrøm': 'LSK',
        'Mjøndalen': 'MIF',
        'Molde': 'MOL',
        'Odd': 'ODD',
        'Rosenborg': 'RBK',
        'Sarpsborg 08': 'S08',
        'Sandefjord': 'SAN',
        'Strømsgodset': 'SIF',
        'Start': 'STA',
        'Stabæk': 'STB',
        'Tromsø': 'TIL',
        'Vålerenga': 'VIF',
        'Viking': 'VIK',
    }


    #Henter inn sida hvor både runde-kamper og tabellen er
    req = requests.get('http://www.altomfotball.no/element.do?cmd=tournament&tournamentId=1&useFullUrl=false')
    soup = bs(req.content)

    #Henter neste runde
    runde_table = soup.find('table', attrs={'id':'sd_fixtures_table_next'})
    runde_table_body = runde_table.find('tbody')
    runde_rows = runde_table_body.find_all('tr')

    #Henter tabell
    table = soup.find('table', attrs={'id':'sd_table_1'})
    table_body = table.find('tbody')
    tabell_rows = table_body.find_all('tr')

    #Setter tomme variabler
    runde_result = ""
    hjemme = []
    borte = []
    plassering = {}
    runde_dager = []
    temp_runde = ""


    #Hent datoene i runden først og putt i list
    for row in runde_rows:
        runde_cols = row.find_all('td')
        matchdate = runde_cols[0].text.strip()
        if matchdate == "":
            matchdate = tempdate
        else:
            tempdate = matchdate
        nowdate = time.strftime("%d.%m.%Y")
        #Sjekker antall dager til første kamp i runden
        days = days_between(matchdate, nowdate)
        #Legg til dato i dictionary 'runde_datoer'
        runde_dager.append(days)

    if runde_dager[0] > 2:
        #print ("break :(")
        if uselog:
            log('ligabot-runde.py kjørte, men runde ikke nær nok i tid. Variabelen days var '+str(days))
        sys.exit(0)

    #Hent plasseringer først og putt i dictionary
    for row in tabell_rows:
        tabell_cols = row.find_all('td')
        plass = tabell_cols[0].text.strip()
        plass = plass.replace(".", "")
        lag = tabell_cols[1].text.strip()
        #Legg til plassering i dictionary 'plassering'
        plassering[lag] = plass

    #Henter runde
    for row in runde_rows:
        cols = row.find_all('td')
        #Henter kampdato og setter inn forrige kampdato hvis vanlig kampdato ikke er tilgjengelig
        matchdate = cols[0].text.strip()
        if matchdate == "":
            matchdate = tempdate
        else:
            tempdate = matchdate
        #Henter info fra hver linje
        global runde
        runde = cols[1].text.strip()
        readtext = open('rundesjekk', 'r')
        rundesjekk = readtext.read()
        readtext.close()
        if temp_runde == "":
            temp_runde = runde
            reddit_post_title = runde
        elif temp_runde != runde:
            break
        #Finn hjemmelaget i kampen og legg til lista 'hjemme'
        hlag = cols[3].text.strip()
        hjemme.append(hlag)
        #Finn bortelaget i kampen og legg til lista 'borte'
        blag = cols[5].text.strip()
        borte.append(blag)
        tidres = cols[4].text.strip()
        resultatlink = cols[4].find('a')['href']
        url = "http://www.altomfotball.no/"
        link = url+resultatlink
        tv = cols[6].text.strip()
        #Slå sammen alle feltene i en linje med separator som er tilpasset tabeller i Reddit
        runde_result += matchdate+"|("+plassering[hlag]+") "+hlag+"|["+tidres+"]("+link+")|"+blag+" ("+plassering[blag]+")|"+tv+"\n"

    #Sett tom variabel
    global tabellResult
    tabellResult = ""

    #Henter tabellen
    for row in tabell_rows:
        tabell_cols = row.find_all('td')
        #Hent plassering og fjern etterfølgende punktum
        plass = tabell_cols[0].text.strip()
        plass = plass.replace(".", "")
        lag = tabell_cols[1].text.strip()
        #Legg til plassering i dictionaryen 'plassering'
        plassering[forkortelse[lag]] = plass
        #Tilpass lagnavn så det er enklere å legge til lag-flair i tabellen, dvs fjern skandinaviske tegn og erstatt mellomrom med bindestrek
        flairlag = lag.replace('æ', 'ae').replace('ø', 'o').replace('å', 'a').replace(' ', '-')
        #Finn ut hvilket lag som tabell-laget skal møte
        møter = ""
        if lag in hjemme:
            hjemmelag = borte[hjemme.index(lag)]
            møter = forkortelse[hjemmelag]+" ("+plassering[hjemmelag]+") hjemme"
        elif lag in borte:
            bortelag = hjemme[borte.index(lag)]
            møter = forkortelse[bortelag]+" ("+plassering[bortelag]+") borte"
        #Hent resten av infoen for tabellen
        kamper = tabell_cols[2].text.strip()
        vunnet = tabell_cols[3].text.strip()
        uavgjort = tabell_cols[4].text.strip()
        tap = tabell_cols[5].text.strip()
        målpluss = tabell_cols[6].text.strip()
        målminus = tabell_cols[7].text.strip()
        måldiff = tabell_cols[8].text.strip()
        poeng = tabell_cols[9].text.strip()
        #Slå sammen alle feltene i en linje med separator som er tilpasset tabeller i Reddit
        tabellResult += plass+"|[](/flair-"+flairlag.lower()+")"+lag+"|"+kamper+"|"+vunnet+"|"+uavgjort+"|"+tap+"|"+målpluss+"|"+målminus+"|"+måldiff+"|"+poeng+"|"+møter+"\n"

    tableheader = "######[](http://reddit.com#)\n\nNr|Lag|K|V|U|T|M+|M-|MF|P|Møter\n"
    tablejust ="---:|:---|---:|---:|---:|---:|---:|---:|---:|:---|:---\n"
    rundeheader = "Dato|Klokkeslett|Hjemmelag|Bortelag|TV-kanal\n"
    rundejust = ":---|---:|---:|:---|:---\n"
    innledning = ["Endelig Tippeliga-runde igjen :D",
        "Det er en herlig dag for fotball!",
        "Da er det dags igjen!"]
    sisteord = ["Så, hva tenker folket?",
        "Hva ser ut til å bli yndlingskampen denne runden?",
        "Hvilken kamp ser dere mest fram til?",
        "Hvem tror dere kommer best ut av denne runden?"]

    output = ""
    output += innledning[randint(0,len(innledning)-1)]+"\n\n**Tabell før runden:**\n"
    output += tableheader
    output += tablejust
    output += tabellResult
    output += "\n\n&nbsp;\n\n**Rundens kamper:**\n\n"
    output += rundeheader
    output += rundejust
    output += runde_result
    output += "\n\n&nbsp;\n\n"+sisteord[randint(0,len(sisteord)-1)]+"\n\n---\n###[](http://reddit.com#)\nHar du forslag til endringer eller ser du feil i denne posten? [Si ifra her!](http://reddit.com/message/compose/?to=ligabot&subject=Tips%20til%20endring/feil%20i%20runde-poster)"

    try:
        #reddit.submit(subreddit, reddit_post_title, output, captcha=None)
        print (output)
    except (SystemExit, KeyboardInterrupt) as e:
        if uselog:
            log('ligabot-runde.py klarte ikke å kjøre ferdig')
        sys.exit(0)


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%d.%m.%Y")
    d2 = datetime.strptime(d2, "%d.%m.%Y")
    return abs((d2 - d1).days)

def createNecessaryFiles():
    createLigabot()
    createFileIfNotExisting("rundesjekk")
    
def createFileIfNotExisting(file):
    path = createFilePathToScriptFolder(file)
    if not os.path.isfile(path):
        newfile = open(path, "w")
        newfile.close()
        return True
    return False
    
def createLigabot():
    wantedFile = "ligabot.py"
    created = createFileIfNotExisting(wantedFile)
    if created:
        with open(createFilePathToScriptFolder(wantedFile), "w") as ligafile:
            ligafile.write("""#!/usr/bin/env python3
twitter = {
    'consumer_key': 'xxx',
    'consumer_secret': 'xxx',
    'access_token_key': 'xxx',
    'access_token_secret': 'xxx'
}

reddit = {
    'username': 'xxx',
    'password': 'xxx',
    'useragent': 'In service for /r/Tippeligaen, made by /u/armandg'
}
""")


def createFilePathToScriptFolder(filename):
    return os.path.join(os.getcwd(), filename)
    
    
if __name__ == "__main__":
    main()
