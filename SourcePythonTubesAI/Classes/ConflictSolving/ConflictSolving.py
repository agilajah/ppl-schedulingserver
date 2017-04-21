# Draft conflict solving in climbing

# STEP 1 - Take MatkulOnlyTime data (list) of Course
	# convert to index by formula (dari daftar_matkul_time)

# STEP 2 - Conflict checking & solving
	# > read Course (repeat from first to last) from Jadwal.py
	# > check conflict status from form.py
		# if no, read next Course
		# if yes, read Course constraint
		# then move that Course from first to the last of constraint
			# if empty space found, move Course to that space
				# change index information in Deepcopy-ed index data
			# if another Course found, find another space
			# if no empty space found, end looping
			# end of loop = move to next Course
from ..Base.Jadwal import Jadwal
import copy
import random
from random import randint, seed

class ConflictSolving:

	@classmethod
	def search_ruang_constraint(cls, code, idx_ruang, day_selected):
		room = Jadwal.daftar_ruangan[idx_ruang]
		ans = (room.hari[day_selected] - 1) * 24
		if code == 0:
			ans += room.jam_awal  # constraint jam awal
		else:
			ans += room.jam_akhir # constraint jam akhir
		return ans

	@classmethod
	def check_matkul_constraint(cls, matkul_selected, r_selected, w_selected):

		banyak_hari = len(matkul_selected.hari)
		for idx_hari in range(banyak_hari):

			# Check idx x (start and end), fulfill the constraint or not
			# If selected slot x fulfill the constraint, continue the check.
			# If not, end the looping, move check next matkul (conflicted or not)
			batas_waktu_awal = (matkul_selected.hari[idx_hari] - 1) * 24 + matkul_selected.jam_awal
			batas_waktu_akhir = batas_waktu_awal + matkul_selected.jam_akhir - matkul_selected.jam_awal #tambah sks
			if (w_selected >= batas_waktu_awal and w_selected + matkul_selected.sks <= batas_waktu_akhir and (matkul_selected.ruangan == '-' or Jadwal.daftar_ruangan[r_selected].nama == matkul_selected.ruangan)):
				return True

			# assumption : len(matkul_selected.ruangan) == 1

			# assumption : len(matkul_selected.ruangan) > 1
#			for idx_hari in range(len(matkul_selected.ruangan)):
#				if (y == matkul_selected.ruangan[idx_hari]):
#					return 1
#					break
		return False

	@classmethod
	def moveMatkul(cls, matrix, list_idx, idx_matkul, ruang_awal, waktu_awal, ruang_akhir, waktu_akhir):
		SKS = Jadwal.daftar_mata_kuliah[idx_matkul].sks
		# delete matkul dari yang lama
		for idx_waktu in range(waktu_awal, waktu_awal + SKS):
			banyak_matkul_di_slot = len(matrix.matriks[ruang_awal][idx_waktu])
			for j in range(banyak_matkul_di_slot):
				if matrix.matriks[ruang_awal][idx_waktu][j].idmatkul == idx_matkul:
					del matrix.matriks[ruang_awal][idx_waktu][j]
					break

		# insert matkul ke yang baru
		for idx_waktu in range(waktu_akhir, waktu_akhir + SKS):
			kuliah = copy.deepcopy(Jadwal.daftar_mata_kuliah[idx_matkul])
			matrix.matriks[ruang_akhir][idx_waktu].append(kuliah)

		# masukin ke list_idx
		list_idx[idx_matkul] = (ruang_akhir, waktu_akhir)

	@classmethod
	def climbing(cls, matrix, list_idx):
		# MAIN ALGORITHM
		# STEP 2 - Conflict checking & solving
		# cek muter
		roundtrip = 0
		found = False
		minconf = -1000000000
		idx_matkul_selected = -1
		ruang_awal_selected = -1
		waktu_awal_selected = -1
		idx_room_selected = -1
		idx_waktu_start_selected = -1
		while (roundtrip != 2 and (not found)):
			for idx_matkul in range(len(list_idx)):
				ruang_awal, waktu_awal = list_idx[idx_matkul] # extract the tuple
				if (len(matrix.matriks[ruang_awal][waktu_awal]) > 1):

					list_temp = matrix.matriks[ruang_awal][waktu_awal]
					# nyari matkul yang mau diubah
					conflicted_matkul = None
					for i in range(len(list_temp)):
						if list_temp[i].idmatkul == idx_matkul:
							conflicted_matkul = copy.deepcopy(Jadwal.daftar_mata_kuliah[idx_matkul])
					# nyari ruangan yang bisa diubah
					first_conflict = 0
					for i in range(waktu_awal, waktu_awal + conflicted_matkul.sks):
						panjang = len(matrix.matriks[ruang_awal][i])
						first_conflict += (panjang * (panjang-1)) // 2

					nRoom = len(Jadwal.daftar_ruangan)
					for idx_room in range(nRoom):
						# Constraint slot waktu di matrix sesuai constraint ruangan
						nDay = len(Jadwal.daftar_ruangan[idx_room].hari)
						for idx_day in range(nDay):
							# convert ke jam basis 120
							jam_converted_start = cls.search_ruang_constraint(0, idx_room, idx_day)
							jam_converted_end 	= cls.search_ruang_constraint(1, idx_room, idx_day) - Jadwal.daftar_mata_kuliah[idx_matkul].sks + 1

							# ini kan available ruangannya
							# looping terhadap jam yang available, basis 120
							for idx_waktu_start in range(jam_converted_start, jam_converted_end):
								# ngecek apakah dia udah diisi atau yang dia pilih itu pernah dipilih sebelumnya
								if (idx_room == ruang_awal and idx_waktu_start == waktu_awal):
									continue
								else:
									# Check if the slot time match with matkul constraint
									matkulsama = False
									SKS = Jadwal.daftar_mata_kuliah[idx_matkul].sks
									totalconflict = 0
									for i in range(idx_waktu_start, idx_waktu_start + SKS):
										panjang = len(matrix.matriks[idx_room][i])
										for j in range(panjang):
											if(matrix.matriks[idx_room][i][j].nama == conflicted_matkul.nama and matrix.matriks[idx_room][i][j].idmatkul !=  conflicted_matkul.idmatkul):
												matkulsama = True
												break
										if matkulsama:
											break
										totalconflict += (panjang * (panjang+1)) // 2

									if matkulsama:
										continue

									time_and_space_matchs = cls.check_matkul_constraint(conflicted_matkul, idx_room, idx_waktu_start)
									if (time_and_space_matchs): # Found the slot
										if(minconf < first_conflict - totalconflict):
											minconf = first_conflict - totalconflict
											idx_matkul_selected = idx_matkul
											ruang_awal_selected = ruang_awal
											waktu_awal_selected = waktu_awal
											idx_room_selected = idx_room
											idx_waktu_start_selected = idx_waktu_start
								if found:
									break
							if found:
								break
						if found:
							break
					if found:
						break
			if not found:
				roundtrip += 1

		if (minconf != -1000000000):
			cls.moveMatkul(matrix, list_idx, idx_matkul_selected, ruang_awal_selected, waktu_awal_selected, idx_room_selected, idx_waktu_start_selected)

	@classmethod
	def climbingrandom(cls, matrix, list_idx):
		# MAIN ALGORITHM
		# Using random to choose which slot will system try to place the conflicted_matkul
		roundtrip = 0
		found = False
		minconf = -1000000000
		idx_matkul_selected = -1
		ruang_awal_selected = -1
		waktu_awal_selected = -1
		idx_room_selected = -1
		idx_waktu_start_selected = -1
		while (roundtrip != 2 and (not found)):
			nmatkul = list(range(len(list_idx)))
			random.shuffle(nmatkul)
			for idx_matkul in nmatkul:
				ruang_awal, waktu_awal = list_idx[idx_matkul] # extract the tuple
				if (len(matrix.matriks[ruang_awal][waktu_awal]) > 1):
					list_temp = matrix.matriks[ruang_awal][waktu_awal]
					# nyari matkul yang mau diubah
					conflicted_matkul = None
					for i in range(len(list_temp)):
						if list_temp[i].idmatkul == idx_matkul:
							conflicted_matkul = copy.deepcopy(Jadwal.daftar_mata_kuliah[idx_matkul])

					first_conflict = 0
					for i in range(waktu_awal, waktu_awal + conflicted_matkul.sks):
						panjang = len(matrix.matriks[ruang_awal][i])
						first_conflict += (panjang * (panjang-1)) // 2
					# nyari ruangan yang bisa diubah
					# Randomize idx_room
					nRoom = list(range(len(Jadwal.daftar_ruangan)))
					random.shuffle(nRoom)
					for idx_room in nRoom:
						# Constraint slot waktu di matrix sesuai constraint ruangan
						nDay = list(range(len(Jadwal.daftar_ruangan[idx_room].hari)))
						random.shuffle(nDay)
						for idx_day in nDay:
							# convert ke jam basis 120
							jam_converted_start = cls.search_ruang_constraint(0, idx_room, idx_day)
							jam_converted_end 	= cls.search_ruang_constraint(1, idx_room, idx_day) - Jadwal.daftar_mata_kuliah[idx_matkul].sks + 1

							# ini kan available ruangannya
							# looping terhadap jam yang available, basis 120
							# Randomize idx_waktu_start
							jam_converted_diff = list(range(jam_converted_start, jam_converted_end))
							random.shuffle(jam_converted_diff)
							for idx_waktu_start in jam_converted_diff:
								# ngecek apakah dia udah diisi atau yang dia pilih itu pernah dipilih sebelumnya
								if (idx_room == ruang_awal and idx_waktu_start == waktu_awal):
									continue
								else:
									# Check if the slot time match with matkul constraint
									matkulsama = False
									SKS = Jadwal.daftar_mata_kuliah[idx_matkul].sks
									totalconflict = 0
									for i in range(idx_waktu_start, idx_waktu_start + SKS):
										panjang = len(matrix.matriks[idx_room][i])
										for j in range(panjang):
											if(matrix.matriks[idx_room][i][j].nama == conflicted_matkul.nama and matrix.matriks[idx_room][i][j].idmatkul !=  conflicted_matkul.idmatkul):
												matkulsama = True
												break
										if matkulsama:
											break
										totalconflict += (panjang * (panjang+1)) // 2

									if matkulsama:
										continue
									time_and_space_matchs = cls.check_matkul_constraint(conflicted_matkul, idx_room, idx_waktu_start)
									if (time_and_space_matchs): # Found the slot
										if(minconf < first_conflict - totalconflict):
											minconf = first_conflict - totalconflict
											idx_matkul_selected = idx_matkul
											ruang_awal_selected = ruang_awal
											waktu_awal_selected = waktu_awal
											idx_room_selected = idx_room
											idx_waktu_start_selected = idx_waktu_start
								if found:
									break
							if found:
								break
						if found:
							break
					if found:
						break
			if not found:
				roundtrip += 1

		if (minconf != -1000000000):
			cls.moveMatkul(matrix, list_idx, idx_matkul_selected, ruang_awal_selected, waktu_awal_selected, idx_room_selected, idx_waktu_start_selected)

	@classmethod
	def __init__(cls):
		seed()
