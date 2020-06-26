from new_models import Student, Teacher, Schedule_maker


# STUDENTS
students = []

students.append( Student(0))
students[0].set_available_time( **{ "pon":(7,10), "wt":(0,0), "srd":(10,12), "czw":(0,0), "pt":(10,15) } )

students.append( Student(1))
students[1].set_available_time( **{ "pon":(0,0), "wt":(7,11), "srd":(0,0), "czw":(11,16), "pt":(12,15) } )

students.append( Student(2))
students[2].set_available_time( **{ "pon":(7,14), "wt":(8,9), "srd":(7,9), "czw":(0,0), "pt":(8,10) } )

students.append( Student(3))
students[3].set_available_time( **{ "pon":(0,0), "wt":(0,0), "srd":(13,15), "czw":(7,11), "pt":(9,11) } )

students.append( Student(4))
students[4].set_available_time( **{ "pon":(0,0), "wt":(0,10), "srd":(0,0), "czw":(0,0), "pt":(7,13) } )

students.append( Student(5) )
students[5].set_available_time( **{ "pon":(9,12), "wt":(8,11), "srd":(0,0), "czw":(0,0), "pt":(10,13) } )

students.append( Student(6))
students[6].set_available_time( **{ "pon":[(12,14), (18,22)], "wt":(0,0), "srd":(11,13), "czw":(8,10), "pt":(0,0) } )

students.append( Student(7) )
students[7].set_available_time( **{ "pon":(0,0), "wt":(7,9), "srd":(0,0), "czw":(0,0), "pt":(7,9) } )

students.append( Student(8))
students[8].set_available_time( **{ "pon":(9,11), "wt":(0,0), "srd":(10,15), "czw":(0,0), "pt":(12,18) } )


#"zrobic tak ze liczenie godzin dostepnych dla students bierze pod uwage rozklad nauczyciela"
"""zeby przy liczeniu minimalnej ilosci godzin do szybkiego return bralo pod uwage faktycznie lekcji moze
byc podczas dnia wedlug dostepnosci uczniow"""



### TESTOWE PON-PT CALY DZIEN JEDEN STUDENT ###
"""
students.append( Student(0) )
students[0].set_available_time( **{ "pon":(7,15) } )

students.append( Student(1) )
students[1].set_available_time( **{ "wt":(7,15) } )

students.append( Student(2) )
students[2].set_available_time( **{ "srd":(7,15) } )

students.append( Student(3) )
students[3].set_available_time( **{ "czw":(7,15) } )

students.append( Student(4) )
students[4].set_available_time( **{ "pt":(7,15) } )
"""













#students2=students[:]
# TEACHER
teacher = Teacher()
teacher.set_available_time( **{ "pon":[(7,15)], "wt":(7,15), "srd":(7,15), "czw":(7,15), "pt":(7,15) } )

# sched =  (teacher, students, debug=False)
# simple_sched = sched.simple_schedule_creator()


# for key, val in simple_sched.items():
#     print(key, val)

# for student in students2:
#     print(student, student.jazdy_in_a_week,student.schedule)

# print( sched.value_of_schedule(simple_sched, student_ls=students2, full_evaluation=True, no_jazdy_together=True))
students2 = students[:]
sched =  Schedule_maker(teacher, students)
full_sched = sched.recursive_schedule_maker(level=0)

print(full_sched)
exit()