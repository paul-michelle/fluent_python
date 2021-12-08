from typing import Union
import desc_models as model


class LineItem:

    description = model.NonBlank()
    weight = model.Quantity()
    price = model.Quantity()

    def __init__(self, description: str,
                 weight: Union[int, float],
                 price: Union[int, float]):

        self.description = description
        self.weight = weight
        self.price = price

    def calculate_subtotal(self):
        return self.weight * self.price

