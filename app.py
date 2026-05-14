"""StillHunter Prep — Vadászvizsga fajfelismerés gyakorló alkalmazás."""
import os
import random

import streamlit as st

from utils.helpers import (
    check_answer,
    compose_exam,
    evaluate_exam,
    filter_by_category,
    filter_by_subcategory,
    filter_trophy,
    generate_choices,
    get_species_list,
    load_species_data,
)

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

st.set_page_config(page_title="Vadászvizsga Képfelismerés", page_icon="🦌", layout="centered")


@st.cache_data
def get_data():
    return load_species_data()


@st.cache_data
def get_all_species():
    return get_species_list(get_data())


def image_path(filename: str) -> str:
    return os.path.join(IMAGES_DIR, filename)


# Animal type options per species
ANIMAL_TYPE_OPTIONS = {
    "Gímszarvas": ["bika", "tehén", "borjú"],
    "Dámvad": ["bika", "tehén", "borjú"],
    "Őz": ["bak", "suta", "gida"],
    "Muflon": ["kos", "juh", "jerke", "bárány"],
    "Vaddisznó": ["kan", "koca", "süldő", "malac"],
}


def check_animal_type(user_answer: str, correct_types: list) -> bool:
    """Check if user's animal type answer matches any of the correct types."""
    return user_answer in correct_types


# --- Session state init ---
def init_state():
    defaults = {
        "page": "Gyakorlás",
        "stats_total": 0,
        "stats_correct": 0,
        "stats_per_species": {},
        "exam_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# --- Sidebar ---
st.sidebar.title("🦌 Vadászvizsga Képfelismerés")
page = st.sidebar.radio(
    "Navigáció",
    ["Gyakorlás", "Vizsgaszimuláció", "Trófea gyakorlás", "Képek", "Statisztika"],
    index=["Gyakorlás", "Vizsgaszimuláció", "Trófea gyakorlás", "Képek", "Statisztika"].index(st.session_state["page"]),
)
st.session_state["page"] = page

multiple_choice = st.sidebar.checkbox("Feleletválasztós mód", value=False)

data = get_data()
all_species = get_all_species()


# --- Helper: update stats ---
def update_stats(species: str, correct: bool):
    st.session_state["stats_total"] += 1
    if correct:
        st.session_state["stats_correct"] += 1
    sp_stats = st.session_state["stats_per_species"].setdefault(species, {"total": 0, "correct": 0})
    sp_stats["total"] += 1
    if correct:
        sp_stats["correct"] += 1


# ============================================================
# GYAKORLÁS (Practice Mode)
# ============================================================
if page == "Gyakorlás":
    st.header("Gyakorlás")
    st.caption("Ismerd fel a képen látható állatfajt!")

    # Pick a random image if needed
    if "practice_entry" not in st.session_state:
        st.session_state["practice_entry"] = random.choice(data)
        st.session_state["practice_answered"] = False
        st.session_state["practice_result"] = None

    entry = st.session_state["practice_entry"]
    st.image(image_path(entry["filename"]), use_container_width=True)

    if not st.session_state["practice_answered"]:
        if multiple_choice:
            choices = generate_choices(entry["species"], all_species)
            answer = st.radio("Válassz:", choices, index=None, key="practice_mc")
            animal_type_answer = None
            if entry["species"] in ANIMAL_TYPE_OPTIONS and entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                animal_type_answer = st.selectbox("Megnevezés:", [""] + ANIMAL_TYPE_OPTIONS[entry["species"]], index=0, key="practice_at_mc")
            submitted = st.button("Ellenőrzés", key="practice_submit")
            if submitted and answer:
                correct = check_answer(answer, entry["species"])
                at_correct = None
                if animal_type_answer and entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                    at_correct = check_animal_type(animal_type_answer, entry["trophy_data"]["animal_type"])
                st.session_state["practice_answered"] = True
                st.session_state["practice_result"] = correct
                st.session_state["practice_at_result"] = at_correct
                update_stats(entry["species"], correct)
                st.rerun()
        else:
            answer = st.selectbox("Fajnév:", [""] + all_species, index=0, key="practice_input", placeholder="Kezdj el gépelni...")
            animal_type_answer = None
            if entry["species"] in ANIMAL_TYPE_OPTIONS and entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                animal_type_answer = st.selectbox("Megnevezés:", [""] + ANIMAL_TYPE_OPTIONS[entry["species"]], index=0, key="practice_at_input")
            submitted = st.button("Ellenőrzés", key="practice_submit_txt")
            if submitted and answer:
                correct = check_answer(answer, entry["species"])
                at_correct = None
                if animal_type_answer and entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                    at_correct = check_animal_type(animal_type_answer, entry["trophy_data"]["animal_type"])
                st.session_state["practice_answered"] = True
                st.session_state["practice_result"] = correct
                st.session_state["practice_at_result"] = at_correct
                update_stats(entry["species"], correct)
                st.rerun()
    else:
        if st.session_state["practice_result"]:
            st.success(f"✅ Helyes! {entry['species']}")
        else:
            st.error(f"❌ Helytelen! A helyes válasz: **{entry['species']}**")

        at_result = st.session_state.get("practice_at_result")
        if at_result is True:
            st.success("✅ Megnevezés helyes!")
        elif at_result is False:
            correct_types = ", ".join(entry["trophy_data"]["animal_type"])
            st.error(f"❌ Megnevezés helytelen! Helyes: **{correct_types}**")

        if entry.get("protection"):
            st.info(f"Védettség: {entry['protection']}")

        if st.button("Következő", key="practice_next"):
            st.session_state["practice_entry"] = random.choice(data)
            st.session_state["practice_answered"] = False
            st.session_state["practice_result"] = None
            st.session_state["practice_at_result"] = None
            st.rerun()


# ============================================================
# VIZSGASZIMULÁCIÓ (Exam Simulation)
# ============================================================
elif page == "Vizsgaszimuláció":
    st.header("Vizsgaszimuláció")

    if "exam_images" not in st.session_state:
        st.session_state["exam_images"] = None
        st.session_state["exam_index"] = 0
        st.session_state["exam_results"] = []
        st.session_state["exam_finished"] = False

    # Start exam
    if st.session_state["exam_images"] is None:
        st.write("A vizsga 15 képből áll a hivatalos összetétel szerint:")
        st.write("- 5 trófeás nagyvad (korcsoport + elejthetőség)")
        st.write("- 3 tarvad nagyvad")
        st.write("- 4 apróvad")
        st.write("- 2 védett")
        st.write("- 1 fokozottan védett")
        if st.button("Vizsga indítása", key="exam_start"):
            st.session_state["exam_images"] = compose_exam(data)
            st.session_state["exam_index"] = 0
            st.session_state["exam_results"] = []
            st.session_state["exam_finished"] = False
            st.rerun()

    elif not st.session_state["exam_finished"]:
        idx = st.session_state["exam_index"]
        exam_images = st.session_state["exam_images"]
        entry = exam_images[idx]

        st.progress((idx) / 15, text=f"Kérdés {idx + 1} / 15")
        st.image(image_path(entry["filename"]), use_container_width=True)

        with st.form(f"exam_form_{idx}"):
            if multiple_choice:
                choices = generate_choices(entry["species"], all_species)
                species_answer = st.radio("Fajnév:", choices, index=None, key=f"exam_mc_{idx}")
            else:
                species_answer = st.selectbox("Fajnév:", [""] + all_species, index=0, key=f"exam_input_{idx}", placeholder="Kezdj el gépelni...")

            animal_type_answer = None
            if entry["species"] in ANIMAL_TYPE_OPTIONS and entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                animal_type_answer = st.selectbox("Megnevezés:", [""] + ANIMAL_TYPE_OPTIONS[entry["species"]], index=0, key=f"exam_at_{idx}")

            trophy_age = None
            trophy_harvest = None
            if entry["is_trophy"]:
                st.divider()
                st.caption("Trófea minősítés:")
                trophy_age = st.selectbox("Korcsoport:", ["fiatal", "középkorú", "öreg"], key=f"exam_age_{idx}")
                trophy_harvest = st.selectbox("Elejthetőség:", ["lőhető", "kímélendő"], key=f"exam_harvest_{idx}")

            protection_answer = None
            if entry.get("protection"):
                st.divider()
                st.caption("Védettségi besorolás:")
                protection_answer = st.selectbox("Védettség:", ["védett", "fokozottan védett", "EU közösségi jelentőségű"], key=f"exam_prot_{idx}")

            submitted = st.form_submit_button("Tovább")
            if submitted:
                if not species_answer:
                    st.warning("Válassz fajnevet!")
                    st.stop()
                if entry["species"] in ANIMAL_TYPE_OPTIONS and entry.get("trophy_data") and entry["trophy_data"].get("animal_type") and not animal_type_answer:
                    st.warning("Válassz megnevezést!")
                    st.stop()
                if entry["is_trophy"] and (not trophy_age or not trophy_harvest):
                    st.warning("Töltsd ki a trófea minősítést!")
                    st.stop()
                if entry.get("protection") and not protection_answer:
                    st.warning("Válassz védettségi besorolást!")
                    st.stop()
                species_correct = check_answer(species_answer or "", entry["species"])

                # Check animal type
                animal_type_correct = None
                if animal_type_answer and entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                    animal_type_correct = check_animal_type(animal_type_answer, entry["trophy_data"]["animal_type"])

                trophy_correct = None
                if entry["is_trophy"] and entry["trophy_data"]:
                    td = entry["trophy_data"]
                    age_ok = trophy_age == td["age_group"]
                    harvest_ok = (trophy_harvest == "lőhető") == td["harvestable"]
                    trophy_correct = age_ok and harvest_ok

                # Check protection level
                protection_correct = None
                if entry.get("protection"):
                    expected_prot = entry["protection"]
                    if expected_prot == "EU jelentős":
                        protection_correct = protection_answer == "EU közösségi jelentőségű"
                    elif expected_prot == "fokozottan védett":
                        protection_correct = protection_answer == "fokozottan védett"
                    else:
                        protection_correct = protection_answer == "védett"

                result = {
                    "id": entry["id"],
                    "filename": entry["filename"],
                    "species": entry["species"],
                    "subcategory": entry.get("subcategory"),
                    "protection": entry.get("protection"),
                    "is_trophy": entry["is_trophy"],
                    "species_correct": species_correct,
                    "trophy_correct": trophy_correct,
                    "protection_correct": protection_correct,
                    "animal_type_correct": animal_type_correct,
                    "user_species": species_answer or "",
                    "correct_species": entry["species"],
                    "user_animal_type": animal_type_answer,
                    "correct_animal_type": entry.get("trophy_data", {}).get("animal_type") if entry.get("trophy_data") else None,
                    "user_age": trophy_age,
                    "user_harvest": trophy_harvest,
                    "user_protection": protection_answer,
                    "trophy_data": entry.get("trophy_data"),
                }
                st.session_state["exam_results"].append(result)
                update_stats(entry["species"], species_correct)

                if idx + 1 >= 15:
                    st.session_state["exam_finished"] = True
                else:
                    st.session_state["exam_index"] = idx + 1
                st.rerun()

    else:
        # Show results
        results = st.session_state["exam_results"]
        evaluation = evaluate_exam(results)

        if evaluation["passed"]:
            st.success("🎉 MEGFELELT!")
        else:
            st.error("❌ NEM FELELT MEG")

        if evaluation["instant_fail"]:
            st.error("⚠️ Azonnali bukás: védett fajt vadászható fajjal tévesztettél össze!")

        st.subheader("Eredmények")
        col1, col2, col3 = st.columns(3)
        col1.metric("Nagyvad", f"{evaluation['nagyvad_correct']}/{evaluation['nagyvad_total']}", "✓" if evaluation["nagyvad_pass"] else "✗")
        col2.metric("Apróvad", f"{evaluation['aprovad_correct']}/{evaluation['aprovad_total']}", "✓" if evaluation["aprovad_pass"] else "✗")
        col3.metric("Védett", f"{evaluation['protected_correct']}/{evaluation['protected_total']}", "✓" if evaluation["protected_pass"] else "✗")

        col4, col5 = st.columns(2)
        col4.metric("Trófea", f"{evaluation['trophy_correct']}/{evaluation['trophy_total']}", "✓" if evaluation["trophy_pass"] else "✗")
        col5.metric("Fok. védett", "✓" if evaluation["fok_vedett_correct"] else "✗")

        st.divider()
        st.subheader("Részletes eredmények")
        for i, r in enumerate(results):
            # Icon logic: ✅ all correct, ⚠️ species correct but trophy/protection/animal_type wrong, ❌ species wrong
            if not r["species_correct"]:
                icon = "❌"
            elif r.get("trophy_correct") is False or r.get("protection_correct") is False or r.get("animal_type_correct") is False:
                icon = "⚠️"
            else:
                icon = "✅"
            with st.expander(f"{i+1}. {icon} {r['correct_species']}"):
                st.image(image_path(r["filename"]), width=300)
                st.write(f"**Te válaszod:** {r['user_species']}")
                st.write(f"**Helyes válasz:** {r['correct_species']}")
                if r.get("correct_animal_type"):
                    at_icon = "✅" if r.get("animal_type_correct") else "❌"
                    correct_at = ", ".join(r["correct_animal_type"])
                    st.write(f"{at_icon} Megnevezés: {r.get('user_animal_type', '—')} (helyes: {correct_at})")
                if r["is_trophy"] and r["trophy_data"]:
                    td = r["trophy_data"]
                    age_icon = "✅" if r.get("user_age") == td["age_group"] else "❌"
                    harvest_expected = "lőhető" if td["harvestable"] else "kímélendő"
                    harvest_icon = "✅" if r.get("user_harvest") == harvest_expected else "❌"
                    st.write(f"{age_icon} Korcsoport: {r.get('user_age', '—')} (helyes: {td['age_group']})")
                    st.write(f"{harvest_icon} Elejthetőség: {r.get('user_harvest', '—')} (helyes: {harvest_expected})")
                if r.get("protection") and r.get("user_protection"):
                    expected_prot = "EU közösségi jelentőségű" if r["protection"] == "EU jelentős" else r["protection"]
                    prot_icon = "✅" if r.get("protection_correct") else "❌"
                    st.write(f"{prot_icon} Védettség: {r.get('user_protection', '—')} (helyes: {expected_prot})")

        # Record in history
        st.session_state["exam_history"].append(evaluation["passed"])

        if st.button("Új vizsga", key="exam_restart"):
            st.session_state["exam_images"] = None
            st.session_state["exam_index"] = 0
            st.session_state["exam_results"] = []
            st.session_state["exam_finished"] = False
            st.rerun()


# ============================================================
# TRÓFEA GYAKORLÁS (Trophy Practice)
# ============================================================
elif page == "Trófea gyakorlás":
    st.header("Trófea gyakorlás")
    st.caption("Ismerd fel a fajt, korcsoportot és elejthetőséget!")

    trophy_data_list = filter_trophy(data)

    if "trophy_entry" not in st.session_state:
        st.session_state["trophy_entry"] = random.choice(trophy_data_list)
        st.session_state["trophy_answered"] = False

    entry = st.session_state["trophy_entry"]
    st.image(image_path(entry["filename"]), use_container_width=True)

    if not st.session_state["trophy_answered"]:
        with st.form("trophy_form"):
            if multiple_choice:
                trophy_species_list = sorted(set(e["species"] for e in trophy_data_list))
                species_answer = st.radio("Fajnév:", trophy_species_list, index=None, key="trophy_mc")
            else:
                trophy_species_list = sorted(set(e["species"] for e in trophy_data_list))
                species_answer = st.selectbox("Fajnév:", [""] + trophy_species_list, index=0, key="trophy_species_input", placeholder="Kezdj el gépelni...")
            animal_type_answer = None
            if entry.get("trophy_data") and entry["trophy_data"].get("animal_type"):
                all_types = ["bika", "tehén", "borjú", "bak", "suta", "gida", "kos", "juh", "jerke", "bárány", "kan", "koca", "süldő", "malac"]
                animal_type_answer = st.selectbox("Megnevezés:", [""] + all_types, index=0, key="trophy_at_input")
            age_answer = st.selectbox("Korcsoport:", ["fiatal", "középkorú", "öreg"], key="trophy_age_input")
            harvest_answer = st.selectbox("Elejthetőség:", ["lőhető", "kímélendő"], key="trophy_harvest_input")
            submitted = st.form_submit_button("Ellenőrzés")

            if submitted and species_answer:
                st.session_state["trophy_answered"] = True
                td = entry["trophy_data"]
                at_correct = None
                if animal_type_answer and td.get("animal_type"):
                    at_correct = check_animal_type(animal_type_answer, td["animal_type"])
                st.session_state["trophy_results"] = {
                    "species_correct": check_answer(species_answer, entry["species"]),
                    "animal_type_correct": at_correct,
                    "age_correct": age_answer == td["age_group"],
                    "harvest_correct": (harvest_answer == "lőhető") == td["harvestable"],
                }
                update_stats(entry["species"], st.session_state["trophy_results"]["species_correct"])
                st.rerun()
    else:
        r = st.session_state["trophy_results"]
        td = entry["trophy_data"]

        sp_icon = "✅" if r["species_correct"] else "❌"
        at_icon = "✅" if r.get("animal_type_correct") else ("❌" if r.get("animal_type_correct") is False else "")
        age_icon = "✅" if r["age_correct"] else "❌"
        harvest_icon = "✅" if r["harvest_correct"] else "❌"

        st.write(f"{sp_icon} **Faj:** {entry['species']}")
        if at_icon and td.get("animal_type"):
            correct_at = ", ".join(td["animal_type"])
            st.write(f"{at_icon} **Megnevezés:** {correct_at}")
        st.write(f"{age_icon} **Korcsoport:** {td['age_group']}")
        harvest_str = "lőhető" if td["harvestable"] else "kímélendő"
        st.write(f"{harvest_icon} **Elejthetőség:** {harvest_str}")

        if st.button("Következő", key="trophy_next"):
            st.session_state["trophy_entry"] = random.choice(trophy_data_list)
            st.session_state["trophy_answered"] = False
            st.session_state.pop("trophy_results", None)
            st.rerun()


# ============================================================
# TANULÁS (Study Mode)
# ============================================================
elif page == "Képek":
    st.header("Képek")
    st.caption("Böngészd a fajokat kategória szerint.")

    # Filters
    cat_filter = st.selectbox("Kategória:", ["Mind", "Apróvad", "Nagyvad trófeás", "Nagyvad tarvad", "Védett", "Fokozottan védett"])

    filtered = data
    if cat_filter == "Apróvad":
        filtered = filter_by_subcategory(filtered, "apróvad")
    elif cat_filter == "Nagyvad trófeás":
        filtered = filter_by_subcategory(filtered, "nagyvad_trófeás")
    elif cat_filter == "Nagyvad tarvad":
        filtered = filter_by_subcategory(filtered, "nagyvad_tarvad")
    elif cat_filter == "Védett":
        filtered = [e for e in filtered if e["protection"] in ("védett", "EU jelentős")]
    elif cat_filter == "Fokozottan védett":
        filtered = filter_by_category(filtered, "fokozottan védett")

    st.write(f"**{len(filtered)} kép**")

    # Display as grid
    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(filtered):
                entry = filtered[i + j]
                with col:
                    st.image(image_path(entry["filename"]), use_container_width=True)
                    st.caption(f"**{entry['species']}**")
                    if entry.get("protection"):
                        st.caption(f"🛡️ {entry['protection']}")
                    if entry.get("trophy_data") and entry["trophy_data"].get("harvestable") is not None:
                        td = entry["trophy_data"]
                        harvest = "lőhető" if td["harvestable"] else "kímélendő"
                        st.caption(f"🏆 {td['age_group']} / {harvest}")


# ============================================================
# STATISZTIKA (Stats)
# ============================================================
elif page == "Statisztika":
    st.header("Statisztika")

    total = st.session_state["stats_total"]
    correct = st.session_state["stats_correct"]

    if total == 0:
        st.info("Még nincs statisztikád. Kezdj el gyakorolni!")
    else:
        accuracy = correct / total * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Összes kérdés", total)
        col2.metric("Helyes válasz", correct)
        col3.metric("Pontosság", f"{accuracy:.1f}%")

        # Exam history
        exam_hist = st.session_state["exam_history"]
        if exam_hist:
            st.divider()
            st.subheader("Vizsgaeredmények")
            passed = sum(exam_hist)
            st.write(f"**{passed}/{len(exam_hist)}** sikeres vizsga")

        # Per-species breakdown
        sp_stats = st.session_state["stats_per_species"]
        if sp_stats:
            st.divider()
            st.subheader("Fajok szerinti eredmények")

            # Sort by accuracy (worst first)
            sorted_species = sorted(
                sp_stats.items(),
                key=lambda x: x[1]["correct"] / x[1]["total"] if x[1]["total"] > 0 else 1,
            )

            # Highlight weakest
            if sorted_species:
                worst = sorted_species[0]
                worst_acc = worst[1]["correct"] / worst[1]["total"] * 100
                st.warning(f"⚠️ Leggyengébb faj: **{worst[0]}** ({worst_acc:.0f}%)")

            for species, stats in sorted_species:
                acc = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
                st.write(f"{'✅' if acc >= 80 else '⚠️' if acc >= 50 else '❌'} **{species}** — {stats['correct']}/{stats['total']} ({acc:.0f}%)")

    if st.button("Statisztika törlése"):
        st.session_state["stats_total"] = 0
        st.session_state["stats_correct"] = 0
        st.session_state["stats_per_species"] = {}
        st.session_state["exam_history"] = []
        st.rerun()
