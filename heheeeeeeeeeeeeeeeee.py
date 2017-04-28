# LIBRARY
from __future__ import division
import calendar
import date
import datetime
import os
import time
from copy import deepcopy
from math import ceil, exp, floor
from random import randint, seed, shuffle

# FUNGSI
def dateToLong(date):
# input string tanggal sesuai format google calendar, output long
    return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())

# FUNGSI
def longtoDate(date):
# input long, output string tanggal sesuai format google calendar
    return datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")

# STRUKTUR DATA
class Event(object):
# kegiatan yang menyebabkan slot waktu tidak bisa dipakai (busy)
    def __init__(self, event_id = None, name = None, date_start = '2000-05-01 07:00:00', date_end = '2000-05-01 07:00:05'):
        self.event_id = event_id
        self.name = name
        self.date_start = date_start
        self.date_end = date_end
        # tipe waktu disimpan juga dalam tipe integer supaya lebih mudah cek lebih besar/kecil nya
        self.long_start = dateToLong(date_start)
        self.long_end = dateToLong(date_end)

# FUNGSI LAMDA
def getEventKey(event):
# digunakan untuk fungsi sort()
    return event.long_start

# VARIABLE GLOBAL
sidang_period = Event(1212, 'Masa Sidang', '2017-05-01 07:00:00', '2017-05-12 18:00:00') # ini hardcode, dan harus dimulai jam 07:00:00
hourToSecond = 3600 # konstanta
dayToSecond = 86400 # konstanta
weekToSecond = 604800 # konstanta

# STRUKTUR DATA
class Lecturer(object):
# dosen
    def __init__(self, lecturer_id = None, name = None, email = None, topics = None, events = None):
        self.lecturer_id = lecturer_id
        self.name = name
        self.email = email
        self.topics = topics
        self.events = events # jadwal sibuk dosen
        self.events.sort(key = getEventKey)

# STRUKTUR DATA
class Room(object):
# ruangan
    def __init__(self, room_id = None, name = None, email = None, events = None):
        self.room_id = room_id
        self.name = name
        self.email = email
        self.events = events # jadwal ruangan sedang dipakai
        self.addClosedSchedule() # generate jadwal ruangan tutup
        self.events.sort(key = getEventKey)
    def addClosedSchedule(self):
        i = sidang_period.long_start # hanya generate di masa sidang, tidak setahun penuh
        while (i < sidang_period.long_end):
            day = (i % weekToSecond) / dayToSecond
            if (day >= 2 and day < 4): # hari sabtu atau minggu
                # ruangan tutup dari jam 7 pagi sampe jam 7 pagi besoknya
                self.events.append(Event(444, 'Libur', longtoDate(i), longtoDate(i + dayToSecond)))
            else: # hari senin sampe jumat
                # ruangan tutup dari jam 6 sore sampe jam 7 besoknya
                self.events.append(Event(555, 'Tutup', longtoDate(i + (hourToSecond * 11)), longtoDate(i + dayToSecond)))
            i += dayToSecond

# STRUKTUR DATA
class Domain(object):
# class Domain sebagai domain dalam genetic algorithm
    def __init__(self, room_id = None, event = None):
        self.room_id = room_id
        self.event = event

# FUNGSI
def isEventConflict(candidateEvent, event):
# cek apakah event 1 (candidateEvent) dengan event 2 (event) bentrok
    if (event.long_start >= candidateEvent.long_start and event.long_start <= candidateEvent.long_end):
        return True # bentrok, dosen bakal cabut atau ruangan bakal dipake ditengah
    elif (event.long_end >= candidateEvent.long_start and event.long_end <= candidateEvent.long_end):
        return True # bentrok, dosen bakal telat atau ruangan baru bisa dipake ditengah
    elif (event.long_start <= candidateEvent.long_start and event.long_end >= candidateEvent.long_end):
        return True # bentrok, dosen gabakal dateng atau ruangan full gabisa dipake
    else:
        return False

# STRUKTUR DATA
class Sidang(object):
# class Sidang sebagai variable dalam genetic algorithm
    def __init__(self, student_id = None, lecturers_id = None):
        self.student_id = student_id
        self.lecturers_id = lecturers_id
        self.events = []
        self.mergeEventsLecturers() # gabungkan semua jadwal sibuk dosen
        self.events.sort(key = getEventKey)
        self.domains = [] # semua kemungkinan ruang&jadwal yang bisa digunakan
        self.idxDomain = -1 # hasil algoritma adalah ini, salah satu ruang&jadwal dari banyak kemungkinan tersebut
        self.searchDomains()
        self.totalDomain = self.idxDomain + 1
    def mergeEventsLecturers(self):
        for lecturer_id in lecturers_id:
            for event in lecturers_list[lecturer_id].events:
                self.events.append(event) # gabunginnya satu satu biar gak jadi list of list
    def searchDomains(self):
        i = sidang_period.long_start
        while (i < sidang_period.long_end):
            candidateEvent = Event(9090, 'Usulan sidang ' + student_id, longtoDate(i), longtoDate(i + hourToSecond))
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
class Student(object):
# mahasiswa
# asumsi: mahasiswa selalu siap sedia, tidak punya jadwal sibuk
    def __init__(self, student_id = None, name = None, email = None, topic = None, dosbing_id = None):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.topic = topic
        self.dosbing_id = dosbing_id
        self.sidang = Sidang(self.student_id, dosbing_id) # harusnya gak cuma dosbing, tapi semua dosen yg hadir

# FUNGSI
def isDomainConflict(domain1, domain2):
# cek apakah usulan sidang 1 (domain1) dengan usulan sidang 2 (domain2) bentrok
    if (domain1.room_id == domain2.room_id and domain1.event.long_start == domain2.event.long_start):
        return 1 # ruangan dan jamnya sama, berarti bentrok
    else:
        return 0

# FUNGSI
def countDomainConflicts(object):
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
def printResult(object):
# mencetak usulan jadwal sidang
    for student in students_list:
        idxDomain = student.sidang.idxDomain
        domain = student.sidang.domains[idxDomain]
        print (student.student_id, ' pada ', domain.event.date_start, ' di ', rooms_list[domain.room_id].name)

# FUNGSI
def execGA(object):
# inisialisasi sebelum manjalankan genetic algorithm
    for gen in listGen:
        del gen[:]
        # inisialisasi, untuk setiap mahasiswa pilih salah 1 domain (kemungkinan jadwal sidang) secara acak
        for student in students_list:
            gen.append(random.randint(0, student.sidang.totalDomain - 1))
    geneticAlgorithm(20)
    printResult()

# MAIN PROGRAM
# setelah data-data di load dari json jadi objek (gak ngerti gimana caranya), tinggal uncomment dibawah ini
# execGA()


























# BTW CODINGAN DIBAWAH INI TOLONG RAPIHIN LAGI YA, SEKALIAN KASIH KOMENTAR YANG JELAS
# PEMILIHAN NAMA FUNGSI/CLASS/VARIABEL JUGA YANG TIDAK AMBIGU WKWKW




def student_data_parser(student_data):
    students = []
    for i in student_data:
        temp_student_data = student_data[i]
        temp_student = Student()
        temp_student.student_id = temp_student_data['user_id']
        temp_student.name = temp_student_data['user_name'] + temp_student_data['last_name']
        temp_student.email = temp_student_data['email']
        temp_student.topic = temp_student_data['topics']
        temp_student.dosbing_id = temp_student_data['id_dosen_pembimbing']
        # now we append all of those information here
        students.append(temp_student)
    return students

def lecturer_data_parser(lecturer_data):
    lecturers = []
    for i in lecturer_data:
        temp_lecturer_data = lecturer_data[i]
        temp_lecturer = Lecturer()
        temp_lecturer.lecturer_id = temp_lecturer_data['user_id']
        temp_lecturer.name = temp_lecturer_data['user_name'] + temp_lecturer_data['last_name']
        temp_lecturer.email = temp_lecturer_data['email']
        temp_lecturer.topics = temp_lecturer_data['topics']
        list_of_events = []
        # create event
        try:
            event_json = temp_lecturer_data['event']
        except:
            print('Event kosong')
        if event_json is not None:
            for j in event_json:
                temp_event = Event(678, event_json[j].name, event_json[j].event_id, event_json[j].date_start, \
                                   event_json[j].date_end)
                list_of_events.append(temp_event)
        temp_lecturer.events = list_of_events
        # now we append all of those information here
        lecturers.append(temp_lecturer)
    return lecturers

def create_initial_data(temp_data = None):
    if temp_data is None:
        print ('We need both of student and lecturer data to proceed')
    else:
        # create dictionary of lists
        data = {}
        data['students_list'] = student_data_parser(temp_data['student_data'])
        data['lecturers_list'] = lecturer_data_parser(temp_data['lecturer_data'])
        data['rooms_list'] = room_data_parser(temp_data['room_data'])

class Data():
    def __init__(self, students=None, lecturers=None, sidangs=None):
        self.students = students
        self.lecturers = lecturers
        self.sidangs = sidangs

# class Scheduler(Resource):
class Scheduler():
    def post(self):
        args = parser.parse_args(strict=True)
        data_json = {}
        for k, v in args.items():
            if v is not None:
                data_json[k] = v
        temp_data = json.load(data_json)
        # student_data = temp_data['student_data']
        # lecturer_data = temp_data['lecturer_data']
        # parse student_data
        # parse professor_data
        # the result is dictionary of lists
        result_data = create_initial_data(temp_data)
        #create data object
        return 1
