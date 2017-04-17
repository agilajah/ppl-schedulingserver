import math
import random
from ..Base.Jadwal import Jadwal
from ..Base.Matriks import Matriks
from ..Base.Assign import Assign
from ..ConflictSolving.ConflictSolving import ConflictSolving
from copy import deepcopy
class SimulatedAnnealing:

	# Acceptance function, energy represent conflict_count
	@classmethod
	def acceptance_function(cls, current_energy, new_energy, temperature):
		if (new_energy <= current_energy):
			return 1
		else:
			return math.exp((current_energy - new_energy) / temperature)

	@classmethod
	def calculate_not_random(cls, matrix_not_random_cur, list_idx_not_random_cur):
		temperature = cls.temperature
		cooling_rate = cls.cooling_rate
		least_conflict = cls.least_conflict

		while temperature >= 1 and least_conflict > 0:
			print (str(temperature) + ' ' + str(least_conflict))
			# Create new Matriks for swapping & conflict_count comparison
			new_solution = deepcopy(matrix_not_random_cur)
			list_idx = deepcopy(list_idx_not_random_cur)

			ConflictSolving.climbing(new_solution, list_idx)
			new_conflict = new_solution.conflict_count()
			# Decide & keep best solution
			if (cls.acceptance_function(least_conflict, new_conflict, temperature) >= random.randrange(0, 1)):
				matrix_not_random_cur = new_solution
				least_conflict = new_conflict
				list_idx_not_random_cur = deepcopy(list_idx)

			# Cooling
			temperature *= (1 - cooling_rate)

		return matrix_not_random_cur

	@classmethod
	def calculate_random(cls, matrix_random_cur, list_idx_random_cur):
		temperature = cls.temperature
		cooling_rate = cls.cooling_rate
		least_conflict = cls.least_conflict

		while temperature >= 1 and least_conflict > 0:
			print (str(temperature) + ' ' + str(least_conflict))
			# Create new Matriks for swapping & conflict_count comparison
			new_solution = deepcopy(matrix_random_cur)
			list_idx = deepcopy(list_idx_random_cur)

			ConflictSolving.climbing(new_solution, list_idx)
			new_conflict = new_solution.conflict_count()
			# Decide & keep best solution
			if (cls.acceptance_function(least_conflict, new_conflict, temperature) >= random.randrange(0, 1)):
				matrix_random_cur = new_solution
				least_conflict = new_conflict
				list_idx_random_cur = deepcopy(list_idx)

			# Cooling
			temperature *= (1 - cooling_rate)

		return matrix_random_cur

	@classmethod
	def calculate(cls):

		matrix_not_random_cur = deepcopy(cls.current_solution)
		list_idx_not_random_cur = deepcopy(cls.current_list_idx)

		matrix_random_cur = deepcopy(cls.current_solution)
		list_idx_random_cur = deepcopy(cls.current_list_idx)

		matrix_not_random_cur = cls.calculate_not_random(matrix_not_random_cur, list_idx_not_random_cur)
		matrix_random_cur = cls.calculate_random(matrix_random_cur, list_idx_random_cur)

		curr_conflict_not_random = matrix_not_random_cur.conflict_count()
		curr_conflict_random = matrix_random_cur.conflict_count()

		if curr_conflict_not_random < curr_conflict_random:
			cls.current_solution = matrix_not_random_cur
			cls.least_conflict = curr_conflict_not_random
		else:
			cls.current_solution = matrix_random_cur
			cls.least_conflict = curr_conflict_random

	@classmethod
	def insert_jadwal_into_matriks(cls):
		cls.current_solution = Matriks(len(Jadwal.daftar_ruangan), 120)
		nMatKul = len(Jadwal.daftar_mata_kuliah)
		for i in range(nMatKul):
			ruang = Assign.daftar_matkul_time[i].r_selected
			waktu = (Assign.daftar_matkul_time[i].h_selected - 1) * 24 + Assign.daftar_matkul_time[i].j_selected
			kuliah = deepcopy(Jadwal.daftar_mata_kuliah[i]) # biar bikin object baru
			SKS = Assign.daftar_matkul_time[i].sks
			for j in range(waktu, waktu + SKS):
				cls.current_solution.matriks[ruang][j].append(kuliah)

		# copy yang pertama banget
		cls.least_conflict = cls.current_solution.conflict_count()

	@classmethod
	def first_initiate(cls):
		# STEP 1 - Take MatkulOnlyTime data (list) of Course
		# convert to index by formula (dari Jadwal.daftar_matkul_time)
		cls.current_list_idx = []
		nMatKul = len(Jadwal.daftar_mata_kuliah)
		for i in range(nMatKul):
			ruang = Assign.daftar_matkul_time[i].r_selected
			waktu = (Assign.daftar_matkul_time[i].h_selected - 1) * 24 + Assign.daftar_matkul_time[i].j_selected
			temp = (ruang, waktu)
			cls.current_list_idx.append(temp)

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
				for matkul in cls.current_solution.matriks[idx_room][idx_waktu]:
					cls.matrix_hasil.matriks[idx_room][idx_waktu].append(deepcopy(matkul.nama))

	@classmethod
	def __init__(cls):
		# Initiate temperature & cooling rate
		cls.temperature = 1000
		cls.cooling_rate = 0.03
		cls.list_idx_cur = []
		# Initiate Matriks - complete assignment
		cls.current_solution = Matriks(len(Jadwal.daftar_ruangan), 120)
		cls.least_conflict = cls.current_solution.conflict_count()
