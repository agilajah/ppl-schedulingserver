######################################## MODULE ########################################

from __future__ import division
from googleapiclient import discovery
from flask import Flask
from flask_restful import Api, Resource, reqparse
from oauth2client import client, tools
from oauth2client.file import Storage
from random import randint
import argparse
import datetime
import httplib2
import json
import os
import pyrebase
import time

######################################## HANDLER ########################################

class Home(Resource):
    def get(self):
        return 'OK'
    def post(self):
        return self.get()

class Scheduler(Resource):
    def get(self):
        try:
            connectFirebase()
            parseDatabase()
            result = runGA()
            saveResult()
            return result
        except Exception as e:
            return str(e)
    def post(self):
        return self.get()

class Login(Resource):
    def get(self):
        try:
            connectFirebase()
            parseDatabase()
            connectCalendar(getCredential(Resource.email))
        except Exception as e:
            return str(e)
    def post(self):
        return self.get()

######################################## STRUKDAT ########################################

class Event():
# kegiatan yang menyebabkan slot waktu tidak bisa dipakai (busy)
    def __init__(self, eventID = None, name = 'An event', startDate = None, endDate = None):
        self.eventID = eventID
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        # tipe waktu disimpan juga dalam tipe integer supaya lebih mudah cek lebih besar/kecil nya
        self.startLong = dateToLong(startDate)
        self.endLong = dateToLong(endDate)

class Room():
# ruangan
    def __init__(self, roomID = None, name = 'A room', email = 'a.room@gmail.com', events = []):
        self.roomID = roomID
        self.name = name
        self.email = email
        self.events = events # jadwal ruangan sedang dipakai
        self.addClosedSchedule() # generate jadwal ruangan tutup
        self.events.sort(key = lambda event : event.startLong)
    def addClosedSchedule(self):
        # generate jam tutup dan jam libur ruangan di masa sidang
        i = sidangPeriod.startLong
        while (i < sidangPeriod.endLong):
            day = (i % WEEKTOSECOND) / DAYTOSECOND
            if (day >= 2 and day < 4): # hari sabtu atau minggu
                # ruangan tutup dari jam 7 pagi sampe jam 7 pagi besoknya
                self.events.append(Event(None, 'Libur', longToDate(i), longToDate(i + DAYTOSECOND)))
            else: # hari senin sampe jumat
                # ruangan tutup dari jam 6 sore sampe jam 7 besoknya
                self.events.append(Event(None, 'Tutup', longToDate(i + (HOURTOSECOND * 11)), longToDate(i + DAYTOSECOND)))
            i += DAYTOSECOND

class Lecturer():
# dosen
    def __init__(self, lecturerID = None, name = 'Foolan', email = 'foolan@gmail.com', topics = [], events = []):
        self.lecturerID = lecturerID
        self.name = name
        self.email = email
        self.topics = topics
        self.events = events # jadwal sibuk dosen
        self.events.sort(key = lambda event : event.startLong)

class Student():
# mahasiswa
# asumsi: mahasiswa selalu siap sedia, tidak punya jadwal sibuk
    def __init__(self, studentID = None, name = 'Foolan', email = 'foolan@gmail.com', topic = None, pembimbingID = [], pengujiID =[]):
        self.studentID = studentID
        self.name = name
        self.email = email
        self.topic = topic
        self.pembimbingID = pembimbingID
        self.pengujiID = pengujiID
    def initSidang(self):
        self.sidang = Sidang(self.studentID, self.pembimbingID + self.pengujiID)

class Sidang():
# class Sidang sebagai variable dalam genetic algorithm
    def __init__(self, studentID = None, lecturersID = []):
        self.studentID = studentID
        self.lecturersID = lecturersID
        self.events = []
        self.mergeEventsLecturers() # gabungkan semua jadwal sibuk dosen
        self.events.sort(key = lambda event : event.startLong)
        self.domains = [] # semua kemungkinan ruang&jadwal yang bisa digunakan
        self.searchDomains()
        if (len(self.domains) == 0):
            raise Exception('Mahasiswa ' + studentID + ' tidak mempunyai kemungkinan jadwal sidang.')
        else:
            self.idxDomain = 0 # hasil algoritma adalah ini, salah satu ruang&jadwal dari banyak kemungkinan tersebut
    def mergeEventsLecturers(self):
        for lecturerID in self.lecturersID:
            # cari dosennya
            lecturer = None
            for lecturerIterator in listLecturer:
                if (lecturerIterator.lecturerID == lecturerID):
                    lecturer = lecturerIterator
                    break
            # gabung jadwalnya
            if (lecturer is not None):
                for event in lecturer.events:
                    self.events.append(event) # gabunginnya satu satu biar gak jadi list of list
    def searchDomains(self):
        i = sidangPeriod.startLong
        while (i < sidangPeriod.endLong):
            candidateEvent = Event(None, 'Usulan sidang ' + str(self.studentID), longToDate(i), longToDate(i + HOURTOSECOND))
            # cek apakah dosen ada yang sedang sibuk
            isConflict = False
            for eventLecturer in self.events:
                if (isEventConflict(candidateEvent, eventLecturer)):
                    isConflict = True
                    break # bentrok, cari waktu lain
                if (eventLecturer.startLong >= candidateEvent.endLong):
                    break # tidak perlu cek lagi event selanjutnya, pasti gak bentrok
            if (not isConflict): # semua dosen bersedia
                for room in listRoom:
                    isConflict = False
                    for eventRoom in room.events:
                        if (isEventConflict(candidateEvent, eventRoom)):
                            isConflict = True
                            break # bentrok, cari ruangan lain
                        if (eventRoom.startLong >= candidateEvent.endLong):
                            break # tidak perlu cek lagi event selanjutnya, pasti gak bentrok
                    if (not isConflict): # ruangan kosong
                        self.domains.append(Domain(room.roomID, candidateEvent))
            i += FORTYMINUTESTOSECOND # cek jadwal 1 sesi (40 menit) berikutnya

class Domain():
# class Domain sebagai domain dalam genetic algorithm
    def __init__(self, roomID, event):
        self.roomID = roomID
        self.event = event

######################################## PROSEDUR ########################################

def dateToLong(date):
# input string tanggal sesuai format google calendar, output long
    return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())

def longToDate(date):
# input long, output string tanggal sesuai format google calendar
    return datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")

def isEventConflict(candidateEvent, event):
# cek apakah event 1 (candidateEvent) dengan event 2 (event) bentrok
    if (event.startLong >= candidateEvent.startLong and event.startLong < candidateEvent.endLong):
        return True # bentrok, dosen bakal cabut atau ruangan bakal dipake ditengah
    elif (event.endLong > candidateEvent.startLong and event.endLong <= candidateEvent.endLong):
        return True # bentrok, dosen bakal telat atau ruangan baru bisa dipake ditengah
    elif (event.startLong <= candidateEvent.startLong and event.endLong >= candidateEvent.endLong):
        return True # bentrok, dosen gabakal dateng atau ruangan full gabisa dipake
    else:
        return False

def isDomainConflict(domain1, domain2):
# cek apakah usulan sidang 1 (domain1) dengan usulan sidang 2 (domain2) bentrok
    if ((domain1.roomID == domain2.roomID) and isEventConflict(domain1.event, domain2.event)):
        return 1 # ruangan dan jamnya sama, berarti bentrok
    else:
        return 0

def countDomainConflicts():
# menghitung berapa banyak mahasiswa yang bentrok jadwal sidangnya
    result = 0
    for student1 in listStudent:
        for student2 in listStudent:
            # cross, kalo sama diri sendiri ya ga diitung wkwk -_-
            if (student1.studentID != student2.studentID):
                domain1 = student1.sidang.domains[student1.sidang.idxDomain]
                domain2 = student2.sidang.domains[student2.sidang.idxDomain]
                result += isDomainConflict(domain1, domain2)
    return int(result / 2)

def geneticAlgorithm(maxGeneration):
# implementasi genetic algorithm
    global listGen
    global listStudent
    fitness = [] # score fitness untuk tiap gen
    generation = 0
    while True:
        generation += 1
        # hitung fitness tiap gen
        del fitness[:]
        for i in range(len(listGen)):
            # pasangkan dulu student dengan domain sesuai dengan yang ada pada gen
            for j in range(len(listGen[i])):
                listStudent[j].sidang.idxDomain = listGen[i][j]
            # hitung berapa student yang konflik, fitnessnya makin kecil makin bagus
            fitness.append(countDomainConflicts())
            if fitness[i] == 0:
                return "Solusi ditemukan dalam generasi ke " + str(generation)
        # masih ada konflik di semua gen, cari gen terjelek dan terbagus
        idxMin = fitness.index(max(fitness))
        idxMax = fitness.index(min(fitness))
        # gak nemu solusi sampai generation ke-maxGeneration
        if generation == maxGeneration:
            # pasangkan lagi student dengan domain kepunyaan gen terbaik (fitness terkecil)
            for i in range(len(listGen[idxMax])):
                listStudent[i].sidang.idxDomain = listGen[idxMax][i]
            return "Tidak ditemukan solusi dalam " + str(generation) + " generasi"
        # lanjut ke generation selanjutnya
        else:
            # gen jelek timpa dengan gen bagus
            for i in range(len(listStudent)):
                listGen[idxMin][i] = listGen[idxMax][i]
            # kawin silang TANPA mutasi, mulai dari idxBelah (random) sampai index terakhir
            idxBelah = randint(1, len(listStudent) - 2)
            for i in range(idxBelah, len(listStudent)):
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
                studentMutasi = randint(0, len(listStudent) - 1)
                domainMutasi = randint(0, len(listStudent[studentMutasi].sidang.domains) - 1)
                gen[studentMutasi] = domainMutasi

def runGA():
# inisialisasi sebelum manjalankan genetic algorithm
    global listGen
    # atur domain
    for student in listStudent:
        student.initSidang()
    # atur gen
    for i in range(len(listGen)):
        del listGen[i][:]
        # untuk setiap mahasiswa pilih salah 1 domain (kemungkinan jadwal sidang) secara acak
        for student in listStudent:
            listGen[i].append(randint(0, len(student.sidang.domains) - 1))
    try:
        return geneticAlgorithm(20)
    except Exception as e:
        raise Exception('Failed to get solution: ' + str(e))

def saveResult():
# mencetak usulan jadwal sidang
    global listStudent
    listStudent.sort(key = lambda student : student.sidang.domains[student.sidang.idxDomain].event.startLong)
    listResult = []
    for student in listStudent:
        idxDomain = student.sidang.idxDomain
        domain = student.sidang.domains[idxDomain]
        # cari ruangan
        room = None
        for roomIterator in listRoom:
            if (roomIterator.roomID == domain.roomID):
                room = roomIterator
                break
        # data untuk upload ke firebase
        result = {"studentID" : student.studentID, "pembimbingID" : student.pembimbingID, "pengujiID" : student.pengujiID,
            "roomID" : room.roomID, "start" : domain.event.startDate, "end" : domain.event.endDate}
        listResult.append(result)
    # upload ke firebase
    try:
        dbFirebase.child('result').remove(tokenFirebase)
        dbFirebase.child('result').set(listResult, tokenFirebase)
    except Exception as e:
        raise Exception('Failed to upload result to Firebase: ' + str(e))

def periodParser(unparsedPeriod):
    global sidangPeriod
    sidangPeriod = Event(None, 'Masa Sidang', unparsedPeriod['start'], unparsedPeriod['end'])

def studentParser(unparsedStudents):
    global listStudent
    del listStudent[:]
    for unparsedStudent in unparsedStudents:
        studentID = unparsedStudent['studentID']
        name = unparsedStudent['name']['first'] + ' ' + unparsedStudent['name']['last']
        email = unparsedStudent['email']
        topic = unparsedStudent['topics']
        pembimbingID = unparsedStudent['pembimbingID']
        pengujiID = unparsedStudent['pengujiID']
        # now we append all of those information here
        listStudent.append(Student(studentID, name, email, topic, pembimbingID, pengujiID))

def lecturerParser(unparsedLecturers):
    global listLecturer
    del listLecturer[:]
    for unparsedLecturer in unparsedLecturers:
        lecturerID = unparsedLecturer['lecturerID']
        name = unparsedLecturer['name']['first'] + ' ' + unparsedLecturer['name']['last']
        email = unparsedLecturer['email']
        topics = unparsedLecturer['topics']
        events = []
        for event in unparsedLecturer['events']:
            events.append(Event(None, 'Sibuk', event['start'], event['end']))
        # now we append all of those information here
        listLecturer.append(Lecturer(lecturerID, name, email, topics, events))

def roomParser(unparsedRooms):
    global listRoom
    del listRoom[:]
    for unparsedRoom in unparsedRooms:
        roomID = unparsedRoom['roomID']
        name = unparsedRoom['name']
        email = unparsedRoom['email']
        events = []
        for event in unparsedRoom['events']:
            events.append(Event(None, 'Dipakai', event['start'], event['end']))
        # now we append all of those information here
        listRoom.append(Room(roomID, name, email, events))

def connectFirebase():
    global dbFirebase
    global tokenFirebase
    config = {
      "apiKey": "AIzaSyBDd1cTxxIAjK-MsJu3d6bLJdAe_I3M0nk",
      "authDomain": "console.firebase.google.com/project/ppl-scheduling",
      "databaseURL": "https://ppl-scheduling.firebaseio.com",
      "storageBucket": "ppl-scheduling.appspot.com",
      "serviceAccount": "credentials/firebase.json"
    }
    email = '13514052@std.stei.itb.ac.id'
    password = 'PPL-K2E'
    try: # ambil data dari firebase
        firebase = pyrebase.initialize_app(config)
        tokenFirebase = firebase.auth().sign_in_with_email_and_password(email, password)['idToken']
        dbFirebase = firebase.database()
    except Exception as e:
        raise Exception('Failed to connect to Firebase: ' + str(e))

def parseDatabase():
    try: # parse data
        unparsedData = dbFirebase.child('raw').get().val()
        periodParser(unparsedData['period'])
        roomParser(unparsedData['listRoom'])
        lecturerParser(unparsedData['listLecturer'])
        studentParser(unparsedData['listStudent'])
    except Exception as e:
        raise Exception('Failed to parse data from Firebase: ' + str(e))

def getCredential(email):
    try:
        path = os.path.join(TOKENPATH, email + '.json')
        store = Storage(path)
        credential = store.get()
        if ((credential is None) or (credential.invalid)):
            scope = 'https://www.googleapis.com/auth/calendar'
            flow = client.flow_from_clientsecrets(TOKENCALENDARPATH, scope)
            flow.user_agent = 'Penjadwalan Seminar/Sidang'
            flag = argparse.ArgumentParser(parents = [tools.argparser]).parse_args()
            credential = tools.run_flow(flow, store, flag)
        return credential
    except Exception as e:
        raise Exception('Failed to get user\'s token: ' + str(e))

def connectCalendar(credential):
    http = credential.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http = http)
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

######################################## VARIABLE ########################################

flask = Flask(__name__)
api = Api(flask)
dbFirebase = None
tokenFirebase = ''
sidangPeriod = None
FORTYMINUTESTOSECOND = 2400
HOURTOSECOND = 3600
DAYTOSECOND = 86400
WEEKTOSECOND = 604800
listGen = [[], [], [], []] # 4 gen (4 populasi), masing-masing gen berupa list of idxDomain (elemennya sebanyak listStudent)
listStudent = []
listLecturer = []
listRoom = []
TOKENPATH = os.path.join(os.getcwd(), 'credentials')
TOKENCALENDARPATH = os.path.join(TOKENPATH, 'calendar.json')

######################################## MAIN ########################################

api.add_resource(Home, '/', endpoint = "home")
api.add_resource(Scheduler, '/schedule')
api.add_resource(Login, '/login')
parser = reqparse.RequestParser()

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    flask.run(debug=False, port=port, host='0.0.0.0')

# testing Scheduler
# try:
#     connectFirebase()
#     parseDatabase()
#     result = runGA()
#     saveResult()
#     print result
# except Exception as e:
#     print str(e)

# testing Login
# try:
#     connectFirebase()
#     parseDatabase()
#     connectCalendar(getCredential('mrnaufal17@gmail.com'))
#     print 'haha'
# except Exception as e:
#     print str(e)