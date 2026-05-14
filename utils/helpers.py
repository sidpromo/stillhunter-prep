"""Helper functions for StillHunter Prep app."""
import json
import os
import random
import unicodedata

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "species.json")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")


def load_species_data(path: str | None = None) -> list[dict]:
    """Load species data from JSON file."""
    with open(path or DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip, remove accents optionally."""
    return text.strip().lower()


def strip_accents(text: str) -> str:
    """Remove diacritical marks from text."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def check_answer(user_answer: str, correct_species: str, strict: bool = False) -> bool:
    """Check if user's answer matches the correct species.

    Args:
        user_answer: What the user typed
        correct_species: The correct species name
        strict: If True, require exact match (for exam mode)
    """
    user = normalize_text(user_answer)
    correct = normalize_text(correct_species)

    if user == correct:
        return True

    if not strict:
        # Also accept without accents
        if strip_accents(user) == strip_accents(correct):
            return True
        # Accept with/without spaces in compound names
        if user.replace(" ", "") == correct.replace(" ", ""):
            return True
        if strip_accents(user).replace(" ", "") == strip_accents(correct).replace(" ", ""):
            return True

    return False


def get_species_list(data: list[dict]) -> list[str]:
    """Get unique species names from data."""
    return sorted(set(e["species"] for e in data))


def filter_by_category(data: list[dict], category: str) -> list[dict]:
    """Filter entries by category."""
    return [e for e in data if e["category"] == category]


def filter_by_subcategory(data: list[dict], subcategory: str) -> list[dict]:
    """Filter entries by subcategory."""
    return [e for e in data if e.get("subcategory") == subcategory]


def filter_trophy(data: list[dict]) -> list[dict]:
    """Get only trophy-bearing images."""
    return [e for e in data if e["is_trophy"]]


def filter_by_group(data: list[dict], group: str) -> list[dict]:
    """Filter by animal group (madár/emlős)."""
    return [e for e in data if e["group"] == group]


def compose_exam(data: list[dict]) -> list[dict]:
    """Compose a 15-image exam with correct distribution.

    Returns 15 entries:
    - 5 trófeás nagyvad (trophy-bearing, each different species)
    - 3 tarvad nagyvad (non-trophy big game)
    - 4 apróvad (small game, each different species)
    - 2 védett (protected)
    - 1 fokozottan védett (strictly protected)
    """
    trophy_pool = filter_by_subcategory(data, "nagyvad_trófeás")
    tarvad_pool = filter_by_subcategory(data, "nagyvad_tarvad") + filter_by_subcategory(data, "nagyvad")
    aprovad_pool = filter_by_subcategory(data, "apróvad")
    vedett_pool = [e for e in data if e["protection"] == "védett" or e["protection"] == "EU jelentős"]
    fok_vedett_pool = [e for e in data if e["protection"] == "fokozottan védett"]

    # Select with species diversity
    trophy_selected = _select_diverse(trophy_pool, 5)
    tarvad_selected = _select_diverse(tarvad_pool, 3)
    aprovad_selected = _select_diverse(aprovad_pool, 4)
    vedett_selected = _select_diverse(vedett_pool, 2)
    fok_vedett_selected = _select_diverse(fok_vedett_pool, 1)

    exam = trophy_selected + tarvad_selected + aprovad_selected + vedett_selected + fok_vedett_selected
    random.shuffle(exam)
    return exam


def _select_diverse(pool: list[dict], count: int) -> list[dict]:
    """Select entries ensuring species diversity where possible."""
    if not pool:
        return []

    # Group by species
    by_species: dict[str, list[dict]] = {}
    for e in pool:
        by_species.setdefault(e["species"], []).append(e)

    selected = []
    species_list = list(by_species.keys())
    random.shuffle(species_list)

    # First pass: one per species
    for sp in species_list:
        if len(selected) >= count:
            break
        selected.append(random.choice(by_species[sp]))

    # If we need more, pick randomly from remaining
    if len(selected) < count:
        remaining = [e for e in pool if e not in selected]
        random.shuffle(remaining)
        selected.extend(remaining[: count - len(selected)])

    return selected[:count]


def generate_choices(correct_species: str, all_species: list[str], count: int = 4) -> list[str]:
    """Generate multiple choice options including the correct answer.

    Returns a shuffled list of `count` species names, one of which is correct.
    """
    distractors = [s for s in all_species if s != correct_species]
    chosen = random.sample(distractors, min(count - 1, len(distractors)))
    choices = chosen + [correct_species]
    random.shuffle(choices)
    return choices


def evaluate_exam(results: list[dict]) -> dict:
    """Evaluate exam results using official pass/fail rules.

    Each result dict should have:
        - subcategory: str
        - protection: str | None
        - species_correct: bool
        - trophy_correct: bool | None (only for trófeás)
        - user_species: str (what user answered)
        - correct_species: str
        - is_trophy: bool

    Returns evaluation dict with pass/fail and breakdown.
    """
    nagyvad_results = [r for r in results if r.get("subcategory") in ("nagyvad_trófeás", "nagyvad_tarvad", "nagyvad")]
    aprovad_results = [r for r in results if r.get("subcategory") == "apróvad"]
    vedett_results = [r for r in results if r.get("protection") in ("védett", "EU jelentős")]
    fok_vedett_results = [r for r in results if r.get("protection") == "fokozottan védett"]
    trophy_results = [r for r in results if r.get("subcategory") == "nagyvad_trófeás"]

    # Check instant fail: védett confused with vadászható
    instant_fail = False
    for r in vedett_results + fok_vedett_results:
        if not r["species_correct"]:
            # Check if user's answer is a huntable species
            user_ans = r.get("user_species", "")
            if _is_huntable_species(user_ans):
                instant_fail = True
                break

    nagyvad_all_correct = all(r["species_correct"] for r in nagyvad_results)
    aprovad_all_correct = all(r["species_correct"] for r in aprovad_results)

    protected_correct = sum(1 for r in vedett_results + fok_vedett_results if r["species_correct"])
    protected_total = len(vedett_results) + len(fok_vedett_results)
    protected_pass = protected_correct >= 2

    fok_vedett_correct = all(r["species_correct"] for r in fok_vedett_results)

    trophy_correct_count = sum(1 for r in trophy_results if r.get("trophy_correct"))
    trophy_pass = trophy_correct_count >= 4

    passed = (
        not instant_fail
        and nagyvad_all_correct
        and aprovad_all_correct
        and protected_pass
        and fok_vedett_correct
        and trophy_pass
    )

    return {
        "passed": passed,
        "instant_fail": instant_fail,
        "nagyvad_correct": sum(1 for r in nagyvad_results if r["species_correct"]),
        "nagyvad_total": len(nagyvad_results),
        "nagyvad_pass": nagyvad_all_correct,
        "aprovad_correct": sum(1 for r in aprovad_results if r["species_correct"]),
        "aprovad_total": len(aprovad_results),
        "aprovad_pass": aprovad_all_correct,
        "protected_correct": protected_correct,
        "protected_total": protected_total,
        "protected_pass": protected_pass,
        "fok_vedett_correct": fok_vedett_correct,
        "trophy_correct": trophy_correct_count,
        "trophy_total": len(trophy_results),
        "trophy_pass": trophy_pass,
    }


# Huntable species for instant-fail detection
_HUNTABLE_SPECIES = {
    "Nagy lilik", "Vetési lúd", "Nyári lúd", "Nílusi lúd", "Kanadai lúd",
    "Tőkés réce", "Fogoly", "Fácán", "Szárcsa", "Örvös galamb", "Balkáni gerle",
    "Erdei szalonka", "Mezei nyúl", "Üregi nyúl", "Dolmányos varjú", "Szarka",
    "Szajkó", "Pézsmapocok", "Róka", "Aranysakál", "Nyestkutya", "Mosómedve",
    "Borz", "Nyest", "Házi görény", "Szikaszarvas", "Gímszarvas", "Dámszarvas",
    "Őz", "Muflon", "Vaddisznó",
}


def _is_huntable_species(name: str) -> bool:
    """Check if a species name refers to a huntable species."""
    normalized = name.strip()
    for sp in _HUNTABLE_SPECIES:
        if check_answer(normalized, sp):
            return True
    return False


def check_animal_type(user_answer: str, correct_types: list) -> bool:
    """Check if user's animal type answer matches any of the correct types."""
    return user_answer in correct_types


def check_protection(user_answer: str, expected: str) -> bool:
    """Check if user's protection level answer is correct."""
    if expected == "EU jelentős":
        return user_answer == "EU közösségi jelentőségű"
    if expected == "fokozottan védett":
        return user_answer == "fokozottan védett"
    return user_answer == "védett"
