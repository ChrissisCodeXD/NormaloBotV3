
class CouldNotFindEnv(Exception):
    pass


class raw_env:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Env:

    def __init__(self):
        self.env = []
        with open("./data/config.env") as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                key, value = line.strip().split('=', 1)
                self.env.append(raw_env(key, value))  # Save to a list

    def get(self, xyz):
        toret = []
        for i in self.env:
            if i.name == xyz:
                toret.append(i.value)

        if len(toret) == 0:
            raise CouldNotFindEnv()

        if len(toret) == 1:
            toret = toret[0]

        return toret
