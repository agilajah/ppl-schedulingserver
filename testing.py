print("wawaw")
tset = "2002-07-31 00:00:05"
print(tset)

#test dateToLong
print(dateToLong(tset))

#test LongToDate
print(longtoDate(dateToLong(tset)))

# STRUKTUR DATA
print("==========================================================")
print("test event")
#test create event
myEvent = Event(1, "makan baso", '2017-05-07 07:00:00', '2017-05-07 09:00:00')
print(myEvent.event_id)
print(myEvent.date_start)
print(myEvent.date_end)
print(myEvent.name)
print(myEvent.long_start, longtoDate(myEvent.long_start))
print(myEvent.long_end, longtoDate(myEvent.long_end))
print(getEventKey(myEvent))

print("==========================================================")
print("test room")
myRoom = Room(999, "kantin", "kantin@gmail.com", [myEvent])
print(myRoom.room_id)
print(myRoom.name)
print(myRoom.email)
for myEvents in myRoom.events:
    print(myEvents.event_id)
    print(myEvents.date_start)
    print(myEvents.date_end)
    print(myEvents.name)
    print(myEvents.long_start, longtoDate(myEvent.long_start))
    print(myEvents.long_end, longtoDate(myEvent.long_end))


print("==========================================================")
print("test domain")
myDomain = Domain(999, myEvent)
print(myDomain.room_id)
print(myDomain.event.event_id)
print(myDomain.event.date_start)
print(myDomain.event.date_end)
print(myDomain.event.name)
print(myDomain.event.long_start, longtoDate(myEvent.long_start))
print(myDomain.event.long_end, longtoDate(myEvent.long_end))
print(getEventKey(myDomain.event))

print("==========================================================")
print("test sidang")
mySidang = Sidang(13514066, [1234567])
print(mySidang.lecturers_id)
print(mySidang.events)
print(mySidang.domains)
print(mySidang.idxDomain)
print(mySidang.totalDomain)

print("==========================================================")
print("test student")
myStudent = Student(13514066, "bimo", "bimo@mama.com", "AI", [1234567])
print(myStudent.student_id)
print(myStudent.name)
print(myStudent.email)
print(myStudent.topic)
print(myStudent.dosbing_id)

print("==========================================================")
print("test isEventConflict")
event1 = Event(111, "test1", "2017-08-10 10:00:00", "2017-08-10 12:00:00")
event2 = Event(111, "test1", "2017-08-10 11:00:00", "2017-08-10 13:00:00")
event3 = Event(111, "test1", "2017-08-10 09:00:00", "2017-08-10 11:00:00")
event4 = Event(111, "test1", "2017-08-10 11:00:00", "2017-08-10 11:30:00")
event5 = Event(111, "test1", "2017-08-10 12:00:00", "2017-08-10 13:30:00")
print(isEventConflict(event1, event2))
print(isEventConflict(event1, event3))
print(isEventConflict(event1, event4))
print(isEventConflict(event3, event2))
print(isEventConflict(event3, event5))
testEvent = [event1, event2, event3, event4, event5]

print("==========================================================")
#dummy rooms_list
room1= Room(222, "room1", "room1@gmail.com", [testEvent])
room2= Room(333, "room2", "room2@gmail.com", [testEvent])

print("test isEventConflict")
domain1 = Domain(222, event1)
domain2 = Domain(222, event2)
domain3 = Domain(222, event3)
domain4 = Domain(222, event4)
domain5 = Domain(333, event2)
print(isDomainConflict(domain1, domain2))
print(isDomainConflict(domain1, domain3))
print(isDomainConflict(domain1, domain4))
print(isDomainConflict(domain2, domain3))
print(isDomainConflict(domain1, domain5))

print("==========================================================")
print("test Lecturer")
lecturer1 = Lecturer(1234567, "lec1", "lec1@email.com", ["AI", "graphic"], testEvent)
print(lecturer1.lecturer_id)
print(lecturer1.name)
print(lecturer1.email)
print(lecturer1.topics)
print(lecturer1.events)
lecturer2 = Lecturer(2345678, "lec2", "lec2@email.com", ["AI", "graphic"], testEvent)
lecturer3 = Lecturer(3456789, "lec3", "lec3@email.com", ["graphic", "graphic"], testEvent)
lecturer4 = Lecturer(4567890, "lec4", "lec4@email.com", ["graphic", "security"], testEvent)
lecturer5 = Lecturer(5678901, "lec5", "lec5@email.com", ["game", "network"], testEvent)

#dummy students_list
student1 = Student(13514065, "bimo1", "bimo1@mama.com", "AI", [1234567, 2345678])
student2 = Student(13514067, "bimo2", "bimo2@mama.com", "graphic", [2345678, 3456789])
student3 = Student(13514068, "bimo3", "bimo3@mama.com", "security", [3456789])
student4 = Student(13514069, "bimo4", "bimo4@mama.com", "game", [5678901])
student5 = Student(13514060, "bimo5", "bimo5@mama.com", "network", [5678901])
students_list = [student1, student2, student3, student4, student5]

#countDomainConflicts(object) masih kurang variable
# print("==========================================================")
# print("test countDomainConflicts")
# print(countDomainConflicts("bait"))

#printResult(object) index error?
# printResult("bait") 