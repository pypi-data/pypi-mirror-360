# AromaTools

AromaTools is a Python package designed for the **analysis of aromaticity** using the three principal approaches:

---

## 🔬 Aromaticity Criteria

### 🧲 Magnetic Criteria (AroMagnetic)
- Compute the **induced magnetic field** in x, y, or z directions.
- Calculate:
  - **NICS** at a single point (NICS-SP)
  - **NICS-XY-Scan** (1D and 2D)
  - **NICS-3D**
- Compute the **ring current strength** by numerical integration.

### 📐 Geometric Criteria (AroGeometric)
- Analyze **Bond Length Alternation** (BLA)
- Compute the **HOMA**, **HOMER**, and **HOMAc** indices:
  - `HOMA`: 0 = non-aromatic, 1 = aromatic
  - `HOMER`: excited-state aromaticity
  - `HOMAc`: -1 = antiaromatic, 0 = non-aromatic, 1 = aromatic

### ⚡ Energetic Criteria (AroEnergetic)
- **Coming soon...**

---

## 📦 Installation

Install via PyPI:

```bash
pip install aromatools
