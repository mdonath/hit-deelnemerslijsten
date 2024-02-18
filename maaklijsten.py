#!/usr/bin/env python
# -*- coding: UTF-8 -*

from datetime import datetime

import pyminizip
import yaml
import shutil
import os
import re
import csv

# ===============================================

HIT_CONFIG = yaml.safe_load(open("hit.yaml"))

HIT_JAAR = HIT_CONFIG['current_year']
PASSWORD_MASK_ZIP = "HIT-%s-" + str(HIT_JAAR) + "-%s"
PASSWORD_MASK_PLAATS = "HIT-%s-" + str(HIT_JAAR)
PASSWORD_MASK_KAMP = "HIT-" + str(HIT_JAAR) + "-%s"


HIT = [hit for hit in HIT_CONFIG['hits'] if hit['year'] == HIT_CONFIG['current_year']][0]
SOL_FORMULIERNR_BASIS = str(HIT['forms'][0])
SOL_FORMULIERNR_KIND_MET_OUDER = str(HIT['forms'][1])
SOL_FORMULIERNR_OUDER_MET_KIND = str(HIT['forms'][2])

PINCODES = HIT['pincodes']

print(PINCODES)

# ===============================================

PRIVACY_BIJSLUITER = "Privacy bijsluiter HIT %d.pdf" % (HIT_JAAR)

def dieet(wat, wie=''):
    if wie == '':
        return "Dieet: %s" % (wat)
    else:
        return "Dieet (%s): %s" % (wie, wat)

def dieet_reden(wat, wie=''):
    if wie == '':
        return "Dieet Reden: %s" % (wat)
    else:
        return "Dieet (%s) Reden: %s" % (wie, wat)

def heeft_iets_medisch(wie=''):
    if wie == '':
        return "Heeft de deelnemer een allergie, lichamelijke of geestelijke beperkingen of gebruikt hij/zij medicijnen?"
    else:
        return "Heeft de deelnemer (%s) een allergie, lichamelijke of geestelijke beperkingen of gebruikt hij/zij medicijnen?" % (wie)


#nieuwe velden
DEELNAMEKOSTEN = "Deelnamekosten HIT %d (onderstaande bankgegevens komen uit SOL, er kan ook met een andere bankrekening betaald worden via iDEAL): " % HIT_JAAR
MEDISCH_HANDELEN = 'De ouder/verzorger of deelnemer (18 jaar of ouder) gaat er mee akkoord dat medisch handelen is toegestaan, als een arts dit noodzakelijk acht.'
TOESTEMMING_FOTO = "Ik geef toestemming voor het maken en gebruik van foto- en/of videomateriaal en publicatie hiervan op de media van Scouting Nederland / HIT"
TOESTEMMING_FOTO_NEE = "Indien NEE, op welke wijze kunnen wij invulling geven aan het bezwaar?"

class Header:
    def __init__(self, kolom, is_normaal, is_ouderkind, export_alles, export_medisch, export_foerage):
        self.kolom = kolom
        self.normaal = is_normaal
        self.ouderkind = is_ouderkind
        self.export_alles = export_alles
        self.export_medisch = export_medisch
        self.export_foerage = export_foerage

class LidHeader(Header):
    def __init__(self, kolom, is_normaal, is_ouderkind, export_alles, export_medisch, export_foerage):
        Header.__init__(self, 'Lid ' + kolom, is_normaal, is_ouderkind, export_alles, export_medisch, export_foerage)

class KostenHeader(Header):
    def __init__(self, kolom, is_normaal, is_ouderkind, export_alles, export_medisch, export_foerage):
        Header.__init__(self, DEELNAMEKOSTEN + kolom, is_normaal, is_ouderkind, export_alles, export_medisch, export_foerage)

HEADERS_NORMAAL_OBJ = [
    Header("Deelnemersnummer", True, True, False, False, False),
    Header("Lidnummer", True, True, False, False, False),
    LidHeader("initialen", True, True, False, False, False),
    LidHeader("voornaam", True, True, False, False, False),
    LidHeader("tussenvoegsel", True, True, False, False, False),
    LidHeader("achternaam", True, True, False, False, False),
    LidHeader("geslacht", True, True, False, False, False),
    LidHeader("straat", True, True, False, False, False),
    LidHeader("huisnummer", True, True, False, False, False),
    LidHeader("toevoegsel huisnr", True, True, False, False, False),
    LidHeader("postcode", True, True, False, False, False),
    LidHeader("plaats", True, True, False, False, False),
    LidHeader("aanvullende adresgegevens", True, True, False, False, False),
    LidHeader("land", True, True, False, False, False),
    LidHeader("geboortedatum", True, True, False, False, False),
    LidHeader("geboorteplaats", True, True, False, False, False),
    LidHeader("e-mailadres", True, True, False, False, False),
    LidHeader("telefoon", True, True, False, False, False),
    LidHeader("mobiel", True, True, False, False, False),
    Header("Organisatienummer", True, True, False, False, False),
    Header("Organisatie", True, True, False, False, False),
    Header("Organisatie plaats", True, True, False, False, False),
    Header("Speleenheid", True, True, False, False, False),
    Header("Functie", True, True, False, False, False),
    Header("Deelnamestatus", True, True, False, False, False),
    Header("Inschrijfdatum", True, True, False, False, False),
    Header("Formuliernummer", True, True, False, False, False),
    Header("Formuliernaam", True, True, False, False, False),
    Header("Ingeschreven door", True, True, False, False, False),
    Header("Totaalbedrag", True, True, False, False, False),
    Header("Openstaand bedrag", True, True, False, False, False),
    Header("Onderdeel van inschrijving", True, True, False, False, False),
    Header("Inschrijving laatst gewijzigd", True, True, False, False, False),

    Header("Kloppen de gegevens bovenaan (adres, huisnummer, telefoonnummer en vooral ook het email adres)?", True, True, False, False, False),
    Header("Telefoonnummer van de mobiele telefoon die je mee neemt naar de HIT.", True, True, False, False, False),
    Header("Heb je een zwemdiploma? (let op: dit kan verplicht zijn voor de HIT waaraan je deelneemt)", True, True, False, False, False),
    Header(dieet("Geen dieet"), True, True, False, False, False),
    Header(dieet("Veganistisch"), True, True, False, False, False),
    Header(dieet("Vegetarisch"), True, True, False, False, False),
    Header(dieet("Melk allergie"), True, True, False, False, False),
    Header(dieet("Lactose intolerantie"), True, True, False, False, False),
    Header(dieet("Noten allergie"), True, True, False, False, False),
    Header(dieet("Glutenvrij"), True, True, False, False, False),
    Header(dieet("Dieet gebaseerd op godsdienst, namelijk"), True, True, False, False, False),
    Header(dieet_reden("Dieet gebaseerd op godsdienst, namelijk"), True, True, False, False, False),
    Header(dieet("Anders, namelijk"), True, True, False, False, False),
    Header(dieet_reden("Anders, namelijk"), True, True, False, False, False),
    Header(heeft_iets_medisch(), True, True, False, False, False),
    Header(MEDISCH_HANDELEN, True, True, False, False, False),
    Header("Naam contactpersoon in geval van nood", True, True, False, False, False),
    Header("Relatie met de deelnemer", True, True, False, False, False),
    Header("Relatie met de deelnemer Reden: anders (vul in)", True, True, False, False, False),
    Header("Telefoonnummer", True, True, False, False, False),
    KostenHeader("betalingswijze", True, True, False, False, False),
    KostenHeader("machtiging incasso", True, True, False, False, False),
    KostenHeader("groepsrekening", True, True, False, False, False),
    KostenHeader("toestemming ouders/verzorgers", True, True, False, False, False),
    KostenHeader("email ouders/verzorgers", True, True, False, False, False),
    KostenHeader("bank- of girorekening", True, True, False, False, False),
    KostenHeader("- tenaamstelling", True, True, False, False, False),
    KostenHeader("- straat", True, True, False, False, False),
    KostenHeader("huisnr.", True, True, False, False, False),
    KostenHeader("toevoegsel", True, True, False, False, False),
    KostenHeader("- postcode", True, True, False, False, False),
    KostenHeader("plaats", True, True, False, False, False),
    KostenHeader("- land", True, True, False, False, False),
    KostenHeader("factuurnummer", True, True, False, False, False),
    Header("Voorwaarden voor deelname: ik heb de voorwaarden gelezen en ga hiermee akkoord.", True, True, False, False, False),
    Header("Ik geef toestemming voor het gebruik van mijn persoonsgegevens", True, True, False, False, False),
    Header(TOESTEMMING_FOTO, True, True, False, False, False),
    Header(TOESTEMMING_FOTO_NEE, True, True, False, False, False),
    Header("Opmerkingen door organisatie (niet zichtbaar voor deelnemer)", True, True, False, False, False)
]

# for h in HEADERS_NORMAAL_OBJ:
#   print(h.kolom)

HEADERS_OUDERKIND = [
    "Deelnemersnummer",
    "Lidnummer",
    "Lid initialen",
    "Lid voornaam",
    "Lid tussenvoegsel",
    "Lid achternaam",
    "Lid geslacht",
    "Lid straat",
    "Lid huisnummer",
    "Lid toevoegsel huisnr",
    "Lid postcode",
    "Lid plaats",
    "Lid aanvullende adresgegevens",
    "Lid land",
    "Lid geboortedatum",
    "Lid geboorteplaats",
    "Lid e-mailadres",
    "Lid telefoon",
    "Lid mobiel",
    "Organisatienummer",
    "Organisatie",
    "Organisatie plaats",
    "Speleenheid",
    "Functie",
    "Deelnamestatus",
    "Inschrijfdatum",
    "Formuliernummer",
    "Formuliernaam",
    "Ingeschreven door",
    "Totaalbedrag",
    "Openstaand bedrag",
    "Onderdeel van inschrijving",
    "Inschrijving laatst gewijzigd",

    "Kloppen de gegevens bovenaan (adres, huisnummer, telefoonnummer en vooral ook het email adres)?",
    "Subgroepnaam",
    "Heb je een zwemdiploma? (let op: dit kan verplicht zijn voor de HIT waaraan je deelneemt)",
    dieet("Geen dieet", "kind"),
    dieet("Veganistisch", "kind"),
    dieet("Vegetarisch", "kind"),
    dieet("Melk allergie", "kind"),
    dieet("Lactose intolerantie", "kind"),
    dieet("Noten allergie", "kind"),
    dieet("Glutenvrij", "kind"),
    dieet("Dieet gebaseerd op godsdienst, namelijk", "kind"),
    dieet_reden("Dieet gebaseerd op godsdienst, namelijk", "kind"),
    dieet("Anders, namelijk", "kind"),
    dieet_reden("Anders, namelijk", "kind"),
    heeft_iets_medisch('kind'),
    "Voornaam:",
    "Tussenvoegsel:",
    "Achternaam:",
    "Geboortedatum:",
    "Geslacht:",
    "Kind is lid van Scouting:",
    "Kind is lid van Scouting: Reden: ja (vul lidnummer in)",
    "Ouder is lid van Scouting:",
    "Ouder is lid van Scouting: Reden: ja (vul lidnummer in)",
    dieet("Geen dieet", "ouder"),
    dieet("Veganistisch", "ouder"),
    dieet("Vegetarisch", "ouder"),
    dieet("Melk allergie", "ouder"),
    dieet("Lactose intolerantie", "ouder"),
    dieet("Noten allergie", "ouder"),
    dieet("Glutenvrij", "ouder"),
    dieet("Dieet gebaseerd op godsdienst, namelijk", "ouder"),
    dieet_reden("Dieet gebaseerd op godsdienst, namelijk", "ouder"),
    dieet("Anders, namelijk", "ouder"),
    dieet_reden("Anders, namelijk", "ouder"),
    heeft_iets_medisch('ouder'),
    "Telefoonnummer van de mobiele telefoon die je mee neemt naar de HIT.",
    MEDISCH_HANDELEN,
    "Naam contactpersoon in geval van nood",
    "Relatie met de deelnemer",
    "Relatie met de deelnemer Reden: anders (vul in)",
    "Telefoonnummer",
    DEELNAMEKOSTEN + "betalingswijze",
    DEELNAMEKOSTEN + "machtiging incasso",
    DEELNAMEKOSTEN + "groepsrekening",
    DEELNAMEKOSTEN + "toestemming ouders/verzorgers",
    DEELNAMEKOSTEN + "email ouders/verzorgers",
    DEELNAMEKOSTEN + "bank- of girorekening",
    DEELNAMEKOSTEN + "- tenaamstelling",
    DEELNAMEKOSTEN + "- straat",
    DEELNAMEKOSTEN + "huisnr.",
    DEELNAMEKOSTEN + "toevoegsel",
    DEELNAMEKOSTEN + "- postcode",
    DEELNAMEKOSTEN + "plaats",
    DEELNAMEKOSTEN + "- land",
    DEELNAMEKOSTEN + "factuurnummer",
    "Ik ga hier mee akkoord",
    "Ik geef toestemming voor het gebruik van mijn persoonsgegevens",
    TOESTEMMING_FOTO,
    "Opmerkingen door organisatie (niet zichtbaar voor deelnemer)"
]


KOLOMMEN_ALLES = [
    "Formuliernaam",
    # "Inschrijfdatum",
    # "Inschrijving laatst gewijzigd",
    "Subgroepnaam",
    "Subgroep maximum aantal deelnemers",
    "Deelnemersnummer",
    "Lidnummer",
    "Lid voornaam",
    "Lid tussenvoegsel",
    "Lid achternaam",
    "Lid geslacht",
    "Lid straat",
    "Lid huisnummer",
    "Lid toevoegsel huisnr",
    "Lid postcode",
    "Lid plaats",
    "Lid aanvullende adresgegevens",
    "Lid land",
    "Lid geboortedatum",
    "Lid e-mailadres",
    "Lid telefoon",
    "Lid mobiel",
    "Organisatie",
    "Organisatie plaats",
    "Heb je een zwemdiploma? (let op: dit kan verplicht zijn voor de HIT waaraan je deelneemt)",
    "Telefoonnummer van de mobiele telefoon die je mee neemt naar de HIT.",
    dieet("Geen dieet"),
    dieet("Veganistisch"),
    dieet("Vegetarisch"),
    dieet("Melk allergie"),
    dieet("Lactose intolerantie"),
    dieet("Noten allergie"),
    dieet("Glutenvrij"),
    dieet("Dieet gebaseerd op godsdienst, namelijk"),
    dieet_reden("Dieet gebaseerd op godsdienst, namelijk"),
    dieet("Anders, namelijk"),
    dieet_reden("Anders, namelijk"),
    heeft_iets_medisch(),
    MEDISCH_HANDELEN,
    "Naam contactpersoon in geval van nood",
    "Relatie met de deelnemer",
    "Relatie met de deelnemer Reden: anders (vul in)",
    "Telefoonnummer",
    TOESTEMMING_FOTO,
    TOESTEMMING_FOTO_NEE,
]

ALLEEN_MEDISCH = [
    heeft_iets_medisch(),
]

ALLEEN_FOERAGE = [
    dieet("Veganistisch"),
    dieet("Vegetarisch"),
    dieet("Melk allergie"),
    dieet("Lactose intolerantie"),
    dieet("Noten allergie"),
    dieet("Glutenvrij"),
    dieet("Dieet gebaseerd op godsdienst, namelijk"),
    dieet_reden("Dieet gebaseerd op godsdienst, namelijk"),
    dieet("Anders, namelijk"),
    dieet_reden("Anders, namelijk"),
    ]

KOLOMMEN_MEDISCH = [
    'Formuliernaam',
    'Subgroepnaam',
    'Deelnemersnummer',
    'Lid voornaam',
    'Lid tussenvoegsel',
    'Lid achternaam',
    'Lid geboortedatum',
    dieet("Geen dieet"),
    dieet("Veganistisch"),
    dieet("Vegetarisch"),
    dieet("Melk allergie"),
    dieet("Lactose intolerantie"),
    dieet("Noten allergie"),
    dieet("Glutenvrij"),
    dieet("Dieet gebaseerd op godsdienst, namelijk"),
    dieet_reden("Dieet gebaseerd op godsdienst, namelijk"),
    dieet("Anders, namelijk"),
    dieet_reden("Anders, namelijk"),
    heeft_iets_medisch(),
    MEDISCH_HANDELEN,
    "Naam contactpersoon in geval van nood",
    "Relatie met de deelnemer",
    "Relatie met de deelnemer Reden: anders (vul in)",
    "Telefoonnummer"
]

KOLOMMEN_FOERAGE = [
    'Formuliernaam',
    'Subgroepnaam',
    'Deelnemersnummer',
    'Lid voornaam',
    'Lid tussenvoegsel',
    'Lid achternaam',
    dieet("Geen dieet"),
    dieet("Veganistisch"),
    dieet("Vegetarisch"),
    dieet("Melk allergie"),
    dieet("Lactose intolerantie"),
    dieet("Noten allergie"),
    dieet("Glutenvrij"),
    dieet("Dieet gebaseerd op godsdienst, namelijk"),
    dieet_reden("Dieet gebaseerd op godsdienst, namelijk"),
    dieet("Anders, namelijk"),
    dieet_reden("Anders, namelijk"),
    heeft_iets_medisch(),
]

# =======================

def splits_en_zip(formuliernummer):
    """
    Splitst het gecombineerde bestand: per plaats / per kamponderdeel / alles|medisch|foerage
    """
    hit = dict()
    fieldnamesAlles = []

    # Alles inlezen
    with open('gecombineerd_'+formuliernummer+'.csv', 'r') as csvfile:
        hitreader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        fieldnamesAlles = hitreader.fieldnames
        for row in hitreader:
            formulier = row['Formuliernaam'].split(' ', 2)
            hitplaats = formulier[1]
            hitkamp = formulier[2]
            if hitplaats not in hit:
                hit[hitplaats] = dict()
            if hitkamp not in hit[hitplaats]:
                hit[hitplaats][hitkamp] = []
            hit[hitplaats][hitkamp].append(row)


    # Alles per plaats en kamp in bestanden uitschrijven
    for plaats, kampen in hit.items():
        if not os.path.isdir(plaats):
            os.makedirs(plaats)
        schrijf_plaats(plaats, kampen, fieldnamesAlles, 'alles')
        schrijf_plaats(plaats, kampen, KOLOMMEN_MEDISCH, 'medisch')
        schrijf_plaats(plaats, kampen, KOLOMMEN_FOERAGE, 'foerage')
        schrijf_wachtwoorden(plaats, kampen)

    # Per kamponderdeel zippen
    zip_per_kamponderdeel(hit, ['alles', 'medisch', 'foerage'])

    # Alles per plaats zippen
    zip_per_plaats(hit, ['alles','medisch','foerage'])

    # Opruimen
    opruimen(hit)

def schrijf_wachtwoorden(plaats, kampen):
    with open(veilige_naam(plaats, 'wachtwoorden'), 'w') as wout:
        wwriter = csv.DictWriter(wout, fieldnames=['Kamp', 'Wachtwoord'], quotechar='"',quoting=csv.QUOTE_ALL, delimiter=';', extrasaction='ignore')
        wwriter.writeheader()

        wwriter.writerow({"Kamp": '_C-team_' + plaats, "Wachtwoord": PASSWORD_MASK_PLAATS % (plaats)})

        for kamp in sorted(kampen):
            wwriter.writerow({"Kamp": kamp, "Wachtwoord": PASSWORD_MASK_KAMP % (extract_kampinfo_id(kamp))})

def schrijf_plaats(plaats, kampen, fieldnames, suffix):
    plaats_totaal = 0
    with open(veilige_naam(plaats, '_'+plaats+'-'+suffix), 'w') as pout:
        pwriter = csv.DictWriter(pout, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL, delimiter=';', extrasaction='ignore')
        pwriter.writeheader()
        # per kamp
        for kamp in sorted(kampen):
            dlns = sorted(kampen[kamp], key = lambda k : (k['Subgroepnaam'], k['Deelnemersnummer']))
            with open(veilige_naam(plaats, kamp+'-'+suffix), 'w') as kout:
                kwriter = csv.DictWriter(kout, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL, delimiter=';', extrasaction='ignore')
                kwriter.writeheader()
                for row in dlns:
                    if (suffix == 'alles') or (suffix == 'medisch' and iets_is_gevuld(row, ALLEEN_MEDISCH)) or (suffix == 'foerage' and iets_is_gevuld(row, ALLEEN_FOERAGE)):
                        plaats_totaal += 1
                        kwriter.writerow(row)
                        pwriter.writerow(row)
    print("Aantal deelnemers geëxporteerd voor %s (%s): %d" % (plaats, suffix, plaats_totaal))

#
#
#
def zip_per_kamponderdeel(hit, suffixen):
    for plaats, kampen in hit.items():
        # bestanden voor C-team
        te_zippen = ['doc/' + PRIVACY_BIJSLUITER]
        
        for suffix in suffixen:
            te_zippen.append(veilige_naam(plaats, "_%s-%s" % (plaats, suffix)))

        pyminizip.compress_multiple(
            te_zippen,
            [],
            veilige_naam(plaats, "_C-Team_%s" % plaats, '.zip'),
            PASSWORD_MASK_PLAATS % (plaats),
            1
        )

        # bestanden per kamponderdeel
        for kamp, dlns in kampen.items():
            te_zippen = ['doc/' + PRIVACY_BIJSLUITER]
            
            for suffix in suffixen:
                te_zippen.append(veilige_naam(plaats, "%s-%s" % (kamp, suffix)))

            pyminizip.compress_multiple(
                te_zippen,
                [],
                veilige_naam(plaats, kamp, '.zip'),
                PASSWORD_MASK_KAMP % (extract_kampinfo_id(kamp)), 
                1
            )

#
#
#
def zip_per_plaats(hit, suffixen):
    if not os.path.isdir('zips'):
        os.makedirs('zips')

    for plaats, kampen in hit.items():
        te_zippen = []

        te_zippen.append(veilige_naam(plaats, "_C-Team_%s" % plaats, '.zip'))
        for kamp, dlns in kampen.items():
            te_zippen.append(veilige_naam(plaats, kamp, '.zip'))
        te_zippen.append(veilige_naam(plaats, 'wachtwoorden'))

        pyminizip.compress_multiple(
            te_zippen,
            [],
            "zips/%s.zip" % (plaats),
            PASSWORD_MASK_ZIP % (plaats, PINCODES[plaats]),
            1
        )
        print("Zippen bestanden voor %s: %d" % (plaats, len(te_zippen)))

#
#
#
def opruimen(hit):
    for plaats in hit:
        shutil.rmtree(plaats)

#
#
#
def copieer_voeding_van_OK_naar_normaal(src, dst, wie):
    voeding_kolommen = [
        "Geen dieet",
        "Veganistisch",
        "Vegetarisch",
        "Melk allergie",
        "Lactose intolerantie",
        "Noten allergie",
        "Glutenvrij",
        "Dieet gebaseerd op godsdienst, namelijk",
        "Anders, namelijk"
    ]

    for kolom in voeding_kolommen:
        dst[dieet(kolom)] = src[dieet(kolom, wie)]

    voeding_extra_kolommen = [
        "Dieet gebaseerd op godsdienst, namelijk",
        "Anders, namelijk",
    ]

    for kolom in voeding_extra_kolommen:
        dst[dieet_reden(kolom)] = src[dieet_reden(kolom, wie)]


def maak_kind_row_OKK1(row, dlnnrKind):
    kindRow = row
    copieer_voeding_van_OK_naar_normaal(row, kindRow, 'kind')
    kindRow[heeft_iets_medisch()] = row[heeft_iets_medisch('kind')]
    return kindRow

def maak_kind_row_OKK2(row, dlnnrKind):
    """
    Ouder is lid, copieer daarom gegevens naar een regel voor het kind
    """
    kindRow = {}
    kindRow['Formuliernaam'] = row['Formuliernaam']
    kindRow['Subgroepnaam'] = row['Subgroepnaam']
    kindRow['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']
    copieer_voeding_van_OK_naar_normaal(row, kindRow, 'kind')
    kindRow[heeft_iets_medisch()] = row[heeft_iets_medisch('kind')]
    kindRow[MEDISCH_HANDELEN] = row[MEDISCH_HANDELEN]
    kindRow['Deelnemersnummer'] = dlnnrKind
    kindRow['Lidnummer'] = row['Kind is lid van Scouting: Reden: ja (vul lidnummer in)']
    kindRow['Lid voornaam'] = row['Voornaam:']
    kindRow['Lid tussenvoegsel'] = row['Tussenvoegsel:']
    kindRow['Lid achternaam'] = row['Achternaam:']
    kindRow['Lid geslacht'] = row['Geslacht:']
    kindRow['Lid geboortedatum'] = row['Geboortedatum:']
    kindRow[TOESTEMMING_FOTO] = row[TOESTEMMING_FOTO]
    return kindRow

def maak_ouder_row_OKK1(row, dlnnrOuder):
    ouderRow = {}
    ouderRow['Formuliernaam'] = row['Formuliernaam']
    ouderRow['Subgroepnaam'] = row['Subgroepnaam']
    ouderRow['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']
    copieer_voeding_van_OK_naar_normaal(row, ouderRow, 'ouder')
    ouderRow[heeft_iets_medisch()] = row[heeft_iets_medisch('ouder')]
    ouderRow[MEDISCH_HANDELEN] = row[MEDISCH_HANDELEN]
    ouderRow['Deelnemersnummer'] = dlnnrOuder
    ouderRow['Lidnummer'] = row['Ouder is lid van Scouting: Reden: ja (vul lidnummer in)']
    ouderRow['Lid voornaam'] = row['Voornaam:']
    ouderRow['Lid tussenvoegsel'] = row['Tussenvoegsel:']
    ouderRow['Lid achternaam'] = row['Achternaam:']
    ouderRow['Lid geslacht'] = row['Geslacht:']
    ouderRow['Lid geboortedatum'] = row['Geboortedatum:']
    ouderRow[TOESTEMMING_FOTO] = row[TOESTEMMING_FOTO]
    return ouderRow

def maak_ouder_row_OKK2(row, dlnnrOuder):
    ouderRow = row
    copieer_voeding_van_OK_naar_normaal(row, ouderRow, 'ouder')
    ouderRow[heeft_iets_medisch()] = row[heeft_iets_medisch('ouder')]
    return ouderRow

def reformat_date(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')

def reformat_date_dmy(date):
    return datetime.strptime(date, '%d-%m-%Y %H:%M').strftime('%Y-%m-%d %H:%M')

def strip_extra(row):
    frmNaam = row['Formuliernaam']
    frmNaam = frmNaam.replace(' (extra kind)', '')
    frmNaam = re.sub(" \\(\\(\\d+\\)\\)", '', frmNaam)
    return frmNaam

def strip_optie_ouder(row):
    """
        "HIT Mook Ouder-kind kamp (Optie OUDER) (754) ((30296))"
    """
    frmNaam = row['Formuliernaam']
    frmNaam = frmNaam.replace(' (Optie OUDER)', '')
    frmNaam = re.sub(" \\(\\(\\d+\\)\\)", '', frmNaam)
    return frmNaam

def extract_kampinfo_id(kampnaam):
    return re.match(r".* \((\d+)\)", kampnaam).group(1)


def veilige_naam(plaats, kampnaam, ext='.csv'):
    veilig = "".join(x for x in kampnaam if x.isalnum() or x in (' ', '-','(',')','_')) + ext
    if plaats is None:
        return veilig
    return plaats + '/' + veilig


def iets_is_gevuld(row, velden):
    for veld in velden:
        if str(row[veld]) != '':
            return True
    return False

#
#
#
def filter_en_combineer(formuliernummer, formuliernummerOK1, formuliernummerOK2):
    deelnemers = dict()

    # Inlezen gewone kampen
    with open(f"download/formuliergegevens_{formuliernummer}.csv", 'r') as csvfile:
        formreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in formreader:
            is_extra = ('extra kind' in row['Formuliernaam'])
            dlnnr = row['Deelnemersnummer']
            if is_extra:
                dlnnr = dlnnr + 'e'
                row['Deelnemersnummer'] = dlnnr
            row['Inschrijfdatum'] = reformat_date_dmy(row['Inschrijfdatum'])
            row['Inschrijving laatst gewijzigd'] = reformat_date(row['Inschrijving laatst gewijzigd'])

            # voeg de gegevens van het extra-kind formulier bij het gewone formulier
            if is_extra:
                row['Formuliernaam'] = strip_extra(row)
            deelnemers[dlnnr] = row

    print("Aantal deelnemers na inlezen gewone kampen: " + str(len(deelnemers)))

    # Ook de ouder-Kind kampen - DEEL 1
    with open('download/formuliergegevens_'+formuliernummerOK1+'.csv', 'r') as csvfile:
        formreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in formreader:
            row['Inschrijfdatum'] = reformat_date_dmy(row['Inschrijfdatum'])
            row['Inschrijving laatst gewijzigd'] = reformat_date(row['Inschrijving laatst gewijzigd'])
            row['Subgroep maximum aantal deelnemers'] = '2'
            dlnnrKind = row['Deelnemersnummer']+'k'
            dlnnrOuder = row['Deelnemersnummer']+'o'
            row['Deelnemersnummer'] = dlnnrKind
            deelnemers[dlnnrKind] = maak_kind_row_OKK1(row, dlnnrKind)
            deelnemers[dlnnrOuder] = maak_ouder_row_OKK1(row, dlnnrOuder)

    print("Aantal deelnemers na inlezen Ouder-Kind kampen (kind is lid): " + str(len(deelnemers)))

    # Ook de ouder-Kind kampen - DEEL 2
    with open('download/formuliergegevens_'+formuliernummerOK2+'.csv', 'r') as csvfile:
        formreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in formreader:
            row['Inschrijfdatum'] = reformat_date_dmy(row['Inschrijfdatum'])
            row['Inschrijving laatst gewijzigd'] = reformat_date(row['Inschrijving laatst gewijzigd'])
            row['Subgroep maximum aantal deelnemers'] = '2'
            dlnnrKind = row['Deelnemersnummer']+'k'
            dlnnrOuder = row['Deelnemersnummer']+'o'
            row['Deelnemersnummer'] = dlnnrOuder
            row['Formuliernaam'] = strip_optie_ouder(row)

            deelnemers[dlnnrKind] = maak_kind_row_OKK2(row, dlnnrKind)
            deelnemers[dlnnrOuder] = maak_ouder_row_OKK2(row, dlnnrOuder)

    print("Aantal deelnemers na inlezen Ouder-Kind kampen (ouder is lid): " + str(len(deelnemers)))

    # Combineer de subgroepgegevens
    with open('download/subgroepen_'+formuliernummer+'.csv', 'r') as csvfile:
        subreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in subreader:
            is_extra = ('extra kind' in row['Formuliernaam'])

            dlnnr = row['Deelnemersnummer']
            if is_extra:
                dlnnr = dlnnr + 'e'
            if dlnnr in deelnemers:
                deelnemers[dlnnr]['Subgroepnaam'] = row['Subgroepnaam']
                deelnemers[dlnnr]['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']

    # Combineer ook de subgroepgegevens van de Ouder-Kind kampen DEEL 1
    with open('download/subgroepen_'+formuliernummerOK1+'.csv', 'r') as csvfile:
        subreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in subreader:
            dlnnrKind = row['Deelnemersnummer']+'k'
            dlnnrOuder = row['Deelnemersnummer']+'o'
            if dlnnrKind in deelnemers:
                deelnemers[dlnnrKind]['Subgroepnaam'] = row['Subgroepnaam']
                deelnemers[dlnnrKind]['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']
            if dlnnrOuder in deelnemers:
                deelnemers[dlnnrOuder]['Subgroepnaam'] = row['Subgroepnaam']
                deelnemers[dlnnrOuder]['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']


    # Combineer ook de subgroepgegevens van de Ouder-Kind kampen DEEL 2
    with open('download/subgroepen_'+formuliernummerOK2+'.csv', 'r') as csvfile:
        subreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in subreader:
            dlnnrKind = row['Deelnemersnummer']+'k'
            dlnnrOuder = row['Deelnemersnummer']+'o'
            if dlnnrKind in deelnemers:
                deelnemers[dlnnrKind]['Subgroepnaam'] = row['Subgroepnaam']
                deelnemers[dlnnrKind]['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']
            if dlnnrOuder in deelnemers:
                deelnemers[dlnnrOuder]['Subgroepnaam'] = row['Subgroepnaam']
                deelnemers[dlnnrOuder]['Subgroep maximum aantal deelnemers'] = row['Subgroep maximum aantal deelnemers']

    gestript = dict()
    # Haal onnodige inhoud weg
    for dlnr in deelnemers:
        gestript[dlnr] = dict()
        for field in deelnemers[dlnr]:
            if field in KOLOMMEN_ALLES:
                value = deelnemers[dlnr][field]
                if value.lower().strip() in ('06-', 'geen', 'geen.', 'nvt', 'n v t', 'n.v.t', 'n.v.t.', '-', '--', 'niks', 'nee', 'x', '/', 'geen bijzonderheden', 'nvtt', 'nvt.', 'n.t.v.', 'no', 'ne', 'n.v.y.', 'g.b.', 'n.vt', 'nee.', 'n.t.v.', 'gb', '///', '////', 'nope', "'-", 'neen', 'neen.', 'niet van toepassing', 'nee, geen bijzonderheden', 'geen beperkingen', 'nee, n.v.t.' ):
                    if not 'toestemming' in field:
                        value = ''
                gestript[dlnr][field] = value 
        
    # Schrijf alles weg naar een nieuw gecombineerd bestand
    with open('gecombineerd_' + formuliernummer + '.csv', 'w') as out:
        writer = csv.DictWriter(out, fieldnames=KOLOMMEN_ALLES, quotechar='"', quoting=csv.QUOTE_ALL, delimiter=';')
        writer.writeheader()
        for dlnr,row in gestript.items():
            writer.writerow(row)


#
#
#
if __name__ == "__main__":
    filter_en_combineer(SOL_FORMULIERNR_BASIS, SOL_FORMULIERNR_KIND_MET_OUDER, SOL_FORMULIERNR_OUDER_MET_KIND)
    splits_en_zip(SOL_FORMULIERNR_BASIS)
