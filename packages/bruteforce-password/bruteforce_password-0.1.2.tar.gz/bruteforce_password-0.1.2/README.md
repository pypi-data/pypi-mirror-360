# 🔐 Bruteforce Password Generator
⚠️ **IMPORTANT: For educational use only. Unauthorized password cracking is illegal.**

**A customized password generator baked to a specific target.**  

## 🧠 How it works

This tool generates likely password guesses based on a target's personal details using:
- Templates (e.g. `{first_name}@123`, `password{dob}`, etc.)
- A list of relevant keywords (like pet names, hobbies, etc.)
- Leetspeak and case transformations (e.g. `blaze` → `Blaze`, `bl4ze`, `BL4ZE`, etc.)

Useful for ethical hacking, CTFs, or security research.

---

## 📦 Installation

You can install this via pip (after publishing):

```bash
pip install smart-brute-force
```

## 🛠️ Usage Example
```python
from bruteforce_password import BruteforcePassword

bp = BruteforcePassword(
    first_name='john',
    dob='01012000',
    last_name="doe",
    target_website="google"
)

bp.add_template("{car_name}@vroom")
bp.add_more_info("car_name", "hyundai")
bp.add_relevant_words(["cookies", "jane", "newyork"])

passwords = bp.brute_force()

for pw in passwords:
    print(pw)
```