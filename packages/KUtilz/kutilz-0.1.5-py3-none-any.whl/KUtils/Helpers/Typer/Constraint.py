class BaseConstraint:
    def validate(self, v) -> bool:
        raise NotImplementedError()

class Equals(BaseConstraint):
    def __init__(self, val):
        self.val = val

    def __call__(self, val) -> bool:
        return self.val == val