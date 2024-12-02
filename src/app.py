
### start


import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os


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



### end

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
# from GraduateStudyPlanParser import GraduateStudyPlanParser
import pandas as pd
import argparse

class GraduateStudyPlanParser:
    """
    A class to parse and process graduate study plans from a CSV file.
    """

    def __init__(self, input_csv):
        self.input_csv = input_csv
        self.df = None

    def load_data(self):
        """
        Load the CSV data into a pandas DataFrame and initialize new columns.
        """
        self.df = pd.read_csv(self.input_csv, header=1)
        self.df = self.df[['Unnamed: 0', 'Fall ', 'Spring*', 'Summer ', 'Fall', 'Spring*.1']]
        self.df['Program'] = None
        self.df['Starting_Semester'] = None

    def process_data(self):
        """
        Process the DataFrame to populate the new columns and drop unnecessary rows.
        """
        current_program = None
        current_semester = None
        section = None
        drop_indexes = []

        for index, row in self.df.iterrows():
            section_now = row['Unnamed: 0']
            section = section_now
            if pd.notna(section):
                if '-' in section:
                    current_program = section.strip()
                    drop_indexes.append(index)
                elif 'Start' in section:
                    current_semester = section.split()[0]  # Extract 'Fall' or 'Spring'
            self.df.at[index, 'Program'] = current_program
            self.df.at[index, 'Starting_Semester'] = current_semester
            self.df.at[index, 'drop_index'] = index in drop_indexes

        self.df = self.df.drop(drop_indexes)

    def rename_columns(self):
        """
        Rename the columns of the DataFrame.
        """
        self.df = self.df[['Fall ', 'Spring*', 'Summer ', 'Fall', 'Spring*.1', 'Program', 'Starting_Semester']]
        self.df.columns = ['Fall1', 'Spring1', 'Summer1', 'Fall2', 'Spring2', 'Program', 'Starting_Semester']

    def display_data(self):
        """
        Display the DataFrame.
        """
        print(self.df.columns)
        print(self.df)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Graduate Study Plan Parser")
    parser.add_argument(
        '--input_csv',
        type=str,
        default='../inputs_new/Graduate Study Plans -revised(Sheet1).csv',
        help='Path to the input CSV file'
    )
    return parser.parse_args()
# from DegreeWorksParser import parse_degreeworks

# read pdf to text
import re
import fitz
# read args
import argparse

pre_req_dict = {}

def parse_degreeworks(pdfpath,resultsprint,debug):
    
    doc = fitz.open(pdfpath)
    text = ""
    for page in doc:
        text += page.get_text("text")
    if debug:
        print(text)

    raw_text = text

    def printseperator(seperator_text= "-"):
        if debug:
            print(seperator_text*100)

    printseperator()

    # Dictionary to store extracted data
    student_info = {}

    # Extract information using regular expressions or string manipulation
    student_name_match = re.search(r'Student name\s+(.+)', text)
    student_info['Student Name'] = student_name_match.group(1).strip() if student_name_match else None

    student_id_match = re.search(r'Student ID\s+(\d+)', text)
    student_info['Student ID'] = student_id_match.group(1).strip() if student_id_match else None

    degree_match = re.search(r'Degree\s+(.+)', text)
    student_info['Degree'] = degree_match.group(1).strip() if degree_match else None

    audit_date_match = re.search(r'Audit date\s+(.+)', text)
    student_info['Audit Date'] = audit_date_match.group(1).strip() if audit_date_match else None

    degree_progress_match = re.search(r'Degree progress\s+(\d+%)', text)
    student_info['Degree Progress'] = degree_progress_match.group(1).strip() if degree_progress_match else None

    overall_gpa_match = re.search(r'Overall GPA\s+(\d\.\d{2})', text)
    student_info['Overall GPA'] = overall_gpa_match.group(1).strip() if overall_gpa_match else None

    # level
    level_match = re.search(r'Level\s+([^\s]+)', text)
    student_info['Level'] = level_match.group(1).strip() if level_match else None

    majorIndex = text.find('Major')
    printseperator()
    if debug:
        print(f"Debug - majorIndex: {majorIndex}")
    classification_match = re.search(r'Classification\s+(.+)', text[:majorIndex])
    student_info['Classification'] = classification_match.group(1).strip() if classification_match else None

    major_match = re.search(r'Major\s+(.+?)\s+Program', text)
    student_info['Major'] = major_match.group(1).strip() if major_match else None

    # program
    concentrationIndex = text.find('Concentration')
    printseperator()
    if debug:
        print(f"Debug - concentrationIndex: {concentrationIndex}")
    program_match = re.search(r'Program\s+([\s\S]+)', text[:concentrationIndex])
    student_info['Program'] = program_match.group(1).strip().replace('\n', ' ') if program_match else None

    collegeindex = text.find('College')
    printseperator()
    if debug:
        print(f"Debug - collegeindex: {collegeindex}")
    concentration_match = re.search(r'Concentration\s+(.+)', text[:collegeindex])
    student_info['Concentration'] = concentration_match.group(1).strip() if concentration_match else None

    overallGPAindex = text.find('Overall GPA')
    printseperator()
    if debug:
        print(f"Debug - overallGPAindex: {overallGPAindex}")
    overallGPAindex2 = overallGPAindex + 1 + text[overallGPAindex+1:].find('Overall GPA')

    printseperator()
    if debug:
        print(f"Debug - overallGPAindex2: {overallGPAindex2}")
    college_match = re.search(r'College\s+(.+)', text[:overallGPAindex2])
    student_info['College'] = college_match.group(1).strip() if college_match else None

    overall_gpa2_match = re.search(r'Overall GPA\s+(\d\.\d{2})', text[overallGPAindex2:])
    student_info['Overall GPA2'] = overall_gpa2_match.group(1).strip() if overall_gpa2_match else None

    institutional_gpa_match = re.search(r'Institutional GPA\s+(\d\.\d{2})', text)
    student_info['Institutional GPA'] = institutional_gpa_match.group(1).strip() if institutional_gpa_match else None

    credits_earned_match = re.search(r'Credits\s+(\d+)', text)
    student_info['Credits Earned'] = credits_earned_match.group(1).strip() if credits_earned_match else None

    credits_required_match = re.search(r'Credits required:\s+(\d+)', text)
    student_info['Credits Required'] = credits_required_match.group(1).strip() if credits_required_match else None

    credits_applied_match = re.search(r'Credits applied:\s+(\d+)', text)
    student_info['Credits Applied'] = credits_applied_match.group(1).strip() if credits_applied_match else None

    catalog_year_match = re.search(r'Catalog year:\s+(.+)', text)
    student_info['Catalog Year'] = catalog_year_match.group(1).strip() if catalog_year_match else None

    gpa_match = re.search(r'GPA:\s+(\d\.\d{2})', text)
    student_info['GPA'] = gpa_match.group(1).strip() if gpa_match else None

    total_credit_rule_match = re.search(r'Total Credit Rule\s+(.+)', text)
    student_info['Total Credit Rule'] = total_credit_rule_match.group(1).strip() if total_credit_rule_match else None

    graduation_application_needed_match = re.search(r'Graduation Application Needed\s+(.+)', text)
    student_info['Graduation Application Needed'] = graduation_application_needed_match.group(1).strip() if graduation_application_needed_match else None

    credits_required_for_major_match = re.search(r'Still needed: (\d+) credits are required for the Major', text)
    student_info['Credits Required for Major'] = credits_required_for_major_match.group(1).strip() if credits_required_for_major_match else None

    current_credits_match = re.search(r'You currently have (\d+),', text)
    student_info['Current Credits'] = current_credits_match.group(1).strip() if current_credits_match else None

    credits_still_needed_match = re.search(r'you still need (\d+) more credits', text)
    student_info['Credits Still Needed'] = credits_still_needed_match.group(1).strip() if credits_still_needed_match else None

    # Graduation Application Needed index
    gradAppIndex = text.find('Graduation Application Needed')
    printseperator()
    if debug:
        print(f"Debug - gradAppIndex: {gradAppIndex}")

    MajorRequirementsIndex = text.find('Major Requirements')
    printseperator()
    if debug:
        print(f"Debug - MajorRequirementsIndex: {MajorRequirementsIndex}")

    still_needed_for_graduation_match = re.search(r'Still needed:\s+([\s\S]+)', text[gradAppIndex:MajorRequirementsIndex])
    student_info['Still Needed for Graduation'] = still_needed_for_graduation_match.group(1).strip() if still_needed_for_graduation_match else None

    blocksIndex = text.find('Blocks included in this block')
    printseperator()
    if debug:
        print(f"Debug - blocksIndex: {blocksIndex}")

    still_needed_for_major_match = re.search(r'Still needed:\s+([\s\S]+)', text[MajorRequirementsIndex:blocksIndex])
    student_info['Still Needed for Major'] = still_needed_for_major_match.group(1).strip() if still_needed_for_major_match else None

    incompleteIndex = blocksIndex + text[blocksIndex:].find('INCOMPLETE')
    printseperator()
    if debug:
        print(f"Debug - incompleteIndex: {incompleteIndex}")

    blocks_match = re.search(r'Blocks included in this block\s+([\s\S]+)', text[blocksIndex:incompleteIndex])
    student_info['Blocks'] = blocks_match.group(1).strip().split('\n')[:-2] if blocks_match else []

    # Print the extracted information
    for key, value in student_info.items():
        printseperator('*')
        if debug or resultsprint:
            print(f"{key}: {value}")

    Block_info = {}
    if student_info['Blocks'] != []:
        for i in range(len(student_info['Blocks'])):
            # finding for block text
            printseperator()
            if debug:
                print(f"finding for block {student_info['Blocks'][i]}")
            if i == len(student_info['Blocks'])-1:
                last_block_index = len(student_info['Blocks']) - 1
                block_pre_index = re.search(rf'{student_info["Blocks"][last_block_index]}\s*', text).start()
                if debug:
                    print(f"in if block {i} Debug - Last block pre_index: {block_pre_index}")
                block_post_index = re.search(r'In-progress', text).start()
                if debug:
                    print(f"in if block {i} Debug - Last block post_index: {block_post_index}")
                block_text = text[block_pre_index:block_post_index]
                Block_info[student_info['Blocks'][last_block_index]] = block_text
            else:       
                block_pre_index = re.search(rf'{student_info["Blocks"][i]}\s*', text).start()
                if debug:
                    print(f"in else block {i} Debug - Block {i} pre_index: {block_pre_index}")
                    print(f"in else block {i} Debug - Block {i+1} : {student_info['Blocks'][i + 1]}")
                block_post_index = re.search(rf'{student_info["Blocks"][i + 1]}\s*', text).start()
                if debug:
                    print(f"in else block {i} Debug - Block {i} post_index: {block_post_index}")
                block_text = text[block_pre_index:block_post_index]
                Block_info[student_info['Blocks'][i]] = block_text
    else:
        pass

    block_pre_index = re.search(r'In-progress', text).start()
    if debug:
        print(f"Debug - In-progress pre_index: {block_pre_index}")
    block_post_index = re.search(r'Notes|Legend', text).start()
    if debug:
        print(f"Debug - In-progress post_index: {block_post_index}")
    block_text = text[block_pre_index:block_post_index]
    # Block_info['In-progress'] = block_text

    if debug:
        print(Block_info.keys())

    courses_info = {} 

    for block in Block_info.keys():
        if debug or resultsprint:
            print('|'*100)
            print(block)
        blktext = Block_info[block]
        
        area_codes = re.findall(r'\bArea\s+\d[^\n]*', blktext,re.IGNORECASE)
        
        for i,area in enumerate(area_codes):
            if debug or resultsprint:
                print('-'*100)
                print("D!",area)
            area_start = blktext.find(area_codes[i])
            if debug:
                print(f"Debug - Area {i} start index: {area_start}")
            area_end = blktext.find(area_codes[i+1]) if i != len(area_codes)-1 else len(blktext)
            if debug:
                print(f"Debug - Area {i} end index: {area_end}")
            area_blktext = blktext[area_start:area_end]
            
            course_codes = re.findall(r'[A-Z]{4}\s+\d{4}[A-Z]?\s+', area_blktext)
            if debug:
                print(course_codes)
            
            for i,course_code in enumerate(course_codes):
                course_pre_index = area_blktext.find(course_codes[i])
                if debug:
                    print(f"Debug - Course {course_code.strip()} pre_index: {course_pre_index}")
                course_post_index = course_pre_index + 1 + area_blktext[course_pre_index+1:].find(course_codes[i+1]) if i != len(course_codes)-1 else len(area_blktext)
                if debug:
                    print(f"Debug - Course {course_code.strip()} post_index: {course_post_index}")
                course_blktext = area_blktext[course_pre_index:course_post_index]
                term_match = re.search(r'Fall\s+\d{4}|Spring\s+\d{4}|Summer\s+\d{4}', course_blktext) 
                term = term_match.group(0) if term_match else 'None'
                grade_match = re.search(r'\b[A-Z]\s*\n+|\nCURR\s*\n+', course_blktext)
                grade = grade_match.group(0) if grade_match else 'None'
                # between grade and term there is a number of credits in digits use regex to find it add \s* to ignore spaces between grade and term
                """  
                ENGR 5236G
                Microelectronic Circuits
                C 
                3
                Fall 2023
                """
                credits_match = re.search(rf'{grade}\s*\(?(\d+)\)?\s*{term}', course_blktext)
                credits = credits_match.group(1) if credits_match else 'None'
                if debug:
                    print(course_blktext)
                if debug or resultsprint:
                    print(course_code.strip(), term.strip(), grade.strip(), credits.strip())
                courses_info[course_code.strip()] = [term.strip(), grade.strip(), credits.strip(),area]
                    
        if len(area_codes) == 0:
            course_codes = re.findall(r'[A-Z]{4}\s+\d{4}[A-Z]?\s+', blktext)
            if debug:
                print(course_codes)
            area_blktext = blktext
            for i,course_code in enumerate(course_codes):
                course_pre_index = area_blktext.find(course_codes[i])
                if debug:
                    print(f"Debug - Course {course_code.strip()} pre_index: {course_pre_index}")
                course_post_index = course_pre_index + 1 + area_blktext[course_pre_index+1:].find(course_codes[i+1]) if i != len(course_codes)-1 else len(area_blktext)
                if debug:
                    print(f"Debug - Course {course_code.strip()} post_index: {course_post_index}")
                course_blktext = area_blktext[course_pre_index:course_post_index]
                term_match = re.search(r'Fall\s+\d{4}|Spring\s+\d{4}|Summer\s+\d{4}', course_blktext)
                term = term_match.group(0) if term_match else 'None'
                grade_match = re.search(r'\b[A-Z]\s*\n+|\nCURR\s*\n+', course_blktext)
                grade = grade_match.group(0) if grade_match else 'None'
                credits_match = re.search(rf'{grade}\s*(\(?\d+\)?)\s*{term}', course_blktext)
                credits = credits_match.group(1) if credits_match else 'None'
                if debug:
                    print(course_blktext)
                if debug or resultsprint:
                    print(course_code.strip(), term.strip(), grade.strip(), credits.strip())
                courses_info[course_code.strip()] = [term.strip(), grade.strip(), credits.strip(),'None']
        if debug or resultsprint:
            print('*'*100)

    print(*courses_info.items(), sep='\n')

    return raw_text,student_info, courses_info

# from FouryearScheduleParser import load_csv_schedule
import pandas as pd

def load_csv_schedule(csv_path, header_row):
    """
    Load a CSV file into a pandas DataFrame.

    Parameters:
    csv_path (str): The file path to the CSV file.
    header_row (int): The row number to use as the column names.

    Returns:
    pd.DataFrame: The loaded DataFrame.
    """
    df_4year = pd.read_csv(csv_path, header=header_row)
    return df_4year

# if __name__ == "__main__":
#     df_4year = load_csv_schedule(r"..\inputs_new\fouryear.csv", 0)
#     print(df_4year)


import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

def extract_course_prerequisites(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    courses = []
    
    for courseblock in soup.find_all('div', class_='courseblock'):
        course_info = courseblock.find('div', class_='cols noindent')
        if course_info:
            course_number = course_info.find('span', class_='detail-code').strong.text.strip()
            course_title = course_info.find('span', class_='detail-title').strong.text.strip()
            
            # Updated logic to extract prerequisites
            prerequisites = []
            prereq_codes = []
            prereq_names = []
            for course_extra in courseblock.find_all('div', class_='courseblockextra'):
                """ Prerequisite(s): 
                    (CPSC 1301 with a minimum grade of C or CPSC 1301H with a minimum grade of C or
                      CPSC 1301K with a minimum grade of C or CPSC 1301I with a minimum grade of C) 
                    and 
                    MATH 2125 (may be taken concurrently) with a minimum grade of C """
                # output : CPSC 1301 or CPSC 1301H or CPSC 1301K or CPSC 1301I and MATH 2125
                if 'Prerequisite(s):' in course_extra.text:
                    text = course_extra.text
                    # replace all non alpha numeric characters with a space
                    text = re.sub(r'[^a-zA-Z0-9/)\(/:]', ' ', text)

                    # Extract the prerequisite text
                    prereq_text = text.split('Prerequisite(s):')[1].strip()
                    prerequisites.append(prereq_text)
                    
                    # Extract course codes and names from the prerequisite text
                    preq_context = prereq_text.split( ' ' )
                    coursedept = preq_context[0]
                    for text in preq_context[1:]:
                        full_course_code = coursedept + ' ' + text
                        # use regex to extract the course code and name
                        match = re.search(r'[A-Z]{4}\s\d{4}[A-Z]?', full_course_code)
                        # print(match, full_course_code)
                        if match:
                            prereq_codes.append(match.group(0))
                        else:
                            # if or or and in text, append it
                            if 'or' in text or 'and' in text:
                                prereq_codes.append(text)
                        coursedept = text
                    
                    
                    
                restrictions = []
                for course_extra in courseblock.find_all('div', class_='courseblockextra'):
                    if 'Restriction(s):' in course_extra.text:
                        restriction_text = course_extra.text.split('Restriction(s):')[1].strip()
                        restrictions.append(restriction_text)
                
            courses.append({
                'course_number': course_number,
                'course_title': course_title,
                'prereq_codes': ' '.join(prereq_codes) if prereq_codes else None,
                'restrictions': ' '.join(restrictions) if restrictions else None,
                'prerequisites': str(' '.join(prerequisites)) if prerequisites else None,
            })
    
    return courses

def extract_course_prerequisites_main( filename=None ):
    url = 'https://catalog.columbusstate.edu/course-descriptions/cpsc/'
    course_data = extract_course_prerequisites(url)
    # Create a DataFrame from the course data
    df = pd.DataFrame(course_data)
    if filename is None:
        filename = 'course_prerequisites.csv'
    # delete the file if it exists
    if os.path.exists(filename): os.remove(filename)

    if os.path.exists(filename):
        base, extension = os.path.splitext(filename)
        counter = 1
        new_filename = f"{base}_{counter}{extension}"
        while os.path.exists(new_filename):
            counter += 1
            new_filename = f"{base}_{counter}{extension}"
        filename = new_filename

    df.to_csv(filename, index=False, encoding='utf-8')

import re
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

globaldict = {
    "default_dw_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\1stsemdeg.pdf",
    "default_gsp_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\Graduate Study Plans -revised(Sheet1).csv",
    "default_schedule_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\fouryear.csv",
    "degreeworks_path": None,
    "gsp_path": None,
    "schedule_path": None,
    "degreeworks_df": None,
    "gsp_df": None,
    "schedule_df": None,
    "degreeworks_parsed": False,
    "gsp_parsed": False,
    "schedule_parsed": False
}

def reset_global_dict():
    global globaldict
    globaldict = {
        "default_dw_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\1stsemdeg.pdf",
        "default_gsp_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\Graduate Study Plans -revised(Sheet1).csv",
        "default_schedule_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\fouryear.csv",
        "degreeworks_path": None,
        "gsp_path": None,
        "schedule_path": None,
        "degreeworks_df": None,
        "gsp_df": None,
        "schedule_df": None,
        "degreeworks_parsed": False,
        "gsp_parsed": False,
        "schedule_parsed": False
        }

# Main Application Window Class
class SmartClassPlanningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Class Planning Tool")
        self.geometry("1200x800")
        
        # Initialize screens
        self.welcome_screen = WelcomeScreen(self)
        self.file_selection_screen = FileSelectionScreen(self)
        self.validation_screen = ValidationScreen(self)
        self.course_planning_screen = CoursePlanningScreen(self)
        self.output_generation_screen = OutputGenerationScreen(self)
        self.completion_screen = CompletionScreen(self)
        self.usage_screen = UsageScreen(self)
        self.prerequisite_extraction_screen = PrerequisiteExtractionScreen(self)  # New screen

        # Show the Welcome Screen initially
        self.show_screen(self.welcome_screen)

    def show_screen(self, screen):
        """Raise the specified screen to the front."""
        # screen center
        screen.tkraise()

    def navigate_to_file_selection_screen(self):
        self.show_screen(self.file_selection_screen)

    def navigate_to_validation_screen(self):
        self.show_screen(self.validation_screen)

    def navigate_to_course_planning_screen(self):
        self.show_screen(self.course_planning_screen)

    def navigate_to_output_generation_screen(self):
        self.show_screen(self.output_generation_screen)

    def navigate_to_completion_screen(self):
        self.show_screen(self.completion_screen)

    def navigate_to_usage_screen(self):
        self.show_screen(self.usage_screen)

    def navigate_to_prerequisite_extraction_screen(self):
        self.show_screen(self.prerequisite_extraction_screen)

# Base Screen Class with common footer
class BaseScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row=0, column=0, sticky="nsew")
        
        # Footer buttons
        footer_frame = tk.Frame(self)
        footer_frame.pack(side="bottom", fill="x", pady=10)

        # Back button
        back_button = tk.Button(footer_frame, text="Back", command=self.go_back)
        back_button.pack(side="left", padx=10)

        go_home_button = tk.Button(footer_frame, text="Go to Home", command=lambda: parent.show_screen(parent.welcome_screen) and reset_global_dict() )
        go_home_button.pack(side="left", padx=10)

        usage_button = tk.Button(footer_frame, text="Usage", command=lambda: parent.show_screen(parent.usage_screen))
        usage_button.pack(side="left", padx=10)

        contact_label = tk.Label(footer_frame, text="Contact Supervisor: supervisor@example.com", fg="blue", cursor="hand2")
        contact_label.pack(side="right", padx=10)
        contact_label.bind("<Button-1>", lambda e: messagebox.showinfo("Contact", "Email: supervisor@example.com"))


    def go_back(self):
        # Get all screens
        screens = [
            self.master.welcome_screen,
            self.master.file_selection_screen, 
            self.master.validation_screen,
            self.master.course_planning_screen,
            self.master.output_generation_screen,
            self.master.completion_screen,
            self.master.usage_screen
        ]
        
        # Find current screen index
        current_index = screens.index(self)
        
        # Go to previous screen if not on first screen
        if current_index > 0:
            self.master.show_screen(screens[current_index - 1])
        
        global globaldict
        globaldict = {
        "default_dw_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\1stsemdeg.pdf",
        "default_gsp_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\Graduate Study Plans -revised(Sheet1).csv",
        "default_schedule_path": r"C:\Users\akshi\Desktop\sftwrdevelopment\Project\inputs_new\fouryear.csv",
        "degreeworks_path": None,
        "gsp_path": None,
        "schedule_path": None,
        "degreeworks_df": None,
        "gsp_df": None,
        "schedule_df": None,
        "degreeworks_parsed": False,
        "gsp_parsed": False,
        "schedule_parsed": False
    }

class WelcomeScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        title_label = tk.Label(self, text="This is Smart Class Planning Tool", font=("Helvetica", 16))
        title_label.pack(pady=10, anchor="center")

        description_label = tk.Label(self, text="Welcome message introducing the application.", font=("Helvetica", 12))
        description_label.pack(pady=10, anchor="center")

        get_started_button = tk.Button(self, text="Get Started", font=("Helvetica", 12), 
                                       command=lambda: parent.show_screen(parent.file_selection_screen))
        get_started_button.pack(pady=20, anchor="center")

class FileSelectionScreen(BaseScreen):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.df = None

        instructions_label = tk.Label(self, text="Please upload the following files:", font=("Helvetica", 12))
        instructions_label.pack(pady=10)

        # File upload fields and buttons
        self.dw_entry = self.create_file_upload_field("DegreeWorks PDF", filetypes=[("PDF files", "*.pdf")])
        self.gsp_entry = self.create_file_upload_field("Graduate Study Plan", filetypes=[("CSV files", "*.csv")])
        self.schedule_entry = self.create_file_upload_field("4-Year Schedule", filetypes=[("CSV files", "*.csv")])
        self.dw_entry.insert(0, globaldict["default_dw_path"])
        self.gsp_entry.insert(0, globaldict["default_gsp_path"])
        self.schedule_entry.insert(0, globaldict["default_schedule_path"])
        proceed_button = tk.Button(self, text="Proceed", command=self.validate_and_proceed)
        proceed_button.pack(pady=20)

        # Parse File Button
        parse_gsp_button = tk.Button(self, text="Parse Graduate Study Plan", command=self.parse_file_gsp)
        parse_gsp_button.pack(pady=10)

        parse_degreeworks_button = tk.Button(self, text="Parse DegreeWorks PDF", command=self.parse_file_dw)
        parse_degreeworks_button.pack(pady=10)

        parse_schedule_button = tk.Button(self, text="Parse 4-Year Schedule", command=self.parse_file_schedule)
        parse_schedule_button.pack(pady=10)

        # Treeview frame with both vertical and horizontal scrollbars
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="x", padx=10, pady=10)

        # Treeview for displaying parsed data with fixed height
        self.tree = ttk.Treeview(self.tree_frame, height=10)
        self.tree.pack(side="left", fill="x", expand=True)

        # Vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)

        # Horizontal scrollbar
        self.h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.h_scrollbar.pack(fill="x", padx=10, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Clear Display Button
        clear_button = tk.Button(self, text="Clear Display", command=self.clear_display)
        clear_button.pack(pady=10)

        prereq_button = tk.Button(self, text="Go to Prerequisite Extraction", command=parent.navigate_to_prerequisite_extraction_screen)
        prereq_button.pack(pady=10)

    def create_file_upload_field(self, label_text, filetypes=None):
        """Create a file upload field with label, entry, and button."""
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=f"{label_text}:").pack(side="left")
        entry = tk.Entry(frame, width=30)
        entry.pack(side="left", padx=5)
        tk.Button(frame, text="Choose File", command=lambda: self.select_file(entry, filetypes)).pack(side="left")
        return entry

    def select_file(self, entry, filetypes=None):
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

    def parse_file_gsp(self):
        """Parse the selected Graduate Study Plan CSV file and display the results."""
        gsp_path = self.gsp_entry.get()
        if not gsp_path:
            messagebox.showerror("Error", "Please select the Graduate Study Plan CSV file.")
            return

        try:
            # Parse the CSV file using GraduateStudyPlanParser
            parser = GraduateStudyPlanParser(gsp_path)
            parser.load_data()
            parser.process_data()
            parser.rename_columns()
            self.df = parser.df  # Store the parsed DataFrame
            globaldict["gsp_df"] = self.df.copy()

            # Display parsed data in Treeview
            self.display_data(is_gsp=True)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse the file: {e}")

    def parse_file_dw(self):
        dw_path = self.dw_entry.get()
        if not dw_path:
            messagebox.showerror("Error", "Please select the DegreeWorks PDF file.")
            return
        try:
            self.raw_text,self.student_info, self.courses_info = parse_degreeworks(dw_path,True,False)
            globaldict["degreeworks_df"] = [
                self.raw_text,
                self.student_info,
                self.courses_info
            ]
            self.display_data(is_degreeworks=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse the file: {e}")

    def parse_file_schedule(self):
        schedule_path = self.schedule_entry.get()
        if not schedule_path:
            messagebox.showerror("Error", "Please select the 4-Year Schedule CSV file.")
            return
        try:
            self.df = load_csv_schedule(schedule_path,0)
            globaldict["schedule_df"] = self.df.copy()
            self.display_data(is_schedule=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse the file: {e}")

    def display_data(self, is_degreeworks=False,is_gsp=False,is_schedule=False):
        """Display the parsed DataFrame in the Treeview table."""
        # Clear any existing data in Treeview
        self.tree.delete(*self.tree.get_children())

        # Set up columns in Treeview
        if is_gsp:
            self.tree["columns"] = list(self.df.columns)
            self.tree["show"] = "headings"

            for col in self.df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            # Insert rows from DataFrame into Treeview
            for _, row in self.df.iterrows():
                self.tree.insert("", "end", values=list(row))
        
        if is_degreeworks:
            self.tree["columns"] = ["key","value"]
            self.tree["show"] = "headings"

            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            self.tree.insert("", "end", values=["raw_text",self.raw_text])
            for key,value in self.student_info.items():
                self.tree.insert("", "end", values=[key,value])
            for key,value in self.courses_info.items():
                self.tree.insert("", "end", values=[key,value])

        if is_schedule:
            self.tree["columns"] = list(self.df.columns[:5])
            self.tree["show"] = "headings"

            for col in self.df.columns[:5]:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=100)

            for _, row in self.df.iterrows():
                self.tree.insert("", "end", values=list(row)[:5])

    def clear_display(self):
        """Clear the Treeview display and column headers."""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        self.tree["show"] = "headings"
        self.df = None

    def validate_and_proceed(self):
        dw_path = self.dw_entry.get()
        gsp_path = self.gsp_entry.get()
        schedule_path = self.schedule_entry.get()
        globaldict["degreeworks_path"] = dw_path
        globaldict["gsp_path"] = gsp_path
        globaldict["schedule_path"] = schedule_path

        if not dw_path or not gsp_path or not schedule_path:
            messagebox.showerror("Error", "Please upload all required files.")
        elif dw_path == gsp_path or dw_path == schedule_path or gsp_path == schedule_path:
            messagebox.showerror("Error", "No two files should be of the same path.")
        else:
            self.parent.validation_screen.update_status()
            self.parent.show_screen(self.parent.validation_screen)

class ValidationScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        self.parsed_status = tk.StringVar(value="Status: Parsing Input Files...")
        tk.Label(self, textvariable=self.parsed_status, font=("Helvetica", 12)).pack(pady=10)

        # Parsed file status
        self.dw_status = tk.StringVar(value="")
        self.gsp_status = tk.StringVar(value="")
        self.schedule_status = tk.StringVar(value="")
        tk.Label(self, textvariable=self.dw_status).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.gsp_status).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.schedule_status).pack(anchor="w", padx=20)

        # Data Summary
        tk.Label(self, text="Extracted Data Summary:", font=("Helvetica", 12)).pack(pady=10)
        self.student_name = tk.StringVar(value="Student Name: N/A   ")
        self.student_id = tk.StringVar(value="Student ID: N/A")    
        # Program
        self.program = tk.StringVar(value="Program: N/A")
        # Concentration
        self.concentration = tk.StringVar(value="Concentration: N/A")
        self.required_credits = tk.StringVar(value="Required Credits: N/A")
        self.applied_credits = tk.StringVar(value="Applied Credits: N/A")
        self.current_credits = tk.StringVar(value="Current Credits: N/A")
        self.current_still_needed = tk.StringVar(value="Still Needed Credits: N/A")
        tk.Label(self, textvariable=self.student_name).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.student_id).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.program).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.concentration).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.required_credits).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.applied_credits).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.current_credits).pack(anchor="w", padx=20)
        tk.Label(self, textvariable=self.current_still_needed).pack(anchor="w", padx=20)

        next_button = tk.Button(self, text="Next", command=self.go_to_course_planning)
        next_button.pack(pady=20)
        self.parent = parent

    def update_status(self):
        self.parsed_status.set("Parsing input files...")
        
        # Parse DegreeWorks PDF
        try:
            raw_text, student_info, courses_info = parse_degreeworks(globaldict["degreeworks_path"],True,False)
            globaldict["degreeworks_parsed"] = True
            globaldict["degreeworks_df"] = [raw_text,student_info,courses_info]
            self.dw_status.set("✓ DegreeWorks PDF parsed successfully.")
        except Exception as e:
            self.dw_status.set("✗ Error parsing DegreeWorks PDF")
            messagebox.showerror("Error", f"Failed to parse DegreeWorks PDF: {str(e)}")
            return

        # Parse Graduate Study Plan
        try:
            gsp_parser = GraduateStudyPlanParser(globaldict["gsp_path"])
            gsp_parser.load_data()
            gsp_parser.process_data()
            gsp_parser.rename_columns()
            gsp_data = gsp_parser.df
            globaldict["gsp_parsed"] = True 
            globaldict["gsp_df"] = gsp_data
            self.gsp_status.set("✓ Graduate Study Plan parsed successfully.")
        except Exception as e:
            self.gsp_status.set("✗ Error parsing Graduate Study Plan")
            messagebox.showerror("Error", f"Failed to parse Graduate Study Plan: {str(e)}")
            return

        # Parse 4-Year Schedule
        try:
            schedule_df = load_csv_schedule(globaldict["schedule_path"], 0)
            globaldict["schedule_parsed"] = True
            globaldict["schedule_df"] = schedule_df
            self.schedule_status.set("✓ 4-Year Schedule parsed successfully.")
        except Exception as e:
            self.schedule_status.set("✗ Error parsing 4-Year Schedule")
            messagebox.showerror("Error", f"Failed to parse 4-Year Schedule: {str(e)}")
            return

        try:
            self.program.set(f"Program: {globaldict['degreeworks_df'][1]['Program']}")
            self.student_name.set(f"Student Name: {globaldict['degreeworks_df'][1]['Student Name']}")
            self.student_id.set(f"Student ID: {globaldict['degreeworks_df'][1]['Student ID']}")
            self.concentration.set(f"Concentration: {globaldict['degreeworks_df'][1]['Concentration']}")
            globaldict["concentration"] = globaldict['degreeworks_df'][1]['Concentration']
        except:
            self.student_name.set(f"Student Name: N/A")
            self.program.set(f"Program: N/A")
            self.student_id.set(f"Student ID: N/A")
            self.concentration.set(f"Concentration: N/A")

        self.required_credits.set(f"Required Credits: {globaldict['degreeworks_df'][1]['Credits Required']}")
        self.applied_credits.set(f"Applied Credits: {globaldict['degreeworks_df'][1]['Credits Applied']}")
        self.current_credits.set(f"Current Credits: {globaldict['degreeworks_df'][1]['Current Credits']}")
        self.current_still_needed.set(f"Still Needed Credits: {globaldict['degreeworks_df'][1]['Credits Still Needed']}")

        self.parsed_status.set("All files parsed successfully!")

    def go_to_course_planning(self):
        if not all([globaldict["degreeworks_parsed"], 
                   globaldict["gsp_parsed"],
                   globaldict["schedule_parsed"]]):
            messagebox.showerror("Error", "Please ensure all files are parsed successfully before proceeding.")
            return
        self.parent.course_planning_screen.update_status()
        self.parent.show_screen(self.parent.course_planning_screen)


class CoursePlanningScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Extracted Course Data:", font=("Helvetica", 12)).pack(pady=10)
        self.course_plan_frame = tk.Frame(self)
        self.course_plan_frame.pack(pady=5, anchor="w", padx=20)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        # self.adjust_button = tk.Button(button_frame, text="Adjust Plan", command=self.adjust_plan)
        # self.adjust_button.grid(row=0, column=0, padx=10)
        self.generate_button = tk.Button(button_frame, text="Generate Plan", command=self.generate_plan)
        self.generate_button.grid(row=0, column=1, padx=10)
        self.parent = parent

    def update_status(self):
        print("Updating status in course planning screen",bool(globaldict["degreeworks_df"]),bool(globaldict["degreeworks_df"][2]))
        if globaldict["degreeworks_df"] and globaldict["degreeworks_df"][2]:
            # Get courses from degreeworks data
            courses = globaldict["degreeworks_df"][2]  # Dictionary of courses
            print(courses)

            # clear all children of course_plan_frame
            for widget in self.course_plan_frame.winfo_children():
                widget.destroy()

            # Extract unique terms and sort them
            terms = sorted(list({courses[course][0] for course in courses }))
            print(terms)
            # get first term into var in global dict
            globaldict["first_term"] = terms[0]
            # store terms
            globaldict["terms"] = terms
            
            for term in terms:
                # Get courses for this term
                term_courses = [course for course in courses.items() if course[1][0] == term]
                total_credits = [re.search(r'\d+', course[1][2]) for course in term_courses]
                total_credits = [int(i.group()) if i != None else 3 for i in total_credits ]
                tc = 0
                for i in total_credits:
                    if i != None:
                        tc += int(i)
                total_credits = tc
                
                # Create term header label
                tk.Label(self.course_plan_frame, text=f"Semester {term}: Total Credits: {total_credits}",
                        font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(10,5))
                
                # Create label for each course in the term
                for course_code, course_data in term_courses:
                    grade = course_data[1]
                    credits = course_data[2]
                    tk.Label(self.course_plan_frame,
                            text=f"  • {course_code} - Credits: {credits} - Grade: {grade}").pack(anchor="w", padx=20)


    # def adjust_plan(self):
    #     messagebox.showinfo("Adjust Plan", "Adjusting the plan...")

    def generate_plan(self):
        self.parent.output_generation_screen.update_status()
        self.master.show_screen(self.master.output_generation_screen)

class OutputGenerationScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Status: Generating Your Course Plan...", font=("Helvetica", 12)).pack(pady=10)
        # conc plan label holder with na
        self.conc_plan_label = tk.StringVar(value="Concentration Plan: N/A")
        tk.Label(self, textvariable=self.conc_plan_label).pack(pady=10)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)
        self.progress.start(10)  # Simulate progress

        self.status_message = tk.StringVar(value="")
        tk.Label(self, textvariable=self.status_message).pack(pady=10)
        download_button = tk.Button(self, text="Saved as output.csv (view your plan in output directory 'outputs/output.csv')", command=self.download_file)
        download_button.pack(pady=20)

        tk.Label(self, text="General Plan for all sems of your concentration", font=("Helvetica", 12, "bold")).pack(pady=10)
        # general plan root view of tree to diplay table
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="x", padx=10, pady=10)

        # utilized following from GraduateStudyPlan label text under this

        
        # Treeview for displaying parsed data with fixed height
        self.tree = ttk.Treeview(self.tree_frame, height=10)
        self.tree.pack(side="left", fill="x", expand=True)

        self.after(2000, self.show_success_message)

    def show_success_message(self):
        self.progress.stop()
        self.status_message.set("✓ Course plan generated successfully!")

    def download_file(self):
        messagebox.showinfo("Download", "Course plan downloaded successfully at ouptut.csv")
        self.master.show_screen(self.master.completion_screen)
    
    def update_status(self):
        # conc 
        concentration = globaldict["concentration"]

        if "Software" in concentration:
            concentration = "ACS -  Software Dev"
        elif "AI" in concentration:
            concentration = "ACS -  AI and Data Science"
        elif "General" in concentration:
            concentration = "ACS -  General"
        elif "Management" in concentration:
            concentration = "CYBR - Management"
        elif "Defense" in concentration:
            concentration = "CYBR -Cyber Defense"
        self.conc_plan_label.set(f"Concentration Plan: {concentration}")

        # selecct that conc in program column of gsp df
        gsp_df = globaldict["gsp_df"]
        gsp_df = gsp_df[gsp_df["Program"] == concentration]
        print(gsp_df)
        print(globaldict["first_term"])

        #  if fall or spring in first term in global dict, then display the gsp df in the general plan frame
        if "Fall" in globaldict["first_term"]:
            gsp_df = gsp_df[gsp_df["Starting_Semester"] == "Fall"]
        elif "Spring" in globaldict["first_term"]:
            gsp_df = gsp_df[gsp_df["Starting_Semester"] == "Spring"]

        # display the gsp df in the general plan frame
        #  columns as header
        #  clear the tree
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(gsp_df.columns)
        self.tree["show"] = "headings"

        for col in gsp_df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        for _, row in gsp_df.iterrows():
            self.tree.insert("", "end", values=list(row))

        #  replace the ffirst term courses with first column of gsp df .. like wise until None of term
        columns = gsp_df.columns
        i = 0
        for term in globaldict["terms"]:
            if term == "None":
                break
            term_courses = [course for course in globaldict["degreeworks_df"][2].items() if course[1][0] == term]
            # print(term,term_courses)
            column = columns[i]
            course_count = 0
            for course in term_courses:
                course_code = course[0]
                gsp_df.iloc[course_count,i] = course_code
                course_count += 1
            # rename column in gsp_df to term
            gsp_df = gsp_df.rename(columns={column: term})
            i += 1
        # save as csv in outputs dir
        import os
        # list os dir ../
        print(os.listdir("../"))
        if not os.path.exists("./outputs"):
            os.makedirs("./outputs",exist_ok=True)
        # print from globaldict the degreeworks path 

        print("(((((((((((((((((((((((((((((((degreeworks_path)))))))))))))))))))))))))))))))))")
        print(globaldict["degreeworks_path"])
        dwpath = globaldict["degreeworks_path"]
        # print from globaldict the four year schedule path
        print("(((((((((((((((((((((((((((((((schedule_path)))))))))))))))))))))))))))))))))")
        print(globaldict["schedule_path"])
        fyspath = globaldict["schedule_path"]
        os.makedirs('tmp', exist_ok=True)
        extract_course_prerequisites_main('tmp/course_prerequisites.csv')
        prereqpath = r".\tmp\course_prerequisites.csv"
        print("(((((((((((((((((((((((((((((((prereqpath)))))))))))))))))))))))))))))))))")
        raw_text, student_info, courses_info = parse_degreeworks(dwpath, False, False)
        print(student_info['Student Name'])

        df_4year = load_csv_schedule(fyspath, 0)
        df_prerequisites = pd.read_csv(prereqpath)
        
        pre_req_dict_1 = get_pre_req_dict(df_prerequisites)
        global pre_req_dict
        pre_req_dict = pre_req_dict_1

        courses_info_df = get_courses_info_df(courses_info)

        print(courses_info_df)

        courses_info_df_new_schedule5 = plan_schedule_recursively(courses_info_df, df_4year)

        result_schedule = transform_schedule(courses_info_df_new_schedule5)
        print(result_schedule)





class CompletionScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Thank you for using the Smart Class Planning Tool!", font=("Helvetica", 12)).pack(pady=10)
        option_frame = tk.Frame(self)
        option_frame.pack(pady=20)
        plan_another_button = tk.Button(option_frame, text="Plan Another Schedule", command=self.plan_another)
        plan_another_button.grid(row=0, column=0, padx=10)
        exit_button = tk.Button(option_frame, text="Exit", command=self.master.quit)
        exit_button.grid(row=0, column=1, padx=10)

    def plan_another(self):
        self.master.show_screen(self.master.welcome_screen)


class UsageScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="How to Use the Smart Class Planning Tool", font=("Helvetica", 16)).pack(pady=10)
        
        steps = [
            "1. Start by clicking 'Get Started' on the Welcome Screen.",
            "2. Upload the required files: DegreeWorks PDF, Graduate Study Plan, and 4-Year Schedule.",
            "3. Proceed to validate your input files.",
            "4. Review the proposed course plan and address any warnings.",
            "5. Generate the final course plan and download it as an Excel file.",
            "6. Optionally, you can plan another schedule or exit the application."
        ]
        for step in steps:
            tk.Label(self, text=step, font=("Helvetica", 12), wraplength=450, anchor="w").pack(pady=2, anchor="w")

class PrerequisiteExtractionScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Prerequisite Extraction", font=("Helvetica", 16)).pack(pady=10)

        self.status_message = tk.StringVar(value="Click the button to extract prerequisites.")
        tk.Label(self, textvariable=self.status_message).pack(pady=10)

        extract_button = tk.Button(self, text="Extract and Update Prerequisites", command=self.extract_prerequisites)
        extract_button.pack(pady=20)

        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(fill="x", padx=10, pady=10)

        self.tree = ttk.Treeview(self.tree_frame, height=10)
        self.tree.pack(side="left", fill="x", expand=True)

    def extract_prerequisites(self):
        try:
            url = 'https://catalog.columbusstate.edu/course-descriptions/cpsc/'
            course_data = extract_course_prerequisites(url)
            df = pd.DataFrame(course_data)
            #  make dir outputs if not exists
            if not os.path.exists("./outputs"):
                os.makedirs("./outputs",exist_ok=True)

            # Save to outputs folder
            output_path = "./outputs/prerequisites.csv"
            df.to_csv(output_path, index=False)
            self.status_message.set(f"Prerequisites extracted and saved to {output_path}")

            # Display data in Treeview
            self.display_data(df)

        except Exception as e:
            self.status_message.set(f"Error extracting prerequisites: {e}")

    def display_data(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

# Run the application
if __name__ == "__main__":
    app = SmartClassPlanningApp()
    app.mainloop()


