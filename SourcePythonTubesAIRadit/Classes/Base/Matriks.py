class Matriks:
    row = 0
    col = 0

    def __init__(self, r = None, c = None):
        if r is not None:
            self.row = r
        if c is not None:
            self.col = c

        self.matriks = []
        for i in range(self.row):
            self.matriks.append([])
            for j in range(self.col):
                self.matriks[i].append([])


    def conflict_count(self):
        total = 0
        for ruang in self.matriks:
            for jam in ruang:
                cnt = len(jam)
                total += cnt * (cnt-1) / 2
        return total

    def __str__(self):
        return (str(self.row) + ' ' + str(self.col) + ' ' + str(self.matriks))
