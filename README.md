# ligabot

Lager en kamptråd for Tippeligaen på Reddit.

## Æres den som æres bør

/u/Armandg har levert en strålende innsats på programmeringsfronten og vært en drivkraft bak /r/Tippeligaen. 

La dette være en påminnelse om at selv om folk heier på veldig rare lag så kan de være skikkelige folk likevel. 

## Installasjon

For å kjøre ligabot trenger du Python 3 og noen ekstra biblioteker. Innstaller Python og kjør så 

    python -m pip install BeautifulSoup4
    python -m pip install twython

fra kommandolinjen. 


## OAuth

Siden PRAW nå har gått over fra å bruke vanlig brukernavn/passord for innlogging til OAuth, kreves det en viss innsats i forkant av kjøring av script. Ved å følge disse skrittene skal det likevel gå ganske greit:

1. Gå til [Reddits app-side](https://www.reddit.com/prefs/apps/) og registrer en ny app. Fyll inn minimum navn og "redirect uri". På sistnevnte kan du egentlig bare fylle inn "http://127.0.0.1:65010/authorize_callback"
 siden dette er noe som kun apper bruker. Klikk på "Create app".
2. Tekststringen under navnet på appen du akkurat lagde er det som du skal fylle inn i "client_id" i ligabot.py.
3. Tekststringen ved "secret" er den som skal fylles inn i "client_secret" i ligabot.py.
4. Kjør filen "reddit_oauth.py" med følgende variabler på egnet måte (i cmd/Terminal eller lignende): "python reddit_oauth.py client_id client_secret https://127.0.0.1:65010/authorize_callback identity
wikiread". De siste (identity og wikiread) er "tilgangene" som botscriptet får tilgang til å bruke. Dette kan utvides til å inneholde alle eller noen av følgende "scopes": identity, edit, flair, history, modconfig, modflair, modlog, modposts, modwiki, mysubreddits, privatemessages, read, report, save, submit, subscribe, vote, wikiedit, wikiread

5. Når du kjører scriptet vil du få en URL, gå inn på den og hent koden på slutten av URL som du ender opp med etter å ha gått inn på den.
6. Lim inn koden tilbake der du kjørte scriptet for å få en refresh-token. Denne legger du inn i ligabot.py under "refreshtoken".
7. Legg inn info i de siste feltene, "username" og "useragent". Husk å følge [Reddits regler for god skikk ved utfylling av "useragent"](https://github.com/reddit/reddit/wiki/API).
8. Test innlogging til Reddit ved å kjøre scriptet "oauth-test.py". Denne henter brukerinfo fra ligabot.py og viser brukernavnet ditt på Reddit og hvor mye karma du har.

Hvis dette fungerte uten videre problemer, gratulerer! 


## Kjøring

...

### Windows

Pass på at Python ligger i PATH-en og gå til katalogen med ligabot-runde.py . Kjør `python ligabot-runde.py`