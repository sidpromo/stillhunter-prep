"""Unit tests for utils/helpers.py"""
import pytest
from utils.helpers import (
    check_animal_type,
    check_answer,
    check_protection,
    compose_exam,
    evaluate_exam,
    filter_by_category,
    filter_by_group,
    filter_by_subcategory,
    filter_trophy,
    generate_choices,
    get_species_list,
    load_species_data,
    normalize_text,
    strip_accents,
)


@pytest.fixture
def species_data():
    return load_species_data()


# --- normalize_text ---

def test_normalize_text_strips_and_lowercases():
    assert normalize_text("  Gímszarvas  ") == "gímszarvas"
    assert normalize_text("FOGOLY") == "fogoly"


# --- strip_accents ---

def test_strip_accents():
    assert strip_accents("Gímszarvas") == "Gimszarvas"
    assert strip_accents("Őz") == "Oz"
    assert strip_accents("Tőkés réce") == "Tokes rece"
    assert strip_accents("Fütyülő") == "Futyulo"


# --- check_answer ---

def test_check_answer_exact():
    assert check_answer("Gímszarvas", "Gímszarvas")
    assert check_answer("gímszarvas", "Gímszarvas")


def test_check_answer_case_insensitive():
    assert check_answer("FOGOLY", "Fogoly")
    assert check_answer("nagy lilik", "Nagy lilik")


def test_check_answer_whitespace():
    assert check_answer("  Fogoly  ", "Fogoly")


def test_check_answer_without_accents():
    assert check_answer("Gimszarvas", "Gímszarvas")
    assert check_answer("Oz", "Őz")
    assert check_answer("Tokes rece", "Tőkés réce")


def test_check_answer_compound_no_space():
    assert check_answer("Tőkésréce", "Tőkés réce")
    assert check_answer("tokesrece", "Tőkés réce")


def test_check_answer_wrong():
    assert not check_answer("Róka", "Borz")
    assert not check_answer("", "Fogoly")


def test_check_answer_strict_rejects_no_accent():
    assert not check_answer("Gimszarvas", "Gímszarvas", strict=True)
    assert check_answer("Gímszarvas", "Gímszarvas", strict=True)
    assert check_answer("gímszarvas", "Gímszarvas", strict=True)


# --- load_species_data ---

def test_load_species_data(species_data):
    assert len(species_data) == 198
    assert all("species" in e for e in species_data)
    assert all("filename" in e for e in species_data)
    assert all("id" in e for e in species_data)


def test_species_data_has_required_fields(species_data):
    required = {"id", "filename", "species", "category", "subcategory", "group", "is_trophy", "protection", "trophy_data"}
    for e in species_data:
        assert required.issubset(e.keys()), f"Entry {e['id']} missing fields"


def test_no_null_species(species_data):
    for e in species_data:
        assert e["species"] is not None and e["species"] != ""


# --- filter functions ---

def test_filter_by_category(species_data):
    vedett = filter_by_category(species_data, "védett")
    assert len(vedett) == 37
    assert all(e["category"] == "védett" for e in vedett)


def test_filter_by_subcategory(species_data):
    trophy = filter_by_subcategory(species_data, "nagyvad_trófeás")
    assert len(trophy) == 57
    assert all(e["subcategory"] == "nagyvad_trófeás" for e in trophy)


def test_filter_trophy(species_data):
    trophy = filter_trophy(species_data)
    assert len(trophy) == 57
    assert all(e["is_trophy"] for e in trophy)


def test_filter_by_group(species_data):
    birds = filter_by_group(species_data, "madár")
    mammals = filter_by_group(species_data, "emlős")
    assert len(birds) + len(mammals) == 198


# --- get_species_list ---

def test_get_species_list(species_data):
    species = get_species_list(species_data)
    assert "Gímszarvas" in species
    assert "Fogoly" in species
    assert "Rétisas" in species
    assert len(species) == len(set(species))  # no duplicates


# --- compose_exam ---

def test_compose_exam_returns_15(species_data):
    exam = compose_exam(species_data)
    assert len(exam) == 15


def test_compose_exam_correct_distribution(species_data):
    exam = compose_exam(species_data)
    trophy = [e for e in exam if e["subcategory"] == "nagyvad_trófeás"]
    tarvad = [e for e in exam if e["subcategory"] in ("nagyvad_tarvad", "nagyvad")]
    aprovad = [e for e in exam if e["subcategory"] == "apróvad"]
    vedett = [e for e in exam if e["protection"] in ("védett", "EU jelentős")]
    fok_vedett = [e for e in exam if e["protection"] == "fokozottan védett"]

    assert len(trophy) == 5
    assert len(tarvad) == 3
    assert len(aprovad) == 4
    assert len(vedett) == 2
    assert len(fok_vedett) == 1


def test_compose_exam_species_diversity(species_data):
    """Trophy images should have different species where possible."""
    exam = compose_exam(species_data)
    trophy = [e for e in exam if e["subcategory"] == "nagyvad_trófeás"]
    trophy_species = [e["species"] for e in trophy]
    # We have 5 trophy species (Gím, Dám, Őz, Muflon, Vaddisznó) but Vaddisznó has no trophy
    # So we should get at least 4 different species
    assert len(set(trophy_species)) >= 4


def test_compose_exam_randomness(species_data):
    """Two exams should not be identical."""
    exam1 = compose_exam(species_data)
    ids1 = [e["id"] for e in exam1]
    # Very unlikely to be identical (but not impossible)
    # Run multiple times to reduce flakiness
    different = any(
        set(e["id"] for e in compose_exam(species_data)) != set(ids1)
        for _ in range(5)
    )
    assert different


# --- generate_choices ---

def test_generate_choices_contains_correct(species_data):
    species = get_species_list(species_data)
    choices = generate_choices("Fogoly", species)
    assert "Fogoly" in choices


def test_generate_choices_correct_count(species_data):
    species = get_species_list(species_data)
    choices = generate_choices("Fogoly", species, count=4)
    assert len(choices) == 4


def test_generate_choices_no_duplicates(species_data):
    species = get_species_list(species_data)
    choices = generate_choices("Fogoly", species)
    assert len(choices) == len(set(choices))


# --- evaluate_exam ---

def _make_result(subcategory, protection, species_correct, trophy_correct=None, user_species="", correct_species="", is_trophy=False):
    return {
        "subcategory": subcategory,
        "protection": protection,
        "species_correct": species_correct,
        "trophy_correct": trophy_correct,
        "user_species": user_species,
        "correct_species": correct_species,
        "is_trophy": is_trophy,
    }


def test_evaluate_exam_all_correct():
    results = (
        [_make_result("nagyvad_trófeás", None, True, True, is_trophy=True)] * 5
        + [_make_result("nagyvad_tarvad", None, True)] * 3
        + [_make_result("apróvad", None, True)] * 4
        + [_make_result(None, "védett", True)] * 2
        + [_make_result(None, "fokozottan védett", True)] * 1
    )
    ev = evaluate_exam(results)
    assert ev["passed"] is True
    assert ev["instant_fail"] is False


def test_evaluate_exam_nagyvad_fail():
    results = (
        [_make_result("nagyvad_trófeás", None, True, True, is_trophy=True)] * 5
        + [_make_result("nagyvad_tarvad", None, False)] * 1  # one wrong
        + [_make_result("nagyvad_tarvad", None, True)] * 2
        + [_make_result("apróvad", None, True)] * 4
        + [_make_result(None, "védett", True)] * 2
        + [_make_result(None, "fokozottan védett", True)] * 1
    )
    ev = evaluate_exam(results)
    assert ev["passed"] is False
    assert ev["nagyvad_pass"] is False


def test_evaluate_exam_trophy_fail():
    results = (
        [_make_result("nagyvad_trófeás", None, True, True, is_trophy=True)] * 3
        + [_make_result("nagyvad_trófeás", None, True, False, is_trophy=True)] * 2  # 2 wrong trophy
        + [_make_result("nagyvad_tarvad", None, True)] * 3
        + [_make_result("apróvad", None, True)] * 4
        + [_make_result(None, "védett", True)] * 2
        + [_make_result(None, "fokozottan védett", True)] * 1
    )
    ev = evaluate_exam(results)
    assert ev["passed"] is False
    assert ev["trophy_pass"] is False
    assert ev["trophy_correct"] == 3


def test_evaluate_exam_instant_fail_vedett_as_huntable():
    results = (
        [_make_result("nagyvad_trófeás", None, True, True, is_trophy=True)] * 5
        + [_make_result("nagyvad_tarvad", None, True)] * 3
        + [_make_result("apróvad", None, True)] * 4
        + [_make_result(None, "védett", False, user_species="Tőkés réce", correct_species="Csörgő réce")] * 1
        + [_make_result(None, "védett", True)] * 1
        + [_make_result(None, "fokozottan védett", True)] * 1
    )
    ev = evaluate_exam(results)
    assert ev["passed"] is False
    assert ev["instant_fail"] is True


def test_evaluate_exam_fok_vedett_missed():
    results = (
        [_make_result("nagyvad_trófeás", None, True, True, is_trophy=True)] * 5
        + [_make_result("nagyvad_tarvad", None, True)] * 3
        + [_make_result("apróvad", None, True)] * 4
        + [_make_result(None, "védett", True)] * 2
        + [_make_result(None, "fokozottan védett", False, user_species="valami", correct_species="Rétisas")] * 1
    )
    ev = evaluate_exam(results)
    assert ev["passed"] is False
    assert ev["fok_vedett_correct"] is False


def test_evaluate_exam_protected_2_of_3_pass():
    """Pass if 2/3 protected correct (and fok_vedett is correct)."""
    results = (
        [_make_result("nagyvad_trófeás", None, True, True, is_trophy=True)] * 5
        + [_make_result("nagyvad_tarvad", None, True)] * 3
        + [_make_result("apróvad", None, True)] * 4
        + [_make_result(None, "védett", False, user_species="valami", correct_species="Csörgő réce")] * 1
        + [_make_result(None, "védett", True)] * 1
        + [_make_result(None, "fokozottan védett", True)] * 1
    )
    ev = evaluate_exam(results)
    assert ev["passed"] is True
    assert ev["protected_correct"] == 2


# --- trophy data in species.json ---

def test_trophy_entries_have_complete_data(species_data):
    trophy = filter_trophy(species_data)
    for e in trophy:
        td = e["trophy_data"]
        assert td is not None, f"Entry {e['id']} missing trophy_data"
        assert td["age_group"] is not None, f"Entry {e['id']} missing age_group"
        assert td["harvestable"] is not None, f"Entry {e['id']} missing harvestable"


def test_trophy_age_groups_valid(species_data):
    valid_ages = {"fiatal", "középkorú", "öreg"}
    trophy = filter_trophy(species_data)
    for e in trophy:
        assert e["trophy_data"]["age_group"] in valid_ages, (
            f"Entry {e['id']} has invalid age_group: {e['trophy_data']['age_group']}"
        )


def test_trophy_harvestable_is_bool(species_data):
    trophy = filter_trophy(species_data)
    for e in trophy:
        assert isinstance(e["trophy_data"]["harvestable"], bool)


# --- check_animal_type ---

def test_check_animal_type_correct():
    assert check_animal_type("bika", ["bika"]) is True
    assert check_animal_type("tehén", ["tehén", "borjú"]) is True
    assert check_animal_type("borjú", ["tehén", "borjú"]) is True


def test_check_animal_type_wrong():
    assert check_animal_type("suta", ["bak"]) is False
    assert check_animal_type("kos", ["bika"]) is False
    assert check_animal_type("", ["bika"]) is False


def test_check_animal_type_multi_correct():
    assert check_animal_type("juh", ["juh", "jerke", "bárány"]) is True
    assert check_animal_type("jerke", ["juh", "jerke", "bárány"]) is True
    assert check_animal_type("kos", ["juh", "jerke", "bárány"]) is False


# --- check_protection ---

def test_check_protection_vedett():
    assert check_protection("védett", "védett") is True
    assert check_protection("fokozottan védett", "védett") is False


def test_check_protection_fokozottan():
    assert check_protection("fokozottan védett", "fokozottan védett") is True
    assert check_protection("védett", "fokozottan védett") is False


def test_check_protection_eu():
    assert check_protection("EU közösségi jelentőségű", "EU jelentős") is True
    assert check_protection("védett", "EU jelentős") is False
