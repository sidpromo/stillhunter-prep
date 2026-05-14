"""Script to generate species data from image filenames and compare against existing species.json.

Usage:
    uv run python generate_species.py          # Compare only, report differences
    uv run python generate_species.py --write  # Overwrite species.json (use with caution)
"""
import json
import os
import re
import sys

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
OUTPUT = os.path.join(os.path.dirname(__file__), "data", "species.json")

# Species that are nagyvad (big game)
NAGYVAD_SPECIES = {"Gímszarvas", "Dámvad", "Őz", "Muflon", "Vaddisznó", "Szikaszarvas", "Zerge"}

# Keywords indicating tarvad (non-trophy big game)
TARVAD_KEYWORDS = ["tehén", "borjú", "borjával", "borjakkal", "koca", "malac", "süldő",
                   "gida", "suta", "juh", "jerke", "bárány", "ünő", "család", "csapat",
                   "vezértehén"]

BIRD_SPECIES = {
    "Nagy lilik", "Vetési lúd", "Nyári lúd", "Nílusi lúd", "Kanadai lúd",
    "Tőkés réce", "Fogoly", "Fácán", "Szárcsa", "Örvös galamb", "Balkáni gerle",
    "Dolmányos varjú", "Erdei szalonka", "Szarka", "Szajkó",
    "Kis lilik", "Vörösnyakú lúd", "Csörgő réce", "Fütyülő réce",
    "Kendermagos réce", "Böjti réce", "Kanalas réce", "Barátréce",
    "Kerceréce", "Nyílfarkú réce", "Cigányréce", "Üstökös réce",
    "Kontyos réce", "Kis bukó", "Kárókatona", "Kis kárókatona",
    "Fürj", "Szürke gém", "Császármadár", "Héja", "Barna kánya",
    "Vörös kánya", "Hamvas rétihéja", "Kékes rétihéja", "Barna rétihéja",
    "Rétisas", "Szirti sas", "Parlagi sas", "Gatyás ölyv", "Egerészölyv",
    "Vörös vércse", "Kék vércse", "Karvaly", "Kerecsensólyom",
    "Vándorsólyom", "Sárszalonka", "Nagy sárszalonka", "Uhu",
    "Erdei fülesbagoly", "Vadgerle", "Kék galamb", "Daru", "Túzok",
    "Vetési varjú", "Holló", "Seregély",
}

APROVAD_SPECIES = {
    "Nagy lilik", "Vetési lúd", "Nyári lúd", "Nílusi lúd", "Kanadai lúd",
    "Tőkés réce", "Fogoly", "Fácán", "Szárcsa", "Örvös galamb", "Balkáni gerle",
    "Erdei szalonka", "Mezei nyúl", "Üregi nyúl", "Dolmányos varjú", "Szarka",
    "Szajkó", "Pézsmapocok", "Róka", "Aranysakál", "Nyestkutya", "Mosómedve",
    "Borz", "Nyest", "Házi görény",
}


def species_from_range(img_id: int) -> str | None:
    """Infer species from image number range when filename is ambiguous."""
    if 110 <= img_id <= 142:
        return "Gímszarvas"
    if 143 <= img_id <= 157:
        return "Dámvad"
    if 158 <= img_id <= 175:
        return "Őz"
    if 176 <= img_id <= 189:
        return "Muflon"
    if 190 <= img_id <= 200:
        return "Vaddisznó"
    return None


def extract_species(filename: str) -> str:
    """Extract species name from filename."""
    id_match = re.match(r"^(\d+)\.", filename)
    img_id = int(id_match.group(1)) if id_match else 0

    name = re.sub(r"^\d+\.\s*", "", filename)
    name = re.sub(r"\.jpg$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*-\s*(Fokozottan védett|Védett|jogszabály változás alapján védett faj|Európai közösségben természetvédelmi szempontból jelentős faj).*$", "", name)

    species_map = {
        "gímszarvas": "Gímszarvas",
        "gím": "Gímszarvas",
        "dám": "Dámvad",
        "őz": "Őz",
        "muflon": "Muflon",
        "vaddisznó": "Vaddisznó",
        "vadkan": "Vaddisznó",
        "vadmalac": "Vaddisznó",
    }

    lower = name.lower()

    for key, species in species_map.items():
        if key in lower:
            return species

    if "tőkésréce" in lower or "tőkés réce" in lower:
        return "Tőkés réce"
    if "fogolycsibe" in lower or "fogoly" in lower:
        return "Fogoly"
    if "fácán" in lower:
        return "Fácán"
    if "csörgőréce" in lower or "csörgő réce" in lower:
        return "Csörgő réce"
    if "barátrécék" in lower or "barátréce" in lower:
        return "Barátréce"
    if "kerceréce" in lower:
        return "Kerceréce"
    if "cigányréce" in lower:
        return "Cigányréce"
    if "üstökös réce" in lower:
        return "Üstökös réce"
    if "kontyos réce" in lower:
        return "Kontyos réce"
    if "kis kárókatona" in lower:
        return "Kis kárókatona"
    if "kárókatona" in lower:
        return "Kárókatona"
    if "rétihéja" in lower:
        if "hamvas" in lower:
            return "Hamvas rétihéja"
        if "kékes" in lower:
            return "Kékes rétihéja"
        if "barna" in lower:
            return "Barna rétihéja"
    if "rétisas" in lower:
        return "Rétisas"
    if "kék vércse" in lower:
        return "Kék vércse"
    if "vörös vércse" in lower:
        return "Vörös vércse"
    if "túzok" in lower:
        return "Túzok"
    if "sárszalonka" in lower and "nagy" in lower:
        return "Nagy sárszalonka"
    if "sárszalonka" in lower:
        return "Sárszalonka"
    if "szarvalt juh" in lower or "kosbárány" in lower or "muflonbárány" in lower or "muflonjuh" in lower:
        return "Muflon"
    if "hermelin" in lower:
        return "Hermelin"
    if "seregély" in lower:
        return "Seregély"

    range_species = species_from_range(img_id)
    if range_species:
        return range_species

    simple = name.split(",")[0].strip()
    simple = re.sub(r"\s+(gácsér|tojó|hím|pár|kakas|tyúk)$", "", simple)
    return simple


def extract_protection(filename: str) -> str | None:
    """Extract protection status from filename."""
    if "Fokozottan védett" in filename:
        return "fokozottan védett"
    if "- Védett" in filename:
        return "védett"
    if "Európai közösségben" in filename:
        return "EU jelentős"
    if "jogszabály változás alapján védett" in filename:
        return "védett"
    return None


def generate_from_filenames() -> list[dict]:
    """Generate species entries from image filenames (baseline only)."""
    entries = []
    for fname in sorted(os.listdir(IMAGES_DIR)):
        if not fname.lower().endswith(".jpg"):
            continue
        match = re.match(r"^(\d+)\.", fname)
        if not match:
            continue

        img_id = int(match.group(1))
        species = extract_species(fname)
        protection = extract_protection(fname)
        group = "madár" if species in BIRD_SPECIES else "emlős"

        entries.append({
            "id": img_id,
            "filename": fname,
            "species": species,
            "protection": protection,
            "group": group,
        })

    entries.sort(key=lambda x: x["id"])
    return entries


def compare(generated: list[dict], existing: list[dict]):
    """Compare generated baseline against existing species.json."""
    existing_by_id = {e["id"]: e for e in existing}
    generated_by_id = {e["id"]: e for e in generated}

    diffs = []

    # Check for missing/extra entries
    gen_ids = set(generated_by_id.keys())
    ext_ids = set(existing_by_id.keys())

    for mid in sorted(gen_ids - ext_ids):
        diffs.append(f"  NEW in images (not in species.json): #{mid} {generated_by_id[mid]['filename']}")
    for mid in sorted(ext_ids - gen_ids):
        diffs.append(f"  REMOVED from images (still in species.json): #{mid} {existing_by_id[mid]['filename']}")

    # Compare shared entries (only fields the generator can determine)
    for img_id in sorted(gen_ids & ext_ids):
        g = generated_by_id[img_id]
        e = existing_by_id[img_id]

        if g["species"] != e["species"]:
            diffs.append(f"  #{img_id} species: generated={g['species']!r}, existing={e['species']!r}")
        if g["protection"] != e.get("protection"):
            diffs.append(f"  #{img_id} protection: generated={g['protection']!r}, existing={e.get('protection')!r}")
        if g["group"] != e.get("group"):
            diffs.append(f"  #{img_id} group: generated={g['group']!r}, existing={e.get('group')!r}")
        if g["filename"] != e["filename"]:
            diffs.append(f"  #{img_id} filename: generated={g['filename']!r}, existing={e['filename']!r}")

    return diffs


if __name__ == "__main__":
    write_mode = "--write" in sys.argv

    generated = generate_from_filenames()
    print(f"Generated {len(generated)} entries from image filenames.")

    if os.path.exists(OUTPUT):
        with open(OUTPUT, encoding="utf-8") as f:
            existing = json.load(f)
        print(f"Existing species.json has {len(existing)} entries.")

        diffs = compare(generated, existing)
        if diffs:
            print(f"\n{len(diffs)} difference(s) found:")
            for d in diffs:
                print(d)
        else:
            print("\n✅ No differences — species.json is consistent with image filenames.")

        if write_mode:
            print("\n⚠️  --write mode: this would overwrite manual edits (trophy_data, subcategory, etc.)")
            print("    Not recommended. Edit species.json manually instead.")
    else:
        if write_mode:
            os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
            with open(OUTPUT, "w", encoding="utf-8") as f:
                json.dump(generated, f, ensure_ascii=False, indent=2)
            print(f"Written to {OUTPUT}")
        else:
            print(f"No existing {OUTPUT} found. Run with --write to create initial version.")
