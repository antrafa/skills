#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p pricing tests
cat > pricing/__init__.py <<'PY'
PY
cat > pricing/discount.py <<'PY'
def apply_discount(amount, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent out of range")
    return round(amount * (100 - percent) / 100, 2)
PY
cat > tests/__init__.py <<'PY'
PY
cat > tests/test_discount.py <<'PY'
import unittest
from pricing.discount import apply_discount

class DiscountTest(unittest.TestCase):
    def test_applies_percent(self):
        self.assertEqual(apply_discount(200, 10), 180)
    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            apply_discount(10, 120)

if __name__ == "__main__":
    unittest.main()
PY
cat > Makefile <<'MK'
test:
	python3 -m unittest discover -s tests -t .
MK
git add -A
git commit -q -m "chore: initial import"
git checkout -q -b fix/discount-rounding
echo "# TODO: cap discount at 90%" >> pricing/discount.py
git commit -qam "fix(discount): note the cap to be applied"
echo "x = 1" > scratch.py
