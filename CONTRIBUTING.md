# Bidra till Stödlotsen

Tack för att du vill hjälpa till! Det viktigaste bidraget du kan göra är att **lägga till nya stöd** och **verifiera att befintlig information stämmer**. Du behöver inte kunna programmera.

## Hur du kan bidra

### 1. Lägga till ett nytt stöd (ingen kodkunskap krävs)

Öppna `data/stod.json` och lägg till ett nytt stöd i listan. Kopiera ett befintligt stöd som mall och fyll i:

```json
{
  "id": "myndighet-kortnamn",
  "namn": "Stödets officiella namn",
  "myndighet": "Ansvarig myndighet",
  "malgrupp": ["privatperson"],
  "kategori": "bostad",
  "taggar": ["relevanta", "sökord"],
  "kort_beskrivning": "En mening som förklarar stödet i klarspråk.",
  "villkor": [
    "Villkor 1",
    "Villkor 2"
  ],
  "belopp": "Ungefärligt belopp eller intervall",
  "ansokan_url": "https://...",
  "info_url": "https://...",
  "relevans_signaler": ["ord som vanliga människor använder"],
  "senast_verifierad": "2026-02-15",
  "region": "nationellt"
}
```

**Tips för relevans_signaler:** Tänk på hur en person som INTE vet att stödet finns skulle beskriva sin situation. Inte "bostadsbidrag" utan "svårt att betala hyran", "dyr bostad", "låg lön".

### 2. Verifiera befintlig information

Välj ett stöd i `data/stod.json`, gå till myndighetens hemsida och kontrollera att:

- Villkoren stämmer
- Beloppen är uppdaterade
- Länkarna fungerar

Uppdatera `senast_verifierad` till dagens datum.

### 3. Lägga till regionala stöd

Många kommuner och regioner har egna stöd som inte finns med. Dessa är särskilt värdefulla att lägga till! Använd `region`-fältet för att ange var stödet gäller, t.ex. `"Ånge kommun"` eller `"Region Västernorrland"`.

### 4. Förbättra sökningen

Om du testar att söka och inte hittar ett stöd som borde dyka upp — lägg till fler `relevans_signaler` på det stödet.

### 5. Översätta

Många nyanlända som behöver stöd har inte svenska som modersmål. Om du kan hjälpa till att skapa en `data/stod_en.json` eller stöd på andra språk är det enormt värdefullt.

## Riktlinjer

- **Klarspråk.** Skriv beskrivningar och villkor så att vem som helst förstår, inte bara myndighetsspråk.
- **Var försiktig med belopp.** Skriv "ca" eller "upp till" om beloppet varierar. Ange alltid vilket år beloppet gäller för.
- **Verifiera mot källan.** Alla uppgifter ska komma från myndighetens officiella hemsida.
- **Ingen reklam.** Inkludera inte kommersiella tjänster.

## Hur du skickar in

### Via GitHub

1. Forka repot
2. Gör dina ändringar i `data/stod.json`
3. Skicka en Pull Request med en kort beskrivning av vad du lagt till/ändrat

### Utan GitHub

Har du ingen GitHub-konto? Skicka informationen via en Issue eller kontakta oss direkt. Beskriv stödet med fälten ovan så lägger vi in det.

## Kategorier

Använd dessa kategorier i `kategori`-fältet:

| Kategori | Beskrivning |
|----------|-------------|
| `bostad` | Boenderelaterat stöd |
| `barn` | Stöd relaterat till barn och familj |
| `hälsa` | Sjukdom, funktionsnedsättning, vård |
| `utbildning` | Studier och kompetensutveckling |
| `grundtrygghet` | Försörjningsstöd, nödhjälp |
| `anställning` | Stöd för att anställa personal |
| `investering` | Investeringsstöd för företag |
| `finansiering` | Lån och kapital för företag |
| `energi` | Energirelaterat stöd |
| `nystart` | Stöd för att starta företag |

Saknas en kategori? Föreslå en ny!
