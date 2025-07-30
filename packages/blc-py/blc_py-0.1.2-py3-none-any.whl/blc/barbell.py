class Barbell:
    def __init__(self, weight=20, type="men"):
        if type == "women":
            self.weight = 15
        else:
            self.weight = weight
        self.type = type
