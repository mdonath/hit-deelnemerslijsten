# Downloaden gegevens via openid-sn
Voordat de lijsten gemaakt kunnen worden, moeten alle gegevens van de deelnemers worden opgehaald. Dat gebeurt niet hier maar met de applicatie die te vinden is in 'https://github.com/mdonath/openid-sn'. Hoe je deze applicatie moet installeren staat daar uitgelegd.

Indien er nog geen configuratie voor het huidige HIT-jaar is, dan moet je die daar toevoegen (in de map van openid-sn).

## hit.yaml
Bovenin het bestand staat een `current_year`, die moet je wijzigen naar... het huidige HIT jaar.

Voeg onderaan het bestand een nieuwe sectie toe, de inhoud ziet er als volgt uit (commentaar kun je weglaten, maar kan handig zijn):

```yaml
  - year: 2024      # huidige HIT jaar
    event_id: 30803 # Event-id van het evenement in SOL
    forms:
      - 53336       # Formulier-id van het Basisformulier
      - 53339       # Formulier-id van het Ouder-kind Basisformulier (kind is lid)
      - 53342       # Formulier-id van het Ouder-kind Basisformulier (ouder is lid)
    participant_status:
      - 1000        # Deelnemer staat ingeschreven
      - 1020        # Ingeschreven, moet nog iDEAL-betaling
      #- 1008       # Op wachtlijst
    pincodes:
      Alphen: '1'   # Wachtwoord = "HIT-Alphen-2024-1"
      Dwingeloo: '2'
      Harderwijk: '3'
      Heerenveen: '4'
      Mook: '5'
      Ommen: '6'
      Zeeland: '7'
```

Het event-id kun je terugvinden in SOL in de adresbalk als je het event hebt geopend, met deze link `https://sol.scouting.nl/as/event/30803/forms/` is het dus **30803**.

De Formulier-id's kun je op vergelijkbare wijze terugvinden, de link `https://sol.scouting.nl/as/form/53336` levert dus **53336** op.

In de sectie 'pincodes' is niet nodig voor het downloaden, maar pas bij het maken van de lijsten. Hier kun je pincodes definiëren, die worden toegevoegd aan het wachtwoord waarmee de zips worden versleuteld. Het wachtwoord van elke zip heeft het volgende patroon: `HIT-Plaats-jaar-pincode`, dus in bovenstaand voorbeeld zal het wachtwoord van Alphen worden: `HIT-Alphen-2024-1`. Voor pincode kun je natuurlijk beter een wat langere 6-cijferige code nemen. De quotes zijn nodig voor als de pincode met een `0` begint.



# Downloaden formulieren
In de map van openid-sn staat een script `./sol_export_deelnemers.py`. Als je dit aanroept, worden de gegevens van alle formulieren gedownload naar 6 bestanden:

- `formuliergegevens_53336.csv` (basisformulier)
- `formuliergegevens_53339.csv` (basisformulier kind is lid)
- `formuliergegevens_53342.csv` (basisformulier ouder is lid)
- `subgroepen_53336.csv` (basisformulier)
- `subgroepen_53339.csv` (basisformulier kind is lid)
- `subgroepen_53342.csv` (basisformulier ouder is lid)
 
De eerste bevat de gegevens van alle deelnemers van formulieren die het basisformulier als basisformulier hebben. Voor de andere twee is het vergelijkbaar, alleen dus dan van de ouder-kind-kampen.

Om van de deelnemers ook te kunnen zien in welke subgroepen men zit, worden ook die gegevens gedownload. Het uiteindelijke script verwerkt alle gegevens tot bestanden per plaats, per kamp, per gebruik.



# Virtual Environment
Om je eigen omgeving niet te vervuilen met de dependencies moet je 'venv' gebruiken.

## Installeer Python 3
In Linux: `sudo apt install python3`

## Update pip
`pip install --upgrade pip`

## Installeer dependencies
`pip install -r requirements`



# Voorbereiden configuratie

## hit.yaml
Maak een symbolic link naar de `hit.yaml` configuratie in `openid-sn/python/hit.yaml`:

`ln -s ../../openid-sn/python/hit.yaml`

Dit zorgt ervoor dat de configuraties hetzelfde blijven.



# Links naar gedownloade formulieren
In de map `downloads` staat een script `link.sh` waarmee je een symlink kan maken naar alle gedownloade formulieren. Je kan ook steeds de in openid-sn gedownloade formulieren kopiëren, maar dit is makkelijker als je de bestanden nog een keertje ophaalt.

De bestanden staan daar in een map genaamd `hit-2024`, dus het linken gaat dan als volgt: `./link.sh 2024`.



# Bijsluiter
Bij alle zips wordt ook een Privacy Bijsluiter toegevoegd. Dat is een PDF met daarin uitleg dat je zorgvuldig moet omgaan met de gegevens.

## Aanpassen
De documenten staan in de map `doc`. Kopieer een bestand en pas het jaartal aan. De bestanden zijn gemaakt met LibreOffice dat gratis is te downloaden. Misschien kan Microsoft Office ze ook openen, maar dat gebruik ik nooit.

 Als je het bestand opent, dan moet je twee eigenschappen van het document wijzigen, de *titel* en een gebruikergedefinieerde eigenschap genaamd *jaartal*, bereikbaar via "Bestand -> Eigenschappen -> Beschrijving" en via "Bestand -> Eigenschappen -> Gebruikergedefinieerde eigenschappen".

Vervolgens exporteren naar PDF en naast het origineel plaatsen.



# Uitvoeren script
Voordat je het script kan uitvoeren, moet je dus het volgende hebben gedaan:
- Zorgen voor een Werkende Python-omgeving (Python, virtual env, requirements)
- In/aanvullen configuratie hit.yaml (o.a. pincodes)
- Downloaden bestanden via openid-sn
- Links maken zodat het script erbij kan
- Updaten bijsluiter (jaartal++)

Het script is dan uit te voeren met: `./maaklijsten.py`.



# Distributie van de zips
Nu moeten de zips nog veilig naar de voorzitters van de C-teams van de HIT Plaatsen.

## Vroeger
Vroeger werden ze gemaild, maar dat werkt niet meer omdat zips-met-een-wachtwoord niet meer veilig worden geacht omdat ze niet gescand kunnen worden door antivirus software van (bijvoorbeeld Gmail).

Ook zijn ze wel eens verspreid via `wetransfer.com`, maar het voelt toch wat oneigenlijk om voor de verspreiding van zoveel privacygevoelige informatie een externe partij te gebruiken.

## Nu
Afgelopen keer zijn de gegevens daarom verspreid via de Office-365 omgeving van Scouting Nederland. Alle downloads staan dan bij elkaar, maar omdat er een wachtwoord op zit, kan iemand van een andere HIT Plaats niets met de andere bestanden.

Na het uploaden van de bestanden kun je alle HIT Voorzitters een bericht sturen dat de lijsten te downloaden zijn en dat ze via een privéberichtje de pincode toegestuurd kunnen krijgen.