""" 
site to extract : https://catalog.columbusstate.edu/course-descriptions/cpsc/

<div class="courseblock">
    <div class="cols noindent">
        <span class="text col-3 detail-code margin--tiny text--semibold text--huge">
            <strong>CPSC 1105</strong>
        </span>&nbsp;<span class="text col-3 detail-title margin--tiny text--bold text--huge">
            <strong>Introduction to Computing Principles and Technology</strong>
        </span>&nbsp;<span class="text detail-coursehours text--bold text--huge"><strong>(3-0-3)</strong></span>&nbsp;
    </div>
    <div class="noindent">
        <div class="courseblockextra noindent">This course provides an introduction to current and emerging computing
            principles and technologies used in various professional environments. It discusses the nature of
            information vs data, computer hardware, software, databases, programming, web, communications and other
            information systems-based technology. In addition, the need for information privacy and security related to
            these technologies is discussed. The theory is complemented by practical work aimed at gaining basic
            proficiency with different types of widely used application software.</div>
    </div>
</div>

<div class="courseblock">
    <div class="cols noindent"><span class="text col-3 detail-code margin--tiny text--semibold text--huge"><strong>CPSC
                1301K</strong></span>&nbsp;<span
            class="text col-3 detail-title margin--tiny text--bold text--huge"><strong>Computer Science
                I</strong></span>&nbsp;<span
            class="text detail-coursehours text--bold text--huge"><strong>(3-3-4)</strong></span>&nbsp;</div>
    <div class="noindent">
        <div class="courseblockextra noindent">This course includes an overview of computers and programming; problem
            solving and algorithm development; simple data types; arithmetic and logic operators; selection structures;
            repetition structures; text files; arrays (one-and-two-dimensional); procedural abstraction and software
            design; modular programming (including sub-programs or the equivalent). It includes a lab component that
            provides hands on projects to apply and reinforce the topics covered.</div>
    </div>
</div>

<div class="courseblock">
    <div class="cols noindent"><span class="text col-3 detail-code margin--tiny text--semibold text--huge"><strong>CPSC
                1302K</strong></span>&nbsp;<span
            class="text col-3 detail-title margin--tiny text--bold text--huge"><strong>Computer Science
                II</strong></span>&nbsp;<span
            class="text detail-coursehours text--bold text--huge"><strong>(3-3-4)</strong></span>&nbsp;</div>
    <div class="noindent">
        <div class="courseblockextra noindent">A continuation of <a href="/search/?P=CPSC%201301K"
                title="CPSC&nbsp;1301K" class="bubblelink code"
                onclick="return showCourse(this, 'CPSC 1301K');">CPSC&nbsp;1301K</a>. This course emphasizes programming
            using object-oriented methods. The fundamentals used in designing, developing and using classes,
            encapsulation, inheritance mechanisms, polymorphism and dynamic binding.</div>
        <div class="courseblockextra noindent">
            <strong>Prerequisite(s): </strong>(CPSC 1301 with a minimum grade of C or
            CPSC 1301H with a minimum grade of C or <a href="/search/?P=CPSC%201301K" title="CPSC&nbsp;1301K"
                class="bubblelink code" onclick="return showCourse(this, 'CPSC 1301K');">CPSC&nbsp;1301K</a> with a
            minimum grade of C or <a href="/search/?P=CSCI%201301K" title="CSCI&nbsp;1301K" class="bubblelink code"
                onclick="return showCourse(this, 'CSCI 1301K');">CSCI&nbsp;1301K</a> with a minimum grade of C or CPSC
            1301I with a minimum grade of C or <a href="/search/?P=CSCI%201301" title="CSCI&nbsp;1301"
                class="bubblelink code" onclick="return showCourse(this, 'CSCI 1301');">CSCI&nbsp;1301</a> with a
            minimum grade of C) and <a href="/search/?P=MATH%201113" title="MATH&nbsp;1113" class="bubblelink code"
                onclick="return showCourse(this, 'MATH 1113');">MATH&nbsp;1113</a> (may be taken concurrently) with a
            minimum grade of C</div>
    </div>
</div>
 """

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

if __name__ == '__main__':

    url = 'https://catalog.columbusstate.edu/course-descriptions/cpsc/'
    course_data = extract_course_prerequisites(url)

    # Create a DataFrame from the course data
    df = pd.DataFrame(course_data)
    

    filename = 'course_prerequisites.csv'
    # delete the file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    if os.path.exists(filename):
        base, extension = os.path.splitext(filename)
        counter = 1
        new_filename = f"{base}_{counter}{extension}"
        while os.path.exists(new_filename):
            counter += 1
            new_filename = f"{base}_{counter}{extension}"
        filename = new_filename

    df.to_csv(filename, index=False, encoding='utf-8')
