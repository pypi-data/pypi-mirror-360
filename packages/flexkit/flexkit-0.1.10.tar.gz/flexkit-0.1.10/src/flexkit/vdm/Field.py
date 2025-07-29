class Field:
    def __init__(self, name: str, default, v_funcs=None):
        if v_funcs is None:
            v_funcs = []
        self.name = name
        self.default = default
        self.value = None
        self.v_funcs = v_funcs
        self.set(self.default)

    def set(self, value):
        new_value = value
        for func in self.v_funcs:
            new_value = func(value=new_value, name=self.name)
        self.value = new_value

    def get(self):
        return self.value
