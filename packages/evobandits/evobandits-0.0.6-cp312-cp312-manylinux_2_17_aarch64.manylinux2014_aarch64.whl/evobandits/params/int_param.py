# Copyright 2025 EvoBandits
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from evobandits.params.base_param import BaseParam


class IntParam(BaseParam):
    """
    A class representing an integer parameter.
    """

    def __init__(self, low: int, high: int, size: int = 1) -> None:
        """
        Creates an IntParam that will suggest integer values during the optimization.

        The parameter can be either an integer, or a list of integers, depending on the specified
        size. The values sampled by the optimization will be limited to the specified granularity,
        lower and upper bounds.

        Args:
            low: The lower bound of the suggested values.
            high: The upper bound of the suggested values.
            size: The size if the parameter shall be a list of integers. Default is 1.

        Returns:
            IntParam: An instance of the parameter with the specified properties.

        Raises:
            ValueError: If low is not an integer, if high is not an integer that is greater than
            low, or if size ist not a positive integers.

        Example:
        >>> param = IntParam(low=1, high=10, size=3)
        >>> print(param)
        IntParam(low=1, high=10, size=3)
        """
        if high <= low:
            raise ValueError("high must be an integer that is greater than low.")

        super().__init__(size)
        self.low: int = int(low)
        self.high: int = int(high)

    def __repr__(self) -> str:
        return f"IntParam(low={self.low}, high={self.high}, size={self.size})"

    @property
    def bounds(self) -> list[tuple[int, int]]:
        """
        Calculate and return the parameter's internal bounds for the optimization.

        The bounds will be used as constraints for the internal representation (or actions)
        of the optimization algorithm about the parameter's value.

        Returns:
            A list of tuples representing the bounds.
        """
        return [(self.low, self.high)] * self.size

    def decode(self, actions: list[int]) -> int | list[int]:
        """
        Decode an action by the optimization problem to the value of the parameter.

        Args:
            actions: A list of integers to map.

        Returns:
            The resulting integer value(s).
        """
        if len(actions) == 1:
            return actions[0]
        return actions
