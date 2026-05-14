"""Eval: compare Claude nutrition estimates vs USDA ground truth for 10 foods.

Run with:
    python tests/run_eval.py

Writes results to tests/eval_dataset.json.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.nutrition.lookup import _estimate_with_claude  # noqa: E402
from src.nutrition.usda_client import search_usda  # noqa: E402

FOODS = [
    "banana",
    "oatmeal",
    "apple",
    "white rice cooked",
    "lentils cooked",
    "scrambled eggs",
    "whole wheat toast",
    "sweet potato cooked",
    "avocado",
    "plain yogurt",
]


def pct_error(llm_val: float | None, usda_val: float | None) -> str:
    if llm_val is None or usda_val is None or usda_val == 0:
        return "n/a"
    return f"{abs(llm_val - usda_val) / usda_val * 100:.1f}%"


def _fmt(val: float | None) -> str:
    """Format a nullable float for the table."""
    return f"{val:.1f}" if val is not None else "n/a"


def main() -> None:
    results = []
    cols = f"{'Food':<25} {'USDA cal':>9} {'LLM cal':>9} {'cal err':>8}"
    cols += f"  {'USDA prot':>10} {'LLM prot':>9} {'prot err':>9}"
    print(f"\n{cols}")
    print("-" * 90)

    for food in FOODS:
        usda = search_usda(food)
        llm = _estimate_with_claude(food)

        usda_cal = usda.calories_kcal if usda else None
        usda_prot = usda.protein_g if usda else None
        cal_err = pct_error(llm.calories_kcal, usda_cal)
        prot_err = pct_error(llm.protein_g, usda_prot)

        print(
            f"{food:<25} "
            f"{_fmt(usda_cal):>9} "
            f"{_fmt(llm.calories_kcal):>9} "
            f"{cal_err:>8}  "
            f"{_fmt(usda_prot):>10} "
            f"{_fmt(llm.protein_g):>9} "
            f"{prot_err:>9}"
        )

        results.append({
            "food": food,
            "usda": usda.model_dump() if usda else None,
            "llm_estimate": llm.model_dump(),
            "calories_pct_error": cal_err,
            "protein_pct_error": prot_err,
        })

    out_path = Path(__file__).with_name("eval_dataset.json")
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
