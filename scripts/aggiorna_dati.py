#!/usr/bin/env python3
"""Scarica e valida i CSV pubblicati di Google Sheets per il sito. Sola lettura."""
import csv
import io
import pathlib
import urllib.request

BASE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSF3TfbWSa8NIZm49Jn2BjVdeQWSOfg31DemfKxVvq_Bhkzklb8KJa5jO2BJeVtmmIw0e7xfyuQvq9c/pub"
SHEETS = {"u15": ("1620985745", 90), "u19": ("1180556936", 110)}
COLUMNS = ["id", "phase", "round", "roundDate", "home", "away", "date", "time", "homeScore", "awayScore", "venue"]
ROOT = pathlib.Path(__file__).resolve().parents[1]

def validate(label, data, expected):
    rows = list(csv.DictReader(io.StringIO(data)))
    if len(rows) != expected:
        raise ValueError(f"{label}: attese {expected} gare, presenti {len(rows)}")
    if not rows or list(rows[0]) != COLUMNS:
        raise ValueError(f"{label}: colonne non conformi")
    ids = [r["id"].zfill(6) for r in rows]
    if len(set(ids)) != expected or any(not x.isdigit() or len(x) != 6 for x in ids):
        raise ValueError(f"{label}: identificativi gara duplicati o invalidi")
    if any(not r['home'] or not r['away'] for r in rows):
        raise ValueError(f"{label}: squadre mancanti")
    if any(bool(r['homeScore'].strip()) != bool(r['awayScore'].strip()) for r in rows):
        raise ValueError(f"{label}: punteggi incompleti")
    return rows

def main():
    # All-or-nothing: no partial updates on download/validation failure.
    downloaded = {}
    for label, (gid, expected) in SHEETS.items():
        url = BASE + '?gid=' + gid + '&single=true&output=csv'
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 StellaBasketMobile/1.0"})
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read().decode('utf-8-sig')
        validate(label, raw, expected)
        downloaded[label] = raw
        print(f"{label.upper()}: {expected} gare validate")
    folder = ROOT / "dati"
    folder.mkdir(parents=True, exist_ok=True)
    for label, raw in downloaded.items():
        (folder / f"{label}.csv").write_text(raw, encoding="utf-8")
    print("Dati sincronizzati da Google Sheets, nessuna scrittura su Google")

if __name__ == "__main__":
    main()
