from .plates import Plate, Plates
from .barbell import Barbell


class Blc:
    def __init__(self, plates: Plates, barbell: Barbell) -> None:
        self.weight = 0
        self.plates = plates  # plates available
        self.barbell = barbell
        self.plates_to_use = []

    def calculate_plates(self, weight):
        self.weight = weight
        target_weight = weight

        weight_to_load = (
            target_weight - self.barbell.weight
        ) / 2  # weights that need to be loaded for one side

        if self.plates.use_collar:
            weight_to_load -= 2.5

        if weight_to_load <= 0:  # or weight_to_load >= 275:
            raise ValueError("Invalid weight")

        for weight, quantity in self.plates:
            while weight_to_load >= weight and quantity >= 2:
                weight_to_load -= weight
                self.plates_to_use.append(weight)
                quantity -= 2
                self.plates.set_quantity(weight, quantity)

        return self.plates_to_use

    def add_weight(self, plate_weight):
        if self.plates.get_quantity(plate_weight) >= 2:
            self.weight += plate_weight * 2
            new_quantity = self.plates.get_quantity(plate_weight) - 2
            self.plates.set_quantity(plate_weight, new_quantity)

            self.plates_to_use.append(plate_weight)
            self.plates_to_use.sort(reverse=True)
        else:
            raise ValueError("Not enough plates available")

    def remove_weight(self, plate_weight):
        new_plates_to_use = []
        plate_removed = False

        if self.weight - plate_weight >= 0 and plate_weight in self.plates_to_use:
            self.weight -= plate_weight * 2
            new_quantity = self.plates.get_quantity(plate_weight) + 2
            self.plates.set_quantity(plate_weight, new_quantity)

            for plate in self.plates_to_use:
                if plate == plate_weight and not plate_removed:
                    plate_removed = True
                    continue  # skip this plate (don't add to new list)
                else:
                    new_plates_to_use.append(plate)  # add all other plates

            self.plates_to_use = new_plates_to_use
        else:
            raise ValueError("error")

    def kg_to_lb(self):
        return self.weight / 2.2
