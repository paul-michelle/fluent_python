from statistics import mean


class Averager:

    def __init__(self):
        self._stored_values = []

    def __call__(self, new_value):
        self._stored_values.append(new_value)
        return mean(self._stored_values)
