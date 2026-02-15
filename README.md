# 🧭 Stödlotsen

En open source MCP-server som hjälper människor att hitta svenska bidrag och stöd de kan ha rätt till — genom att beskriva sin situation med vanliga ord.

**Supports Swedish, English, and Arabic** 🇸🇪 🇬🇧 🇸🇦

## Varför?

De som behöver stöd mest har ofta svårast att hitta det. Informationen är utspridd, skriven på byråkratsvenska, och kräver att man redan vet vad man letar efter. Stödlotsen vänder på det: beskriv din situation, få tillbaka vad du kan ha rätt till.

### Exempel

- *"Jag är ensamstående med två barn och har svårt att få ihop hyran"*
  → Bostadsbidrag, Underhållsstöd, Barnbidrag, Ekonomiskt bistånd

- *"I'm a newcomer to Sweden and want to find support"*
  → Results in English with relevant benefits

- *"Jag driver en byggfirma i Ånge och vill investera i en ny maskin"*
  → Generellt investeringsstöd Västernorrland, Regionalt investeringsstöd, Företagsstöd landsbygd

## Databasen

**29 stöd** i nuvarande version, inklusive:

| Kategori | Antal | Exempel |
|----------|-------|---------|
| Bostad | 4 | Bostadsbidrag, ROT-avdrag |
| Barn & familj | 4 | Föräldrapenning, Underhållsstöd, VAB |
| Hälsa & funktionsnedsättning | 5 | Sjukpenning, Aktivitetsersättning, Assistansersättning |
| Investering | 7 | Regionalt investeringsstöd, Vinnova, Affärsutvecklingscheckar |
| Anställning | 2 | Nystartsjobb, Introduktionsjobb |
| Grundtrygghet | 2 | A-kassa, Ekonomiskt bistånd |
| Utbildning | 1 | Studiemedel |
| Energi | 1 | Energieffektivisering |
| Nystart | 2 | Starta eget, Utvecklingsstödet Västernorrland |
| Finansiering | 1 | Almis mikrolån |

**5 regionala stöd** specifikt för Västernorrland (Region Västernorrland).

## Kom igång

### Alt 1: Koppla till Claude.ai via webben (enklast)

Stödlotsen kan köras som en webbtjänst och kopplas direkt till Claude.ai i webbläsaren — precis som andra MCP-connectors.

**Om någon redan har lagt upp Stödlotsen på nätet** (t.ex. på Render):

1. Gå till [claude.ai](https://claude.ai)
2. Klicka på ditt namn → Inställningar → Connectors (eller MCP-servrar)
3. Lägg till en ny connector med URL:en: `https://stodlotsen.onrender.com/mcp`
4. Skriv i chatten: *"Vilka bidrag kan jag ha rätt till som ensamstående pappa med barn i Ånge?"*

**Om du vill lägga upp den själv på Render (gratis):**

1. Lägg koden på GitHub (skapa ett repo, ladda upp filerna)
2. Gå till [render.com](https://render.com) och skapa ett gratis konto
3. Klicka "New" → "Web Service" → koppla ditt GitHub-repo
4. Render hittar `render.yaml` automatiskt och startar tjänsten
5. Du får en URL som `https://ditt-namn.onrender.com/mcp`
6. Lägg till den URL:en som connector i Claude.ai (se steg ovan)

> ⚠️ Render gratis-plan sätter tjänsten i viloläge efter 15 min utan trafik.
> Första anropet kan ta ~30 sek att vakna. Efterföljande är snabba.

### Alt 2: Snabbtest lokalt (för utvecklare)

```bash
git clone https://github.com/ditt-användarnamn/stodlotsen.git
cd stodlotsen
pip install mcp
python test_standalone.py     # Kör 15 automatiska tester
```

### Alt 3: Claude Desktop / Claude Code (lokal MCP)

Kräver [Claude Desktop](https://claude.ai/download) (macOS 12+) eller Claude Code.

**Claude Desktop** — redigera konfigurationen:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stodlotsen": {
      "command": "python",
      "args": ["/sökväg/till/stodlotsen/server.py"]
    }
  }
}
```

**Claude Code:**
```bash
claude mcp add stodlotsen python /sökväg/till/stodlotsen/server.py
```

### Alt 4: MCP Inspector (interaktiv testning)

```bash
npx @modelcontextprotocol/inspector python server.py
```

## Verktyg

| Verktyg | Beskrivning |
|---------|-------------|
| `sok_stod` | Fritextsökning — beskriv din situation på svenska, engelska eller arabiska |
| `stod_detaljer` | Fullständig info om ett specifikt stöd |
| `lista_stod` | Lista alla stöd, filtrerat på målgrupp |
| `stod_statistik` | Databasstatistik och verifieringsstatus |

### Flerspråksstöd

Alla verktyg har en `sprak`-parameter: `"sv"` (svenska), `"en"` (English), `"ar"` (العربية).

## Scrapers

Automatiska scrapers som kontrollerar att myndigheternas sidor fortfarande är nåbara och uppdaterar verifieringsdatum:

```bash
# Dry run (visar bara resultat)
python scrapers/run_all.py

# Uppdatera databasen
python scrapers/run_all.py --live
```

Tillgängliga scrapers:
- `forsakringskassan.py` — Kontrollerar 11 sidor på FK
- `region_vasternorrland.py` — Kontrollerar Region Västernorrlands företagsstöd

Scrapers kräver: `pip install requests beautifulsoup4`

## Bidra

Se [CONTRIBUTING.md](CONTRIBUTING.md). Du behöver **inte kunna programmera** — det viktigaste bidraget är att lägga till och verifiera stöd i `data/stod.json`.

### Mest eftersökta bidrag

- Fler regionala stöd (andra län och kommuner)
- Fler språk (tigrinja, dari, somaliska, ukrainska)
- Stöd för pensionärer
- EU-bidrag för företag
- Stöd specifikt för nyanlända

## Projektstruktur

```
stodlotsen/
├── server.py              # MCP-servern (lokal + webb)
├── data/
│   └── stod.json          # 29 stöd med sv/en/ar
├── test_standalone.py     # 15 automatiska tester
├── requirements.txt       # Python-beroenden
├── render.yaml            # Deploy-config för Render.com
├── scrapers/
│   ├── run_all.py         # Kör alla scrapers
│   ├── forsakringskassan.py
│   └── region_vasternorrland.py
├── CONTRIBUTING.md        # Guide för att bidra (ingen kod krävs)
├── LICENSE                # MIT
└── README.md
```

## Ansvarsfriskrivning

Stödlotsen är ett hjälpverktyg, inte en myndighet. Informationen kan vara felaktig eller inaktuell. Kontrollera alltid hos ansvarig myndighet. Stöd som inte verifierats på 6+ månader flaggas med ⚠️.

## Licens

MIT — använd fritt, bidra gärna tillbaka.
