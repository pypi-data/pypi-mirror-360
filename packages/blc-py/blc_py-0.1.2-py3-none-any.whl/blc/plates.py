class Plate:
    def __init__(self, weight, quantity) -> None:
        self.weight = weight 
        self.quantity = quantity


class Plates:
    weights = [25, 20, 15, 10, 5, 2.5, 2, 1.5, 1, 0.5]

    def __init__(self):
        self.plates = {}
        for weight in self.weights:
            self.plates[weight] = Plate(weight, 8)

    def add_plate(self, weight: float, quantity: int = 2):
        if quantity % 2 != 0:
            raise ValueError(f"Quantity must be even, got {quantity}")
        if weight not in self.plates:
            self.plates[weight] = Plate(weight, 0)
        self.plates[weight].quantity += quantity

    def remove_plate(self, weight: float, quantity: int = 2):
        if quantity % 2 != 0:
            raise ValueError(f"Quantity must be even, got {quantity}")
        if weight not in self.plates or self.plates[weight].quantity < quantity:
            raise ValueError(f"Not enough plates of weight {weight}")
        self.plates[weight].quantity -= quantity
        if self.plates[weight].quantity == 0:
            del self.plates[weight]

    def get_quantity(self, weight: float) -> int:
        if weight not in self.plates:
            return 0
        return self.plates[weight].quantity

    def set_quantity(self, weight:float, new_quantity):
        if weight not in self.plates:
            raise(ValueError(f"not in plates"))
        self.plates[weight].quantity = new_quantity


    def total_quantity(self):
        return [(plate, value.quantity) for plate, value in zip(self.plates, self.plates.values())]

    def __repr__(self) -> str:
        return str([(plate.weight, plate.quantity) for plate in self.plates.values()])

    def __iter__(self):
        return iter((plate.weight, plate.quantity) for plate in self.plates.values())

    def __getitem__(self, weight: float) -> int:
        if weight not in self.plates:
            return 0
        return self.plates[weight].quantity
