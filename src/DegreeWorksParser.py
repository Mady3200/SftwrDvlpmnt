# read pdf to text
import re
import fitz
# read args
import argparse



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
                print(area)
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
                courses_info[course_code.strip()] = [term.strip(), grade.strip(), credits.strip()]
                    
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
                courses_info[course_code.strip()] = [term.strip(), grade.strip(), credits.strip()]
        if debug or resultsprint:
            print('*'*100)

    print(*courses_info.items(), sep='\n')

    return raw_text,student_info, courses_info

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DegreeWorks Parser')
    parser.add_argument('--alldebug', action='store_true', help='Enable debug mode')
    parser.add_argument('--pdfpath', type=str, help='Path to the PDF file', default=r"..\inputs_new\degreeworks.pdf")
    # resultsprint
    parser.add_argument('--resultsprint', action='store_true', help='Enable resultsprint mode')
    args = parser.parse_args()
    debug = args.alldebug
    pdfpath = args.pdfpath
    resultsprint = args.resultsprint
    print(debug,pdfpath,resultsprint)
    parse_degreeworks(pdfpath,resultsprint,debug)
