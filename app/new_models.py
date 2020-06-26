from copy import copy, deepcopy
from inspect import getframeinfo, stack
import sys
from debug_function.debug import DEBUG
import models

# debug_code standard, Schedule().schedule_maker => [x[0,1,2] for x in "Schedule".split("_")][0]+"_"+"".join([ x[0] for x in "schedule_maker".split('_')]) + "%d"
# = Sch_sm0
all_debug_codes = ["Sch_lj0", "Sch_lj1", "Tea_catfj0", "Tea_catfj1", "Sch_pnj0", "Sch_pnj1", "Sch_mak_rsm_level", "Sch_mak_rsm_SEPARATE",
        "Sch_mak_rsm_psfh", "Sch_mak_rsm_so", "Sch_mak_rsm_csw","Sch_mak_rsm_pnj", "Sch_mak_rsm_so1", "Sch_mak_rsm_csw1"," Sch_mak_rsm_pnj1",
        "Sch_mak_rsm_nca", "Sch_mak_rsm_nj1", "Sch_es1", "Sch_es2", "Sch_es_nemjl", "Sch_es_minjazdy", "Sch_mak_rsm_bad_ret1", "Sch_mak_rsm_sd2",
        "Sch_mak_rsm_sd1", "Sch_mak_rsm_ret1" , "Sch_mak_lolbjiw1", "Sch_mak_losbjiw_ret", "Sch_mak_bs1", "Sch_mak_bs2", "Sch_es_mj1", "Sch_es3",
        "Sch_mak_rsm0", "Sch_unj1", "Sch_mak_rsm_nj3", "Sch_pnj_ret1", "Stu_jis1", "Sch_mak_rsm_schls1", "Sch_mak_rsm_Aac1", "positional",
        "Stu_jis_sch1", "Sch_mak_rsm_schev1", "Sch_mak_rsm_RETURN", "Sch_mak_rsm_BEST", "Sch_es_minjazdy1", "Sch_mak_init3", "Sch_bpo_ret1", "Sch_mak_rsm_schv1",
        "Sch_mak_rsm_mxos1_drop", "Sch_mjm_retF", "Sch_mak_ssbp_retLS", "Sch_mak_ssba_retLS", "Sch_mak_init_stud1", "Sch_es_maxday_jazdy1", "Sch_es_maxday_jazdy2",
        "Sch_mjid_retF"  ]

# if u are intersted in debugging Schedule_maker recursive_schedule_maker then debug_code_ls = [x for x in all_debug_codes if x[:11]=="Sch_mak_rsm"]

debug_codes_ls = ["Sch_lj0", "Tea_catfj0", "Tea_catfj1", "Sch_pnj0", "Sch_pnj1", "Sch_mak_rsm_SEPARATE", "Sch_mak_rsm_level"]
debugging = True
debug_codes_ls = [ x for x in all_debug_codes if x[:7]=="Sch_mak" ]
debug_codes_ls = ["Sch_mak_rsm_level", "Sch_mak_rsm_RETURN", "Sch_mak_rsm_BEST", "Sch_mak_rsm_schv1",
        "Sch_mak_ssbp_retLS", "Sch_mak_ssba_retLS", "Sch_mak_init_stud1" ]


class Student:
    def __init__(self, S_id, **kwargs):
        self.available = { "pon":[(0,0)], "wt":[(0,0)], "srd":[(0,0)], "czw":[(0,0)], "pt":[(0,0)], "sob":[(0,0)], "niedz":[(0,0)]  }

        self.min_jazdy = kwargs["jazdy"] if "min_jazdy" in kwargs else 0
        self.priority = kwargs["priority"] if "priority" in kwargs else self.min_jazdy
        self.max_day_jazdy = kwargs["max_day_jazdy"] if "max_day_jazdy" in kwargs else 2
        self.jazdy_in_a_week = 0 # variable used to control how many jazdy Student needs to have more
        self.available_time_sum = 0
        
        self.id = S_id
        self.name       = kwargs["name"] if "name" in kwargs else "John"
        self.last_name  = kwargs["last_name"] if "last_name" in kwargs else "Doe"

        # here are variables used for saving the schedule  a
        self.schedule = { "pon":[], "wt":[], "srd":[], "czw":[], "pt":[], "sob":[], "niedz":[] }
        self.time_available_with_teacher = []
        self.hours_jazda_can_start = {"pon":[], "wt":[], "srd":[], "czw":[], "pt":[], "sob":[], "niedz":[]}
        self.time_in_day = {"pon":0, "wt":0, "srd":0, "czw":0, "pt":0, "sob":0, "niedz":0}

    def __repr__(self):
        return "<%s.%s. Student nr %d>" %(self.name[0], self.last_name[0], self.id)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.id == other.id

    def set_available_time(self, **kwargs) -> None:
        try:
            for day, time in kwargs.items():
                if type(time) == list:
                    self.available[day.lower()] = time
                elif type(time) == tuple:
                    self.available[day.lower()] = [time]
                else:
                    print("Wrong format of input time of availability.")
                    print("Zły format wprowadzonych danych czasu dostępności.")
        except:
            print("Wrong format of input time of availability.")
            print("Zły format wprowadzonych danych czasu dostępności.")
        
        # ustalajac dostepnosc bierze pod uwagę czas dostepnosci wspolny z nauczycielem
        if not ("teacher" in kwargs and not "teacher_time_count" in kwargs and type(kwargs["teacher"])==Teacher and kwargs["teacher_time_count"]):
            for day, interval_time in self.available.items():
                # browse through every day
                for interval in interval_time:
                    # check every time interval in a day
                    time_start = interval[0]
                    time_end = interval[1]
                    if time_end - time_start >=2:
                        self.available_time_sum += time_end-time_start
        else:
            self.time_with_teacher(kwargs["teacher"])
            for time_in_day in  self.time_in_day.values():
                self.available_time_sum += time_in_day

    def requirements_made(self, schedule) -> bool:
        return self.jazdy_in_schedule(schedule) >= self.min_jazdy

    def is_available_in_this_time(self, day: str, start_hour: int) -> bool:
        """Takes in day and start hour of class and returns boolean if jazda can be made or not"""
        for interval in self.available[day]:
            if start_hour >= interval[0] and start_hour+2 <= interval[1]:
                return True
        return False

    def jazdy_in_schedule(self, schedule: dict) -> int:
        """counts jazdy in a schedule"""
        jazdy_in_sched = 0
        for classes_list in schedule.values():
            for jazda in classes_list:
                if jazda.student==self:
                    jazdy_in_sched+=1
        DEBUG(debugging, (self, "jazdy in schedule:", jazdy_in_sched, schedule), debug_code="Stu_jis_sch1", debug_codes=debug_codes_ls)
        return jazdy_in_sched

    def update_hours_jazda_can_start(self) -> None:
        for day, jazdy in self.available.items():
            ls = [] # list with hours to start jazdy
            for jazda in jazdy:
                if jazda[1]-jazda[0]>=2:
                    ls += list(range(jazda[0], jazda[1]-1))
            self.hours_jazda_can_start[day] = ls

    def time_with_teacher(self, teacher: "Teacher") -> None:
        """counts start_hours shared with teacher in a day"""

        self.time_in_day = {"pon":0, "wt":0, "srd":0, "czw":0, "pt":0, "sob":0, "niedz":0}
        for day, hours in self.hours_jazda_can_start.items():
            try:
                last_hour = hours[0]
            except IndexError:
                continue
            # check for every start_hour if it is in teachers start_hours
            for hour in hours:
                if hour in teacher.hours_jazda_can_start[day]:
                    if hour-last_hour>1:
                        self.time_in_day[day] += 2
                    else:
                        self.time_in_day[day] += 1
            
            # add one hour if there was at least one start_hour together found 
            if self.time_in_day[day]>0:
                self.time_in_day[day] += 1


class Teacher:
    def __init__(self, **kwargs):
        self.available = { "pon":[(0,0)], "wt":[(0,0)], "srd":[(0,0)], "czw":[(0,0)], "pt":[(0,0)], "sob":[(0,0)], "niedz":[(0,0)] }
        self.hours_jazda_can_start = {"pon":[], "wt":[], "srd":[], "czw":[], "pt":[], "sob":[], "niedz":[]}

    def set_available_time(self, **kwargs):
        try:
            for day, time in kwargs.items():
                if type(time) == list:
                    self.available[day.lower()] = time
                elif type(time) == tuple:
                    self.available[day.lower()] = [time]
                else:
                    print("Wrong format of input time of availability.")
                    print("Zly format wprowadzonych danych czasu dostepnosci.")
        except:
            print("Wrong format of input time of availability.")
            print("Zly format wprowadzonych danych czasu dostepnosci.")

    def is_available_in_this_time(self, day: str, start_hour: int) -> bool:
        for interval in self.available[day]:
            if start_hour>=interval[0] and start_hour+2<=interval[1]:
                return True
        return False

    def closest_available_time_for_jazda(self, start_day: str, start_hour: int) -> bool or dict:
        """return {"day":start_day, "hour":start_hour}"""
        if self.is_available_in_this_time(start_day, start_hour):
            DEBUG(debugging, ("return dict:", {"day":start_day, "hour":start_hour}), debug_code="Tea_catfj1", debug_codes=debug_codes_ls)
            return {"day":start_day, "hour":start_hour}
            
        else:
            after_the_start_day = False # used to find out if we are after or before the day in a week
            for day, intervals in self.available.items():
                if day!=start_day and not after_the_start_day:
                    continue
                else:
                    # kiedy pierwszy raz wejdzie w else to after_the_start_day bedzie jeszcze False
                    # ale kolejne dni beda ustawialy juz start_hour na poczatkowa godzine pierwszego interval 
                    if after_the_start_day:
                        if intervals and intervals[0]:
                            start_hour = intervals[0][0]
                        # czyli nie ma zadnych wolnych lekcji, wiec przeskakujemy do nastepnego dnia
                        else:
                            continue
                        
                    after_the_start_day = True
                    for interval in intervals:
                        if start_hour+2<=interval[1]:
                            for time in range(start_hour, interval[1]-1):
                                if self.is_available_in_this_time(start_day, time):
                                    DEBUG(debugging, ("return dict:", {"day":day, "hour":time}), debug_code="Tea_catfj0", debug_codes=debug_codes_ls)
                                    return {"day":day, "hour":time}
                    
        return False

    def update_hours_jazda_can_start(self) -> None:
        """updates dict with start hours"""
        for day, jazdy in self.available.items():
            ls = [] # list with hours to start jazdy
            for jazda in jazdy:
                if jazda[1]-jazda[0]>=2:
                    ls += list(range(jazda[0], jazda[1]-1))
            self.hours_jazda_can_start[day] = ls


class Jazda:
    def __init__(self, start_day:str, start_hour:int, student: Student, schedule_parent: "Schedule"):
        self.day = start_day
        self.start_hour = start_hour
        self.end_hour = start_hour+2
        self.student = student
        self.schedule_parent = schedule_parent

    def  __repr__(self):
        return "<{}-{} St.{}>".format( self.start_hour, self.end_hour, self.student.id)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return self.day==other.day and self.start_hour==other.start_hour and self.student==other.student


class Schedule:
    def __init__(self, teacher: Teacher, students_ls: list, **kwargs):
        self.dict_schedule = kwargs["dict_schedule"] if "dict_schedule" in kwargs else {"pon":[], "wt":[], "srd":[], "czw":[], "pt":[],"sob":[], "niedz":[]}
        self.teacher = teacher
        self.students_ls = students_ls
        self.update_next_jazda()
        self.done = False
        self.value = None

    def __repr__(self):
        return str(self.dict_schedule)

    def __eq__(self, other: "Schedule"):
        if type(other) != type(self):
            return False
        return self.dict_schedule == other.dict_schedule

    def possible_next_jazda(self, **kwargs) -> dict or None:
        """returns {"day":day, "hour":start_time} or False if None jazda are available"""
        last_jazda = self.last_jazda()
        DEBUG(debugging, ("last_jazda", last_jazda), debug_code="Sch_pnj0", debug_codes=debug_codes_ls)
        if type(last_jazda) is Jazda:
            return_val = self.teacher.closest_available_time_for_jazda(last_jazda.day, last_jazda.end_hour)
            DEBUG(debugging, ("return_val", return_val), debug_code="Sch_pnj_ret1", debug_codes=debug_codes_ls )
            return return_val
        elif last_jazda is None:
            return_val = self.teacher.closest_available_time_for_jazda("pon", 0)
            DEBUG(debugging, ("return_val", return_val), debug_code="Sch_pnj_ret1", debug_codes=debug_codes_ls )
            return return_val

        DEBUG(debugging, ("ERROR last_jazda", last_jazda), debug_code="Sch_pnj1", debug_codes=debug_codes_ls)

    def last_jazda(self) -> Jazda or None:
        "None if schedule is empty, else returns last jazda object."
        """DEBUG Code = 'Sch_lj0' """
        for day, jazdy in reversed( self.dict_schedule.items() ):
            if jazdy:
                DEBUG(debugging, ("jazda:", jazdy[-1]), debug_code="Sch_lj0", debug_codes=debug_codes_ls)
                return jazdy[-1]
        DEBUG(debugging, ("The Schedule is empty", ""), debug_code="Sch_lj1", debug_codes=debug_codes_ls)
        return None

    def update_next_jazda(self) -> None:
        self.next_jazda = self.possible_next_jazda()
        DEBUG(debugging, ("next_jazda:", self.next_jazda), debug_code="Sch_unj1", debug_codes=debug_codes_ls)

    def next_day_and_hour(self, previous_day: str) -> bool or dict:
        found_day = False
        for day in self.dict_schedule.keys():
            if found_day:
                next_day = day
                break

            if day==previous_day:
                found_day = True
        # it is the last day
        return self.teacher.closest_available_time_for_jazda(next_day, 0)

    def min_jazdy_made(self, list_in=None) -> bool and (Student or dict):
        """Checks if minimum in a week and  maximum in a day of jazdy is made"""
        # because return xxxx, count !
        count = {}
        if not list_in == []:
            list_of_students_to_check = self.students_ls if list_in==None else list_in

            list_of_students = []
            
            for jazdy in self.dict_schedule.values():
                for jazda in jazdy:

                    # this if-else is responsible for counting in a week jazdy
                    if jazda.student.id in count:
                        count[jazda.student.id] += 1
                    else:
                        list_of_students.append(jazda.student)
                        # jazdy = 0; jazdy ++ # z tego wynika ze '1'
                        count.update( {jazda.student.id:1} )

            for student in list_of_students_to_check:
                if student.id in count:
                    if not count[student.id] >= student.min_jazdy:
                        DEBUG(debugging, ("This student has not enough jazdy:", jazda.student, ", .min_jazdy =", jazda.student.min_jazdy), debug_code="Sch_mjm_retF", debug_codes=debug_codes_ls  )
                        return False, student
                else:
                    if student.min_jazdy > 0:
                        return False, student

        return True, count

    def max_jazdy_in_day(self):
        """Checks if maximum in a day of jazdy is not surpassed"""
        for day, jazdy in self.dict_schedule.items():
            day_count = {}
            for jazda in jazdy:
                # this if-else is responsible for counting jazdyy in a day    
                if jazda.student.id in day_count:
                    day_count[jazda.student.id] += 1
                    if day_count[jazda.student.id] > jazda.student.max_day_jazdy:
                        DEBUG(debugging, ("This student has to much jazdy in a day:", jazda.student, ", .max_day_jazdy =", jazda.student.max_day_jazdy), debug_code="Sch_mjid_retF", debug_codes=debug_codes_ls  )
                        return False, jazda.student
                else:
                    day_count.update( {jazda.student.id:1} )

        return True, day_count
     
    def evaluate_self(self, **kwargs):
        """check for two yes/no type of requirements and then calculates the value
        can be run with 'no_srednia_z_odchylenie_standardowe=True',
        this will return True in self.value it means the branch is good to go.
        self.value=False only if it does not meet requirements like jazdy together
        or no min jazdy.
        When everything is good and full evaluation is run:
        self.value = odchylenie_standardowe, amount_of_jazdy"""
        DEBUG(debugging, ("evaluating_schedule", self.dict_schedule), debug_code="Sch_es1", debug_codes=debug_codes_ls )
        student_ls = self.students_ls
        DEBUG(debugging, ("running schedule evaluation"), ("-- students_ls:", student_ls), debug_code="Sch_es2", debug_codes=debug_codes_ls )

        if not( "no_min_jazdy" in kwargs and kwargs["no_min_jazdy"] ):
            # sprawdza czy dla kazdego ucznia zostala spelniona minimalna ilosc godzin
            BOOL, student = self.min_jazdy_made(kwargs["students_ls_for_min_jazdy"] if "students_ls_for_min_jazdy" in kwargs else None)
            DEBUG(debugging, ("return: BOOL", BOOL, ", student or count:", student), debug_code="Sch_es_minjazdy1", debug_codes=debug_codes_ls )
            if not BOOL:
                DEBUG(debugging, ("not enough jazdy in week:", student, "student.min_jazdy:", student.min_jazdy), debug_code="Sch_es_minjazdy", debug_codes=debug_codes_ls )
                return False

        if not( "no_max_jazdy_in_day" in kwargs and kwargs["no_max_jazdy_in_day"]):
            BOOL, student = self.max_jazdy_in_day()
            DEBUG(debugging, ("return: BOOL", BOOL, ", student or day_count:", student), debug_code="Sch_es_maxday_jazdy1", debug_codes=debug_codes_ls )
            if not BOOL:
                DEBUG(debugging, ("not enough jazdy in week:", student, "student.max_day_jazdy:", student.min_jazdy), debug_code="Sch_es_maxday_jazdy2", debug_codes=debug_codes_ls )
                return False

        if not ( "no_jazdy_together" in kwargs and kwargs["no_jazdy_together"] ):
            # sprawdza czy jazdy jedego dnia są obook siebie
            for student in self.students_ls:
                for day, jazdy in self.dict_schedule.items():
                    # jezeli w dniu jest wiecej niz dwie jazdy
                    if len(jazdy)>2:
                        student_had_jazda = False
                        for jazda in jazdy:
                            if jazda.student == student:
                                if not student_had_jazda:
                                    student_had_jazda = True
                                    end_hour = jazda.end_hour
                                else:
                                    if end_hour!=jazda.start_hour:
                                        DEBUG(debugging, ("jazdy not together for:", student), ("schedule:", self.dict_schedule), debug_code="Sch_es_mj1", debug_codes=debug_codes_ls )
                                        self.value = False
                                        return False
                                    else:
                                        end_hour = jazda.end_hour

        # gdyby ktos nie chcial standardowa srednia, return wywali blad
        odchylenie_standarowe_srednia = 0
        if not ( "no_srednia_z_odchylenie_standardowe" in kwargs and kwargs["no_srednia_z_odchylenie_standardowe"] ):
            min_of_jazdy_students_nested_ls = [ [] for x in range(41) ]
            sum_of_odchylenie_standardowe = 0 # potem zrobie z tego srednią
            ilosc_roznych_min_of_jazdy = 0 # to bedzie mianownik sredniej 
            for student in student_ls:
                # posortuj studentow zgodnie z .min_jazdy
                min_of_jazdy_students_nested_ls[student.min_jazdy].append( student )      
            not_empty_min_jazdy_ls = [ students for students in min_of_jazdy_students_nested_ls if students]
            DEBUG(debugging, ("not_empty_min_jazdy_ls", not_empty_min_jazdy_ls), debug_code="Sch_es_nemjl", debug_codes=debug_codes_ls )
            

            for students in not_empty_min_jazdy_ls:
                ilosc_roznych_min_of_jazdy+=1
                suma_of_jazdy_weekly = 0
                suma_kwadratow_wariancji = 0
                nr_of_students = len(students)

                for student in students:
                    jazdy_in_a_week = student.jazdy_in_schedule(self.dict_schedule)
                    suma_of_jazdy_weekly +=  jazdy_in_a_week
                    suma_kwadratow_wariancji += jazdy_in_a_week**2
                
                wariancja = suma_kwadratow_wariancji / nr_of_students - (suma_of_jazdy_weekly / nr_of_students)**2
                sum_of_odchylenie_standardowe += wariancja**0.5
            odchylenie_standarowe_srednia = sum_of_odchylenie_standardowe / ilosc_roznych_min_of_jazdy
            DEBUG(debugging, ("odchylenie standardowe srednia:", odchylenie_standarowe_srednia), debug_code="Sch_es3", debug_codes=debug_codes_ls )

        else: # this option is used to cut of branches that will return False anyway
            self.value = True
            return True

        # how many jazdy in a week
        amount_of_jazdy_in_week = 0
        for day, list_of_jazdy in self.dict_schedule.items():
            for jazda in list_of_jazdy:
                amount_of_jazdy_in_week += 1
         
        self.value = odchylenie_standarowe_srednia, amount_of_jazdy_in_week
        return odchylenie_standarowe_srednia, amount_of_jazdy_in_week   # just if anyone wants it in another variable

    def best_possible_odchylenie(self):
        """returns best possible value of odchylenie standardowe"""
        mianownik = len(self.students_ls)
        count = {}
        suma = 0
        for jazdy in self.dict_schedule.values():
            for jazda in jazdy:
                suma += 1
                if jazda.student.id in count:
                    count[jazda.student.id] += 1
                else:
                    count.update( {jazda.student.id:1} )

        # for debug
        copy_count = copy(count)

        #nr_rest_of_students = mianownik-len( count.keys())
        amounut_of_possible_jazdy = int(self.teacher.hours_available/2) - suma
        
        #jazdy_na_studenta = amounut_of_possible_jazdy // nr_rest_of_students
        #wolne_jazdy = amounut_of_possible_jazdy - jazdy_na_studenta * nr_rest_of_students
        
        for i in range(mianownik):
            if i in count:
                continue
            else:
                count.update( {i:0} )

        # for debug
        #wolne = wolne_jazdy

        while amounut_of_possible_jazdy>0:
            student_id = min( count, key=count.get )
            count[student_id] += 1
            amounut_of_possible_jazdy -= 1

        return_val = Schedule_maker.odchylenie_standardowe( *count.values() )
        DEBUG(debugging, ("count in", copy_count), ("-- return value:", return_val, "count:", count),  ("-- amount_of_possible_jazdy", amounut_of_possible_jazdy), debug_code="Sch_bpo_ret1", debug_codes=debug_codes_ls)
        return return_val
        

class Schedule_maker:
    def __init__(self, teacher, students_ls, **kwargs):
        self.students = students_ls
        self.teacher = teacher
        self.schedule = {"pon":[], "wt":[], "srd":[], "czw":[], "pt":[],"sob":[], "niedz":[]}
        """Sample Schedule format: ({day:[ [start_time_of_class, end_time_of_class, student] ] })
        ex.: {"pon":[ [7,9, self.students[12]], [9,11, self.students[3]], [11,13, self.students[0]], [13,15, self.students[5]] ]}"""
        self.max_odchyelnie_standardowe = kwargs["max_odchylenie_standardowe"] if "max_odchyelnie_standardowe" in kwargs else 1

        time_available_sum = 0
        for intervals in self.teacher.available.values():
            for interval in intervals:
                time = interval[1]-interval[0]
                if time >= 2:
                    time_available_sum += time

        self.teacher.hours_available = time_available_sum
        self.min_amount_of_jazdy = self.count_min_jazdy()
        DEBUG(debugging, ("Schedule_maker.teacher.hours_available", self.teacher.hours_available, "Schedule_maker.min_amount_of_jazdy", self.min_amount_of_jazdy), debug_code="Sch_mak_init3", debug_codes=debug_codes_ls )

        # setting list order
        nested_list = []
        prev_prio = None
        for st in self.sort_students_by_priority():
            if prev_prio == None:
                nested_list.append([st])
            elif prev_prio != st.priority:
                nested_list.append( [st] )
            else:
                nested_list[-1].append(st)
            prev_prio = st.priority

        sorted_list = []
        # sort students by availability while keeping the main segregation by priority
        for list_of_students in nested_list:
            if len(list_of_students)>2:
                sorted_list += self.sort_students_by_availability(list_of_students)
            else:
                sorted_list += list_of_students

        # do we have to check minimum of jazdy? lets create a list of students that have min above 0
        list_of_students_for_min_jazdy = []
        for student in sorted_list:
            if student.min_jazdy>0:
                list_of_students_for_min_jazdy.append( student )
        self.students_min_jazdy = list_of_students_for_min_jazdy

        self.students = sorted_list
        DEBUG(debugging, ("sorted students by priority and availability: self.students:", [ "<ID:{} ,prio:{}, ava:{}>".format(st.id, st.priority, st.available_time_sum) for st in self.students ]),  debug_code="Sch_mak_init_stud1", debug_codes=debug_codes_ls  )

    def sort_students_by_priority(self, list_in=[]):
        "sorts list so it starts from students with highest priority"
        students_ls = list_in if list_in else self.students[:]
        return sorted(students_ls, key=lambda x: x.priority)

        """     return_students_ls = []
        while len(students_ls)>0:
            student_with_highest_priority = None
            highest_priority = -10000000
            for student in students_ls:
                if student.priority > highest_priority:
                    highest_priority = student.priority
                    student_with_highest_priority = student

            # append stuudent with highest priority
            if not student_with_highest_priority == None:
                return_students_ls.append( students_ls.pop( students_ls.index( student_with_highest_priority)) )

        DEBUG(debugging, ("return_students_ls:", return_students_ls, ", this list should be empty:", students_ls), ("-- sorted students priorities", [ st.priority for st in return_students_ls ] ), debug_code="Sch_mak_ssbp_retLS", debug_codes=debug_codes_ls )
        return return_students_ls + students_ls """

    def sort_students_by_availability(self, list_in=[]):
        "sorts  list so it starts from students with lowest priority"
        students_ls = list_in if list_in else self.students[:]
        return sorted(students_ls, key = lambda x: x.available_time_sum)
        """
        return_students_ls = []
        while len(students_ls)>0:
            student_with_lowest_availability = None
            lowest_availability = 100000
            for student in students_ls:
                if student.available_time_sum < lowest_availability:
                    lowest_availability = student.available_time_sum
                    student_with_lowest_availability = student

            # append stuudent with highest priority
            if not student_with_lowest_availability == None:
                return_students_ls.append( students_ls.pop( students_ls.index( student_with_lowest_availability)) )

        DEBUG(debugging, ("return_students_ls:", return_students_ls, ", this list should be empty:", students_ls), ("-- sorted students availability", [ st.available_time_sum for st in return_students_ls ] ), debug_code="Sch_mak_ssba_retLS", debug_codes=debug_codes_ls )
        return return_students_ls + students_ls"""

    def count_min_jazdy(self):
        sched_maker = models.Schedule_maker(self.teacher, self.students)
        sched_maker.debug_lvl = 10000
        schedule = sched_maker.create_schedule_from_partial_schedule(sched_maker.schedule, self.students, self.teacher, level=0)
        DEBUG(debugging, ("schedule:", schedule), debug_code="Sch_mak_cmj_sched", debug_codes=debug_codes_ls)
        
        dictionary = {"pon":[], "wt":[], "srd":[], "czw":[], "pt":[],"sob":[], "niedz":[]}
        for day, hours in self.teacher.hours_jazda_can_start.items():
            

        


    @staticmethod
    def minus_one_adding(from_number):
        "returns n+(n-1)+(n-2)+...+1"
        return sum(list(range(from_number+1)))

    @staticmethod
    def list_of_schedule_by_jazdy_in_week( schedule_list, nr_of_schedules_to_return=1):
        "returns list of lists sorted by the most jazdy in week"
        nested_list_sorted_by_jazdy_in_week = [ [] for x in range(40) ]
        for schedule in schedule_list:
            if type(schedule.value) == tuple:
                nested_list_sorted_by_jazdy_in_week[schedule.value[1]].append( schedule )
            else:
                DEBUG(debugging, ("wrong schedule.value, schedule.value =", schedule.value), debug_code="Sch_mak_lolbjiw1", debug_codes=debug_codes_ls)
                # the first list of jazdy will be with the most jazdy in week
        nested_list_sorted_by_jazdy_in_week_no_empty_lists = reversed( [ list_of_jazdy for list_of_jazdy in nested_list_sorted_by_jazdy_in_week if not list_of_jazdy==[]  ])
        # get first three of best, get 2 out of the second best and take 1 from the worst for
        ret = []
        max_index = nr_of_schedules_to_return
        count = 0
        for jazdy in nested_list_sorted_by_jazdy_in_week_no_empty_lists:
            if count<max_index:
                for jazda in jazdy[:max_index-count]:
                    ret.append(jazda)
            else:
                break
            count += 1

        DEBUG(debugging, ("ret:", ret), debug_code="Sch_mak_losbjiw_ret", debug_codes=debug_codes_ls)
        return ret

    @staticmethod
    def list_of_schedule_by_odchylenie_standardowe(schedule_list, nr_of_schedules_to_return=1 ):
        "returns list sorted from lowest odchylenie to highest odchylenie"
        sorted_by_wariancja = []
        nr_of_schedules_to_return = Schedule_maker.minus_one_adding( nr_of_schedules_to_return )
        
        for schedule in schedule_list:
            index = 0
            # if not empty
            if sorted_by_wariancja:
                while index <= len( sorted_by_wariancja )-1:
                    if schedule.value[1] < sorted_by_wariancja[ index ].value[1]:
                        sorted_by_wariancja = sorted_by_wariancja[:index] + [schedule] + sorted_by_wariancja[index:]
                        break
                    index += 1
                else:
                    sorted_by_wariancja.append( schedule )
            else:
                sorted_by_wariancja.append( schedule )

        return sorted_by_wariancja[:nr_of_schedules_to_return]

    @staticmethod
    def odchylenie_standardowe(*lista):
        mian = len(lista)
        suma = sum(lista)
        war_suma = sum(map(lista, lambda x: x**2))
        return ( war_suma/mian - (suma/mian)**2 )**0.5

    def best_schedules(self, schedule_list, nr_of_top_schedules=1, **kwargs ):
        "take in list and return best, or top best"
        # the first list of jazdy will be with the most jazdy in week
        if "odchylenie_first" in kwargs and kwargs["odchylenie_first"]:
            rtn_ls = self.list_of_schedule_by_jazdy_in_week( self.list_of_schedule_by_odchylenie_standardowe(schedule_list, nr_of_top_schedules, **kwargs) )
            DEBUG(debugging, ("return:", rtn_ls), debug_code="Sch_mak_bs1", debug_codes=debug_codes_ls )
            return rtn_ls
        
        else:
            rtn_ls = self.list_of_schedule_by_odchylenie_standardowe( self.list_of_schedule_by_jazdy_in_week(schedule_list, nr_of_top_schedules, **kwargs) )
            DEBUG(debugging, ("return:", rtn_ls), debug_code="Sch_mak_bs2", debug_codes=debug_codes_ls )
            return rtn_ls

    def recursive_schedule_maker(self, **kwargs):
        # schedule if not found in kwargs is set to default
        DEBUG(debugging, ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"), debug_code="Sch_mak_rsm0", debug_codes=debug_codes_ls)
        DEBUG(debugging, ("level:", kwargs["level"]), debug_code="Sch_mak_rsm_level", debug_codes=debug_codes_ls )
        kwargs["level"] += 1
        schedule = kwargs["schedule"] if "schedule" in kwargs else Schedule(self.teacher, self.students)
        # even
        DEBUG(debugging, ("Schedule.next_jazda:", schedule.next_jazda), debug_code="Sch_mak_rsm_nj3", debug_codes=debug_codes_ls)
        start_day = schedule.next_jazda["day"]
        start_hour = schedule.next_jazda["hour"]

        # inside are Schedule objects
        schedule_ls = []
        schedule_done = []
        # used to check if new class was added
        new_class_added = False

        "Not done yet, we have to sort them by who has smallest number of jazdy"
        sorted_list_of_students = self.students

        # appends available jazda
        for interval in self.teacher.available[start_day]:
            if new_class_added:
                break

            if start_hour>=interval[0] and interval[1]>=start_hour+2:
                pos_next_jazda2 = False
                DEBUG(debugging, ("possible jazda for hours:", start_hour, "-", start_hour+2), debug_code="Sch_mak_rsm_psfh", debug_codes=debug_codes_ls )
                for student in sorted_list_of_students:
                    if student.is_available_in_this_time(start_day, start_hour):
                        new_class_added = True
                        DEBUG(debugging, ("creating schedule with: ", student), debug_code="Sch_mak_rsm_csw", debug_codes=debug_codes_ls )
                        schedule_out = deepcopy( schedule )
                        schedule_out.dict_schedule[start_day].append( Jazda(start_day, start_hour, student, schedule_out) )
                        DEBUG(debugging, ("schedule_out", schedule_out), debug_code="Sch_mak_rsm_so", debug_codes=debug_codes_ls )

                        # is used to stop from checking possible jazda every time
                        if pos_next_jazda2 == False:
                            possible_next_jazda = schedule_out.possible_next_jazda()
                            pos_next_jazda2 = True
                        DEBUG(debugging, ("possible_next_jazda", possible_next_jazda), debug_code="Sch_mak_rsm_pnj", debug_codes=debug_codes_ls)

                        # checks if there is time for next jazda
                        if not ( possible_next_jazda == False):
                            schedule_out.next_jazda = possible_next_jazda
                            schedule_ls.append(schedule_out)

                        # if there is no time then sets status of schedule to done
                        else:
                            schedule_out.done = True
                            if schedule_out.evaluate_self()!=False:
                                schedule_done.append( schedule_out )


            if start_hour+1>=interval[0] and interval[1]>=start_hour+3:
                pos_next_jazda3 = False
                for student in sorted_list_of_students:
                    if student.is_available_in_this_time(start_day, start_hour+1):
                        new_class_added = True
                        DEBUG(debugging, ("creating schedule with: ", student), debug_code="Sch_mak_rsm_csw1", debug_codes=debug_codes_ls )
                        schedule_out = deepcopy( schedule )
                        schedule_out.dict_schedule[start_day].append( Jazda(start_day, start_hour+1, student, schedule_out) )
                        DEBUG(debugging, ("schedule_out", schedule_out), debug_code="Sch_mak_rsm_so1", debug_codes=debug_codes_ls )

                        # is used to stop from checking possible jazda every time
                        if pos_next_jazda3==False:
                            possible_next_jazda = schedule_out.possible_next_jazda()
                            pos_next_jazda3 = True
                        DEBUG(debugging, ("possible_next_jazda", possible_next_jazda), debug_code="Sch_mak_rsm_pnj1", debug_codes=debug_codes_ls)

                        # checks if there is time for next jazda
                        if not ( possible_next_jazda == False):
                            schedule_out.next_jazda = possible_next_jazda
                            schedule_ls.append( schedule_out )
                        # if there is no time then sets status of schedule to done
                        else:
                            schedule_out.done = True
                            if schedule_out.evaluate_self()!=False:
                                schedule_done.append( schedule_out )
        
        DEBUG(debugging, ("  "), (" ### POSITIONAL ###", "AFTER MAIN LOOP OF ADDING JAZDY TO SCHEDULE"), ("  "), debug_code="postional", debug_codes=debug_codes_ls)
        DEBUG(debugging, ("--schedule_ls:",""), *schedule_ls, ("--schedule_done", ""), *schedule_done, debug_code="Sch_mak_rsm_Aac1", debug_codes=debug_codes_ls)


        if not new_class_added:
            DEBUG(debugging, ("new_class_added: ", new_class_added), ("schedule with no new class:", schedule), debug_code="Sch_mak_rsm_nca", debug_codes=debug_codes_ls )
            
            next_jazda = schedule.next_day_and_hour(start_day)
            DEBUG(debugging, ("next_jazda:", next_jazda), debug_code="Sch_mak_rsm_nj1", debug_codes=debug_codes_ls )
            if next_jazda == None:
                schedule.done = True
                schedule.evaluate_self()
                schedule_done.append(schedule)
            else:
                schedule.next_jazda = next_jazda
                schedule_ls.append(schedule)

        #DEBUG(debugging, ("schedule_ls:", ""), *schedule_ls, debug_code="Sch_mak_rsm_schls1", debug_codes=debug_codes_ls)
        # recursive loop
        for schedule in schedule_ls:
            DEBUG(debugging, ("  "), (" ### POSITIONAL ### last for loop in recrsive schedule maker", " one repetition"), ("  "), debug_code="positional", debug_codes=debug_codes_ls)
            # only if the schedule isnt messed up now we will continue with recursive generation
            # so we dont waste time 
            if schedule.evaluate_self(no_srednia_z_odchylenie_standardowe=True, no_min_jazdy=True, students_ls_for_min_jazdy=self.students_min_jazdy):

                if schedule.best_possible_odchylenie() <= self.max_odchyelnie_standardowe:
                    kwargs["schedule"] = schedule

                    ret = self.recursive_schedule_maker( **kwargs)

                    DEBUG(debugging, ("returned value", schedule_done), debug_code="Sch_mak_rsm_ret1", debug_codes=debug_codes_ls)
                    if type(ret) == list:
                        schedule_done += ret
                        DEBUG(debugging, ("schedule_done", schedule_done), debug_code="Sch_mak_rsm_sd1", debug_codes=debug_codes_ls)

                    elif type(ret) == Schedule:
                        schedule_done.append(ret)
                    
                    elif ret is None or ret==[]:
                        DEBUG(debugging, ("schdeule could not be recursively continiued", schedule), debug_code="Sch_mak_rsm_sd2", debug_codes=debug_codes_ls)

                    # THIS MEANS THE SCHEDULE IS GOOD ENOUGH
                    elif type(ret) == tuple and ret[1]:
                        DEBUG(debugging, ("GOOD ENOUGH SCHEDULE", schedule), debug_code="Sch_mak_rsm_BEST", debug_codes=debug_codes_ls)
                        return ret

                    else:
                        DEBUG(debugging, ("type( ret ):", type(ret), "   |  ret:", ret), ("--schdeule that returned different ret", schedule), debug_code="Sch_mak_rsm_bad_ret1", debug_codes=debug_codes_ls)
                else:
                    DEBUG(debugging, ("droping schedule to no good possible odchylenie standardowe", schedule), debug_code="Sch_mak_rsm_mxos1_drop", debug_codes=debug_codes_ls)
            
            else:
                DEBUG(debugging, ("CORRECT schedule evaluation, BUT the schedule did not meet requiremts", schedule), debug_code="Sch_mak_rsm_schev1", debug_codes=debug_codes_ls)
            
            # If schedule is good enough
            if schedule_done:
                DEBUG(debugging, ("schedule good enough? lets see!, schedule.value =", schedule_done[-1].value), debug_code="Sch_mak_rsm_schv1", debug_codes=debug_codes_ls)
                if schedule_done[-1].value[0] <= self.max_odchyelnie_standardowe and schedule_done[-1].value[1] >= self.min_amount_of_jazdy:
                    # Special type of return, will be detected and sent up with no further investigation
                    return schedule_done[-1], True


        list_of_best_schedules = self.best_schedules( schedule_done, kwargs["top_return"] if "top_return" in kwargs else 1 , **kwargs["best_schedules"] if "best_schedules" in kwargs else {} )
        DEBUG(debugging, ("RETURN list:", list_of_best_schedules), debug_code="Sch_mak_rsm_RETURN", debug_codes=debug_codes_ls )
        return list_of_best_schedules
