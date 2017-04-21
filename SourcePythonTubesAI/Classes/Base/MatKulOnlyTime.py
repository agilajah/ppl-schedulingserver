class MatKulOnlyTime:
    def __init__(self, idmatkul):
        self.idmatkul = idmatkul
        self.r_selected = -1
        self.j_selected = -1
        self.h_selected = -1
        self.sks = -1

    def setTime(self, r, j, h, s):
        self.r_selected = int(r)
        self.j_selected = int(j)
        self.h_selected = int(h)
        self.sks = int(s)

    def __str__(self):
        return "Ruang : " + str(self.r_selected) + '\nHari : ' + str(self.h_selected) + '\nJam Mulai : ' + str(self.j_selected) + '\nSKS : ' + str(self.sks)
