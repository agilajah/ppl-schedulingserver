from ..Base.MatKulOnlyTime import MatKulOnlyTime
from ..Base.Matriks import Matriks
from ..Base.Jadwal import Jadwal
from random import randint, shuffle, seed
from math import ceil, floor
from copy import deepcopy

class Genetic
  inputs = []
  result = []

  def __init__(self):
      if(Jadwal.total_pasangan == 0):
          n = len(Jadwal.daftar_mata_kuliah)
      temp_total = 0
      for i in range(n):
        Jadwal.total_pasangan += temp_total * Jadwal.daftar_mata_kuliah[i].sks
        temp_total += Jadwal.daftar_mata_kuliah[i].sks
        Jadwal.total_pasangan += 1

        @classmethod
        def convertToMatriks(self, chromosome):
            M = Matriks(len(Jadwal.daftar_ruangan), 120)
        idx = 0
        for mkot in chromosome:

          awal = (mkot.h_selected-1) * 24 + (mkot.j_selected)
          for i in range(awal, awal + mkot.sks):
            M.matriks[mkot.r_selected][i].append(Jadwal.daftar_mata_kuliah[idx].nama)
            idx += 1
            return M

            @classmethod
            def fitness(self, chromosome):
                M = self.convertToMatriks(chromosome)
            con = int(M.conflict_count())
            return Jadwal.total_pasangan - int(M.conflict_count())

            # mutate ini dilakukan abis chromosomenya digabungin
            @classmethod
            def random_assign(self, x):

                bisa = False
            MBaru = MatKulOnlyTime(x)
            COMB_PER_HARI = Jadwal.daftar_mata_kuliah[x].jam_akhir - Jadwal.daftar_mata_kuliah[x].jam_awal - Jadwal.daftar_mata_kuliah[x].sks + 1
            JUMLAH_HARI = len(Jadwal.daftar_mata_kuliah[x].hari)
            comb_waktu = COMB_PER_HARI * JUMLAH_HARI
            urut_waktu = []
            for i in range(comb_waktu):
              urut_waktu.append(i)

              shuffle(urut_waktu)
              if(Jadwal.daftar_mata_kuliah[x].ruangan == '-'):
                  urut_ruangan = []
              comb_ruangan = len(Jadwal.daftar_ruangan)

              for i in range(comb_ruangan):
                urut_ruangan.append(i)

                shuffle(urut_ruangan)
                for ruangan_selected in urut_ruangan:
                  if bisa:
                      break
                  for z in urut_waktu:
                    hari_selected = Jadwal.daftar_mata_kuliah[x].hari[floor(z / COMB_PER_HARI)]
                    jam_selected = Jadwal.daftar_mata_kuliah[x].jam_awal + (z % COMB_PER_HARI)
                    temp_ruangan = Jadwal.daftar_ruangan[ruangan_selected]
                    if(hari_selected in temp_ruangan.hari and jam_selected >= temp_ruangan.jam_awal and jam_selected + Jadwal.daftar_mata_kuliah[x].sks <= temp_ruangan.jam_akhir):
                        MBaru.setTime(ruangan_selected, jam_selected, hari_selected, Jadwal.daftar_mata_kuliah[x].sks)
                    break
                    else:

                        for idxruangan in range(len(Jadwal.daftar_ruangan)):
                          assigned = False
                          if(Jadwal.daftar_ruangan[idxruangan].nama == Jadwal.daftar_mata_kuliah[x].ruangan):
                              ruangan_selected = idxruangan
                          for z in urut_waktu:
                            hari_selected = Jadwal.daftar_mata_kuliah[x].hari[floor(z / COMB_PER_HARI)]
                            jam_selected = Jadwal.daftar_mata_kuliah[x].jam_awal + (z % COMB_PER_HARI)

                            temp_ruangan = Jadwal.daftar_ruangan[ruangan_selected]
                            if(hari_selected in temp_ruangan.hari and jam_selected >= temp_ruangan.jam_awal and jam_selected + Jadwal.daftar_mata_kuliah[x].sks <= temp_ruangan.jam_akhir):
                                MBaru.setTime(ruangan_selected, jam_selected, hari_selected, Jadwal.daftar_mata_kuliah[x].sks)
                            break
                            if assigned:
                                break
                            return MBaru

                            @classmethod
                            def mutate(self, chromosome):
                                panjang = len(chromosome)
                            bnyk = int(ceil(panjang / 20))
                            for i in range(bnyk):
                              x = randint(0, panjang - 1)
                              chromosome[x] = self.random_assign(x)

                              @classmethod
                              def selectidx(self, n, fitness_total, r_num):
                                  now = 0
                              idx = 0
                              for i in range(n):
                                now += fitness_total[i]
                                if(now > r_num):
                                    break
                                idx += 1
                                return idx

                                @classmethod
                                def run(self, loops):
                                    for xxx in range(loops):
                                      print (xxx)
                                      fitness_total = []
                                      n = len(self.inputs)

                                      # calculate total fitness
                                      for chromosome in self.inputs:
                                        fitness_total.append(self.fitness(chromosome))

                                        # sort based on fitness_total
                                        for i in range(n):
                                          for j in range(n-i-1):
                                            if (fitness_total[j] > fitness_total[j+1]):
                                                fitness_total[j], fitness_total[j+1] = fitness_total[j+1], fitness_total[j]
                                            self.inputs[j], self.inputs[j+1] = self.inputs[j+1], self.inputs[j]

                                            pivot = randint(1, len(Jadwal.daftar_mata_kuliah))

                                            # calculate the total chance
                                            total_chance = 0
                                            for i in range(n):
                                              total_chance += fitness_total[i]

                                              self.result = []
                                              for i in range(n):
                                                x = self.inputs[self.selectidx(n, fitness_total, randint(0, total_chance-1))][:pivot]
                                                y = self.inputs[self.selectidx(n, fitness_total, randint(0, total_chance-1))][pivot:]
                                                child = x
                                                child.extend(y)
                                                if(n > randint(1, n*n)):
                                                    self.mutate(child)

                                                self.result.append(child)
                                                self.sort()
                                                self.result = deepcopy(self.result[91:])
                                                self.result.extend(self.inputs)
                                                self.sort()
                                                self.inputs = deepcopy(self.result[10:])

                                                @classmethod
                                                def init(self):
                                                    seed()
                                                self.inputs = []
                                                self.result = []
                                                banyak = 100
                                                n = len(Jadwal.daftar_mata_kuliah)
                                                for i in range(banyak):
                                                  self.inputs.append([])
                                                  for x in range(n):
                                                    self.inputs[i].append(self.random_assign(x))

                                                    @classmethod
                                                    def add(self, jadwal):
                                                        self.inputs.append(jadwal)

                                                    @classmethod
                                                    def best(self):
                                                        return self.result[-1]

                                                    @classmethod
                                                    def sort(self):
                                                        fitness_total = []
                                                    n = len(self.result)

                                                    for chromosome in self.result:
                                                      fitness_total.append(self.fitness(chromosome))

                                                      for i in range(n):
                                                        for j in range(n-i-1):
                                                          if (fitness_total[j] > fitness_total[j+1]):
                                                              fitness_total[j], fitness_total[j+1] = fitness_total[j+1], fitness_total[j]
                                                          self.result[j], self.result[j+1] = self.result[j+1], self.result[j]`