from .Ruangan import Ruangan
from .MatKul import MatKul
from .MatKulOnlyTime import MatKulOnlyTime

class Jadwal:
    daftar_ruangan = []
    daftar_mata_kuliah = []
    total_pasangan = 0

    @classmethod
    def process_ruangan_dan_mata_kuliah(self, ruangan_raw, mata_kuliah_raw):
        idruangan = 0
        for ruangan in ruangan_raw:
            temp = ruangan.split(';')
            temp[3] = temp[3].split(',')
            for i in range(len(temp[3])):
                temp[3][i] = int(temp[3][i])
            temp_ruangan = Ruangan(idruangan,temp[0], int(float(temp[1])), int(float(temp[2])), temp[3])
            idruangan += 1
            self.daftar_ruangan.append(temp_ruangan)

        idmatkul = 0
        for mata_kuliah in mata_kuliah_raw:
            temp = mata_kuliah.split(';')
            temp[5] = temp[5].split(',')
            for i in range(len(temp[5])):
                temp[5][i] = int(temp[5][i])
            temp_mata_kuliah = MatKul(idmatkul, temp[0], temp[1], int(float(temp[2])), int(float(temp[3])), int(temp[4]), temp[5])
            idmatkul += 1
            self.daftar_mata_kuliah.append(temp_mata_kuliah)

        n = len(self.daftar_mata_kuliah)
        temp_total = 0
        for i in range(0,n):
            self.total_pasangan += temp_total * self.daftar_mata_kuliah[i].sks
            temp_total += self.daftar_mata_kuliah[i].sks
        self.total_pasangan += 1

    @classmethod
    def read_file(self,ruangan_raw, mata_kuliah_raw, nama_file):
        f = open(nama_file, "r")
        mylist = f.read().splitlines()
        ruangan_loaded = False
        for line in mylist:
            if line == 'Ruangan' or line == '':
                pass
            elif line == 'Jadwal':
                ruangan_loaded = True
            elif not ruangan_loaded:
                ruangan_raw.append(line)
            else:
                mata_kuliah_raw.append(line)
        f.close()

    @classmethod
    def init_file(self,nama_file):
        ruangan_raw = []
        mata_kuliah_raw = []
        self.read_file(ruangan_raw, mata_kuliah_raw, nama_file)
        self.process_ruangan_dan_mata_kuliah(ruangan_raw, mata_kuliah_raw)

    @classmethod
    def __init__(self, nama_file):
        self.daftar_ruangan = []
        self.daftar_mata_kuliah = []
        self.init_file(nama_file)
