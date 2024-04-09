import copy
from functools import reduce
import heapq
from dataclasses import dataclass
import operator
from typing import Any, Callable


@dataclass
class Parameter:
    name: str


@dataclass
class ParameterValueSet:
    available: dict[Any, int]

    def deepcopy(self) -> dict[Any, int]:
        return copy.deepcopy(self.available)

    def __hash__(self) -> int:
        return id(self)


@dataclass
class CombinationResult:
    parameter_values: tuple[Any]
    score: float

    def __lt__(self, other: "CombinationResult") -> bool:
        return self.score.__lt__(other.score)

    def __gt__(self, other: "CombinationResult") -> bool:
        return self.score.__gt__(other.score)

    def to_str(self, parameter_names: tuple[str, ...], interpretation: Callable[..., str]) -> str:
        params_to_values = (f"{name}={value}" for name, value in zip(parameter_names, self.parameter_values))
        params_to_values_str = ", ".join(params_to_values)
        input_str = f"({params_to_values_str})"
        return f"{input_str} => (score={self.score}, {interpretation(*self.parameter_values)})"


@dataclass
class CombinationResults:
    results: list[CombinationResult]
    parameters: tuple[Parameter, ...]
    interpretation: Callable[..., str]

    def to_str(self, separator: str = '\n') -> str:
        parameter_names = tuple(param.name for param in self.parameters)
        return separator.join(res.to_str(parameter_names, self.interpretation) for res in self.results)

    def __repr__(self) -> str:
        return self.to_str("")


@dataclass
class ParameterAndRemainingValue:
    parameter: Parameter
    available: dict[Any, int]


@dataclass
class Finder:
    parameters_to_set: tuple[tuple[Parameter, ParameterValueSet], ...]
    score: Callable[..., float]
    interpretation: Callable[..., str]

    def estimate_iteration_count(self) -> int:
        if not any(self.parameters_to_set):
            return 0

        return reduce(
            operator.mul,
            (len(value_set.available) for _param, value_set in self.parameters_to_set),
            1
        )

    def get_best(self, count: int) -> CombinationResults:

        def copy_sets() -> list[ParameterAndRemainingValue]:
            copied_parameters_to_set: list[ParameterAndRemainingValue] = []
            set_of_sets: set[ParameterValueSet] = { value_set for _param, value_set in self.parameters_to_set }
            sets_to_copies: dict[ParameterValueSet, dict[Any, int]] = {
                value_set: value_set.deepcopy() for value_set in set_of_sets
            }
            for param, value_set in self.parameters_to_set:
                copied_parameters_to_set.append(
                    ParameterAndRemainingValue(param, sets_to_copies[value_set])
                )
            return copied_parameters_to_set

        copied_parameters_to_set: list[ParameterAndRemainingValue] = copy_sets()

        def add_combinations(combination_results: list[CombinationResult], previous_parameter_values: list[Any | None], parameter_index: int) -> None:
            available_values = copied_parameters_to_set[parameter_index].available
            for value, instance_count in available_values.items():
                if instance_count <= 0:
                    continue
                available_values[value] -= 1
                try:
                    previous_parameter_values[parameter_index] = value
                    if parameter_index + 1 < len(previous_parameter_values):
                        add_combinations(combination_results, previous_parameter_values, parameter_index + 1)
                    else:
                        parameters = previous_parameter_values
                        combination_results.append(CombinationResult(tuple(parameters), self.score(*parameters)))
                finally:
                    available_values[value] += 1

        combination_results: list[CombinationResult] = []
        parameter_values = [None for _ in self.parameters_to_set]
        add_combinations(combination_results, parameter_values, 0)
        combination_count = len(combination_results)
        result_count = min(count, combination_count) if 0 <= count else combination_count
        return CombinationResults(
            heapq.nlargest(result_count, combination_results),
            tuple(param for param, _value_set in self.parameters_to_set),
            self.interpretation
        )
