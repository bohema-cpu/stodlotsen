"""
Stödlotsen - MCP-server för svenska bidrag och stöd
====================================================
En open source MCP-server som hjälper människor att hitta
bidrag och stöd de kan ha rätt till.

Stödjer svenska, engelska och arabiska.

Kräver: pip install mcp
Kör: python server.py (via MCP-klient)
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ── Konfiguration ─────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "data"
STOD_FILE = DATA_DIR / "stod.json"
SUPPORTED_LANGUAGES = {"sv": "svenska", "en": "English", "ar": "العربية"}


def ladda_stod() -> list[dict]:
    """Laddar alla stöd från JSON-databasen."""
    with open(STOD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_name(stod: dict, lang: str = "sv") -> str:
    """Hämtar namn på valt språk med fallback till svenska."""
    if lang == "sv":
        return stod["namn"]
    return stod.get(f"namn_{lang}", stod["namn"])


def get_description(stod: dict, lang: str = "sv") -> str:
    """Hämtar beskrivning på valt språk med fallback till svenska."""
    if lang == "sv":
        return stod["kort_beskrivning"]
    return stod.get(f"kort_beskrivning_{lang}", stod["kort_beskrivning"])


def verifierings_flagga(stod: dict) -> str:
    """Returnerar varningsflagga om info kan vara inaktuell."""
    verifierad = stod.get("senast_verifierad", "")
    try:
        ver_datum = datetime.strptime(verifierad, "%Y-%m-%d")
        if datetime.now() - ver_datum > timedelta(days=180):
            return " ⚠️"
    except ValueError:
        return " ⚠️"
    return ""


def berakna_relevans(stod: dict, fraga_lower: str, sokord: set) -> int:
    """Beräknar relevanspoäng för ett stöd mot en sökfråga."""
    poang = 0

    # Matcha mot relevans_signaler (viktigast)
    for signal in stod.get("relevans_signaler", []):
        signal_lower = signal.lower()
        if signal_lower in fraga_lower:
            poang += 3
        for ord in sokord:
            if len(ord) > 2 and (ord in signal_lower or signal_lower in ord):
                poang += 1

    # Matcha mot taggar
    for tagg in stod.get("taggar", []):
        if tagg.lower() in fraga_lower:
            poang += 2

    # Matcha mot namn och beskrivning (alla språk)
    for falt in ["namn", "namn_en", "kort_beskrivning", "kort_beskrivning_en"]:
        val = stod.get(falt, "").lower()
        if any(ord in val for ord in sokord if len(ord) > 2):
            poang += 1

    return poang


# ── MCP-server ────────────────────────────────────────────────────

# ── MCP-server ────────────────────────────────────────────────────

port = int(os.environ.get("PORT", 8000))

mcp = FastMCP(
    "Stödlotsen",
    instructions=(
        "Hjälper dig hitta svenska bidrag och stöd för privatpersoner och företag. "
        "Supports Swedish, English, and Arabic."
    ),
    host="0.0.0.0",
    port=port,
)


@mcp.tool()
def sok_stod(
    fraga: str,
    malgrupp: str = "",
    kategori: str = "",
    region: str = "",
    sprak: str = "sv",
) -> str:
    """Söker efter relevanta bidrag och stöd baserat på en fritextfråga.

    Beskriv din situation med vanliga ord, t.ex.:
    - "Jag är ensamstående med två barn och har svårt med hyran"
    - "I'm a single parent struggling to pay rent"
    - "Jag driver en liten byggfirma och vill anställa"

    Args:
        fraga: Beskriv din situation eller vad du söker stöd för. Kan vara på svenska, engelska eller arabiska.
        malgrupp: Valfritt filter — "privatperson" eller "företag" / "individual" or "business".
        kategori: Valfritt filter — t.ex. "bostad", "barn", "anställning", "investering", "energi", "utbildning", "hälsa", "grundtrygghet", "finansiering", "nystart".
        region: Valfritt filter — t.ex. "nationellt", "Västernorrland", "kommunalt".
        sprak: Språk för resultat — "sv" (svenska), "en" (English), "ar" (العربية). Standard: "sv".
    """
    alla_stod = ladda_stod()
    fraga_lower = fraga.lower()
    sokord = set(fraga_lower.split())

    # Mappa engelska termer till filter
    malgrupp_map = {"individual": "privatperson", "business": "företag", "person": "privatperson"}
    if malgrupp.lower() in malgrupp_map:
        malgrupp = malgrupp_map[malgrupp.lower()]

    resultat = []

    for stod in alla_stod:
        if malgrupp and malgrupp.lower() not in [m.lower() for m in stod["malgrupp"]]:
            continue
        if kategori and kategori.lower() != stod.get("kategori", "").lower():
            continue
        if region and region.lower() not in stod.get("region", "").lower():
            continue

        poang = berakna_relevans(stod, fraga_lower, sokord)
        if poang > 0:
            resultat.append((poang, stod))

    resultat.sort(key=lambda x: x[0], reverse=True)

    if not resultat:
        msgs = {
            "sv": "Hittade inga stöd som matchar din sökning. Prova att beskriva din situation med andra ord, eller använd lista_stod() för att se alla.",
            "en": "No matching benefits found. Try describing your situation differently, or use lista_stod() to see all available benefits.",
            "ar": "لم يتم العثور على دعم مطابق. حاول وصف وضعك بشكل مختلف.",
        }
        return msgs.get(sprak, msgs["sv"])

    output = []
    for poang, stod in resultat[:8]:
        flagga = verifierings_flagga(stod)
        namn = get_name(stod, sprak)
        beskr = get_description(stod, sprak)

        output.append(
            f"### {namn}{flagga}\n"
            f"**{'Myndighet' if sprak == 'sv' else 'Authority'}:** {stod['myndighet']}\n"
            f"**{'Målgrupp' if sprak == 'sv' else 'Target'}:** {', '.join(stod['malgrupp'])}\n"
            f"**{'Beskrivning' if sprak == 'sv' else 'Description'}:** {beskr}\n"
            f"**{'Belopp' if sprak == 'sv' else 'Amount'}:** {stod['belopp']}\n"
            f"**{'Mer info' if sprak == 'sv' else 'More info'}:** {stod.get('info_url', '-')}\n"
            f"**ID:** {stod['id']}"
        )

    headers = {
        "sv": f"Hittade {len(resultat)} möjliga stöd (visar topp {min(len(resultat), 8)}):\n\n",
        "en": f"Found {len(resultat)} potential benefits (showing top {min(len(resultat), 8)}):\n\n",
        "ar": f"تم العثور على {len(resultat)} دعم محتمل:\n\n",
    }
    return headers.get(sprak, headers["sv"]) + "\n\n---\n\n".join(output)


@mcp.tool()
def stod_detaljer(stod_id: str, sprak: str = "sv") -> str:
    """Hämtar fullständig information om ett specifikt stöd.

    Args:
        stod_id: ID för stödet, t.ex. "fk-bostadsbidrag". Får du från sok_stod().
        sprak: Språk — "sv", "en", eller "ar". Standard: "sv".
    """
    alla_stod = ladda_stod()

    for stod in alla_stod:
        if stod["id"] == stod_id:
            namn = get_name(stod, sprak)
            beskr = get_description(stod, sprak)
            villkor_lista = "\n".join(f"  • {v}" for v in stod.get("villkor", []))
            flagga = verifierings_flagga(stod)
            varning = ""
            if flagga:
                varning = "\n\n⚠️ Information may be outdated." if sprak == "en" else "\n\n⚠️ Informationen kan vara inaktuell."

            return (
                f"# {namn}\n\n"
                f"**{'Myndighet' if sprak == 'sv' else 'Authority'}:** {stod['myndighet']}\n"
                f"**{'Målgrupp' if sprak == 'sv' else 'Target'}:** {', '.join(stod['malgrupp'])}\n"
                f"**{'Kategori' if sprak == 'sv' else 'Category'}:** {stod.get('kategori', '-')}\n"
                f"**{'Region' if sprak == 'sv' else 'Region'}:** {stod.get('region', '-')}\n\n"
                f"## {'Beskrivning' if sprak == 'sv' else 'Description'}\n{beskr}\n\n"
                f"## {'Villkor' if sprak == 'sv' else 'Requirements'}\n{villkor_lista}\n\n"
                f"## {'Belopp' if sprak == 'sv' else 'Amount'}\n{stod['belopp']}\n\n"
                f"## {'Länkar' if sprak == 'sv' else 'Links'}\n"
                f"- {'Ansökan' if sprak == 'sv' else 'Apply'}: {stod.get('ansokan_url') or '-'}\n"
                f"- {'Mer info' if sprak == 'sv' else 'More info'}: {stod.get('info_url', '-')}\n\n"
                f"{'Senast verifierad' if sprak == 'sv' else 'Last verified'}: {stod.get('senast_verifierad', '?')}"
                f"{varning}"
            )

    return f"No benefit found with ID '{stod_id}'." if sprak == "en" else f"Hittade inget stöd med ID '{stod_id}'."


@mcp.tool()
def lista_stod(malgrupp: str = "", sprak: str = "sv") -> str:
    """Listar alla tillgängliga stöd i databasen.

    Args:
        malgrupp: "privatperson" / "individual" eller "företag" / "business". Tomt = alla.
        sprak: Språk — "sv", "en", eller "ar". Standard: "sv".
    """
    alla_stod = ladda_stod()
    malgrupp_map = {"individual": "privatperson", "business": "företag", "person": "privatperson"}
    if malgrupp.lower() in malgrupp_map:
        malgrupp = malgrupp_map[malgrupp.lower()]

    if malgrupp:
        alla_stod = [s for s in alla_stod if malgrupp.lower() in [m.lower() for m in s["malgrupp"]]]

    if not alla_stod:
        return "Inga stöd hittades." if sprak == "sv" else "No benefits found."

    output = []
    nuvarande_kategori = ""
    sorterade = sorted(alla_stod, key=lambda s: s.get("kategori", "övrigt"))

    for stod in sorterade:
        kat = stod.get("kategori", "övrigt").capitalize()
        if kat != nuvarande_kategori:
            nuvarande_kategori = kat
            output.append(f"\n## {nuvarande_kategori}")

        namn = get_name(stod, sprak)
        beskr = get_description(stod, sprak)
        flagga = verifierings_flagga(stod)
        region_tag = f" 📍{stod['region']}" if stod.get("region") not in ["nationellt", ""] else ""
        output.append(f"- **{namn}**{flagga}{region_tag} ({stod['myndighet']}) — {beskr} [ID: {stod['id']}]")

    header = f"Totalt {len(alla_stod)} stöd"
    if malgrupp:
        header += f" (filtrerat: {malgrupp})"
    header += ":\n"

    return header + "\n".join(output)


@mcp.tool()
def stod_statistik() -> str:
    """Visar statistik om stöddatabasen."""
    alla_stod = ladda_stod()
    kategorier, malgrupper, myndigheter = {}, {}, {}
    inaktuella, regionala = 0, 0
    sprak_count = {"en": 0, "ar": 0}

    for stod in alla_stod:
        kat = stod.get("kategori", "övrigt")
        kategorier[kat] = kategorier.get(kat, 0) + 1
        for mg in stod["malgrupp"]:
            malgrupper[mg] = malgrupper.get(mg, 0) + 1
        myn = stod["myndighet"]
        myndigheter[myn] = myndigheter.get(myn, 0) + 1
        if stod.get("region", "nationellt") != "nationellt":
            regionala += 1
        if stod.get("namn_en"):
            sprak_count["en"] += 1
        if stod.get("namn_ar"):
            sprak_count["ar"] += 1
        try:
            ver = datetime.strptime(stod.get("senast_verifierad", ""), "%Y-%m-%d")
            if datetime.now() - ver > timedelta(days=180):
                inaktuella += 1
        except ValueError:
            inaktuella += 1

    kat_str = "\n".join(f"  - {k}: {v}" for k, v in sorted(kategorier.items()))
    mg_str = "\n".join(f"  - {k}: {v}" for k, v in sorted(malgrupper.items()))
    myn_str = "\n".join(f"  - {k}: {v}" for k, v in sorted(myndigheter.items()))

    return (
        f"# Stödlotsen — Databasstatistik\n\n"
        f"**Totalt:** {len(alla_stod)} stöd\n"
        f"**Regionala:** {regionala}\n"
        f"**Potentiellt inaktuella:** {inaktuella}\n"
        f"**Översatta till engelska:** {sprak_count['en']}\n"
        f"**Översatta till arabiska:** {sprak_count['ar']}\n\n"
        f"## Per kategori\n{kat_str}\n\n"
        f"## Per målgrupp\n{mg_str}\n\n"
        f"## Per myndighet\n{myn_str}"
    )


# ── Kör servern ───────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if "--web" in sys.argv or os.environ.get("PORT"):
        # Webbläge — för deployment på Render/Vercel/etc.
        # Nås via URL som MCP-connector i Claude.ai
        print(f"🧭 Stödlotsen startar i webbläge på port {port}...")
        mcp.run(transport="streamable-http")
    else:
        # Lokalt läge — för Claude Desktop / Claude Code
        mcp.run()
