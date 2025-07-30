from typing import Callable

from bayes_opt import BayesianOptimization, UtilityFunction

from naludaq.helpers import validations
from naludaq.helpers.exceptions import OperationCanceledError


class BayesianOptimizer:
    def __init__(self, cost_function, bounds, **kwargs):
        """Wrapper for the bayes_opt module.

        Bayesian optimization is used for black-box functions where
        you want to find the maximum output by probing the input parameters, using Bayes Theorem to
        estimate the best next input parameters to try.

        This class may be used either as a one-off, or iteratively. If used iteratively, the
        cost function need not be specified, as it is not used -- the suggest and register methods
        are used instead to probe the input space.

        This constructor initializes a Bayesian Optimization object, which will try to find the maximum
        output of a cost function by probing within the given bounds. Discrete input space is not supported.
        If you want discrete inputs only, that conversion has to happen within the cost function.

        Args:
            cost_function (Callable): Function that returns a single float with inputs x and y
            bounds (dict): Dictionary with bounds of the parameter space.
                Example: {'x': [1100, 1500], 'y': [900, 1500]}

        References: https://distill.pub/2020/bayesian-optimization/
        """
        self._cancel = False
        self._progress: list = []

        self.optimizer = BayesianOptimization(f=cost_function, pbounds=bounds, **kwargs)
        self.iteration_history = self.optimizer.res
        self._cancel_flag = 0
        self.iterations = 50
        self._utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)

    @property
    def maximum(self) -> dict:
        """Get the current maximum output value found by the optimizer."""
        return self.optimizer.max

    def maximize(self, n_iter: int) -> dict:
        """
        Finds the input values that result in the maximum output value when run through the cost
        function.

        Args:
            n_iter (int): Number of iterations to run. (i.e. how many attempts to find max value.)

        Returns:
            dict: Dictionary with the stored input params that resulted in the largest output value.
        """
        self._utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)
        for i in range(n_iter):
            self._raise_if_canceled()
            next_point_to_probe = self.suggest()
            target = self.cost_function(**next_point_to_probe)
            self.register(next_point_to_probe, target)
            self._progress.append((int(100 * i / n_iter), f"Scanning {(i+1)}/{n_iter}"))

        return self.optimizer.max

    def suggest(self) -> dict:
        """Suggest the next point to probe.

        Only for use in an iterative operation.

        Returns:
            dict: Dictionary with the next input parameters to try.
        """
        return self.optimizer.suggest(self._utility)

    def register(self, point: dict, value: float):
        """Register a point and its value with the optimizer.

        Only for use in an iterative operation.

        Args:
            point (dict): Dictionary with the input parameters that resulted in the given value.
            value (float): The output value of the cost function when run with the given input
        """
        self.optimizer.register(params=point, target=value)

    def run(self):
        self.maximize(self.iterations)

    def cancel(self):
        self._cancel = True

    def _raise_if_canceled(self):
        """Raise an ``OperationCanceledError`` if the cancel flag is set."""
        if self._cancel:
            raise OperationCanceledError("Pedestals generation was canceled.")

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook to read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    @property
    def cost_function(self):
        """Get/Set the cost function.

        Can be set to None when this object is used for iterative operations.
        """
        return self._cost_function

    @cost_function.setter
    def cost_function(self, cost_func):
        if not type(Callable):
            raise TypeError("Cost Function has to be a function")
        if cost_func is not None:
            validations.validate_callable_or_raise(cost_func)
        self._cost_function = cost_func
