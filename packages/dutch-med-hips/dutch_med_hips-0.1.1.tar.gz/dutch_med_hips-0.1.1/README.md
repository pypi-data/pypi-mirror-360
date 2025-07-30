# 🇳🇱 dutch-med-hips

**dutch-med-hips** is a Python package for anonymizing Dutch medical reports using the *Hide-In-Plain-Sight* (HIPS) methodology. It replaces sensitive personal data with realistic surrogates while preserving the readability and overall structure of the text.

---

## 🚀 Features

* Replace personally identifiable information (PII) with synthetic, context-aware surrogates.
* Supports replacement for names, dates, locations, hospitals, study names, phone numbers, IDs, and more.
* Uses real-world statistical distributions (e.g. for age, character frequency) to generate natural-looking output.
* Adds a disclaimer to the final anonymized report.
* Configurable behavior via JSON weight configuration files.

---

## 📦 Installation

Create a fresh conda environment:

```bash
conda create -n dutch-med-hips python=3.11
conda activate dutch-med-hips
```

Install the package via pip:

```bash
pip install dutch-med-hips
```

Or from source:

```bash
git clone https://github.com/DIAGNijmegen/dutch-med-hips.git
cd dutch-med-hips
pip install .
```

---

## 🛠️ Usage

### CLI

After installation, use the CLI to anonymize a report:

```bash
hips \
  --input_file path/to/input_report.txt \
  --output_file path/to/output_report.txt \
  --seed 42
```

Arguments:

* `--input_file`: Path to the file containing the original report.
* `--output_file`: Path to write the anonymized report.
* `--seed`: (Optional) Seed for reproducibility. Default is `42`.
* `--ner_labels`: (Optional) List of NER labels for offset adjustment, currently disabled via CLI.

---

### Python API

```python
from dutch_med_hips.hips_functions import HideInPlainSight

report = "<PERSOON> had a consultation on <DATUM> at <TIJD>."
hips = HideInPlainSight()
anonymized_report = hips.apply_hips(report)
print(anonymized_report)
```

---

## 📄 Supported Tags

The following tags in the report will be replaced:

| Tag                   | Replacement                           |
| --------------------- | ------------------------------------- |
| `<PERSOON>`           | Realistic person names                |
| `<DATUM>`             | Randomized date                       |
| `<TIJD>`              | Randomized time                       |
| `<TELEFOONNUMMER>`    | Synthetic phone number                |
| `<PATIENTNUMMER>`     | Synthetic patient ID                  |
| `<ZNUMMER>`           | Synthetic Z-number                    |
| `<PLAATS>`            | Dutch city                            |
| `<RAPPORT-ID.*>`      | Custom report ID                      |
| `<PHINUMMER>`         | Synthetic PHI number                  |
| `<LEEFTIJD>`          | Realistic age (GMM-based)             |
| `<PERSOONAFKORTING>`  | Name abbreviation                     |
| `<ZIEKENHUIS>`        | Dutch hospital                        |
| `<ACCREDATIE_NUMMER>` | Accreditation number                  |
| `<STUDIE-NAAM>`       | Study name (optionally with UZR code) |

---

## ⚙️ Configuration

The package loads a configuration files and multiple lookup lists from its `config/` directory.
Modify these files to adjust behavior without changing the code.
In particular, `config/config.json` contains weights for various replacement strategies. Adjust these to fit your dataset needs.

---

## 🤝 Contributing

Want to help improve Dutch Med HIPS?

1. Fork the repository.
2. Create your feature branch.
3. Submit a pull request with tests if applicable.
