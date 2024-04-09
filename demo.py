from combination_ranker import Parameter, ParameterValueSet, Finder
from functools import reduce
from dataclasses import dataclass


def main() -> None:
    import pprint, math, time

    def proximity(value: float, target: float) -> float:
        return math.cos(math.atan(value - target))

    def proximity_exp(value: float, target: float) -> float:
        return math.exp(-(value - target) ** 2)

    def score(r1: float, r2: float, c1: float, c2: float) -> float:
        return proximity_exp(r2 * c2, 0.76) * proximity_exp((r1 * c1) / (r2 * c2), 10)

    def interpretation(r1: float, r2: float, c1: float, c2: float) -> str:
        return f"T={r2 * c2}, a={(r1 * c1) / (r2 * c2)}"

    rn = 1
    r_set = ParameterValueSet({
        # 1.0: rn, 10: rn, 100: rn, 1.0e3: rn, 10e3: rn, 100e3: rn, 1.0e6: rn,
        # 1.1: rn, 11: rn, 110: rn, 1.1e3: rn, 11e3: rn, 110e3: rn, 1.1e6: rn,
        # 1.2: rn, 12: rn, 120: rn, 1.2e3: rn, 12e3: rn, 120e3: rn, 1.2e6: rn,
        1.3: rn, 13: rn, 130: rn, 1.3e3: rn, 13e3: rn, 130e3: rn, 1.3e6: rn,
        # 1.5: rn, 15: rn, 150: rn, 1.5e3: rn, 15e3: rn, 150e3: rn, 1.5e6: rn,
        # 1.6: rn, 16: rn, 160: rn, 1.6e3: rn, 16e3: rn, 160e3: rn, 1.6e6: rn,
        1.8: rn, 18: rn, 180: rn, 1.8e3: rn, 18e3: rn, 180e3: rn, 1.8e6: rn,
        # 2.0: rn, 20: rn, 200: rn, 2.0e3: rn, 20e3: rn, 200e3: rn, 2.0e6: rn,
        # 2.2: rn, 22: rn, 220: rn, 2.2e3: rn, 22e3: rn, 220e3: rn, 2.2e6: rn,
        # 2.4: rn, 24: rn, 240: rn, 2.4e3: rn, 24e3: rn, 240e3: rn, 2.4e6: rn,
        # 2.7: rn, 27: rn, 270: rn, 2.7e3: rn, 27e3: rn, 270e3: rn, 2.7e6: rn,
        3.0: rn, 30: rn, 300: rn, 3.0e3: rn, 30e3: rn, 300e3: rn, 3.0e6: rn,
        # 3.3: rn, 33: rn, 330: rn, 3.3e3: rn, 33e3: rn, 330e3: rn, 3.3e6: rn,
        # 3.6: rn, 36: rn, 360: rn, 3.6e3: rn, 36e3: rn, 360e3: rn, 3.6e6: rn,
        3.9: rn, 39: rn, 390: rn, 3.9e3: rn, 39e3: rn, 390e3: rn, 3.9e6: rn,
        # 4.3: rn, 43: rn, 430: rn, 4.3e3: rn, 43e3: rn, 430e3: rn, 4.3e6: rn,
        # 4.7: rn, 47: rn, 470: rn, 4.7e3: rn, 47e3: rn, 470e3: rn, 4.7e6: rn,
        5.1: rn, 51: rn, 510: rn, 5.1e3: rn, 51e3: rn, 510e3: rn, 5.1e6: rn,
        # 5.6: rn, 56: rn, 560: rn, 5.6e3: rn, 56e3: rn, 560e3: rn, 5.6e6: rn,
        6.2: rn, 62: rn, 620: rn, 6.2e3: rn, 62e3: rn, 620e3: rn, 6.2e6: rn,
        6.8: rn, 68: rn, 680: rn, 6.8e3: rn, 68e3: rn, 680e3: rn, 6.8e6: rn,
        # 7.5: rn, 75: rn, 750: rn, 7.5e3: rn, 75e3: rn, 750e3: rn, 7.5e6: rn,
        # 8.2: rn, 82: rn, 820: rn, 8.2e3: rn, 82e3: rn, 820e3: rn, 8.2e6: rn,
        9.1: rn, 91: rn, 910: rn, 9.1e3: rn, 91e3: rn, 910e3: rn, 9.1e6: rn,
    })

    cn = 1
    c_set = ParameterValueSet({
        # 10e-12: cn, 100e-12: cn, 1000e-12: cn, .010e-3: cn, .10e-3: cn, 1.0e-3: cn, 10e-3: cn,
        12e-12: cn, 120e-12: cn, 1200e-12: cn, .012e-3: cn, .12e-3: cn, 1.2e-3: cn,
        # 15e-12: cn, 150e-12: cn, 1500e-12: cn, .015e-3: cn, .15e-3: cn, 1.5e-3: cn,
        18e-12: cn, 180e-12: cn, 1800e-12: cn, .018e-3: cn, .18e-3: cn, 1.8e-3: cn,
        # 22e-12: cn, 220e-12: cn, 2200e-12: cn, .022e-3: cn, .22e-3: cn, 2.2e-3: cn, 22e-3: cn,
        27e-12: cn, 270e-12: cn, 2700e-12: cn, .027e-3: cn, .27e-3: cn, 2.7e-3: cn,
        # 33e-12: cn, 330e-12: cn, 3300e-12: cn, .033e-3: cn, .33e-3: cn, 3.3e-3: cn, 33e-3: cn,
        39e-12: cn, 390e-12: cn, 3900e-12: cn, .039e-3: cn, .39e-3: cn, 3.9e-3: cn,
        # 47e-12: cn, 470e-12: cn, 4700e-12: cn, .047e-3: cn, .47e-3: cn, 4.7e-3: cn, 47e-6: cn,
        56e-12: cn, 560e-12: cn, 5600e-12: cn, .056e-3: cn, .56e-3: cn, 5.6e-3: cn,
        # 68e-12: cn, 680e-12: cn, 6800e-12: cn, .068e-3: cn, .68e-3: cn, 6.8e-3: cn,
        # 82e-12: cn, 820e-12: cn, 8200e-12: cn, .082e-3: cn, .82e-3: cn, 8.2e-3: cn,
    })

    finder = Finder(
        (
            (Parameter("r1"), r_set),
            (Parameter("r2"), r_set),
            (Parameter("c1"), c_set),
            (Parameter("c2"), c_set),
        ),
        score,
        interpretation
    )

    estimate_iter_count = finder.estimate_iteration_count()
    print(f"{estimate_iter_count} combination{'s' if 2 <= estimate_iter_count else ''} at most")
    start_time = time.time()
    best_results = finder.get_best(10)
    print(best_results.to_str())
    print(f"-> {time.time() - start_time} seconds")


if __name__ == "__main__":
    main()
