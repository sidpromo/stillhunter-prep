# 🦌 StillHunter Prep

Vadászvizsga fajfelismerés gyakorló alkalmazás. A magyar vadászvizsgán szereplő 200 darabos képsorozatból gyakorolhatsz fajfelismerést, vizsgaszimulációt és trófea-minősítést.

## Funkciók

- **Gyakorlás** — Véletlenszerű képek, szabad szöveges vagy feleletválasztós válaszadás
- **Vizsgaszimuláció** — 15 kép a hivatalos összetétel szerint (5 trófeás + 3 tarvad + 4 apróvad + 2 védett + 1 fokozottan védett), hivatalos értékelési szabályokkal
- **Trófea gyakorlás** — Faj + korcsoport + elejthetőség meghatározása trófeás nagyvadnál
- **Tanulás** — Böngészd az összes fajt kategória és csoport szerint
- **Statisztika** — Pontosság, fajok szerinti eredmények, vizsgaeredmények

## Telepítés és futtatás

```bash
# uv-vel (ajánlott)
uv sync
uv run streamlit run app.py

# vagy pip-pel
pip install -r requirements.txt
streamlit run app.py
```

## Tesztek futtatása

```bash
uv run pytest tests/ -v
```

## Deployment (Streamlit Community Cloud)

1. Push a repót GitHub-ra
2. Jelentkezz be: https://share.streamlit.io
3. Deploy: repo = `sidpromo/stillhunter-prep`, branch = `main`, file = `app.py`

## Projekt struktúra

```
├── app.py              # Streamlit alkalmazás
├── data/species.json   # Fajadatok (198 kép metaadatai)
├── images/             # 198 vadfotó
├── utils/helpers.py    # Segédfüggvények
├── tests/              # Unit tesztek
├── generate_species.py # species.json generáló script
└── SPEC.md             # Részletes specifikáció
```

## Vizsgaszabályok

A vizsga 15 képből áll:
- 8 nagyvad (5 trófeás + 3 tarvad)
- 4 apróvad
- 2 védett + 1 fokozottan védett

**Megfelelt**, ha:
- Minden nagyvad és apróvad helyesen felismert
- Legalább 2/3 védett faj helyes (fokozottan védett nem téveszthető)
- 4/5 trófea-minősítés helyes (korcsoport + elejthetőség)

**Azonnali bukás:** védett faj vadászhatóval való összetévesztése.
