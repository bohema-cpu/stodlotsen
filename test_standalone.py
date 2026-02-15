#!/usr/bin/env python3
"""
Stödlotsen – snabbtest utan MCP-klient
=======================================
Kör: python test_standalone.py

Testar alla 4 verktyg direkt via funktionsanrop.
"""

import sys
import os

# Lägg till rätt sökväg
sys.path.insert(0, os.path.dirname(__file__))

from server import sok_stod, stod_detaljer, lista_stod, stod_statistik

GREEN = "\033[92m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[96m"

def header(text):
    print(f"\n{BOLD}{CYAN}{'─'*60}")
    print(f"  {text}")
    print(f"{'─'*60}{RESET}\n")

def test(name, result, check_fn=None):
    ok = bool(result) and (check_fn(result) if check_fn else True)
    status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    print(f"  {status} {name}")
    if not ok:
        print(f"    {RED}Oväntat resultat:{RESET}")
        print(f"    {result[:200]}...")
    return ok

# ── 1. sok_stod ──────────────────────────────────────────────────

header("1. sok_stod – fritextsökning")

tests_passed = 0
tests_total = 0

# Svenska sökningar
tests_total += 1
r = sok_stod("ensamstående mamma hyra")
tests_passed += test(
    "SV: 'ensamstående mamma hyra' → bostadsbidrag?",
    r, lambda x: "ostadsbidrag" in x
)

tests_total += 1
r = sok_stod("funktionsnedsättning kan inte arbeta")
tests_passed += test(
    "SV: 'funktionsnedsättning kan inte arbeta' → sjuk/aktivitetsersättning?",
    r, lambda x: "rsättning" in x
)

tests_total += 1
r = sok_stod("starta företag arbetslös Ånge")
tests_passed += test(
    "SV: 'starta företag arbetslös Ånge' → starta-eget?",
    r, lambda x: "tarta" in x.lower()
)

tests_total += 1
r = sok_stod("bygga om badrum")
tests_passed += test(
    "SV: 'bygga om badrum' → ROT-avdrag?",
    r, lambda x: "ROT" in x or "rot" in x.lower()
)

# Engelska – notera: sök träffar på svenska signaler, AI-lagret gör NLU
tests_total += 1
r = sok_stod("single parent rent help", sprak="en")
tests_passed += test(
    "EN: 'single parent rent help' → returnerar resultat?",
    r, lambda x: len(x) > 50
)

# Arabiska
tests_total += 1
r = sok_stod("مساعدة", sprak="ar")
tests_passed += test(
    "AR: 'مساعدة' → returnerar resultat?",
    r, lambda x: len(x) > 50
)

# Filtrering
tests_total += 1
r = sok_stod("investering", malgrupp="Företag")
tests_passed += test(
    "SV: 'investering' + målgrupp Företag → investering?",
    r, lambda x: "nvestering" in x
)

# Regionalt
tests_total += 1
r = sok_stod("bidrag maskin verkstad", region="Västernorrland")
tests_passed += test(
    "SV: 'bidrag maskin verkstad' + region VN → regionalt stöd?",
    r, lambda x: "ästernorrland" in x or "nvestering" in x
)

# ── 2. stod_detaljer ────────────────────────────────────────────

header("2. stod_detaljer – hämta fullständig info")

tests_total += 1
r = stod_detaljer("fk-bostadsbidrag")
tests_passed += test(
    "Detaljer: fk-bostadsbidrag → FK + belopp?",
    r, lambda x: "örsäkringskassan" in x and "kr" in x.lower()
)

tests_total += 1
r = stod_detaljer("fk-bostadsbidrag", sprak="en")
tests_passed += test(
    "Detaljer EN: fk-bostadsbidrag → English name?",
    r, lambda x: "ousing" in x.lower() or "allowance" in x.lower()
)

tests_total += 1
r = stod_detaljer("finns-inte-123")
tests_passed += test(
    "Detaljer: okänt ID → felmeddelande?",
    r, lambda x: "ittar" in x.lower() or "inte" in x.lower()
)

# ── 3. lista_stod ───────────────────────────────────────────────

header("3. lista_stod – lista alla")

tests_total += 1
r = lista_stod()
tests_passed += test(
    "Lista alla → 29 stöd?",
    r, lambda x: "29" in x
)

tests_total += 1
r = lista_stod(malgrupp="privatperson")
tests_passed += test(
    "Lista målgrupp privatperson → barnbidrag?",
    r, lambda x: "arnbidrag" in x
)

tests_total += 1
r = lista_stod(sprak="en")
tests_passed += test(
    "Lista EN → engelska namn?",
    r, lambda x: "hild" in x or "ousing" in x or "allowance" in x.lower()
)

# ── 4. stod_statistik ───────────────────────────────────────────

header("4. stod_statistik – databasöversikt")

tests_total += 1
r = stod_statistik()
tests_passed += test(
    "Statistik → antal, kategorier, verifiering?",
    r, lambda x: "29" in x and "ategori" in x.lower()
)

# ── Sammanfattning ───────────────────────────────────────────────

header("RESULTAT")

pct = int(100 * tests_passed / tests_total)
color = GREEN if pct == 100 else RED
print(f"  {color}{tests_passed}/{tests_total} tester lyckades ({pct}%){RESET}\n")

if tests_passed == tests_total:
    print(f"  {GREEN}🎉 Alla tester klarade! Redo att koppla till en MCP-klient.{RESET}\n")
else:
    print(f"  {RED}⚠  Vissa tester misslyckades. Kolla ovan.{RESET}\n")

sys.exit(0 if tests_passed == tests_total else 1)
