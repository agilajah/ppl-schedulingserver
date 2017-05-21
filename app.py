######################################## MODULE ########################################

from __future__ import division
from dateutil.parser import parse
from flask import Flask
from flask_restful import Api, Resource, reqparse
from googleapiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage
from random import randint
import argparse
import ast
import datetime
import httplib2
import json
import os
import pyrebase
import time

######################################## HANDLER ########################################

class Home(Resource):
    def get(self):
        return 'Penjadwalan Seminar/Sidang'
    def post(self):
        return self.get()

class Scheduler(Resource):
    def get(self):
        try:
            connectFirebase()
            parseDatabase()
            result = runGA()
            saveResult()
            print 'Done.'
            return result
        except Exception as e:
            return str(e)
    def post(self):
        return self.get()

class Login(Resource):
    def get(self):
        return self.post()
    def post(self):
        try:
            jsonRuby = parser.parse_args(strict = True)['token']
            jsonRuby = ast.literal_eval(jsonRuby)
            jsonPath = saveCredential(jsonRuby)
            connectCalendar(jsonPath)
            result = getCalendarList()
            print 'Done.'
            return result
        except Exception as e:
            return str(e)

class TestHehe(Resource):
    def get(self):
        sidangPeriod = Event(startDate = '2017-08-01', endDate = '2017-08-29')
        dosens = getAllUserEvents()
        for dosen in dosens:
            print dosen.lecturerID, dosen.name, dosen.email, dosen.topics
            for event in dosen.events:
                print event.name, event.startDate, event.endDate
        return 'OK'
    def post(self):
        return self.get()

######################################## STRUKDAT ########################################

class Event():
# kegiatan yang menyebabkan slot waktu tidak bisa dipakai (busy)
    def __init__(self, eventID = '', name = 'An event', startDate = '', endDate = ''):
        self.eventID = eventID
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        # tipe waktu disimpan juga dalam tipe integer supaya lebih mudah cek lebih besar/kecil nya
        self.startLong = dateToLong(startDate)
        self.endLong = dateToLong(endDate)

class Room():
# ruangan
    def __init__(self, roomID = '', name = 'A room', email = 'ruang.labtek5@gmail.com', events = []):
        print 'Creating a room object:', name
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
                startDate = longToDate(i)
                endDate = longToDate(i + DAYTOSECOND)
            else: # hari senin sampe jumat
                # ruangan tutup dari jam 6 sore sampe jam 7 besoknya
                startDate = longToDate(i + (HOURTOSECOND * 11))
                endDate = longToDate(i + DAYTOSECOND)
            self.events.append(Event(name = 'Tutup', startDate = startDate, endDate = endDate)) # tanpa eventID
            i += DAYTOSECOND

class Lecturer():
# dosen
    def __init__(self, lecturerID = '', name = 'Fulan', email = 'fulan@gmail.com', topics = [], events = []):
        print 'Creating a lecturer object:', name
        self.lecturerID = lecturerID
        self.name = name
        self.email = email
        self.topics = topics
        self.events = events # jadwal sibuk dosen
        self.events.sort(key = lambda event : event.startLong)

class Student():
# mahasiswa
# asumsi: mahasiswa selalu siap sedia, tidak punya jadwal sibuk
    def __init__(self, studentID = '', name = 'Fulan', email = 'fulan@gmail.com', topic = '', pembimbingID = [], pengujiID =[]):
        print 'Creating a student object:', name
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
    def __init__(self, studentID = '', lecturersID = []):
        print 'Creating a sidang object:', studentID
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
            candidateEvent = Event(name = 'Usulan sidang ' + str(self.studentID), startDate = longToDate(i), endDate = longToDate(i + HOURTOSECOND))
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
    return time.mktime(parse(date).timetuple())

def longToDate(seconds):
# input long, output string tanggal sesuai format google calendar / ISO
    return datetime.datetime.fromtimestamp(seconds).isoformat()

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
        print 'Running algorithm:', generation
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
    print 'Saving result to Firebase...'
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
    print 'Parsing sidang period data...'
    global sidangPeriod
    sidangPeriod = Event(name = 'Masa Sidang', startDate = unparsedPeriod['start'], endDate = unparsedPeriod['end'])

def studentParser(unparsedStudents):
    print 'Parsing student data...'
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
    print 'Parsing lecturer data...'
    global listLecturer
    del listLecturer[:]
    for unparsedLecturer in unparsedLecturers:
        lecturerID = unparsedLecturer['lecturerID']
        name = unparsedLecturer['name']['first'] + ' ' + unparsedLecturer['name']['last']
        email = unparsedLecturer['email']
        topics = unparsedLecturer['topics']
        events = []
        for event in unparsedLecturer['events']:
            events.append(Event(name = 'Busy', startDate = event['start'], endDate = event['end']))
        # now we append all of those information here
        listLecturer.append(Lecturer(lecturerID, name, email, topics, events))

def roomParser(unparsedRooms):
    print 'Parsing room data...'
    global listRoom
    del listRoom[:]
    for unparsedRoom in unparsedRooms:
        roomID = unparsedRoom['roomID']
        name = unparsedRoom['name']
        email = unparsedRoom['email']
        events = []
        for event in unparsedRoom['events']:
            events.append(Event(name = 'Busy', startDate = event['start'], endDate = event['end']))
        # now we append all of those information here
        listRoom.append(Room(roomID, name, email, events))

def connectFirebase():
    print 'Connecting to Firebase...'
    global dbFirebase
    global tokenFirebase
    # konfigurasi token yang digunakan untuk akses firebase
    config = {
      "apiKey": "AIzaSyBDd1cTxxIAjK-MsJu3d6bLJdAe_I3M0nk",
      "authDomain": "console.firebase.google.com/project/ppl-scheduling",
      "databaseURL": "https://ppl-scheduling.firebaseio.com",
      "storageBucket": "ppl-scheduling.appspot.com",
      "serviceAccount": "admin/firebase.json"
    }
    email = '13514052@std.stei.itb.ac.id'
    password = 'PPL-K2E'
    # connect dan ambil data dari firebase
    try:
        firebase = pyrebase.initialize_app(config)
        tokenFirebase = firebase.auth().sign_in_with_email_and_password(email, password)['idToken']
        dbFirebase = firebase.database()
    except Exception as e:
        raise Exception('Failed to connect to Firebase: ' + str(e))

def parseDatabase():
    # parse data dari firebase, asumsi koneksi (dbFirebase) sudah establish
    try:
        unparsedData = dbFirebase.child('raw').get().val()
        periodParser(unparsedData['period'])
        roomParser(unparsedData['listRoom'])
        lecturerParser(unparsedData['listLecturer'])
        studentParser(unparsedData['listStudent'])
    except Exception as e:
        raise Exception('Failed to parse data from Firebase: ' + str(e))

def saveCredential(jsonRuby):
    print 'Converting token...'
    # load token yang digunakan untuk akses google calendar
    with open('admin/calendar.json') as inFile:
        tokenCalendar = json.load(inFile)['installed']
    # ubah json dengan format ruby menjadi sesuai dengan python
    jsonPython = {
        "_module":"oauth2client.client",
        "scopes":[
          "https://www.googleapis.com/auth/calendar"
        ],
        "token_expiry":longToDate(jsonRuby['expiration_time_millis'] / 1000),
        "id_token":None,
        "user_agent":"Penjadwalan Seminar/Sidang",
        "access_token":jsonRuby['access_token'],
        "token_uri":tokenCalendar['token_uri'],
        "invalid":False,
        "token_response":{
            "access_token":jsonRuby['access_token'],
            "token_type":"Bearer",
            "expires_in":3600,
            "refresh_token":jsonRuby['refresh_token']
        },
        "client_id":tokenCalendar['client_id'],
        "token_info_uri":"https://www.googleapis.com/oauth2/v3/tokeninfo",
        "client_secret":tokenCalendar['client_secret'],
        "revoke_uri":"https://accounts.google.com/o/oauth2/revoke",
        "_class":"OAuth2Credentials",
        "refresh_token":jsonRuby['refresh_token'],
        "id_token_jwt":None
    }
    # dump ke file
    print 'Saving converted token...'
    filename = 'user/' + jsonRuby['email'] + '.json'
    with open(filename, 'w') as outFile:
        json.dump(jsonPython, outFile)
    # return jsonPath nya sekalian untuk connectCalendar
    return os.path.join(USERPATH, jsonRuby['email'] + '.json')

def connectCalendar(jsonPath):
    print 'Connecting to Google Calendar...'
    global calendarService
    # hanya establish connection, tidak mengambil data apa-apa
    try:
        credential = Storage(jsonPath).get()
        http = credential.authorize(httplib2.Http())
        calendarService = discovery.build('calendar', 'v3', http = http)
    except Exception as e:
        raise Exception('Failed to connect to Google Calendar: ' + str(e))

def getCalendarList():
    print 'Retrieving calendar list...'
    # dapatkan semua kalender, asumsi koneksi (calendarService) sudah establish
    result =[]
    calendarList = calendarService.calendarList().list().execute()['items']
    for calendar in calendarList:
        result.append({'id':calendar['id'], 'summary':calendar['summary']})
    return result

def getEvents(calendarList):
    print 'Retrieving events...'
    # asumsi koneksi (calendarService) sudah establish dan sesuai dengan calendarList nya
    result = []
    timeMin = longToDate(sidangPeriod.startLong) + '+07:00'
    timeMax = longToDate(sidangPeriod.endLong) + '+07:00'
    for calendar in calendarList:
        # dapatkan semua event di tiap kalendar pada rentang waktu sidangPeriod
        events = calendarService.events().list(calendarId = calendar['id'], timeMin = timeMin, timeMax = timeMax, singleEvents = True).execute()['items']
        for event in events:
            eventID = event['id']
            name = event['summary']
            startDate = event['start']
            if ('dateTime' in startDate):
                startDate = startDate['dateTime']
            elif ('date' in startDate):
                startDate = startDate['date']
            endDate = event['end']
            if ('dateTime' in endDate):
                endDate = endDate['dateTime']
            elif ('date' in endDate):
                endDate = endDate['date']
            result.append(Event(eventID, name, startDate, endDate))
    return result

def getAllUserEvents():
    result = []
    for filename in os.listdir(USERPATH):
        # load semua token milik dosen, dapatkan jadwalnya masing-masing
        try:
            jsonPath = os.path.join(USERPATH, filename)
            connectCalendar(jsonPath)
            events = getEvents(getCalendarList())
            result.append(Lecturer(events = events))
        except Exception as e:
            continue
    return result

######################################## VARIABLE ########################################

dbFirebase = None
tokenFirebase = ''
calendarService = None
sidangPeriod = None
FORTYMINUTESTOSECOND = 2400
HOURTOSECOND = 3600
DAYTOSECOND = 86400
WEEKTOSECOND = 604800
listGen = [[], [], [], []] # 4 gen (4 populasi), masing-masing gen berupa list of idxDomain (elemennya sebanyak listStudent)
listStudent = []
listLecturer = []
listRoom = []
USERPATH = os.path.join(os.getcwd(), 'user')
ADMINPATH = os.path.join(os.getcwd(), 'admin')

######################################## MAIN ########################################

flask = Flask(__name__)
api = Api(flask)
api.add_resource(Home, '/', endpoint = "home")
api.add_resource(Scheduler, '/schedule')
api.add_resource(Login, '/login')
api.add_resource(TestHehe, '/testhehe')
parser = reqparse.RequestParser()
parser.add_argument('token', type = str, required = False, help='Please submit a valid json.', location = 'json')

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    flask.run(debug=False, port=port, host='0.0.0.0')

######################################## TEST ########################################

# testing geneticAlgorithm
# try:
#     connectFirebase()
#     print 'Updating rooms schedule...'
#     #
#     print 'Updating users schedule...'
#     #
#     parseDatabase()
#     result = runGA()
#     saveResult()
#     print 'Done.'
#     print result
# except Exception as e:
#     print str(e)

# testing login
# ikhwan = json.dumps({
#     "email":"ikhwan.m1996@gmail.com",
#     "client_id":"637504288783-0868kkjoilbol4l8o8bum9s9fkjji38t.apps.googleusercontent.com",
#     "access_token":"ya29.GltPBGyBm5f0u4U524qowqjsVjA-MiYTU3Xh7M-WDPW1odiq80sPaR6l084PcGjJckyX2kfJQqgDUgbTtMSFAPC-t5YF65n1HNkp9xQfverL4xzTeRVNC9ITl1Y2",
#     "refresh_token":"1/Y1mQ51qnJGZSe3rOk2BVZQBY_b_Q07DLWBuIZEC9egQ",
#     "scope":[
#         "https://www.googleapis.com/auth/calendar"
#     ],
#     "expiration_time_millis":1495212704000
# })
# try:
#     jsonRuby = json.loads(ikhwan)
#     jsonPath = saveCredential(jsonRuby)
#     connectCalendar(jsonPath)
#     result = getCalendarList()
#     print 'Done.'
#     print json.dumps(result)
# except Exception as e:
#     print str(e)

# testing getEvents
# connectFirebase()
# parseDatabase()
# jsonPath = os.path.join(USERPATH, 'mrnaufal17@gmail.com.json')
# connectCalendar(jsonPath)
# calendarList = getCalendarList()
# result = getEvents(calendarList)
# print 'Done.'
# for hehe in result:
#     print hehe.name, hehe.startDate, hehe.endDate

# testing getAllUserEvents
# sidangPeriod = Event(startDate = '2017-08-01', endDate = '2017-08-29')
# dosens = getAllUserEvents()
# for dosen in dosens:
#     print dosen.lecturerID
#     print dosen.name
#     print dosen.email
#     print dosen.topics
#     for event in dosen.events:
#         print event.name, event.startDate, event.endDate