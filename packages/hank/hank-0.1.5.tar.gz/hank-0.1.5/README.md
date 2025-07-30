# 🐶 Hank

**Hank** is a playful and educational Python package inspired by a very good dog. It’s perfect for learning package structure, object-oriented programming, and integrating libraries like `pandas`, `numpy`, and `pytest`.

---

## 📦 Features

- Greet and interact with Hank
- Track Hank’s treats using a `pandas` DataFrame
- Analyze treat stats and timestamps
- Bark, fetch toys, and sleep
- Easily extendable for more fun behavior

---

## 🔧 Installation

```bash
git clone https://github.com/yourusername/hank.git
cd hank
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

---

## Running Tests

```
pytest
```

## Example Usage

```
from hank import Hank

h = Hank(name="Hank", favorite_toy="stick")

print(h.greet())                   # "Hi! I'm Hank, a 3-year-old good boy who loves stick!"
print(h.bark())                    # "Woof! 🐾"
print(h.fetch("frisbee"))          # "Hank fetches the frisbee and brings it back to you!"

h.give_hank_treat("bacon", 2)      # Adds to treat log
print(h.get_treat_log())           # View treat log as a pandas DataFrame
```

## Dependencies
- `pandas`
- `numpy`
- `pytest`
