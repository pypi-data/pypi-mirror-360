def build_external_mappings(externe_df):
    external = {}
    external_pis = {}
    for _, row in externe_df.iterrows():
        raw = row.get("leiter/in doktorarbeit", "")
        if not isinstance(raw, str) or "," not in raw:
            continue

        last, rest = [part.strip() for part in raw.split(",", 1)]
        first = rest.split()[0] if rest else ""

        advisor_key = last.capitalize()
        advisor_full = f"{last.capitalize()} {first}"

        student_full = f"{row.get('name', '').strip()} {row.get('vorname', '').strip()}"

        external[student_full] = advisor_key
        if advisor_key not in external_pis:
            external_pis[advisor_key] = advisor_full

    return external, external_pis