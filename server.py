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


# ── Inbakad databas (fallback om data/stod.json saknas) ─────────
EMBEDDED_STOD = [
  {
    "id": "fk-bostadsbidrag",
    "namn": "Bostadsbidrag",
    "namn_en": "Housing allowance",
    "namn_ar": "بدل السكن",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "bostad",
    "taggar": [
      "bostad",
      "barn",
      "låg inkomst",
      "hyra",
      "ungdom"
    ],
    "kort_beskrivning": "Ekonomiskt stöd för boendekostnader till barnfamiljer och unga utan barn.",
    "kort_beskrivning_en": "Financial support for housing costs for families with children and young people without children.",
    "kort_beskrivning_ar": "دعم مالي لتكاليف السكن للعائلات التي لديها أطفال والشباب بدون أطفال.",
    "villkor": [
      "Barnfamilj (oavsett ålder) eller person 18-28 år utan barn",
      "Inkomst under viss gräns beroende på familjestorlek",
      "Boendekostnad som överstiger viss nivå i förhållande till inkomst",
      "Folkbokförd i Sverige"
    ],
    "belopp": "Varierar beroende på inkomst, hyra och antal barn. Upp till ca 5 300 kr/mån för barnfamiljer.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/bostadsbidrag",
    "info_url": "https://www.forsakringskassan.se/privatperson/bostadsbidrag",
    "relevans_signaler": [
      "ensamstående",
      "barn",
      "hyra",
      "låg inkomst",
      "deltid",
      "boende",
      "ungdom",
      "ung",
      "student",
      "dyr hyra",
      "svårt att betala hyran"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-underhallsstod",
    "namn": "Underhållsstöd",
    "namn_en": "Maintenance support",
    "namn_ar": "دعم النفقة",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "barn",
    "taggar": [
      "barn",
      "ensamstående",
      "underhåll",
      "separation"
    ],
    "kort_beskrivning": "Stöd till förälder som inte får underhållsbidrag från den andra föräldern.",
    "kort_beskrivning_en": "Support for a parent who does not receive maintenance from the other parent.",
    "kort_beskrivning_ar": "دعم للوالد الذي لا يتلقى نفقة من الوالد الآخر.",
    "villkor": [
      "Barnet bor varaktigt hos dig",
      "Andra föräldern betalar inte underhållsbidrag eller betalar för lite",
      "Barnet är under 18 år"
    ],
    "belopp": "1 773 kr/mån per barn (2025). Förhöjt belopp för barn 15+: 2 223 kr/mån.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/foralder/underhallsstod",
    "info_url": "https://www.forsakringskassan.se/privatperson/foralder/underhallsstod",
    "relevans_signaler": [
      "ensamstående förälder",
      "separation",
      "underhåll",
      "barn",
      "ensam vårdnad",
      "delad vårdnad",
      "skilsmässa",
      "den andra föräldern betalar inte"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-barnbidrag",
    "namn": "Barnbidrag och flerbarnstillägg",
    "namn_en": "Child allowance",
    "namn_ar": "بدل الأطفال",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "barn",
    "taggar": [
      "barn",
      "familj"
    ],
    "kort_beskrivning": "Automatiskt bidrag för alla barn folkbokförda i Sverige.",
    "kort_beskrivning_en": "Automatic allowance for all children registered in Sweden.",
    "kort_beskrivning_ar": "بدل تلقائي لجميع الأطفال المسجلين في السويد.",
    "villkor": [
      "Barnet är folkbokfört i Sverige",
      "Barnet är under 16 år (förlängt till 18 vid gymnasiestudier)"
    ],
    "belopp": "1 250 kr/mån per barn. Flerbarnstillägg: 150 kr för 2 barn, 730 kr för 3 barn.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/foralder/barnbidrag",
    "info_url": "https://www.forsakringskassan.se/privatperson/foralder/barnbidrag",
    "relevans_signaler": [
      "barn",
      "förälder",
      "familj",
      "nyfödd",
      "flera barn"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-sjukpenning",
    "namn": "Sjukpenning",
    "namn_en": "Sickness benefit",
    "namn_ar": "تعويض المرض",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "hälsa",
    "taggar": [
      "sjukdom",
      "sjukskriven",
      "inkomst",
      "arbetsförmåga"
    ],
    "kort_beskrivning": "Ersättning vid sjukdom som gör att du inte kan arbeta.",
    "kort_beskrivning_en": "Compensation when illness prevents you from working.",
    "kort_beskrivning_ar": "تعويض عندما يمنعك المرض من العمل.",
    "villkor": [
      "Nedsatt arbetsförmåga pga sjukdom (minst 25%)",
      "Sjukperioden överstiger arbetsgivarens sjuklöneperiod (14 dagar)",
      "SGI måste vara fastställd"
    ],
    "belopp": "Ca 80% av SGI, max ca 1 116 kr/dag (2025).",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/sjuk/sjukpenning",
    "info_url": "https://www.forsakringskassan.se/privatperson/sjuk/sjukpenning",
    "relevans_signaler": [
      "sjuk",
      "sjukskriven",
      "kan inte jobba",
      "arbetsförmåga",
      "läkarintyg",
      "utbränd",
      "utmattning",
      "depression",
      "ångest"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-foraldrapenning",
    "namn": "Föräldrapenning",
    "namn_en": "Parental benefit",
    "namn_ar": "بدل الوالدين",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "barn",
    "taggar": [
      "barn",
      "föräldraledig",
      "bebis",
      "nyfödd"
    ],
    "kort_beskrivning": "Ersättning när du är hemma med ditt barn istället för att arbeta.",
    "kort_beskrivning_en": "Compensation when you stay home with your child instead of working.",
    "kort_beskrivning_ar": "تعويض عندما تبقى في المنزل مع طفلك بدلاً من العمل.",
    "villkor": [
      "Barnet är under 12 år",
      "Du avstår från att arbeta",
      "480 dagar per barn att dela mellan föräldrarna"
    ],
    "belopp": "Ca 80% av SGI i 390 dagar, därefter 180 kr/dag i 90 dagar.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/foralder/foraldrapenning",
    "info_url": "https://www.forsakringskassan.se/privatperson/foralder/foraldrapenning",
    "relevans_signaler": [
      "föräldraledig",
      "bebis",
      "nyfödd",
      "hemma med barn",
      "pappaledig",
      "mammaledig"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-vab",
    "namn": "Tillfällig föräldrapenning (VAB)",
    "namn_en": "Temporary parental benefit (care of sick child)",
    "namn_ar": "إعانة الوالدين المؤقتة",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "barn",
    "taggar": [
      "barn",
      "sjukt barn",
      "VAB",
      "förälder"
    ],
    "kort_beskrivning": "Ersättning när du stannar hemma för att ta hand om sjukt barn.",
    "kort_beskrivning_en": "Compensation when staying home to care for a sick child.",
    "kort_beskrivning_ar": "تعويض عند البقاء في المنزل لرعاية طفل مريض.",
    "villkor": [
      "Barnet är under 12 år (i vissa fall äldre)",
      "Du avstår från arbete",
      "Barnet är sjukt eller smittat"
    ],
    "belopp": "Ca 80% av SGI.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/foralder/vard-av-sjukt-barn-vab",
    "info_url": "https://www.forsakringskassan.se/privatperson/foralder/vard-av-sjukt-barn-vab",
    "relevans_signaler": [
      "sjukt barn",
      "VAB",
      "vabba",
      "hemma med sjukt barn"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-aktivitetsersattning",
    "namn": "Aktivitetsersättning",
    "namn_en": "Activity compensation",
    "namn_ar": "تعويض النشاط",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "hälsa",
    "taggar": [
      "funktionsnedsättning",
      "ung",
      "arbetsförmåga",
      "sjukdom"
    ],
    "kort_beskrivning": "Ersättning till dig 19-29 år som inte kan arbeta pga sjukdom eller funktionsnedsättning.",
    "kort_beskrivning_en": "Compensation for people aged 19-29 unable to work due to illness or disability.",
    "kort_beskrivning_ar": "تعويض للأشخاص 19-29 الذين لا يستطيعون العمل بسبب المرض أو الإعاقة.",
    "villkor": [
      "Ålder 19-29 år",
      "Nedsatt arbetsförmåga under minst 1 år",
      "Läkarutlåtande krävs"
    ],
    "belopp": "Garantiersättning: ca 10 990 kr/mån vid hel ersättning.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/vuxen-med-funktionsnedsattning/aktivitetsersattning-for-unga-vuxna",
    "info_url": "https://www.forsakringskassan.se/privatperson/vuxen-med-funktionsnedsattning/aktivitetsersattning-for-unga-vuxna",
    "relevans_signaler": [
      "ung",
      "funktionsnedsättning",
      "kan inte jobba",
      "sjuk",
      "19 år",
      "handikapp",
      "nedsatt arbetsförmåga",
      "psykisk ohälsa"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-sjukersattning",
    "namn": "Sjukersättning",
    "namn_en": "Sickness compensation",
    "namn_ar": "تعويض العجز",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "hälsa",
    "taggar": [
      "funktionsnedsättning",
      "varaktig",
      "arbetsförmåga"
    ],
    "kort_beskrivning": "Ersättning om du är 19-65 år och troligen aldrig kommer kunna arbeta heltid pga sjukdom.",
    "kort_beskrivning_en": "Compensation if aged 19-65 and likely never able to work full-time.",
    "kort_beskrivning_ar": "تعويض إذا كان عمرك 19-65 ولن تتمكن أبدًا من العمل بدوام كامل.",
    "villkor": [
      "Ålder 19-65 år",
      "Arbetsförmågan varaktigt nedsatt minst 25%",
      "Alla rehabiliteringsmöjligheter uttömda"
    ],
    "belopp": "Ca 64% av antagen inkomst, garantiersättning ca 10 990 kr/mån.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/sjuk/sjukersattning",
    "info_url": "https://www.forsakringskassan.se/privatperson/sjuk/sjukersattning",
    "relevans_signaler": [
      "varaktigt sjuk",
      "aldrig kunna jobba",
      "förtidspension",
      "kronisk",
      "funktionsnedsättning"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-merkostnadsersattning",
    "namn": "Merkostnadsersättning",
    "namn_en": "Additional cost compensation",
    "namn_ar": "تعويض التكاليف الإضافية",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "hälsa",
    "taggar": [
      "funktionsnedsättning",
      "merkostnad",
      "hjälpmedel"
    ],
    "kort_beskrivning": "Ersätter extra kostnader du har pga funktionsnedsättning.",
    "kort_beskrivning_en": "Compensates extra costs caused by a disability.",
    "kort_beskrivning_ar": "يعوض التكاليف الإضافية الناتجة عن الإعاقة.",
    "villkor": [
      "Funktionsnedsättning som påverkar dig",
      "Merkostnader över 14 800 kr/år",
      "Kostnaderna ska bero på funktionsnedsättningen"
    ],
    "belopp": "5 nivåer: från ca 1 190 till 3 563 kr/mån.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/funktionsnedsattning/merkostnadsersattning-for-vuxna",
    "info_url": "https://www.forsakringskassan.se/privatperson/funktionsnedsattning/merkostnadsersattning-for-vuxna",
    "relevans_signaler": [
      "funktionsnedsättning",
      "extra kostnader",
      "handikapp",
      "hjälpmedel",
      "specialkost",
      "slitage"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-bostadstillagg",
    "namn": "Bostadstillägg vid sjuk-/aktivitetsersättning",
    "namn_en": "Housing supplement with disability benefits",
    "namn_ar": "ملحق السكن مع إعانات العجز",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "bostad",
    "taggar": [
      "bostad",
      "sjukersättning",
      "aktivitetsersättning"
    ],
    "kort_beskrivning": "Extra stöd för boendekostnader om du har sjuk- eller aktivitetsersättning.",
    "kort_beskrivning_en": "Extra housing support if you receive sickness/activity compensation.",
    "kort_beskrivning_ar": "دعم سكن إضافي إذا كنت تتلقى تعويض المرض أو النشاط.",
    "villkor": [
      "Du har sjuk- eller aktivitetsersättning",
      "Boendekostnader",
      "Inkomst och förmögenhet under vissa gränser"
    ],
    "belopp": "Upp till 7 500 kr/mån.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/funktionsnedsattning/bostadstillagg",
    "info_url": "https://www.forsakringskassan.se/privatperson/funktionsnedsattning/bostadstillagg",
    "relevans_signaler": [
      "sjukersättning",
      "aktivitetsersättning",
      "hyra",
      "boende",
      "funktionsnedsättning"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "fk-assistansersattning",
    "namn": "Assistansersättning",
    "namn_en": "Personal assistance compensation",
    "namn_ar": "تعويض المساعدة الشخصية",
    "myndighet": "Försäkringskassan",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "hälsa",
    "taggar": [
      "funktionsnedsättning",
      "assistans",
      "hjälp",
      "LSS"
    ],
    "kort_beskrivning": "Ersättning för personlig assistans vid stora funktionsnedsättningar.",
    "kort_beskrivning_en": "Compensation for personal assistance with major disabilities.",
    "kort_beskrivning_ar": "تعويض المساعدة الشخصية عند الإعاقات الكبيرة.",
    "villkor": [
      "Behov av personlig assistans >20 timmar/vecka",
      "Tillhör personkrets enligt LSS",
      "Under 66 år vid första ansökan"
    ],
    "belopp": "Ca 332 kr/timme (2025). Timmar bestäms individuellt.",
    "ansokan_url": "https://www.forsakringskassan.se/privatperson/funktionsnedsattning/assistansersattning",
    "info_url": "https://www.forsakringskassan.se/privatperson/funktionsnedsattning/assistansersattning",
    "relevans_signaler": [
      "personlig assistans",
      "funktionsnedsättning",
      "hjälp hemma",
      "LSS",
      "stor funktionsnedsättning"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "af-nystartsjobb",
    "namn": "Nystartsjobb",
    "namn_en": "New start jobs",
    "namn_ar": "وظائف البداية الجديدة",
    "myndighet": "Arbetsförmedlingen",
    "malgrupp": [
      "företag"
    ],
    "kategori": "anställning",
    "taggar": [
      "anställa",
      "subvention",
      "långtidsarbetslös",
      "nyanländ"
    ],
    "kort_beskrivning": "Ekonomiskt stöd till arbetsgivare som anställer personer som stått utanför arbetsmarknaden.",
    "kort_beskrivning_en": "Financial support for employers hiring people outside the labour market.",
    "kort_beskrivning_ar": "دعم مالي لأصحاب العمل الذين يوظفون أشخاصًا خارج سوق العمل.",
    "villkor": [
      "Den anställde har varit arbetslös länge, sjukskriven, eller är nyanländ",
      "Anställningsvillkor enligt kollektivavtal",
      "Ansökan via Arbetsförmedlingen"
    ],
    "belopp": "Stöd motsvarande arbetsgivaravgiften (ca 31%) i upp till 2-3 år.",
    "ansokan_url": "https://arbetsformedlingen.se/for-arbetsgivare/anstallningsstod/nystartsjobb",
    "info_url": "https://arbetsformedlingen.se/for-arbetsgivare/anstallningsstod/nystartsjobb",
    "relevans_signaler": [
      "anställa",
      "första anställd",
      "personal",
      "rekrytera",
      "lönestöd",
      "subvention",
      "arbetsgivare"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "af-introduktionsjobb",
    "namn": "Introduktionsjobb",
    "namn_en": "Introduction jobs",
    "namn_ar": "وظائف تمهيدية",
    "myndighet": "Arbetsförmedlingen",
    "malgrupp": [
      "företag"
    ],
    "kategori": "anställning",
    "taggar": [
      "anställa",
      "subvention",
      "nyanländ",
      "ung",
      "lärling"
    ],
    "kort_beskrivning": "Subventionerad anställning med handledning och utbildning.",
    "kort_beskrivning_en": "Subsidised employment with mentoring and training.",
    "kort_beskrivning_ar": "توظيف مدعوم مع إرشاد وتدريب.",
    "villkor": [
      "Nyanländ, ung utan gymnasie, eller långtidsarbetslös",
      "Minst 25% utbildning/handledning",
      "Lön enligt kollektivavtal"
    ],
    "belopp": "Upp till 80% av lönekostnaden.",
    "ansokan_url": "https://arbetsformedlingen.se/for-arbetsgivare/anstallningsstod/introduktionsjobb",
    "info_url": "https://arbetsformedlingen.se/for-arbetsgivare/anstallningsstod/introduktionsjobb",
    "relevans_signaler": [
      "anställa",
      "handledning",
      "utbildning",
      "nyanländ",
      "ung",
      "lärling"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "af-starta-eget",
    "namn": "Stöd att starta eget",
    "namn_en": "Support to start your own business",
    "namn_ar": "دعم لبدء عملك الخاص",
    "myndighet": "Arbetsförmedlingen",
    "malgrupp": [
      "privatperson",
      "företag"
    ],
    "kategori": "nystart",
    "taggar": [
      "starta företag",
      "eget företag",
      "arbetslös"
    ],
    "kort_beskrivning": "Aktivitetsstöd i 6 månader medan du startar eget, om du är arbetssökande.",
    "kort_beskrivning_en": "Activity support for 6 months while starting your own business.",
    "kort_beskrivning_ar": "دعم لمدة 6 أشهر أثناء بدء عملك الخاص.",
    "villkor": [
      "Inskriven som arbetssökande",
      "Livskraftig affärsidé",
      "Arbetsförmedlingen bedömer stödet ökar dina chanser"
    ],
    "belopp": "Aktivitetsstöd motsvarande a-kasseersättning i normalt 6 månader.",
    "ansokan_url": "https://arbetsformedlingen.se/for-arbetssokande/extra-stod/starta-eget",
    "info_url": "https://arbetsformedlingen.se/for-arbetssokande/extra-stod/starta-eget",
    "relevans_signaler": [
      "starta eget",
      "starta företag",
      "arbetslös",
      "egenföretagare",
      "affärsidé",
      "bli egen"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "tv-regionalt-investeringsstod",
    "namn": "Regionalt investeringsstöd",
    "namn_en": "Regional investment support",
    "namn_ar": "دعم الاستثمار الإقليمي",
    "myndighet": "Tillväxtverket / Region",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "investering",
      "expansion",
      "maskin",
      "lokal",
      "glesbygd"
    ],
    "kort_beskrivning": "Stöd till företag som investerar i stödområden, t.ex. Norrlands inland.",
    "kort_beskrivning_en": "Support for businesses investing in designated support areas.",
    "kort_beskrivning_ar": "دعم للشركات التي تستثمر في مناطق الدعم المحددة.",
    "villkor": [
      "Företaget verkar i stödområde A eller B",
      "Investeringen avser byggnader, maskiner eller utrustning",
      "Bidrar till hållbar tillväxt",
      "Ansökan INNAN investering påbörjas"
    ],
    "belopp": "15-40% av investeringskostnaden.",
    "ansokan_url": "https://tillvaxtverket.se/tillvaxtverket/sokfinansiering/utlysningar/fastautlysningar/regionaltinvesteringsstod.3519.html",
    "info_url": "https://tillvaxtverket.se/tillvaxtverket/sokfinansiering/utlysningar/fastautlysningar/regionaltinvesteringsstod.3519.html",
    "relevans_signaler": [
      "investera",
      "maskin",
      "bygga",
      "lokal",
      "verkstad",
      "expandera",
      "norrland",
      "glesbygd"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "stödområde A och B (bl.a. Västernorrland)"
  },
  {
    "id": "tv-affarsutvecklingscheckar",
    "namn": "Affärsutvecklingscheckar",
    "namn_en": "Business development checks",
    "namn_ar": "شيكات تطوير الأعمال",
    "myndighet": "Tillväxtverket",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "konsult",
      "utveckling",
      "extern kompetens"
    ],
    "kort_beskrivning": "Stöd för att ta in extern kompetens som konsulter och designers.",
    "kort_beskrivning_en": "Support for hiring external expertise.",
    "kort_beskrivning_ar": "دعم لتوظيف خبرات خارجية.",
    "villkor": [
      "2-49 anställda",
      "Omsättning 3-100 miljoner kr",
      "Vilja att växa"
    ],
    "belopp": "Upp till 250 000 kr, max 50% av kostnaden.",
    "ansokan_url": "https://tillvaxtverket.se/tillvaxtverket/sokfinansiering.1133.html",
    "info_url": "https://tillvaxtverket.se/tillvaxtverket/sokfinansiering.1133.html",
    "relevans_signaler": [
      "konsult",
      "extern hjälp",
      "affärsutveckling",
      "design",
      "marknadsföring",
      "strategi",
      "växa"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "tv-foretagsstod-landsbygd",
    "namn": "Företagsstöd på landsbygd",
    "namn_en": "Rural business support",
    "namn_ar": "دعم الأعمال الريفية",
    "myndighet": "Tillväxtverket / Länsstyrelsen",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "landsbygd",
      "investering",
      "småföretag"
    ],
    "kort_beskrivning": "Stöd till småföretag på landsbygden för investeringar.",
    "kort_beskrivning_en": "Support for rural small businesses.",
    "kort_beskrivning_ar": "دعم للشركات الصغيرة الريفية.",
    "villkor": [
      "Utanför tätorter med >3000 invånare",
      "Max 49 anställda",
      "Ökad sysselsättning eller tillväxt"
    ],
    "belopp": "Upp till 50%, max ca 1,2 miljoner kr.",
    "ansokan_url": "https://jordbruksverket.se/stod/foretagsstod-landsbygd",
    "info_url": "https://jordbruksverket.se/stod/foretagsstod-landsbygd",
    "relevans_signaler": [
      "landsbygd",
      "litet företag",
      "småföretag",
      "by",
      "investera",
      "ort"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "landsbygd nationellt"
  },
  {
    "id": "rvn-generellt-investeringsstod",
    "namn": "Generellt investeringsstöd Västernorrland",
    "namn_en": "General investment support Västernorrland",
    "namn_ar": "دعم الاستثمار فيسترنورلاند",
    "myndighet": "Region Västernorrland",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "investering",
      "maskin",
      "utrustning",
      "västernorrland"
    ],
    "kort_beskrivning": "Regionalt stöd för investeringar i maskiner, utrustning, marknadsföring och produktutveckling i Västernorrland.",
    "kort_beskrivning_en": "Regional support for investments in Västernorrland.",
    "kort_beskrivning_ar": "دعم إقليمي للاستثمارات في فيسترنورلاند.",
    "villkor": [
      "SME i Västernorrlands län",
      "Skapa varaktig sysselsättning",
      "Producera/förädla egna produkter",
      "Minst en heltidsanställd inom ett år",
      "Ej hobbyverksamhet",
      "Löner enligt kollektivavtal"
    ],
    "belopp": "35-50% av investeringen. Max 3 MSEK per företag/3 år.",
    "ansokan_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/generellt-investeringsstod/",
    "info_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/generellt-investeringsstod/",
    "relevans_signaler": [
      "maskin",
      "utrustning",
      "verkstad",
      "lokal",
      "investera",
      "västernorrland",
      "ånge",
      "sundsvall",
      "härnösand",
      "kramfors",
      "sollefteå",
      "örnsköldsvik",
      "marknadsföring",
      "hemsida",
      "produktutveckling",
      "byggföretag"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "Västernorrland"
  },
  {
    "id": "rvn-utvecklingsstod",
    "namn": "Utvecklingsstödet Västernorrland",
    "namn_en": "Development support Västernorrland",
    "namn_ar": "دعم التطوير فيسترنورلاند",
    "myndighet": "Region Västernorrland",
    "malgrupp": [
      "företag"
    ],
    "kategori": "nystart",
    "taggar": [
      "nystart",
      "litet företag",
      "utveckling",
      "västernorrland"
    ],
    "kort_beskrivning": "Mindre stöd (max 30 000 kr) till nya och små företag i Västernorrland.",
    "kort_beskrivning_en": "Smaller support for new/small businesses in Västernorrland.",
    "kort_beskrivning_ar": "دعم أصغر للشركات الجديدة في فيسترنورلاند.",
    "villkor": [
      "SME i Västernorrland",
      "En gång per företag per 3-årsperiod"
    ],
    "belopp": "Upp till 50%, max 30 000 kr.",
    "ansokan_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/",
    "info_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/",
    "relevans_signaler": [
      "nystartat",
      "litet företag",
      "komma igång",
      "västernorrland",
      "ånge",
      "sundsvall",
      "första steget"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "Västernorrland"
  },
  {
    "id": "rvn-innovationsstod",
    "namn": "Innovationsstöd Västernorrland",
    "namn_en": "Innovation support Västernorrland",
    "namn_ar": "دعم الابتكار فيسترنورلاند",
    "myndighet": "Region Västernorrland",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "innovation",
      "ny idé",
      "västernorrland"
    ],
    "kort_beskrivning": "Stöd till innovativa företag inom Västernorrlands nyckelbranscher.",
    "kort_beskrivning_en": "Support for innovative businesses in Västernorrland's key industries.",
    "kort_beskrivning_ar": "دعم للشركات المبتكرة في فيسترنورلاند.",
    "villkor": [
      "Nyckelbranscher: tillverkning, förnybar energi, govtech, bioekonomi, foodtech m.fl.",
      "Innovativ tjänst eller produkt",
      "Företag i Västernorrland"
    ],
    "belopp": "Varierar.",
    "ansokan_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/",
    "info_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/",
    "relevans_signaler": [
      "innovation",
      "ny produkt",
      "patent",
      "ny teknik",
      "västernorrland",
      "ånge",
      "bioekonomi",
      "energi",
      "tillverkning"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "Västernorrland"
  },
  {
    "id": "rvn-kommersiell-service",
    "namn": "Stöd till kommersiell service",
    "namn_en": "Commercial service support",
    "namn_ar": "دعم الخدمات التجارية",
    "myndighet": "Region Västernorrland",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "dagligvarubutik",
      "drivmedel",
      "service",
      "glesbygd"
    ],
    "kort_beskrivning": "Stöd till dagligvarubutiker och drivmedelsanläggningar på glesbygd.",
    "kort_beskrivning_en": "Support for grocery stores and fuel stations in rural areas.",
    "kort_beskrivning_ar": "دعم لمحلات البقالة ومحطات الوقود في المناطق الريفية.",
    "villkor": [
      "Dagligvarubutik eller drivmedelsanläggning",
      "Gles- eller landsbygd",
      "Bidrar till god servicenivå"
    ],
    "belopp": "Varierar.",
    "ansokan_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/",
    "info_url": "https://www.rvn.se/sv/utveckla-vasternorrland/stod-och-finansiering/foretagsstod/",
    "relevans_signaler": [
      "butik",
      "matbutik",
      "bensinstation",
      "drivmedel",
      "landsbygd",
      "glesbygd",
      "bybutik"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "Västernorrland"
  },
  {
    "id": "almi-mikrolan",
    "namn": "Almis mikrolån",
    "namn_en": "Almi microloan",
    "namn_ar": "قرض ألمي الصغير",
    "myndighet": "Almi",
    "malgrupp": [
      "företag"
    ],
    "kategori": "finansiering",
    "taggar": [
      "lån",
      "startkapital",
      "finansiering",
      "nystart"
    ],
    "kort_beskrivning": "Lån upp till 250 000 kr för små och nya företag.",
    "kort_beskrivning_en": "Loan up to SEK 250,000 for small/new businesses.",
    "kort_beskrivning_ar": "قرض يصل إلى 250,000 كرونة للشركات الصغيرة.",
    "villkor": [
      "Svårt att få fullständig bankfinansiering",
      "Livskraftig affärsidé",
      "Max 50% av kapitalbehovet"
    ],
    "belopp": "Upp till 250 000 kr.",
    "ansokan_url": "https://www.almi.se/tjanster/lan/mikrolan/",
    "info_url": "https://www.almi.se/tjanster/lan/mikrolan/",
    "relevans_signaler": [
      "startkapital",
      "lån",
      "finansiering",
      "starta företag",
      "nystartad",
      "kapital",
      "pengar",
      "nekas banklån"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "vinnova-innovativa-startups",
    "namn": "Innovativa Startups (Vinnova)",
    "namn_en": "Innovative Startups (Vinnova)",
    "namn_ar": "الشركات الناشئة المبتكرة",
    "myndighet": "Vinnova",
    "malgrupp": [
      "företag"
    ],
    "kategori": "investering",
    "taggar": [
      "innovation",
      "startup",
      "bidrag",
      "forskning"
    ],
    "kort_beskrivning": "Bidrag till nystartade företag med innovativa idéer och internationell potential.",
    "kort_beskrivning_en": "Grants for startups with innovative ideas and international potential.",
    "kort_beskrivning_ar": "منح للشركات الناشئة ذات الأفكار المبتكرة.",
    "villkor": [
      "Svenskt aktiebolag",
      "Ej börsnoterat/vinstutdelande",
      "Max 10 år",
      "Innovativ affärsidé med internationell potential"
    ],
    "belopp": "Steg 1: upp till 500 000 kr. Steg 2: upp till 900 000 kr.",
    "ansokan_url": "https://www.vinnova.se/e/innovativa-startups/",
    "info_url": "https://www.vinnova.se/e/innovativa-startups/",
    "relevans_signaler": [
      "startup",
      "innovation",
      "ny teknik",
      "forskning",
      "utveckling",
      "patent",
      "internationellt",
      "skalbar"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "energi-effektivisering",
    "namn": "Stöd för energieffektivisering",
    "namn_en": "Energy efficiency support",
    "namn_ar": "دعم كفاءة الطاقة",
    "myndighet": "Energimyndigheten",
    "malgrupp": [
      "företag"
    ],
    "kategori": "energi",
    "taggar": [
      "energi",
      "effektivisering",
      "hållbarhet",
      "klimat",
      "solceller"
    ],
    "kort_beskrivning": "Stöd till företag för minskad energianvändning.",
    "kort_beskrivning_en": "Support for businesses to reduce energy use.",
    "kort_beskrivning_ar": "دعم للشركات لتقليل استخدام الطاقة.",
    "villkor": [
      "Energikartläggning genomförs",
      "Leder till minskad energianvändning",
      "Ansökan före investering"
    ],
    "belopp": "Energikartläggningscheckar: upp till 50 000 kr.",
    "ansokan_url": "https://www.energimyndigheten.se/",
    "info_url": "https://www.energimyndigheten.se/",
    "relevans_signaler": [
      "energi",
      "el",
      "värme",
      "solceller",
      "isolering",
      "effektivisera",
      "klimat",
      "hållbar",
      "elräkning"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "csn-studiemedel",
    "namn": "Studiemedel",
    "namn_en": "Student finance",
    "namn_ar": "تمويل الطلاب",
    "myndighet": "CSN",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "utbildning",
    "taggar": [
      "studier",
      "utbildning",
      "komvux",
      "högskola"
    ],
    "kort_beskrivning": "Bidrag och lån för studier på gymnasial eller eftergymnasial nivå.",
    "kort_beskrivning_en": "Grant and loan for studies.",
    "kort_beskrivning_ar": "منحة وقرض للدراسة.",
    "villkor": [
      "Studier på minst halvtid",
      "Under 60 år (bidragsdelen)",
      "Tillräckliga studieresultat"
    ],
    "belopp": "Bidrag: ca 4 268 kr/mån. Lån: ca 9 616 kr/mån.",
    "ansokan_url": "https://www.csn.se/bidrag-och-lan/studiestod/studiemedel.html",
    "info_url": "https://www.csn.se/bidrag-och-lan/studiestod/studiemedel.html",
    "relevans_signaler": [
      "studera",
      "utbildning",
      "skola",
      "komvux",
      "universitet",
      "yrkesutbildning",
      "omskolning",
      "byta yrke"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "soc-ekonomiskt-bistand",
    "namn": "Ekonomiskt bistånd (försörjningsstöd)",
    "namn_en": "Social assistance",
    "namn_ar": "المساعدة الاجتماعية",
    "myndighet": "Kommunen (socialtjänsten)",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "grundtrygghet",
    "taggar": [
      "socialbidrag",
      "försörjningsstöd",
      "nödhjälp"
    ],
    "kort_beskrivning": "Sista skyddsnätet för den som inte kan försörja sig.",
    "kort_beskrivning_en": "Last safety net for those who cannot support themselves.",
    "kort_beskrivning_ar": "شبكة الأمان الأخيرة لمن لا يستطيعون إعالة أنفسهم.",
    "villkor": [
      "Alla andra möjligheter uttömda",
      "Stå till arbetsmarknadens förfogande",
      "Tillgångar beaktas",
      "Ansökan hos din kommun"
    ],
    "belopp": "Riksnorm: ensamstående ca 4 180 kr/mån + skäliga boendekostnader.",
    "ansokan_url": "",
    "info_url": "https://www.socialstyrelsen.se/kunskapsstod-och-regler/omraden/ekonomiskt-bistand/ekonomiskt-bistand-for-privatpersoner/",
    "relevans_signaler": [
      "inga pengar",
      "kan inte betala",
      "desperat",
      "hemlös",
      "försörjning",
      "socialbidrag",
      "socialtjänsten",
      "inga inkomster",
      "svält"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "kommunalt"
  },
  {
    "id": "akassa",
    "namn": "A-kassa",
    "namn_en": "Unemployment insurance",
    "namn_ar": "تأمين البطالة",
    "myndighet": "A-kassan / Arbetsförmedlingen",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "grundtrygghet",
    "taggar": [
      "arbetslös",
      "a-kassa",
      "uppsagd"
    ],
    "kort_beskrivning": "Ersättning vid arbetslöshet.",
    "kort_beskrivning_en": "Compensation when unemployed.",
    "kort_beskrivning_ar": "تعويض عند البطالة.",
    "villkor": [
      "Inskriven hos Arbetsförmedlingen",
      "Arbetsför och tillgänglig",
      "Arbetat minst 6 av senaste 12 månaderna",
      "Söker aktivt arbete"
    ],
    "belopp": "Grundersättning: ca 510 kr/dag. Med medlemskap: upp till 80% av lön, max ca 1 200 kr/dag.",
    "ansokan_url": "https://www.arbetsformedlingen.se/for-arbetssokande/ersattning/a-kassa",
    "info_url": "https://www.arbetsformedlingen.se/for-arbetssokande/ersattning/a-kassa",
    "relevans_signaler": [
      "arbetslös",
      "uppsagd",
      "förlorat jobbet",
      "a-kassa",
      "varsel",
      "ingen inkomst"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "rot-avdrag",
    "namn": "ROT-avdrag",
    "namn_en": "ROT deduction (renovation tax credit)",
    "namn_ar": "خصم الترميم الضريبي",
    "myndighet": "Skatteverket",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "bostad",
    "taggar": [
      "renovering",
      "byggarbete",
      "skatteavdrag"
    ],
    "kort_beskrivning": "Skattereduktion på 30% av arbetskostnaden vid renovering.",
    "kort_beskrivning_en": "30% tax reduction on labour costs for renovation.",
    "kort_beskrivning_ar": "تخفيض ضريبي 30% على تكاليف العمالة للتجديد.",
    "villkor": [
      "Du äger bostaden",
      "Arbetet utförs av F-skattsedelsinnehavare",
      "Max 50 000 kr/person/år"
    ],
    "belopp": "30% av arbetskostnaden, max 50 000 kr/person/år.",
    "ansokan_url": "https://www.skatteverket.se/privat/fastigheterochbostad/rotochrutarbete",
    "info_url": "https://www.skatteverket.se/privat/fastigheterochbostad/rotochrutarbete",
    "relevans_signaler": [
      "renovera",
      "bygga om",
      "snickare",
      "målare",
      "badrum",
      "kök",
      "tak",
      "ombyggnad"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  },
  {
    "id": "rut-avdrag",
    "namn": "RUT-avdrag",
    "namn_en": "RUT deduction (household services)",
    "namn_ar": "خصم خدمات المنزل",
    "myndighet": "Skatteverket",
    "malgrupp": [
      "privatperson"
    ],
    "kategori": "bostad",
    "taggar": [
      "städning",
      "hushållstjänster",
      "skatteavdrag"
    ],
    "kort_beskrivning": "Skattereduktion på 50% av arbetskostnaden för hushållstjänster.",
    "kort_beskrivning_en": "50% tax reduction for household services.",
    "kort_beskrivning_ar": "تخفيض ضريبي 50% لخدمات المنزل.",
    "villkor": [
      "Arbete i eller nära din bostad",
      "F-skattsedelsinnehavare",
      "Max 75 000 kr/person/år"
    ],
    "belopp": "50% av arbetskostnaden, max 75 000 kr/person/år.",
    "ansokan_url": "https://www.skatteverket.se/privat/fastigheterochbostad/rotochrutarbete",
    "info_url": "https://www.skatteverket.se/privat/fastigheterochbostad/rotochrutarbete",
    "relevans_signaler": [
      "städning",
      "trädgård",
      "hemhjälp",
      "barnpassning",
      "flytt",
      "tvätt"
    ],
    "senast_verifierad": "2026-02-15",
    "region": "nationellt"
  }
]
# ── Slut inbakad databas ─────────────────────────────────────────


def ladda_stod() -> list[dict]:
    """Laddar alla stöd från JSON-databasen (med inbakad fallback)."""
    if STOD_FILE.exists():
        with open(STOD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return EMBEDDED_STOD


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
