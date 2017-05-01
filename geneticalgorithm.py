# LIBRARY
from __future__ import division
from copy import deepcopy
from math import ceil, exp, floor
from random import randint, seed, shuffle
import calendar
import datetime
import json
import os
import time

# FUNGSI
def dateToLong(date):
# input string tanggal sesuai format google calendar, output long
    return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())

# FUNGSI
def longToDate(date):
# input long, output string tanggal sesuai format google calendar
    return datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")

# STRUKTUR DATA
class Event():
# kegiatan yang menyebabkan slot waktu tidak bisa dipakai (busy)
    def __init__(self, event_id, name = 'An event', date_start = '', date_end= ''):
        self.event_id = event_id
        self.name = name
        self.date_start = date_start
        self.date_end = date_end
        # tipe waktu disimpan juga dalam tipe integer supaya lebih mudah cek lebih besar/kecil nya
        self.long_start = dateToLong(date_start)
        self.long_end = dateToLong(date_end)

# VARIABLE GLOBAL
sidang_period = Event(1212, 'Masa Sidang', '2017-05-01 07:00:00', '2017-05-12 18:00:00') # ini hardcode, dan harus dimulai jam 07:00:00
hourToSecond = 3600 # konstanta
dayToSecond = 86400 # konstanta
weekToSecond = 604800 # konstanta

# STRUKTUR DATA
class Lecturer():
# dosen
    def __init__(self, lecturer_id, name = 'Foolan', email = 'foolan@gmail.com', topics = [], events = []):
        self.lecturer_id = lecturer_id
        self.name = name
        self.email = email
        self.topics = topics
        self.events = events # jadwal sibuk dosen
        self.events.sort(key = lambda event : event.long_start)

# STRUKTUR DATA
class Room():
# ruangan
    def __init__(self, room_id, name = 'A room', email = 'a_room@gmail.com', events = []):
        self.room_id = room_id
        self.name = name
        self.email = email
        self.events = events # jadwal ruangan sedang dipakai
        self.addClosedSchedule() # generate jadwal ruangan tutup
        self.events.sort(key = lambda event : event.long_start)
    def addClosedSchedule(self):
        i = sidang_period.long_start # hanya generate di masa sidang, tidak setahun penuh
        while (i < sidang_period.long_end):
            day = (i % weekToSecond) / dayToSecond
            if (day >= 2 and day < 4): # hari sabtu atau minggu
                # ruangan tutup dari jam 7 pagi sampe jam 7 pagi besoknya
                self.events.append(Event(None, 'Libur', longToDate(i), longToDate(i + dayToSecond)))
            else: # hari senin sampe jumat
                # ruangan tutup dari jam 6 sore sampe jam 7 besoknya
                self.events.append(Event(None, 'Tutup', longToDate(i + (hourToSecond * 11)), longToDate(i + dayToSecond)))
            i += dayToSecond

# STRUKTUR DATA
class Domain():
# class Domain sebagai domain dalam genetic algorithm
    def __init__(self, room_id, event):
        self.room_id = room_id
        self.event = event

# FUNGSI
def isEventConflict(candidateEvent, event):
# cek apakah event 1 (candidateEvent) dengan event 2 (event) bentrok
    if (event.long_start >= candidateEvent.long_start and event.long_start < candidateEvent.long_end):
        return True # bentrok, dosen bakal cabut atau ruangan bakal dipake ditengah
    elif (event.long_end > candidateEvent.long_start and event.long_end <= candidateEvent.long_end):
        return True # bentrok, dosen bakal telat atau ruangan baru bisa dipake ditengah
    elif (event.long_start <= candidateEvent.long_start and event.long_end >= candidateEvent.long_end):
        return True # bentrok, dosen gabakal dateng atau ruangan full gabisa dipake
    else:
        return False

# STRUKTUR DATA
class Sidang():
# class Sidang sebagai variable dalam genetic algorithm
    def __init__(self, student_id, lecturers_id = []):
        self.student_id = student_id
        self.lecturers_id = lecturers_id
        self.events = []
        self.mergeEventsLecturers() # gabungkan semua jadwal sibuk dosen
        self.events.sort(key = lambda event : event.long_start)
        self.domains = [] # semua kemungkinan ruang&jadwal yang bisa digunakan
        self.idxDomain = -1 # hasil algoritma adalah ini, salah satu ruang&jadwal dari banyak kemungkinan tersebut
        self.searchDomains()
        self.totalDomain = self.idxDomain + 1
    def mergeEventsLecturers(self):
    	return
        for lecturer_id in lecturers_id:
            for event in lecturers_list[lecturer_id].events:
                self.events.append(event) # gabunginnya satu satu biar gak jadi list of list
    def searchDomains(self):
        i = sidang_period.long_start
        while (i < sidang_period.long_end):
            candidateEvent = Event(None, 'Usulan sidang ' + str(self.student_id), longToDate(i), longToDate(i + hourToSecond))
            # cek apakah dosen ada yang sedang sibuk
            for lecturer_event in self.events:
                if (isEventConflict(candidateEvent, lecturer_event)):
                    break # bentrok, cari waktu lain
                elif (lecturer_event.long_start >= candidateEvent.long_end): # semua dosen available
                    # cek ruangan mana saja yang sedang kosong
                    for room in rooms_list:
                        for room_event in room.events:
                            if (isEventConflict(candidateEvent, room_event)):
                                break # bentrok, cari ruangan lain
                            elif (room_event.long_start >= candidateEvent.long_end): # ruangan kosong
                                self.domains.append(Domain(room.room_id, candidateEvent))
                                self.idxDomain = self.idxDomain + 1
                                break # dapat 1 kemungkinan ruang&jadwal, cari ruangan lain
            i += hourToSecond # cek jadwal 1 jam berikutnya

# STRUKTUR DATA
class Student():
# mahasiswa
# asumsi: mahasiswa selalu siap sedia, tidak punya jadwal sibuk
    def __init__(self, student_id, name = 'Foolan', email = 'foolan@gmail.com', topic = None, dosbing_id = None):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.topic = topic
        self.dosbing_id = dosbing_id
        self.sidang = Sidang(student_id, dosbing_id) # harusnya gak cuma dosbing, tapi semua dosen yg hadir

# FUNGSI
def isDomainConflict(domain1, domain2):
# cek apakah usulan sidang 1 (domain1) dengan usulan sidang 2 (domain2) bentrok
    if ((domain1.room_id == domain2.room_id) and isEventConflict(domain1.event, domain2.event)):
        return 1 # ruangan dan jamnya sama, berarti bentrok
    else:
        return 0

# FUNGSI
def countDomainConflicts():
# menghitung berapa banyak mahasiswa yang bentrok jadwal sidangnya
    result = 0
    for student1 in students_list:
        for student2 in students_list:
            # cross, kalo sama diri sendiri ya ga diitung wkwk -_-
            if (student1.student_id != student2.student_id):
                domain1 = student1.sidang.domains[student1.sidang.idxDomain]
                domain2 = student2.sidang.domains[student2.sidang.idxDomain]
                result += isDomainConflict(domain1, domain2)
    return result

# VARiABLE GLOBAL
listGen = [[], [], [], []] # 4 gen (4 populasi), masing-masing gen berupa list of idxDomain (elemennya sebanyak students_list)

# FUNGSI
def GeneticAlgorithm(maxGeneration):
# implementasi genetic algorithm
    fitness = [] # score fitness untuk tiap gen
    generation = 0
    while True:
        # hitung fitness tiap gen
        del fitness[:]
        for i in range(len(listGen)):
            # pasangkan dulu student dengan domain sesuai dengan yang ada pada gen
            for j in range(len(listGen[i])):
                students_list[j].idxDomain = listGen[i][j]
            # hitung berapa student yang konflik, fitnessnya makin kecil makin bagus
            fitness.append(countDomainConflicts())
            if fitness[i] == 0:
                print ("SOLUSI DITEMUKAN DALAM GENERASI", generation)
                return
        # masih ada konflik di semua gen, cari gen terjelek dan terbagus
        idxMin = fitness.index(max(fitness))
        idxMax = fitness.index(min(fitness))
        generation += 1
        # gak nemu solusi sampai generation ke-maxGeneration
        if generation == maxGeneration:
            # pasangkan lagi student dengan domain kepunyaan gen terbaik (fitness terkecil)
            for i in range(len(listGen[idxMax])):
                students_list[i].idxDomain = listGen[idxMax][i]
            # cetak berapa konflik
            print (fitness[idxMax], "KONFLIK DALAM GENERASI", generation)
            break # break while True
        # lanjut ke generation selanjutnya
        else:
            # gen jelek timpa dengan gen bagus
            for i in range(len(students_list)):
                listGen[idxMin][i] = listGen[idxMax][i]
            # kawin silang TANPA mutasi, mulai dari idxBelah (random) sampai index terakhir
            idxBelah = random.randint(1, len(students_list) - 2)
            for i in range(idxBelah, len(students_list)):
                #swap gen 0 dengan gen 1
                temp = listGen[0][i]
                listGen[0][i] = listGen[1][i]
                listGen[1][i] = temp
                #swap gen 2 dengan gen 3
                temp = listGen[2][i]
                listGen[2][i] = listGen[3][i]
                listGen[3][i] = temp
            # mutasi = student ke-studentMutasi setiap gen, domainnya berubah menjadi domainMutasi
            for gen in listGen:
                studentMutasi = random.randint(0, len(students_list) - 1)
                domainMutasi = random.randint(0, students_list[studentMutasi].totalDomain - 1)
                gen[studentMutasi] = domainMutasi

# FUNGSI
def printResult():
# mencetak usulan jadwal sidang
    for student in students_list:
        idxDomain = student.sidang.idxDomain
        domain = student.sidang.domains[idxDomain]
        print (student.student_id, ' pada ', domain.event.date_start, ' di ', rooms_list[domain.room_id].name)

# FUNGSI
def execGA():
# inisialisasi sebelum manjalankan genetic algorithm
    for gen in listGen:
        del gen[:]
        # inisialisasi, untuk setiap mahasiswa pilih salah 1 domain (kemungkinan jadwal sidang) secara acak
        for student in students_list:
            gen.append(random.randint(0, student.sidang.totalDomain - 1))
    geneticAlgorithm(20)
    printResult()

def studentParser(unparsedStudents):
    students_list = []
    for unparsedStudent in unparsedStudents:
        student_id = unparsedStudent['user_id']
        name = unparsedStudent['name']['first'] + unparsedStudent['name']['last']
        email = unparsedStudent['email']
        topic = unparsedStudent['topic']
        dosbing_id = unparsedStudent['dosbing_id']
        # now we append all of those information here
        students_list.append(Student(student_id, name, email, topic, dosbing_id))
    return students_list

def lecturerParser(unparsedLecturers):
    lecturers_list = []
    for unparsedLecturer in unparsedLecturers:
        lecturer_id = unparsedLecturer['user_id']
        name = unparsedLecturer['name']['first'] + unparsedLecturer['name']['last']
        email = unparsedLecturer['email']
        topics = unparsedLecturer['topic']
        events = []
        # create event
        try:
            listEventData = unparsedLecturer['event']
        except:
            print('Event kosong')
        if listEventData is not None:
            for eventData in listEventData:
                event_start = eventData['start_date']
                event_end = eventData['end_date']
                # now we append all of those information event here
                events.append(Event(None, None, event_start, event_end))
        # now we append all of those information here
        lecturers_list.append(Lecturer(lecturer_id, name, email, topics, events))
    return lecturers_list

def roomParser(unparsedRooms):
    rooms_list = []
    for unparsedRoom in unparsedRooms:
        room_id = unparsedRoom['user_id']
        name = unparsedRoom['name']['first'] + unparsedRoom['name']['last']
        email = unparsedRoom['email']
        events = []
        # create event
        try:
            listEventData = unparsedRoom['event']
        except:
            print('Event kosong')
        if listEventData is not None:
            for eventData in listEventData:
                event_start = eventData['start_date']
                event_end = eventData['end_date']
                # now we append all of those information event here
                events.append(Event(None, None, event_start, event_end))
        # now we append all of those information here
        rooms_list.append(Room(room_id, name, email, events))
    return rooms_list

def initData():
    global students_list
    global lecturers_list
    global rooms_list
    # ambil data dari json
    with open('data.json') as rawData:
        unparsedData = json.load(rawData)
    # parse data
    students_list = studentParser(unparsedData['student_data'])
    lecturers_list = lecturerParser(unparsedData['lecturer_data'])
    # rooms_list = roomParser(unparsedData['room_data'])

# MAIN PROGRAM
initData()
# execGA()
