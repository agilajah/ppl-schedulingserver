import copy
from random import randint, seed
from ..Base.Matriks import Matriks
from ..Base.Jadwal import Jadwal
from ..Base.Assign import Assign
from ..ConflictSolving.ConflictSolving import ConflictSolving

class HillClimbing:

	@classmethod
	def calculate_not_random(cls, matrix_nrb, list_idx_nrb):
		curr_conflict_not_random = cls.curr_conflict
		cnt = 0
		while cnt < 10:
			print (curr_conflict_not_random)
			matrix = copy.deepcopy(matrix_nrb)
			list_idx = copy.deepcopy(list_idx_nrb)

			# climbing method
			ConflictSolving.climbing(matrix, list_idx)

			# Count conflict of new solution, if cnt reaches 10 then it terminates
			next_conflict = matrix.conflict_count()
			if (next_conflict >= curr_conflict_not_random):
				cnt += 1
			else:
				cnt = 0
				curr_conflict_not_random = next_conflict
				matrix_nrb = copy.deepcopy(matrix)
				list_idx_nrb = copy.deepcopy(list_idx)

		return matrix_nrb

	@classmethod
	def calculate_random(cls, matrix_random_best, list_idx_random_best):
		curr_conflict_random = cls.curr_conflict
		cnt = 0
		while cnt < 10:
			print (curr_conflict_random)
			matrix = copy.deepcopy(matrix_random_best)
			list_idx = copy.deepcopy(list_idx_random_best)

			# climbing method
			ConflictSolving.climbingrandom(matrix, list_idx)

			# Count conflict of new solution, if cnt reaches 10 then it terminates
			next_conflict = matrix.conflict_count()
			if (next_conflict >= curr_conflict_random):
				cnt += 1
			else:
				cnt = 0
				curr_conflict_random = next_conflict
				matrix_random_best = copy.deepcopy(matrix)
				list_idx_random_best = copy.deepcopy(list_idx)

		return matrix_random_best

	@classmethod
	def calculate(cls):
		matrix_nrb = copy.deepcopy(cls.matrix_best)
		list_idx_nrb = copy.deepcopy(cls.list_idx_best)

		matrix_rb = copy.deepcopy(cls.matrix_best)
		list_idx_rb = copy.deepcopy(cls.list_idx_best)

		matrix_nrb = cls.calculate_not_random(matrix_nrb, list_idx_nrb)
		matrix_rb = cls.calculate_random(matrix_rb, list_idx_rb)

		curr_conflict_not_random = matrix_nrb.conflict_count()
		curr_conflict_random = matrix_rb.conflict_count()

		if(curr_conflict_not_random < curr_conflict_random):
			cls.curr_conflict = curr_conflict_not_random
			cls.matrix_best = matrix_nrb
		else:
			cls.curr_conflict = curr_conflict_random
			cls.matrix_best = matrix_rb

	@classmethod
	def insert_jadwal_into_matriks(cls):
		cls.matrix_best = Matriks(len(Jadwal.daftar_ruangan), 120)
		nMatKul = len(Jadwal.daftar_mata_kuliah)
		for i in range(nMatKul):
			ruang = Assign.daftar_matkul_time[i].r_selected
			waktu = (Assign.daftar_matkul_time[i].h_selected - 1) * 24 + Assign.daftar_matkul_time[i].j_selected
			kuliah = copy.deepcopy(Jadwal.daftar_mata_kuliah[i]) # biar bikin object baru
			SKS = Assign.daftar_matkul_time[i].sks
			for j in range(waktu, waktu + SKS):
				cls.matrix_best.matriks[ruang][j].append(kuliah)
		# copy yang pertama banget

		cls.curr_conflict = cls.matrix_best.conflict_count()

	@classmethod
	def first_initiate(cls):
		# STEP 1 - Take MatkulOnlyTime data (list) of Course
		# convert to index by formula (dari Jadwal.daftar_matkul_time)

		cls.list_idx_best = []
		nMatKul = len(Jadwal.daftar_mata_kuliah)

		for i in range(nMatKul):
			ruang = Assign.daftar_matkul_time[i].r_selected
			waktu = (Assign.daftar_matkul_time[i].h_selected - 1) * 24 + Assign.daftar_matkul_time[i].j_selected
			temp = (ruang, waktu)
			cls.list_idx_best.append(temp)

	@classmethod
	def init(cls):
		cls.first_initiate()
		cls.insert_jadwal_into_matriks()

	@classmethod
	def finishing(cls):
		cls.matrix_hasil = Matriks(len(Jadwal.daftar_ruangan), 120)
		nRoom = len(Jadwal.daftar_ruangan)
		for idx_room in range(nRoom):
			for idx_waktu in range(120):
				for matkul in cls.matrix_best.matriks[idx_room][idx_waktu]:
					cls.matrix_hasil.matriks[idx_room][idx_waktu].append(copy.deepcopy(matkul.nama))
	@classmethod
	def __init__(cls):
		seed()
		cls.matrix_best = Matriks(len(Jadwal.daftar_ruangan), 120) # bedanya ini cuma nyimpen nama matkulnya doang
		cls.curr_conflict = 0
		cls.list_idx_best = []


# catetan :
# urutan milih didalemnya belum random
