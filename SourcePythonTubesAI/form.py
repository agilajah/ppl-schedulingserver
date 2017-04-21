import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
from Classes.Base.Jadwal import Jadwal
from Classes.Genetic.Genetic import Genetic
from Classes.SimulatedAnnealing.SimulatedAnnealing import SimulatedAnnealing
from Classes.HillClimbing.HillClimbing import HillClimbing
from Classes.Base.Assign import Assign

from math import floor

Days = ('Senin','Selasa','Rabu','Kamis','Jumat')
class form(Frame):

	def __init__(self, parent):
		Frame.__init__(self,parent)
		self.parent = parent
		self.parent.title('AI berDARAH')
		self.nRoom = 0
		self.nSchedule = 0
		self.rooms = []
		self.schedules = []
		self.mulai()
		self.jadwal = []
		self.numberofConflicts = 0


	def mulai(self):
		self.grid()
		#self.resizable(False,False)

		#frame ruangan
		frRuang = ttk.Frame(self.parent, borderwidth= 2, relief = "solid")
		frRuang.grid(column=0, row=0,sticky="NWES", padx=(10,10), pady=(10,10))
		#frRuang.columnconfigure(0, weight=1)
		#frRuang.rowconfigure(0, weight=1)

		labelRuangan = tkinter.Label(frRuang, text=u"Ruangan", anchor="w")
		labelRuangan.grid(column=0, row=0, pady=(0,10))

		self.entryRuangVariable = tkinter.StringVar()
		self.entryRuang = tkinter.Entry(frRuang, textvariable=self.entryRuangVariable, width = 20)
		self.entryRuang.grid(column=1, row=0,padx=(10,0),columnspan=6, sticky="w")
		self.entryRuang.focus_set()
		#entryRuangVariable.set(u"Masukan nama ruangan"

		labelHari = tkinter.Label(frRuang, text=u"Hari", anchor="w")
		labelHari.grid(column=0, row=1, sticky="W")

		self.checkR = []
		self.RDay = []
		i=0
		for d in Days:
			self.checkR.append(tkinter.IntVar())
			self.RDay.append(tkinter.Checkbutton(frRuang,text=d,variable=self.checkR[i],onvalue=1, offvalue=0))
			self.RDay[i].grid(column=1, row=i+1,sticky="w")
			i+=1

		labelJam = tkinter.Label(frRuang, text=u"Jam", anchor="w")
		labelJam.grid(column=2, row = 1, sticky ="w", padx=(30,0))

		self.entryJamMulaiVar = tkinter.IntVar()
		self.entryJamMulai = tkinter.Spinbox(frRuang, textvariable=self.entryJamMulaiVar, from_=0, to=22, width = 3, justify="right")
		self.entryJamMulai.grid(column=3, row=1, sticky="w")
		label00 = tkinter.Label(frRuang, text=": 00 -", anchor="w")
		label00.grid(column=4, row=1, sticky = "w")

		self.entryJamSelesaiVar = tkinter.IntVar()
		self.entryJamSelesai = tkinter.Spinbox(frRuang, textvariable=self.entryJamSelesaiVar, from_=1, to=23, width = 3, justify="right")
		self.entryJamSelesai.grid(column=5, row=1, sticky="w")
		label00_ = tkinter.Label(frRuang, text=": 00", anchor="w")
		label00_.grid(column=6, row=1, sticky = "w")

		self.entryJamMulaiVar.set(7)
		self.entryJamSelesaiVar.set(8)

		buttonRuangan = tkinter.Button(frRuang,text=u"Submit Ruangan",command=self.validateRuang)
		buttonRuangan.grid(column=0, row=9, columnspan=9, padx=(10,10), pady=(10,0), sticky="s")

		labelHapusR = tkinter.Label(frRuang, text=u"Hapus Ruangan").grid(column=0, row=10, columnspan=2, pady=(20,0),sticky="e")
		self.delRuang=tkinter.StringVar()
		self.delRuang.set("0")
		self.delRuangBox = tkinter.Entry(frRuang, textvariable=self.delRuang, width=3, justify="right").grid(column=2, row=10, sticky="e",pady=(20,0))
		buttonHapusR = tkinter.Button(frRuang, text=u"Hapus",command=self.onClickDeleteRuang).grid(column=3,row=10,padx=(5,0),pady=(20,0),columnspan=4)

		frJadwal = ttk.Frame(self.parent, borderwidth=2, relief="solid")
		frJadwal.grid(column=1, row=0, sticky="NESW", padx=(10,10),pady=(10,10))
		#frJadwal.columnconfigure(0, weight=1)
		#frJadwal.rowconfigure(0,weight=1)

		labelJadwal = tkinter.Label(frJadwal, text=u"Mata Kuliah", anchor="w")
		labelJadwal.grid(column=0,row=0, sticky="nw")

		self.entryScheduleVar = tkinter.StringVar()
		self.entrySchedule = tkinter.Entry(frJadwal, textvariable=self.entryScheduleVar, width = 20)
		self.entrySchedule.grid(column=1, row=0, sticky="nw", columnspan=3)

		labelJadwal = tkinter.Label(frJadwal, text=u"       SKS", anchor="w")
		labelJadwal.grid(column=3,row=0, sticky="ne",columnspan=2)
		self.sks = tkinter.IntVar()
		self.entrySKS = tkinter.Spinbox(frJadwal,textvariable=self.sks, width=3,justify="right", from_=2, to=4)
		self.entrySKS.grid(column=5, row=0, sticky="nw")
		self.sks.set(2)

		labelRoom = tkinter.Label(frJadwal, text=u"Ruangan", anchor="w")
		labelRoom.grid(column=0,row=1, sticky="nw")

		self.roomFree = tkinter.IntVar()
		self.radioBebas = tkinter.Radiobutton(frJadwal, text = "Bebas", variable=self.roomFree, value = 0, command=self.selectingRuang)
		self.radioBebas.grid(column=1, row=1, sticky="nw")
		self.roomFree.set(0)
		self.radioSpec = tkinter.Radiobutton(frJadwal, text="Spesifik", variable=self.roomFree, value = 1, command=self.selectingRuang)
		self.radioSpec.grid(column=1, row=2, sticky="nw")
		self.entryRoomVar = tkinter.StringVar()
		self.entryRoom = tkinter.Entry(frJadwal, textvariable=self.entryRoomVar, width = 20, state="disabled")
		self.entryRoom.grid(column=2, row=2, sticky="nw",columnspan=3)

		labelHariJ = tkinter.Label(frJadwal, text=u"Hari", anchor="w")
		labelHariJ.grid(column=0, row=3, sticky="W")

		self.checkS = []
		self.SDay = []
		i = 0
		for d in Days:
			self.checkS.append(tkinter.IntVar())
			self.SDay.append(tkinter.Checkbutton(frJadwal,text=d,variable=self.checkS[i],onvalue=1, offvalue=0))
			self.SDay[i].grid(column=1, row=i+3,sticky="w")
			i += 1

		labelJamJ = tkinter.Label(frJadwal, text=u"Jam", anchor="w")
		labelJamJ.grid(column=2, row = 3, sticky ="w", padx=(30,0))

		self.entryJamMulaiJVar = tkinter.IntVar()
		self.entryJamMulaiJ = tkinter.Spinbox(frJadwal, textvariable=self.entryJamMulaiJVar, from_=0, to=22, width = 3, justify="right")
		self.entryJamMulaiJ.grid(column=3, row=3, sticky="w")
		label00J = tkinter.Label(frJadwal, text=": 00 -", anchor="w")
		label00J.grid(column=4, row=3, sticky = "w")

		self.entryJamSelesaiJVar = tkinter.IntVar()
		self.entryJamSelesaiJ = tkinter.Spinbox(frJadwal, textvariable=self.entryJamSelesaiJVar, width = 3, from_=1, to=23, justify="right")
		self.entryJamSelesaiJ.grid(column=5, row=3, sticky="w")
		label00J_ = tkinter.Label(frJadwal, text=": 00", anchor="w")
		label00J_.grid(column=6, row=3, sticky = "w")

		self.entryJamMulaiJVar.set(7)
		self.entryJamSelesaiJVar.set(8)

		buttonJadwal = tkinter.Button(frJadwal,text=u"Submit Jadwal", command=self.validateJadwal)
		buttonJadwal.grid(column=0, row=9, columnspan=9, padx=(10,10), pady=(10,0), sticky="s")

		labelHapusJ = tkinter.Label(frJadwal, text=u"Hapus Jadwal").grid(column=0, row=10, columnspan=2, pady=(20,0),sticky="e")
		self.delJadwal=tkinter.StringVar()
		self.delJadwal.set("0")
		self.delJadwalBox = tkinter.Entry(frJadwal, textvariable=self.delJadwal, width=3, justify="right").grid(column=2, row=10, sticky="e",pady=(20,0))

		buttonHapusR = tkinter.Button(frJadwal, text=u"Hapus", command=self.onClickDeleteJadwal).grid(column=3,row=10,padx=(5,0),pady=(20,0),columnspan=4)


		labelPilihSolusi = tkinter.Label(self.parent,text=u"=======================PILIH SOLUSINYA=======================")
		labelPilihSolusi.grid(row=2,pady=(5,0), sticky=N+E+S+W, columnspan=3)
		printHC = tkinter.Button(self.parent, text=u"Hill Climbing", command=self.runHillClimbing).grid(column=0, row=3, pady=(5,10))
		printGA = tkinter.Button(self.parent, text=u"Genetic Algorithm", command = self.runGenetic).grid(column=1, row=3,pady=(5,10))
		printRes = tkinter.Button(self.parent, text=u"Simulated Annealing", command=self.runSimulatedAnnealing).grid(column=0, row=3, pady=(5,10), columnspan=2)
		labelFrame = tkinter.Label(self.parent, text=u"==========================================================").grid(row=4, columnspan=2)

		self.entryFileVar = tkinter.StringVar()
		self.entryFile = tkinter.Entry(self.parent, textvariable=self.entryFileVar, width=100).grid(column=0, row=5, columnspan=2, pady=(30,0))
		path = os.path.abspath('Testcase_1.txt')
		self.entryFileVar.set(path)
		buttonBrowse = tkinter.Button (self.parent, text=u"Telusuri", command=self.loadBerkas).grid(column=0, row=6, columnspan=2)
		buttonRead = tkinter.Button(self.parent, text=u"Baca", command=self.bacaRuang).grid(column=0,row=7, columnspan=2)

		printR = tkinter.Button(self.parent, text=u"Cetak Ruangan", command=self.onClickPrintRoom)
		printR.grid(column=0, row=1,pady=(10,20))
		printJ = tkinter.Button(self.parent, text=u"Cetak Jadwal", command=self.onClickPrintSchedule)
		printJ.grid(column=1, row=1, pady=(10,20))

	def loadBerkas(self):
		self.fname = filedialog.askopenfilename(title="Pilih Berkas")

		if self.fname:
			try:
				self.entryFileVar.set(os.path.abspath(self.fname))
			except:
				messagebox.showerror("Kesalahan", "Terdapat kesalahan dalam membaca berkas")
			return

	def selectingRuang(self):
		if(self.roomFree.get() == 0):
			self.entryRoom.config(state="disabled")
		elif(self.roomFree.get()==1):
			self.entryRoom.config(state="normal")


	def validateRuang(self):
		self.entryRuang.focus_set()
		if(self.entryRuangVariable.get()==''):
			msg = messagebox.showerror("Kesalahan", "Ruangan harus diisi")
			self.entryRuang.focus_set()
		elif(self.entryJamMulaiVar.get()>=self.entryJamSelesaiVar.get()):
			msg = messagebox.showerror("Kesalahan", "Jam mulai harus lebih awal daripada jam selesai")
			self.entryJamMulai.focus_set()
			self.entryJamMulai.selection_range(0,tkinter.END)
		else:
			self.onClickRoom()

	def validateJadwal(self):
		liatJadwal = []
		for i in range(5):
			liatJadwal.append(self.checkS[i].get())

		if(self.entryScheduleVar.get()==''):
			msg = messagebox.showerror("Kesalahan", "Kode mata kuliah harus diisi")
			self.entrySchedule.focus_set()
			self.entrySchedule.selection_range(0,tkinter.END)
		elif(self.sks.get()<=0):
			msg = messagebox.showerror("Kesalahan", "SKS harus lebih dari 0")
			self.entrySKS.focus_set()
			self.entrySKS.selection_range(0,tkinter.END)
		elif(self.roomFree.get()==1 and self.entryRoomVar.get()==''):
			msg = messagebox.showerror("Kesalahan", "Ruangan spesifik tidak boleh kosong")
			self.entryRoom.focus_set()
		elif(self.entryJamMulaiJVar.get()>=self.entryJamSelesaiJVar.get()):
			msg = messagebox.showerror("Kesalahan", "Jam mulai harus lebih awal daripada jam selesai")
			self.entryJamMulaiJ.focus_set()
			self.entrySchedule.selection_range(0,tkinter.END)
		elif(liatJadwal==[0,0,0,0,0]):
			msg = messagebox.showerror("Kesalahan", "Jadwal minimal punya satu hari perkuliahan")
		else:
			self.onClickSchedule()

	def onClickRoom(self):
		hasil = []
		hasil.append(self.entryRuangVariable.get())
		hasil.append(self.entryJamMulaiVar.get())
		hasil.append(self.entryJamSelesaiVar.get())
		hari = []
		for j in range(5):
			if(self.checkR[j].get()==1):
				hari.append(j+1)
		hasil.append(hari)
		tup = tuple(hasil)
		self.rooms.append(tup)
		self.nRoom+=1
		print(tup)

		self.entryRuangVariable.set('')
		self.entryJamMulaiVar.set(7)
		self.entryJamSelesaiVar.set(8)
		self.entryRuang.focus_set()
		for j in range(5):
			self.RDay[j].deselect()

	def onClickPrintRoom(self):
		print('Ruangan terkumpul:')
		print(self.rooms)

	def onClickShow(self):
		dataPass = [self.nRoom, self.nSchedule, self.rooms, self.schedules, self.hasilPagi, self.hasilMalam, self.numberofConflicts, self.freePercentage]
		app = Toplevel(self.parent)
		childWindow = result(app, dataPass, self)
		#app.title('Result')
		#print(self.nRoom)

	def onClickSchedule(self):
		liatJadwal=[]
		for i in range(5):
			liatJadwal.append(self.checkS[i].get())
		hasil = []
		hasil.append(self.entryScheduleVar.get())

		if(self.roomFree.get()==0):
			hasil.append('-')
		else:
			hasil.append(self.entryRoomVar.get())

		hasil.append(self.entryJamMulaiJVar.get())
		hasil.append(self.entryJamSelesaiJVar.get())
		hasil.append(self.sks.get())
		hari = []
		for j in range(5):
			if(self.checkS[j].get()==1):
				hari.append(j+1)
		hasil.append(hari)
		tup = tuple(hasil)
		self.schedules.append(tup)
		self.nSchedule+=1
		print(tup)

		self.entryScheduleVar.set('')
		self.sks.set(2)
		self.entryJamMulaiJVar.set(7)
		self.entryRoomVar.set('')
		self.roomFree.set(0)
		self.entryJamSelesaiJVar.set(8)
		self.entrySchedule.focus_set()
		for j in range(5):
			self.SDay[j].deselect()

	def onClickPrintSchedule(self):
		print('Jadwal terkumpul:')
		print(self.schedules)

	def onClickDeleteRuang(self):
		idx = -1
		for i in range(self.nRoom):
			if(self.rooms[i][0] == self.delRuang.get()):
				idx = i

		if(self.nRoom==0):
			msg=messagebox.showerror('Kesalahan','Ruangan masih kosong')
		elif(idx == -1):
			msg=messagebox.showerror('Kesalahan','ID Ruangan tidak ditemukan')
		elif(messagebox.askyesno('Konfirmasi','Anda yakin ingin menghapus ruangan '+self.rooms[idx][0]+'?')):
			print('Ruangan '+self.rooms[idx][0]+' terhapus')
			del self.rooms[idx]
			del Jadwal.daftar_ruangan[idx]
			self.nRoom-=1

	def onClickDeleteJadwal(self):
		idx = -1
		for i in range(self.nSchedule):
			if(self.schedules[i][0] == self.delJadwal.get()):
				idx = i

		if(self.nSchedule==0):
			msg=messagebox.showerror('Kesalahan','Jadwal masih kosong')
		elif(idx == -1):
			msg=messagebox.showerror('Kesalahan','ID Jadwal tidak ditemukan')
		elif(messagebox.askyesno('Konfirmasi','Anda yakin ingin menghapus ruangan '+self.schedules[idx][0]+'?')):
			print('Jadwal ' + self.schedules[idx][0] + ' terhapus')
			del self.schedules[idx]
			del Jadwal.daftar_mata_kuliah[idx]
			self.nSchedule-=1

	def setRuang(self,value):
		self.nRoom=value

	def setJadwal(self,value):
		self.nSchedule=value

	# baca file
	def convertJadwalToRoomsAndSchedules(self, J):
		self.setRuang(len(J.daftar_ruangan))
		self.setJadwal(len(J.daftar_mata_kuliah))
		self.rooms = []
		self.schedules = []
		for i in range(self.nRoom):
			tempJ = J.daftar_ruangan[i]
			self.rooms.append((tempJ.nama, tempJ.jam_awal, tempJ.jam_akhir, tempJ.hari))
		for i in range(self.nSchedule):
			tempS = J.daftar_mata_kuliah[i]
			self.schedules.append((tempS.nama, tempS.ruangan, tempS.jam_awal, tempS.jam_akhir, tempS.sks, tempS.hari))


	def bacaRuang(self):
		nama_file=self.entryFileVar.get()
		J = Jadwal(nama_file)
		self.convertJadwalToRoomsAndSchedules(J)
		print('Testcase berhasil dibaca')

	# interface
	def space_percentage(self, M):
		total_slot = 0
		for i in range(self.nRoom):
			total_slot += (Jadwal.daftar_ruangan[i].jam_akhir - Jadwal.daftar_ruangan[i].jam_awal) * len(Jadwal.daftar_ruangan[i].hari)

		total_keisi = 0
		for i in range(self.nRoom):
			for j in range(120):
				if len(M.matriks[i][j]) != 0:
					total_keisi += 1
		return 100 * total_keisi / total_slot

	def interfaceMatriks(self, M): #M merupakan Matriks
		self.hasilPagi = []
		self.hasilMalam = []
		self.numberofConflicts=M.conflict_count()
		self.freePercentage = self.space_percentage(M)

		for i in range(self.nRoom):
			self.hasilPagi.append([])
			self.hasilMalam.append([])
			for j in range(5):
				self.hasilPagi[i].append([])
				self.hasilMalam[i].append([])
				for k in range(12):
					self.hasilPagi[i][j].append([])
					self.hasilMalam[i][j].append([])

		for i in range(self.nRoom):
			idx = i
			for j in range(i):
				if(self.rooms[j][0] == self.rooms[i][0]):
					idx = j
					break
			for j in range(120):
				hari = floor(j / 24)
				jam = j % 24
				if(len(M.matriks[i][j]) == 0):
					continue
				if(jam < 12):
						self.hasilPagi[idx][hari][jam] = M.matriks[i][j]
				else:
					self.hasilMalam[idx][hari][jam-12] = M.matriks[i][j]

		for i in range(self.nRoom):
			for j in range(5):
				for k in range(12):
					if(self.hasilPagi[i][j][k] == []):
						self.hasilPagi[i][j][k] = '-'
					else:
						tempstr = ""
						n = len(self.hasilPagi[i][j][k])
						for l in range(n):
							if(tempstr != ''):
								tempstr += ' '
							tempstr += self.hasilPagi[i][j][k][l]
						self.hasilPagi[i][j][k] = []
						self.hasilPagi[i][j][k].append(tempstr)

					if(self.hasilMalam[i][j][k] == []):
						self.hasilMalam[i][j][k] = '-'
					else:
						tempstr = ""
						n = len(self.hasilMalam[i][j][k])
						for l in range(n):
							if(tempstr != ''):
								tempstr += ' '
							tempstr += self.hasilMalam[i][j][k][l]
						self.hasilMalam[i][j][k] = []
						self.hasilMalam[i][j][k].append(tempstr)

		for i in range(self.nRoom):
			for j in range(5):
				self.hasilPagi[i][j] = tuple(self.hasilPagi[i][j])
				self.hasilMalam[i][j] = tuple(self.hasilMalam[i][j])

	# Algorithm
	def runGenetic(self):
		Assign()
		Genetic()
		Genetic.init()
		Genetic.add(Assign.daftar_matkul_time)
		Genetic.run(100)
		Genetic.sort()
		M = Genetic.convertToMatriks(Genetic.best())
		print ("Genetic CONFLICT = " + str(M.conflict_count()))
		self.interfaceMatriks(M)
		self.onClickShow()

	def runHillClimbing(self):
		Assign()
		HillClimbing()
		HillClimbing.init()
		HillClimbing.calculate()
		HillClimbing.finishing()
		print ("Hill Climbing CONFLICT = " + str(HillClimbing.matrix_hasil.conflict_count()))
		self.interfaceMatriks(HillClimbing.matrix_hasil)
		self.onClickShow()

	def runSimulatedAnnealing(self):
		Assign()
		SimulatedAnnealing()
		SimulatedAnnealing.init()
		SimulatedAnnealing.calculate()
		SimulatedAnnealing.finishing()
		print ("Simulated Annealing CONFLICT = " + str(SimulatedAnnealing.matrix_hasil.conflict_count()))
		self.interfaceMatriks(SimulatedAnnealing.matrix_hasil)
		self.onClickShow()

class result(Frame):

	def __init__(self,parent,lists,app):
		Frame.__init__(self,parent)
		self.parent=parent
		self.lists=lists
		self.app=app
		self.parent.title('RESULT')
		self.mulai()
		self.hasilPagi = []
		self.hasilMalam = []
		#self.jumlahRuang = jumlahRuang
		#self.jumlahJadwal = jumlahJadwal

	def mulai(self):
		self.nRoom = self.lists[0]
		self.nSchedule = self.lists[1]
		self.rooms = self.lists[2]
		self.schedules = self.lists[3]
		self.hasilPagi = self.lists[4]
		self.hasilMalam = self.lists[5]
		self.numberofConflicts=self.lists[6]
		self.freePercentage = self.lists[7]

		style = ttk.Style(self.parent)
		style.configure('Treeview',rowheight=20)
		tabel = ttk.Treeview(self.parent, height=6)
		tabel.grid(column=0, row=0,columnspan=2)
		tabelScrollY = ttk.Scrollbar(self.parent,orient='vertical',command=tabel.yview).grid(column=2,row=0,sticky='ns')
		tabelScrollX = ttk.Scrollbar(self.parent,orient='horizontal',command=tabel.xview).grid(column=0,row=1,columnspan=2,sticky='ew')
		#tabel.configure(yscroll=tabelScroll.set)
		Time1=('00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00')
		Time2= ('12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00')

		tabel.column("#0",minwidth=100, width=100)
		tabel.heading("#0", text="Ruangan")
		tabel["columns"]=Time1
		for d in Time1:
			tabel.column(d,minwidth=70,width=70,anchor="center")
			tabel.heading(d, text=d)

		tabel1=ttk.Treeview(self.parent,height=6)
		tabel1.grid(column=0,row=2,columnspan=2)
		tabel1ScrollY = ttk.Scrollbar(self.parent,orient='vertical',command=tabel1.yview).grid(column=2,row=2,sticky='ns')
		tabel1ScrollX = ttk.Scrollbar(self.parent,orient='horizontal',command=tabel1.xview).grid(column=0,row=3,columnspan=2,sticky='ew')
		#tabel1.configure(yscroll=tabel1Scroll.set)
		tabel1.column("#0",width=100, minwidth=100)
		tabel1.heading("#0",text="Ruangan")
		tabel1["columns"]=Time2
		for d in Time2:
			tabel1.column(d,minwidth=70,width=70, anchor="center")
			tabel1.heading(d,text=d)

		print(self.nRoom)
		for j in range(self.nRoom):
			namaRuang = self.rooms[j][0]
			idRuang = "r"+str(j)
			print(idRuang)
			exists=0
			for z in range(j):
				if(self.rooms[z][0]==self.rooms[j][0]):
					exists=1
					break
			if(exists==0):
				tabel.insert("", j, idRuang, text=namaRuang)
				tabel1.insert("", j, idRuang, text=namaRuang)
				i=0
				for d in Days:
					tabel.insert(idRuang,i,text=d,values=self.hasilPagi[j][i]) # hasil pagi
					tabel1.insert(idRuang,i,text=d,values=self.hasilMalam[j][i]) # hasil malam
					i+=1



		labelKonflik = tkinter.Label(self.parent, text=u"Number of Conflicts: ").grid(column=0, row=4, sticky="e")
		labelNumOfConflicts = tkinter.Label(self.parent, text=self.numberofConflicts).grid(column=1, row=4, sticky="w")

		labelPersen = tkinter.Label(self.parent, text=u"Percentage : ").grid(column=0, row=5, sticky="e")
		labelNumOfPercentage = tkinter.Label(self.parent, text=str(self.freePercentage)+' %').grid(column=1, row=5, sticky="w")

if __name__ == "__main__":
	root = Tk()
	app = form(root)
	#app.title('AI berDARAH')
	root.mainloop()
