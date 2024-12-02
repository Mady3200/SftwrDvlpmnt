import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os



# df_prerequisites = pd.read_csv('tmp/course_prerequisites.csv')

def get_pre_req_dict(df_prerequisites):
    pre_req_dict = {}
    for index, row in df_prerequisites[2:].iterrows():
        course_number = row['course_number']
        prerequisites = str(row['prereq_codes'])
        if str(prerequisites) != 'nan' and prerequisites != 'None' and len(prerequisites) > 4:
            first_part = prerequisites.split(' or ')[0]
            second_part = [fp.split(' and ') if ' and ' in fp else fp for fp in first_part.split(' or ')]
            third_part_all_expanded = []
            for fp in second_part:
                if len(fp) > 1 and type(fp) == list:
                    for fp2 in fp:
                        third_part_all_expanded.append(fp2)
                else:
                    third_part_all_expanded.append(fp)
            pre_req_dict[course_number] = third_part_all_expanded
        else:
            pre_req_dict[course_number] = []
    return pre_req_dict

import datetime

map_code_to_sem = {
    'FA': 'Fall',
    'SP': 'Spring',
    'SU': 'Summer'
}
map_sem_to_code = {v: k for k, v in map_code_to_sem.items()}

def get_next_semester_based_on_time():
    nowtime = datetime.datetime.now()
    sem_name = ''     
    year = nowtime.year
    if nowtime.month >= 8 and nowtime.month < 12:
        sem_name = "Fall"
        # year does not change
    elif nowtime.month >= 5 and nowtime.month < 8:
        sem_name = "Summer"
        # year does not change
    else:
        sem_name = "Spring"
        # year changes
        year += 1
    return sem_name,year

def semesters_list(courses_info_df: pd.DataFrame):
    sems_set = set()
    for sem in courses_info_df['Semester'].values:
        if sem != 'None':
            sems_set.add(sem)
    
    sems_list = []
    for sem in sems_set:
        sem_split = sem.split(' ')
        sems_list.append(sem_split)
    
    semorder = ['Spring', 'Summer', 'Fall']
    sems_list.sort(key=lambda x: (int(x[1]), semorder.index(x[0])))
    
    return sems_list  # Return the ordered list of semesters

def get_next_semester(semester):
    # print(semester)
    semorder = ['Spring', 'Summer', 'Fall']
    sem_index = semorder.index(semester[0])
    next_sem_index = (sem_index + 1) % 3
    year = semester[1] 
    if next_sem_index == 0 :
        year = str(int(year)+1)
    return semorder[next_sem_index] + ' ' + year

def get_nextsem_based_on_maxsem(courses_info_df):
    sem_order = ['Spring', 'Summer', 'Fall']
    sem_next, year_next = get_next_semester_based_on_time()
    sems = semesters_list(courses_info_df)
    print(sems)
    maxsem = sems[-1]
    print(maxsem)
    sem = get_next_semester(maxsem)
    sem, year = sem.split(' ')
    print(sem,year)
    if year_next > int(year):
        return sem_next, year_next
    elif sem_order.index(sem) < sem_order.index(sem_next):
        return sem_next, year_next
    # sem_code = map_sem_to_code[sem]+str(year)[2:]
    return sem, year

# get_nextsem_based_on_maxsem(courses_info_df)
def get_courses_info_df(courses_info):
    courses_info_df = pd.DataFrame(courses_info.values(), columns=['Semester', 'Grade', 'Credits', 'Area'])
    courses_info_df['Course'] = courses_info.keys()
    sems_list = semesters_list(courses_info_df)
    print(sems_list)
    sems_list_join = [ ' '.join(sem) for sem in sems_list] + ['None']
    courses_info_df['semindex'] = courses_info_df['Semester'].apply(lambda x: sems_list_join.index(x))
    courses_info_df = courses_info_df.sort_values(by='semindex')
    return courses_info_df

def get_prereqs_for_course(course_number):
    global pre_req_dict
    return pre_req_dict.get(course_number,[])

def get_recursive_prereqs_for_course(course_number):
    prereqs = get_prereqs_for_course(course_number)
    if len(prereqs) == 0:
        return []
    else:
        return prereqs + [get_recursive_prereqs_for_course(prereq) for prereq in prereqs if len(get_recursive_prereqs_for_course(prereq)) > 0]


def get_courses_without_prereqs(courses_todo_final_dict_prreqs, courses_todo_final,courses_info_df):
    courses_without_prereqs = [course for course in courses_todo_final if len(courses_todo_final_dict_prreqs[course]) == 0]
    courses_with_prereqs = [course for course in courses_todo_final if len(courses_todo_final_dict_prreqs[course]) > 0]
    # for course in courses_with_prereqs if for each preq sem is not None then add course to courses_without_prereqs
    for course in courses_with_prereqs:
        all_preq_done = True
        for preq in courses_todo_final_dict_prreqs[course]:
            semvalues = courses_info_df.loc[courses_info_df['Course'] == preq, 'Semester'].values
            if not(semvalues) or  semvalues[0] == 'None':
                all_preq_done = False
                break
        if all_preq_done:
            courses_without_prereqs.append(course)
    # remove 'CPSC 6000' from courses_without_prereqs
    courses_without_prereqs = [course for course in courses_without_prereqs if course != 'CPSC 6000']
    return courses_without_prereqs

def get_courses_todo_final_dict_prreqs(courses_info_df):
    courses_todo = courses_info_df[courses_info_df['Semester'] == 'None'].Course.values
    # get all prereqs for these courses
    courses_todo_final = set(courses_todo.copy())
    for course in courses_todo:
        prereqs = get_recursive_prereqs_for_course(course)
        # print(course, prereqs)
        if len(prereqs) > 0:
            print("Found course with prereqs", course, prereqs)
            courses_todo_final = courses_todo_final.union(set(prereqs))

    courses_todo_final_dict_prreqs = {course: get_recursive_prereqs_for_course(course) for course in courses_todo_final}
    return courses_todo_final_dict_prreqs, courses_todo_final

#here
def plan_and_add_to_schedule(df_course,df_4year,courses_without_prereqs,sem,year,debug=True):
    sem_code = map_sem_to_code[sem]+str(year)[2:]    
    course_schedle_nextsem = df_4year[df_4year['Course'].isin(courses_without_prereqs)][['Course', 'Course Title', sem_code]]
    course_schedle_nextsem = course_schedle_nextsem[course_schedle_nextsem[sem_code].str.contains(r'[F,D,N,O]', na=False)]
    courses = course_schedle_nextsem.Course.values
    courses = list(courses)
    
    for course in courses_without_prereqs:
        if course not in df_4year['Course'].values:
            courses.append(course)
    if debug:
        print("courses 1", courses)
    
    for course in ['CPSC 6985', 'CPSC 6986', 'CYBR 6985']:
        # if that course Semester is None append
        semvalues =  list(df_course.loc[df_course['Course'] == course, 'Semester'].values)
        if semvalues and semvalues[0] == 'None':
            courses.append(course)
    if debug:
        print("courses 2", courses)
    courses_to_add = courses.copy()
    for course in courses:
        # if that course Semester is None append
        semvalues =  list(df_course.loc[df_course['Course'] == course, 'Semester'].values)
        if semvalues and semvalues[0] != 'None':
            courses_to_add.remove(course)
    if debug:
        print("courses_to_add", courses_to_add)
    if sem != 'Summer':
        courses = courses_to_add[:3]    
    else:
        courses = courses_to_add[:1]
    print("courses for adding to schedule", courses)
    # update courses_info_df_new_schedule where Course is in course_schedle_nextsem
    df_course.loc[df_course['Course'].isin(courses), 'Semester'] = sem+' '+str(year)
    # add new row course name on NONE-sem-year
    if len(courses) == 0:
        df_none_course = pd.DataFrame({'Course': ['None'], 'Semester': [sem+' '+str(year)]})
        df_course = pd.concat([df_course, df_none_course], ignore_index=True)
    else:
        # remove where course is None
        df_course = df_course[df_course['Course'] != 'None']
    return df_course,courses

def update_schedule(courses_info_df, df_4year):
    sem, year = get_nextsem_based_on_maxsem(courses_info_df)
    print(sem, year)
    
    courses_info_df_new_schedule = courses_info_df.copy()
    courses_info_df_new_schedule.columns

    courses_todo_final_dict_prreqs, courses_todo_final = get_courses_todo_final_dict_prreqs(courses_info_df_new_schedule)

    courses_without_prereqs = get_courses_without_prereqs(courses_todo_final_dict_prreqs, courses_todo_final,courses_info_df)

    print("courses_without_prereqs", courses_without_prereqs)

    courses_info_df_new_schedule,planned_courses = plan_and_add_to_schedule(courses_info_df_new_schedule, df_4year, courses_without_prereqs, sem, year)

    sems_list = [
        ' '.join(sem) for sem in semesters_list(courses_info_df_new_schedule)
    ] + ['None']

    courses_info_df_new_schedule['semindex'] = courses_info_df_new_schedule['Semester'].apply(lambda x: sems_list.index(x))

    courses_info_df_new_schedule = courses_info_df_new_schedule.sort_values(by='semindex')

    return courses_info_df_new_schedule,planned_courses

#  recursively plan until only CPSC 6000 is left or no courses are left 

def plan_schedule_recursively(courses_info_df, df_4year, planned_previously = False):
    courses_left = courses_info_df[courses_info_df['Semester'] == 'None'].Course.values
    print("courses_left", courses_left, " || proceeding in plan_schedule_recursively")
    #  if len 2 print courses_info_df
    print(courses_info_df)
    if len(courses_left) == 0:
        return courses_info_df
    elif len(courses_left) == 1 and 'CPSC 6000' in courses_left:
        print("CPSC 6000 found in courses_left")
        sems_list = semesters_list(courses_info_df)
        lastsem, year = sems_list[-1]
        #  update cpsc 6000 to lastsem+year
        courses_info_df.loc[courses_info_df['Course'] == 'CPSC 6000', 'Semester'] = lastsem+' '+year
        return courses_info_df
    else:
        new_courses_info_df,planned_courses = update_schedule(courses_info_df, df_4year)
        sems_list = semesters_list(courses_info_df)
        lastsem, year = sems_list[-1]
        # if planned_previously == False and len(planned_courses) == 0 and lastsem != 'Summer':
        #     return new_courses_info_df
        return plan_schedule_recursively(new_courses_info_df, df_4year, True if len(planned_courses) > 0 else False)



def transform_schedule(courses_info_df_new_schedule5):
    semlists = semesters_list(courses_info_df_new_schedule5)
    semlists_join = [ ' '.join(sem) for sem in semlists] + ['None']
    sems_lists_Courses_dict = {}
    max_courses = 0
    for sem in semlists_join:
        if sem == 'None':
            continue
        sems_lists_Courses_dict[sem] = list(courses_info_df_new_schedule5[courses_info_df_new_schedule5['Semester'] == sem]['Course'].values)
        if sems_lists_Courses_dict[sem] and len(sems_lists_Courses_dict[sem]) > max_courses:
            max_courses = len(sems_lists_Courses_dict[sem])


    # append None to the lists in sems_lists_Courses_dict until all lists are of same length
    for sem in sems_lists_Courses_dict:
        if sems_lists_Courses_dict[sem]:
            while len(sems_lists_Courses_dict[sem]) < max_courses:
                sems_lists_Courses_dict[sem] =sems_lists_Courses_dict[sem] + ['None']
        else:
            sems_lists_Courses_dict[sem] = ['None']*max_courses

    # sems_lists_Courses_dict  keys are columns and values are lists of courses

    final_schedule = pd.DataFrame(sems_lists_Courses_dict)
    return final_schedule



