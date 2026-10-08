#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p pricing tests
: > pricing/__init__.py
: > tests/__init__.py
cat > pricing/discount.py <<'PY'
def apply_discount(amount, percent):
    return round(amount * (100 - percent) / 100, 2)
PY
cat > tests/test_discount.py <<'PY'
import unittest
from pricing.discount import apply_discount

class DiscountTest(unittest.TestCase):
    def test_applies_percent(self):
        self.assertEqual(apply_discount(200, 10), 180)

if __name__ == "__main__":
    unittest.main()
PY
cat > Makefile <<'MK'
test:
	python3 -m unittest discover -s tests -t .
MK
git add -A
git commit -q -m "chore: initial import"
git checkout -q -b feat/discount-range
cat > pricing/discount.py <<'PY'
def apply_discount(amount, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent out of range")
    return round(amount * (100 - percent) / 100, 2)
PY
cat >> tests/test_discount.py <<'PY'

class RangeTest(unittest.TestCase):
    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            apply_discount(10, 120)
PY
git commit -qam "feat(pricing): reject discount out of range"
# main moves after the branch was cut: two commits the branch has not seen
git checkout -q main
cat > pricing/tax.py <<'PY'
def with_tax(amount):
    return round(amount * 1.1, 2)
PY
git add pricing/tax.py
git commit -q -m "feat(pricing): add tax"
echo "# pricing" > README.md
git add README.md
git commit -q -m "docs: add readme"
git checkout -q feat/discount-range
