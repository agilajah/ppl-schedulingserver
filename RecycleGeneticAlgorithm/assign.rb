from .Jadwal import Jadwal
from .MatKulOnlyTime import MatKulOnlyTime
from .Matriks import Matriks
from copy import deepcopy

class Assign:
    daftar_matkul_time = []

@classmethod
def hitung_kosong(cls, ruang, jam_awal, jam_akhir):
    selisih = jam_akhir - jam_awal
hitung = 0
for i in range(selisih):
  if len(cls.matriks.matriks[ruang][jam_awal+i]) == 0:
      hitung += 1
  return hitung

  @classmethod
  def min_kosong(cls, daftar):
      minim = 0
  for i in range(len(daftar)):
    if daftar[i] < daftar[minim]:
        minim = i
    return minim

    @classmethod
    def cariruang(cls, matkul):
        daftar_temp = []
    daftar_kosong = []
    temp_matkul_time = MatKulOnlyTime(matkul.idmatkul)
    if matkul.ruangan != '-': # ruangan udah ditentuin
        # tambahin looping aja didepannya
        for ruangan in Jadwal.daftar_ruangan:
          if ruangan.nama != matkul.ruangan:
              continue
          idx = ruangan.idruangan
          ruang = Jadwal.daftar_ruangan[idx]
          for hari in matkul.hari:
            for haris in ruang.hari:
              if hari == haris:
                  if max(matkul.jam_awal, ruang.jam_awal) + matkul.sks <= min(matkul.jam_akhir, ruang.jam_akhir):
                      temp_matkul_time.setTime(idx, max(matkul.jam_awal, ruang.jam_awal), hari, matkul.sks)
                  kosong = cls.hitung_kosong(temp_matkul_time.r_selected, temp_matkul_time.j_selected, min(matkul.jam_akhir, ruang.jam_akhir))
                  kosong = kosong - matkul.sks
                  if kosong < 0:
                      kosong = abs(kosong) + 100
                  daftar_kosong.append(kosong)
                  temp_masukin = deepcopy(temp_matkul_time)
                  daftar_temp.append(temp_masukin)

                  else:
                      n = len(Jadwal.daftar_ruangan)
                  for idx in range(n):
                    ruang = Jadwal.daftar_ruangan[idx]
                    for hari in matkul.hari:
                      for haris in ruang.hari:
                        if hari == haris:
                            if max(matkul.jam_awal, ruang.jam_awal) + matkul.sks <= min(matkul.jam_akhir, ruang.jam_akhir):
                                temp_matkul_time.setTime(idx, max(matkul.jam_awal, ruang.jam_awal), hari, matkul.sks)
                            kosong = cls.hitung_kosong(temp_matkul_time.r_selected, temp_matkul_time.j_selected, min(matkul.jam_akhir, ruang.jam_akhir))
                            kosong = kosong - matkul.sks
                            if kosong < 0:
                                kosong = abs(kosong) + 100
                            daftar_kosong.append(kosong)
                            temp_masukin = deepcopy(temp_matkul_time)
                            daftar_temp.append(temp_masukin)
                            if(len(daftar_temp) == 0):
                                cls.daftar_remove.append(matkul)
                            else:
                                minim = cls.min_kosong(daftar_kosong)
                            temp_matkul_time_final = daftar_temp[minim]
                            cls.daftar_matkul_time.append(temp_matkul_time_final)

                            c = (temp_matkul_time_final.h_selected - 1) * 24 + temp_matkul_time_final.j_selected
                            for i in range(temp_matkul_time_final.sks):
                              tempmatkul = deepcopy(matkul)
                              cls.matriks.matriks[temp_matkul_time_final.r_selected][c+i].append(tempmatkul)

                              @classmethod
                              def __init__(cls):
                                  cls.daftar_remove = []
                              cls.matriks = Matriks(len(Jadwal.daftar_ruangan), 120)
                              cls.daftar_matkul_time = []
                              for matkul in Jadwal.daftar_mata_kuliah:
                                cls.cariruang(matkul)

                                for matkul in cls.daftar_remove:
                                  Jadwal.daftar_mata_kuliah.remove(matkul)

                                  cnt = 0
                                  for matkul in Jadwal.daftar_mata_kuliah:
                                    matkul.idmatkul = cnt
                                    cnt += 1