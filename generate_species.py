"""Script to generate data/species.json from image filenames."""
import json
import os
import re

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
OUTPUT = os.path.join(os.path.dirname(__file__), "data", "species.json")

# Species that are nagyvad trófeás (trophy-bearing big game)
TROPHY_SPECIES = {"Gímszarvas", "Dámszarvas", "Őz", "Muflon", "Vaddisznó"}

# Keywords indicating tarvad (non-trophy big game)
TARVAD_KEYWORDS = ["tehén", "borjú", "borjával", "borjakkal", "koca", "malac", "süldő",
                   "gida", "suta", "juh", "jerke", "bárány", "ünő", "család", "csapat",
                   "vezértehén"]

# Species → group mapping
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

# Apróvad species (huntable small game)
APROVAD_SPECIES = {
    "Nagy lilik", "Vetési lúd", "Nyári lúd", "Nílusi lúd", "Kanadai lúd",
    "Tőkés réce", "Fogoly", "Fácán", "Szárcsa", "Örvös galamb", "Balkáni gerle",
    "Erdei szalonka", "Mezei nyúl", "Üregi nyúl",
}

# Huntable predators/other (egyéb vadászható)
EGYEB_VADASZHATÓ = {
    "Dolmányos varjú", "Szarka", "Szajkó", "Pézsmapocok",
    "Róka", "Aranysakál", "Nyestkutya", "Mosómedve", "Borz", "Nyest", "Házi görény",
}

# Nagyvad species
NAGYVAD_SPECIES = {
    "Gímszarvas", "Dámszarvas", "Őz", "Muflon", "Vaddisznó", "Szikaszarvas", "Zerge",
}


def species_from_range(img_id: int) -> str | None:
    """Infer species from image number range when filename is ambiguous."""
    if 110 <= img_id <= 142:
        return "Gímszarvas"
    if 143 <= img_id <= 157:
        return "Dámszarvas"
    if 158 <= img_id <= 175:
        return "Őz"
    if 176 <= img_id <= 189:
        return "Muflon"
    if 190 <= img_id <= 200:
        return "Vaddisznó"
    return None


def extract_species(filename: str) -> str:
    """Extract species name from filename."""
    # Get image ID for range-based fallback
    id_match = re.match(r"^(\d+)\.", filename)
    img_id = int(id_match.group(1)) if id_match else 0

    # Remove number prefix
    name = re.sub(r"^\d+\.\s*", "", filename)
    # Remove extension
    name = re.sub(r"\.jpg$", "", name, flags=re.IGNORECASE)
    # Remove protection suffix
    name = re.sub(r"\s*-\s*(Fokozottan védett|Védett|jogszabály változás alapján védett faj|Európai közösségben természetvédelmi szempontból jelentős faj).*$", "", name)

    # Map to canonical species name
    species_map = {
        "gímszarvas": "Gímszarvas",
        "gím": "Gímszarvas",
        "dám": "Dámszarvas",
        "őz": "Őz",
        "muflon": "Muflon",
        "vaddisznó": "Vaddisznó",
        "vadkan": "Vaddisznó",
        "vadmalac": "Vaddisznó",
    }

    lower = name.lower()

    # Check for nagyvad species keywords in the description
    for key, species in species_map.items():
        if key in lower:
            return species

    # Handle specific compound names
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

    # Range-based inference for ambiguous nagyvad filenames
    # (e.g., "Fiatal, villás bak, kímélendő" → Őz based on range 158-175)
    range_species = species_from_range(img_id)
    if range_species:
        # Verify with contextual keywords
        nagyvad_context = {
            "Gímszarvas": ["bika", "tehén", "borj"],
            "Dámszarvas": ["bika", "tehén", "borj", "ünő"],
            "Őz": ["bak", "suta", "gida"],
            "Muflon": ["kos", "juh", "jerke", "bárány"],
            "Vaddisznó": ["kan", "koca", "süldő", "malac"],
        }
        # If any contextual keyword matches, or if no better match, use range
        return range_species

    # For simple names: take the first part before comma
    simple = name.split(",")[0].strip()
    # Remove gender/age qualifiers
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


def extract_trophy_data(filename: str, species: str) -> dict | None:
    """Extract trophy assessment data from filename."""
    lower = filename.lower()

    if "lőhető" not in lower and "kímélendő" not in lower:
        return None

    harvestable = "lőhető" in lower

    # Age group
    age_group = None
    if "golyóérett" in lower:
        age_group = "öreg"
    elif "öreg" in lower or "visszarakott" in lower:
        age_group = "öreg"
    elif "középkor végén" in lower or "középkor elején" in lower or "középkorú" in lower or "középkor" in lower:
        age_group = "középkorú"
    elif "fiatal" in lower or "2. agancsú" in lower or "csapos" in lower or "gombnyársas" in lower:
        age_group = "fiatal"
    elif "érett agancsú" in lower or "érett" in lower:
        age_group = "öreg"
    elif "selejt" in lower:
        age_group = "középkorú"

    # Animal type
    animal_type = None
    if species == "Gímszarvas":
        if "bika" in lower:
            animal_type = "bika"
        elif "tehén" in lower:
            animal_type = "tehén"
        elif "borj" in lower:
            animal_type = "borjú"
    elif species == "Dámszarvas":
        if "bika" in lower:
            animal_type = "bika"
        elif "tehén" in lower:
            animal_type = "tehén"
    elif species == "Őz":
        if "bak" in lower:
            animal_type = "bak"
        elif "suta" in lower:
            animal_type = "suta"
        elif "gida" in lower:
            animal_type = "gida"
    elif species == "Muflon":
        if "kos" in lower:
            animal_type = "kos"
        elif "juh" in lower or "jerke" in lower:
            animal_type = "juh"
        elif "bárány" in lower:
            animal_type = "bárány"
    elif species == "Vaddisznó":
        if "kan" in lower:
            animal_type = "kan"
        elif "koca" in lower:
            animal_type = "koca"
        elif "süldő" in lower:
            animal_type = "süldő"
        elif "malac" in lower:
            animal_type = "malac"

    # Remove number prefix and extension for description
    desc = re.sub(r"^\d+\.\s*", "", filename)
    desc = re.sub(r"\.jpg$", "", desc, flags=re.IGNORECASE)

    return {
        "age_group": age_group,
        "harvestable": harvestable,
        "animal_type": animal_type,
        "description": desc,
    }


def is_tarvad(filename: str, species: str, trophy_data: dict | None) -> bool:
    """Determine if a nagyvad image is tarvad (non-trophy)."""
    if species not in NAGYVAD_SPECIES:
        return False
    lower = filename.lower()
    # If it has trophy data (lőhető/kímélendő), it's trófeás
    if trophy_data is not None:
        return False
    # If it contains tarvad keywords, it's tarvad
    for kw in TARVAD_KEYWORDS:
        if kw in lower:
            return True
    # Nagyvad without trophy keywords = tarvad
    return True


def categorize(species: str, protection: str | None) -> tuple[str, str | None]:
    """Return (category, subcategory)."""
    if protection:
        return (protection, None)
    if species in NAGYVAD_SPECIES:
        return ("vadászható", "nagyvad")
    if species in APROVAD_SPECIES:
        return ("vadászható", "apróvad")
    if species in EGYEB_VADASZHATÓ:
        return ("vadászható", "egyéb")
    return ("vadászható", "apróvad")


def generate():
    entries = []
    for fname in sorted(os.listdir(IMAGES_DIR)):
        if not fname.lower().endswith(".jpg"):
            continue
        # Extract ID
        match = re.match(r"^(\d+)\.", fname)
        if not match:
            continue

        img_id = int(match.group(1))
        species = extract_species(fname)
        protection = extract_protection(fname)
        trophy_data = extract_trophy_data(fname, species)
        category, subcategory = categorize(species, protection)

        # Determine if trophy
        is_trophy = trophy_data is not None

        # Override subcategory for nagyvad
        if species in NAGYVAD_SPECIES and protection is None:
            if is_tarvad(fname, species, trophy_data):
                subcategory = "nagyvad_tarvad"
            else:
                subcategory = "nagyvad_trófeás" if is_trophy else "nagyvad_tarvad"

        group = "madár" if species in BIRD_SPECIES else "emlős"

        entries.append({
            "id": img_id,
            "filename": fname,
            "species": species,
            "category": category,
            "subcategory": subcategory,
            "group": group,
            "is_trophy": is_trophy,
            "protection": protection,
            "trophy_data": trophy_data,
        })

    entries.sort(key=lambda x: x["id"])

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(entries)} entries in {OUTPUT}")
    return entries


if __name__ == "__main__":
    entries = generate()
    # Print summary
    from collections import Counter
    cats = Counter((e["category"], e["subcategory"]) for e in entries)
    for k, v in sorted(cats.items()):
        print(f"  {k}: {v}")
    trophy_count = sum(1 for e in entries if e["is_trophy"])
    print(f"  Trophy images: {trophy_count}")
