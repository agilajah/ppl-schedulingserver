# LIBRARY
import calendar
import date
import datetime
import os
import time
from __future__ import division
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
    def __init__(self, event_id = None, name = None, date_start = None, date_end = None):
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
sidang_period = Event('Masa Sidang', '2017-05-01 07:00:00', '2017-05-12 18:00:00') # ini hardcode, dan harus dimulai jam 07:00:00
hourToSecond = 3600 # konstanta
dayToSecond = 86400 # konstanta
weekToSecond = 604800 # konstanta

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
                self.events.append(Event('Libur', longtoDate(i), longtoDate(i + dayToSecond)))
            else: # hari senin sampe jumat
                # ruangan tutup dari jam 6 sore sampe jam 7 besoknya
                self.events.append(Event('Tutup', longtoDate(i + (hourToSecond * 11)), longtoDate(i + dayToSecond)))
            i += dayToSecond

# STRUKTUR DATA
class Domain(object):
# class Domain sebagai domain dalam genetic algorithm
    def __init__(self, room_id = None, event = None):
        self.room_id = room_id
        self.event = event

# FUNGSI
def isConflict(domain, event):
# cek apakah event 1 (domain) dengan event 2 (event) bentrok
    if (event.long_start >= domain.long_start and event.long_start <= domain.long_end):
        return True # bentrok, dosen bakal cabut atau ruangan bakal dipake ditengah
    else if (event.long_end >= domain.long_start and event.long_end <= domain.long_end):
        return True # bentrok, dosen bakal telat atau ruangan baru bisa dipake ditengah
    else if (event.long_start <= domain.long_start and event.long_end >= domain.long_end):
        return True # bentrok, dosen gabakal dateng atau ruangan full gabisa dipake
    else:
        return False

# STRUKTUR DATA
class Sidang(object):
# class Sidang sebagai variable dalam genetic algorithm
    def __init__(self, student_id = None, lecturers_id):
        self.lecturers_id = lecturers_id
        self.events = []
        self.mergeEventsLecturers() # gabungkan semua jadwal sibuk dosen
        self.events.sort(key = getEventKey)
        self.domains = [] # semua kemungkinan ruang&jadwal yang bisa digunakan
        self.idxDomain = -1 # hasil algoritma adalah ini, salah satu ruang&jadwal dari banyak kemungkinan tersebut
        self.searchDomains()
    def mergeEventsLecturers(self):
        for lecturer_id in lecturers_id:
            for event in lecturers_list[lecturer_id].events:
                self.events.append(event) # gabunginnya satu satu biar gak jadi list of list
    def searchDomains(self):
        i = sidang_period.long_start
        while (i < sidang_period.long_end):
            domain = Event('Usulan sidang ' . student_id, longtoDate(i), longtoDate(i + hourToSecond))
            # cek apakah dosen ada yang sedang sibuk
            for event in self.events:
                if (isConflict(domain, event)):
                    break # bentrok, cari waktu lain
                else if (event.long_start >= domain.long_end): # semua dosen available
                    # cek ruangan mana saja yang sedang kosong
                    for room in rooms_list:
                        for room_event in room.events:
                            if (isConflict(domain, room_event)):
                                break # bentrok, cari ruangan lain
                            else if (event.long_start >= domain.long_end): # ruangan kosong
                                self.domains.append(Domain(room.room_id, domain))
                                idxDomain++
                                break # dapat 1 kemungkinan ruang&jadwal, cari ruangan lain
            i += hourToSecond # cek jadwal selanjutnya tiap 1 jam















# BTW CODINGAN DIBAWAH INI TOLONG RAPIHIN LAGI YA, SEKALIAN KASIH KOMENTAR YANG JELAS
# PEMILIHAN NAMA FUNGSI/CLASS/VARIABEL JUGA YANG TIDAK AMBIGU WKWKW




def student_data_parser(student_data):
    students = []
    for i in student_data:
        temp_student_data = student_data[i]
        temp_student = Mahasiswa()
        temp_student.user_id = temp_student_data['user_id']
        temp_student.dosen_pembimbing_id = temp_student_data['id_dosen_pembimbing']
        temp_student.first_name = temp_student_data['user_name']
        temp_student.last_name = temp_student_data['last_name']
        temp_student.email = temp_student_data['email']
        temp_student.topics = temp_student_data['topics']
        list_of_events = []
        # create event
        try:
            event_json = temp_student_data['event']
        except:
            print('Event kosong')
        if event_json is not None:
            for j in event_json:
                temp_event = Event(event_json[j].name, event_json[j].event_id, event_json[j].date_start, \
                    event_json[j].date_end)
                list_of_events.append(temp_event)

        # now we append all of those information here
        students.append(temp_student)

    return students

def lecturer_data_parser(lecturer_data):
    lecturers = []
    for i in lecturer_data:
        temp_lecturer_data = lecturer_data[i]
        temp_lecturer = Dosen()
        temp_lecturer.user_id = temp_lecturer_data['user_id']
        temp_lecturer.first_name = temp_lecturer_data['user_name']
        temp_lecturer.last_name = temp_lecturer_data['last_name']
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
                temp_event = Event(event_json[j].name, event_json[j].event_id, event_json[j].date_start, \
                                   event_json[j].date_end)
                list_of_events.append(temp_event)

        # now we append all of those information here
        lecturers.append(temp_lecturer)

    return lecturers

def create_sessions(students_list = None, lecturers_list = None):
    return 0

def create_initial_data(temp_data = None):
    if temp_data is None:
        print ('We need both of student and lecturer data to proceed')
    else:
        # create dictionary of lists
        data = {}
        data['students_list'] = student_data_parser(temp_data['student_data'])
        data['lecturers_list'] = lecturer_data_parser(temp_data['lecturer_data'])
        data['rooms_list'] = room_data_parser(temp_data['room_data'])
        # create session from given students and lecturers list
        data['sessions_list'] = create_sessions(data['students_list'], data['lecturers_list'])
        
def get_year():
    now = datetime.datetime.now()
    return now.year
    
def cetak_nomor_hari():
    print ("[", end='')
    for i in range (1, 365):
        print (i, end='')
        print(", ", end='')
    print (365, end='')
    x = get_year()
    if (calendar.isleap(x)):
        print (", 366", end='')
    print ("]")
    return
    
def number_to_date(x):
    year = get_year()
    date = datetime.datetime(year, 1, 1) + datetime.timedelta(x - 1)
    return date
    
def date_to_day(date):
    day_name = date.strftime("%A")
    return day_name

class Data():
    def __init__(self, students=None, lecturers=None, sidangs=None):
        self.students = students
        self.lecturers = lecturers
        self.sidangs = sidangs

class Scheduler(Resource):
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

