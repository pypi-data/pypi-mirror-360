# Physics TA Assignment Tool (`physethta`)

This Python package automates the assignment of teaching assistants (TAs) to physics courses at ETH Zurich. It processes structured data from internal and external sources, applies configuration rules, and generates LaTeX reports summarizing TA allocations by group and course.

---

## 🧠 Overview

The assignment pipeline consists of:

1. **Data Loading**: Reading input files from Excel/CSV format.
2. **Mapping Supervisors**: Combining internal (via `vorg.csv`) and external (via `Externe.xlsx`) PhD supervisors.
3. **Course Title Normalization**: Creating consistent course titles via `config.yaml`.
4. **Assignment Logic**:

   * Organizing assistants under supervisors (PIs).
   * Associating students with courses (with language information).
5. **Report Generation**:

   * Producing `LaTeX` documents sorted by PI and course.
   * Optionally compiling them into PDFs.

---

## 📁 Project Structure

```
physethta/
│
├── assigner.py          # Core logic for building PI and course dictionaries
├── config.py            # YAML config loader
├── external.py          # Handles mappings for external PhD students
├── loader.py            # Loads and cleans data from Excel/CSV
├── report.py            # Generates LaTeX reports (per group and per course)
├── utils.py             # Name normalization and exclusion helpers
├── assets/
│   └── Logo.pdf         # ETH footer logo (copied into output)
├── __init__.py
│
run_assignment.py        # Main command-line entry point
setup.py                 # Install script (for pip)
```

---

## ⚙️ Input Files

All expected in the same input directory (default: current working directory):

* `Externe.xlsx`: List of external PhDs and their advisors.
* `vorg.csv`: Internal assignments linking assistants to supervisors.
* `alle.csv`: All applicants with metadata and course assignments.
* `sprachen.csv`: Language flags (e.g., `unterricht_deutsch`).
* `config.yaml`: Configuration file with exclusions, aliases, formatting overrides.

---

## ✏️ Configuration

The `config.yaml` file lets you:

* **Exclude supervisors or MAS** from reports (`exclude_pis`, `exclude_mas`)
* **Reassign supervisors** (`reassignments`)
* **Rename courses** (`course_overrides`, `conditional_courses`)
* **Group and label special roles** (`special_modules`, `praktikum_modules`)
* **Override responsible lecturers** (`lecturer_aliases`)
* **Set metadata** for LaTeX output (`meta.semester`, `meta.author`)

See the included `config.yaml` for a working example.

---

## 🚀 Installation

From the project root, install with:

```bash
pip install physethta
```

This provides the command-line tool:

```bash
run_assignment
```

---

## 🛠️ Usage

From the directory containing your input files:

```bash
run_assignment --draft
```

Optional arguments:

* `--input DIR`: Input folder (default: `.`)
* `--config FILE`: Path to `config.yaml` (default: `./config.yaml`)
* `--output DIR`: Output folder (default: `./output`)
* `--draft`: Adds a "Draft" watermark to the PDF output

---

## 📆 Output

Two `.tex` files will be created in `output/`:

* `AssHS25_perGroup.pdf`: Sorted by PI/supervisor
* `AssHS25_perCourse.pdf`: Sorted by course title


In the folder `output/tables` you will find csv files per course, for VMP, etc.

> `Logo.pdf` will be copied into the output folder automatically.

---

## 🔄 Start of New Semester

To prepare the tool for a new semester:

1. Do all the assignments in hat-admin https://swc.itsapp.ethz.ch/hat-swc/app
2. To get to the OIS report, use https://zo-srv-citweb.ethz.ch/Citrix/ETH_CitrixWeb/
3. Once done, export via citrix viewer -> OIS reports
    * Bedarfszuweisung -> Choose semester -> Export CSV (UTF8) to alle.csv
    * Vorgesetzte und Mitarbeiter -> Choose semester -> Export CSV (UTF8) to vorg.csv
    * Bewerbungen -> Choose semester --> Export CSV (UTF8) to sprachen.csv
4. Duplicate and edit `config.yaml`:
   * Update `meta.semester` to `FS26` or `HS26`
   * Update exclusions, reassignments, or course overrides as needed
5. Run:

   ```bash
   run_assignment --draft
   ```
6. Check `.pdf` output in `output/` and the csv's in `output/tables`


---

## Package things

```
python -m build --no-isolation
```
And then 
```
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=...my API TOKEN...
twine upload dist/*
```
