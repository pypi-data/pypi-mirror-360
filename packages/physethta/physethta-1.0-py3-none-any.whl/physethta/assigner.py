import pandas as pd
from .utils import canonical_name, is_excluded
from .utils import overwrite_module


def build_pis_dict(data, external, external_pis, config):
    pis = {}
    exclude_pis = config.get("exclude_pis", [])
    exclude_mas = config.get("exclude_mas", [])
    reassignments = config.get("reassignments", {})


    vorg = data["vorg"]
    alle = data["alle"]

    for _, row in alle.iterrows():
        if row.get("person_typ_kuerzel") != "A":
            continue  # skip if not an assistant

        persid = row.get("persid")
        famname = row.get("famname", "").strip()
        vorname = row.get("vorname", "").strip()
        modul = row.get("modul_nummer")
        reason = row.get("bedarf_bezeichnung", "")
        modul,reason = overwrite_module(reason,modul,config)
        full_name = f"{famname} {vorname}"

        # Case 1: no supervisor found in vorg.csv
        if vorg[vorg["bewerber_persid"] == persid].empty:
            if full_name in external:
                boss_key = external[full_name]
                supervisor = external_pis.get(boss_key)
                if supervisor:
                    if supervisor in reassignments:
                        supervisor = reassignments[supervisor]
                    if not is_excluded(supervisor, exclude_pis):
                        pis.setdefault(supervisor, []).append([vorname, famname, modul, reason])
            else:
                print(f"Warning: External assistant without supervisor: {full_name} ({persid})")
        else:
            entry = vorg[vorg["bewerber_persid"] == persid].iloc[0]
            if pd.notna(entry.get("vorgesetzter_vorname")):
                supervisor = f"{entry['vorgesetzter_famname']} {entry['vorgesetzter_vorname'].split()[0]}"
            else:
                boss_key = external.get(full_name)
                supervisor = external_pis.get(boss_key)

            if supervisor in reassignments:
                supervisor = reassignments[supervisor]
            if not is_excluded(supervisor, exclude_pis) and famname not in exclude_mas:
                pis.setdefault(supervisor, []).append([vorname, famname, modul, reason])
    return pis


def build_course_dict(data, external, config):
    courses = {}
    emails = {}
    langs = {}
    lang_stats = {"total": 0, "german": 0}

    alle = data["alle"]
    vorg = data["vorg"]
    sprachen = data["sprachen"]

    lecturer_aliases = config.get("lecturer_aliases", {})
    course_overrides = config.get("course_overrides", {})
    conditional_courses = config.get("conditional_courses", {})

    for _, row in alle.iterrows():
        bedarf = row.get("bedarf_bezeichnung", "")
        title = course_overrides.get(bedarf)

        if not title and bedarf in conditional_courses:
            lookup = conditional_courses[bedarf]
            key = row.get("modul_name", "")
            title = lookup.get(key)

        if not title and pd.notna(row.get("modul_nummer")):
            verantwortliche = str(row.get("modul_verantwortliche", ""))
            modulname = row.get("modul_name", "Unbenannt")
            modulnummer = row.get("modul_nummer", "")
            responsible = verantwortliche.split(" ")[0].upper()
            responsible = lecturer_aliases.get(responsible, responsible)
            title = f"{responsible} - {modulname}, {modulnummer}"

        if not title:
            continue

        full_name = f"{row.get('famname', '').strip()} {row.get('vorname', '').strip()}"
        persid = row.get("persid")
        role = "Assistent*in"

        if row.get("person_typ_kuerzel") == "HA":
            role = "Hilfsassistent*in"
        elif not vorg[vorg["bewerber_persid"] == persid].empty:
            entry = vorg[vorg["bewerber_persid"] == persid].iloc[0]
            if pd.notna(entry.get("vorgesetzter_famname")):
                role = entry["vorgesetzter_famname"]
        elif full_name in external:
            role = external[full_name]
        else:
            print(f"Panic! No Vorg found for {full_name}")

        courses.setdefault(title, []).append([row.get("vorname", ""), row.get("famname", ""), role])
        emails.setdefault(title, []).append([row.get("vorname", ""), row.get("famname", ""), row.get("email", "")])

        if "persid" in sprachen.columns:
            matches = sprachen[sprachen["persid"] == persid]
        else:
            matches = pd.DataFrame()

        if not matches.empty and pd.notna(matches["unterricht_deutsch"].values[0]):
            deutsch_flag = int(matches["unterricht_deutsch"].values[0])
        else:
            nationality = row.get("nationalitaet_txt", "").strip().lower()
            if nationality in ["schweiz", "österreich", "deutschland"]:
                deutsch_flag = 1
            else:
                deutsch_flag = 0

        langs.setdefault(title, []).append([
            row.get("vorname", ""),
            row.get("famname", ""),
            row.get("email", ""),
            deutsch_flag,
            verantwortliche if 'verantwortliche' in locals() else ""
        ])
        lang_stats["total"] += 1
        if deutsch_flag == 1:
            lang_stats["german"] += 1

    return courses, emails, langs, lang_stats