import numpy as np
import matplotlib.pyplot as plt
import colorsys

def create_RGB_list(N):
    HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    return RGB_tuples

def line_type(line):
    if 0 == line.count('/'):
        return 'header'
    if 1 == line.count('/'):
        return 'header'
    if not 'Science:' in line:
        return 'clicks'
#    if 2 == line.count('/'):
#        return 'clicks'
    if 3 == line.count('/'):
        return 'course'
    if 4 == line.count('/'):
        return 'exam'
    if 5 == line.count('/'):
        return 'question'
    return 'other'

def hms_to_sec(mytime):
    h,m,s = mytime.split(':')
    return int(s) + 60*int(m) + 60*60*int(h)

def add_to_target_dict(line,target_dict):
    page,pageviews,unique_pageviews,unique_visitors,avg_time,pages_per_visit,visit_duration = line.strip().split(',')
    target_dict['pageviews'] = int(pageviews)
    target_dict['unique_pageviews'] = int(unique_pageviews)
    target_dict['avg_time'] = hms_to_sec(avg_time)
    target_dict['pages_per_visit'] = float(pages_per_visit)
    target_dict['visit_duration'] = hms_to_sec(visit_duration)
    return target_dict

def add_course_info(page_info,line,course_name):
    if not page_info.has_key(course_name):
        page_info[course_name] = {}
    target_dict = page_info[course_name]
    target_dict = add_to_target_dict(line,target_dict)
    return page_info

def add_exam_info(page_info,line,course_name,exam_name):
    if not page_info.has_key(course_name):

        page_info[course_name] = {}
    if not page_info[course_name].has_key(exam_name):
        page_info[course_name][exam_name] = {}
    target_dict = page_info[course_name][exam_name]
    add_to_target_dict(line,target_dict)
    return page_info

def add_question_info(page_info,line,course_name,exam_name,question_name):
    if not page_info.has_key(course_name):
        page_info[course_name] = {}
    if not page_info[course_name].has_key(exam_name):
        page_info[course_name][exam_name] = {}
    page_info[course_name][exam_name][question_name] = {}
    target_dict = page_info[course_name][exam_name][question_name]
    add_to_target_dict(line,target_dict)
    return page_info

def add_page_info(page_info,line,which_type):
    if 'exam' == which_type:
        course_name = line.split(',')[0].split('/')[-2]
        exam_name = line.split(',')[0].split('/')[-1]
        page_info = add_exam_info(page_info,line,course_name,exam_name)
    elif 'course' == which_type:
        course_name = line.split(',')[0].split('/')[-1]
        page_info = add_course_info(page_info,line,course_name)
    elif 'question' == which_type:
        course_name = line.split(',')[0].split('/')[-3]
        exam_name = line.split(',')[0].split('/')[-2]
        question_name = line.split(',')[0].split('/')[-1]
        page_info = add_question_info(page_info, line, course_name, exam_name, question_name)
    return page_info

def list_courses(page_info):
    sorted_keys = sorted(page_info.keys())
    list_of_courses = []
    for key in sorted_keys:
        if type({}) == type(page_info[key]):
            list_of_courses.append(key)
    return list_of_courses

def list_exams(page_info, course):
    list_of_exams = []
    sorted_keys = sorted(page_info[course].keys())
    for key in sorted_keys:
        if type({}) == type(page_info[course][key]):
            list_of_exams.append(key)
    return list_of_exams

def list_questions(page_info, course, exam):
    list_of_questions = []
    sorted_keys = sorted(page_info[course][exam].keys())
    for key in sorted_keys:
        if type({}) == type(page_info[course][exam][key]) and 'Question' in key:
            list_of_questions.append(key)
    return list_of_questions

def print_course_exam_questions(page_info):
    for course in list_courses(page_info):
        for exam in list_exams(page_info,course):
            print course,exam,list_questions(page_info,course,exam)

def visit_duration_dist(page_info, course, include_subpages=True):
    front_page_dist = {}
    front_and_subpages_dist = {}
    for exam in list_exams(page_info, course):
        try:
            front_page_dist[exam] = page_info[course][exam]['visit_duration']
            front_and_subpages_dist[exam] = front_page_dist[exam]
            for question in list_questions(page_info, course, exam):
                front_and_subpages_dist[exam] += page_info[course][exam][question]['visit_duration']
        except ValueError:
            continue
        except KeyError:
            continue
    if not include_subpages:
        return front_page_dist
    else:
        return front_and_subpages_dist

def plot_visit_duration_dist(page_info, course, style='pie', include_subpages=True):
    dict_to_plot = visit_duration_dist(page_info, course, include_subpages)
    y = []
    my_labels = []
    for num,key in enumerate(sorted(dict_to_plot.keys())):
        # disregard entries below 1%
        if float(dict_to_plot[key])/sum(dict_to_plot.values()) < 0.01:
            continue
        y.append(dict_to_plot[key])
        if 'pie' == style:
            my_labels.append(key.replace('_','') + ' [' + str(int(y[num]/60/60)) + 'h ' + str(int(100*round(float(dict_to_plot[key])/sum(dict_to_plot.values()),2))) + '%]')
        elif 'bar' == style:
            my_labels.append(key.replace('December_','Dec').replace('April_','Apr').replace('20','') + '\n' + str(int(100*round(float(dict_to_plot[key])/sum(dict_to_plot.values()),2))) + '%')
    y = np.asarray(y)
    if 'pie' == style:
        plt.pie(y, labels = my_labels, startangle = 90)
    elif 'bar' == style:
        plt.bar(range(len(y)),y/60/60,align='center',color=create_RGB_list(len(y)))
        plt.gca().set_xticks(range(len(y)))
        plt.gca().set_xticklabels(my_labels)
        plt.ylabel('Total pageview time in hours')
    plt.title(course + ' - Total pageview time per exam')

def data_to_dict_clickdates_clickscount(filename):
    f = open(filename,'r')
    page_info = {}
    click_dates = []
    click_counts = []
    for line in f:
        if line_type(line) == 'header':
            continue
        elif line_type(line) == 'exam' or line_type(line) == 'course' or line_type(line) == 'question':
            page_info = add_page_info(page_info,line,line_type(line))
        elif line_type(line) == 'clicks':
            date,count = line.strip().split(',')
            click_dates.append(date)
            click_counts.append(int(count))
    return page_info,click_dates,click_counts

def clean_dict(mydict, valid_course_numbers):
    for course in list_courses(mydict):
        if not course in valid_course_numbers:
            del mydict[course]
            continue
        for exam in list_exams(mydict,course):
            if not is_valid_exam(exam):
                del mydict[course][exam]
                continue
            for question in list_questions(mydict,course,exam):
                if not is_valid_question(question):
                    del mydict[course][exam][question]

# Returns a boolean telling whether an exam is valid based on its name.
def is_valid_exam(exam):
    cond1 = len(exam) > 4        # Exam name is longer than 4 chars
    cond2 = True            # Last four chars are integers
    for ch in exam[-4:]:
        try:
            type(int(ch))
        except ValueError:
            cond2 = False
    cond3 = not 'logid' in exam        # 'logid' is NOT in the exam name.
    return cond1 and cond2 and cond3    #IF all above cond. are satisfied, return TRUE

# Returns a boolean indicating if a question is valid based on the URL
def is_valid_question(question):
    cond1 = len(question) > 4        # Question is longer than 4 chars
    cond2 = not 'logid' in question    # 'logid' is NOT in the question
    return cond1 and cond2        # IF all above cond. are satisfied, return TRUE

def plot_clicks(num_clicks):
    myarray = np.asarray(num_clicks)
    plt.plot(myarray)
    plt.xlabel('Days since start of term')
    plt.ylabel('Number of clicks')
    plt.title('Total number of clicks: ' + str(np.sum(myarray)))

def fraction_course_exam_question_by_key(mydict,mykey):
    total_course_time = 0
    total_exam_time = 0
    total_question_time = 0
    for course in list_courses(mydict):
        try:
            total_course_time += mydict[course][mykey]
        except KeyError:
            pass
        for exam in list_exams(mydict,course):
            try:
                total_exam_time += mydict[course][exam][mykey]
            except KeyError:
                pass
            for question in list_questions(mydict,course,exam):
                try:
                    total_question_time += mydict[course][exam][question][mykey]
                except KeyError:
                    pass
    total_time = float(total_course_time + total_exam_time + total_question_time)
    return total_course_time/total_time, total_exam_time/total_time, total_question_time/total_time


def plot_question_dist(mydict, course, exam, mykey, plot_type = 'bar'):
    question_keys = sorted(list_questions(mydict, course, exam))
    if len(question_keys) > 1:
        y = []
        my_labels = []
        num = 0
        for question in question_keys:
            value = mydict[course][exam][question][mykey]
            #disregard pages with less than too few unique pageviews. High chance these are typos
            if 10 > mydict[course][exam][question]['unique_pageviews']:
                continue
            y.append(float(value))
            label_question = question.replace('_','').replace('Question','Q')
            if 'pageviews' == mykey:
                label_data = str(value)
                ylabel = 'Total page views'
            elif 'unique_pageviews' == mykey:
                label_data = str(value)
                ylabel  = 'Unique page views'
            elif 'avg_time' == mykey:
                label_data = '[' + str(int(value/60)) + 'm' + str(int(value%60)) + 's]'
                ylabel = 'Average time spent in m'
                y[num] /= 60
            elif 'pages_per_visit' == mykey:
                NotImplemented
            elif 'visit_duration' == mykey:
                label_data = '[' + str(int(value/60/60)) + 'h' + str(int((value%(60*60))/60)) + 'm]'
                ylabel = 'Total time spent in h'
                y[num] /= 3600
            if 'bar' == plot_type:
                my_labels.append(label_question)
            elif 'pie' == plot_type:
                my_labels.append(label_question + ' ' + label_data)
            num += 1
        y = np.asarray(y)
        if 'bar' == plot_type:
            plt.bar(range(len(y)),y,align='center',color=create_RGB_list(len(y)))
            plt.gca().set_xticks(range(len(y)))
            plt.gca().set_xticklabels(my_labels)
            plt.xticks(rotation='vertical')
            plt.ylabel(ylabel)
            plot_title = course + ' ' + exam.replace('_',' ')
        elif 'pie' == plot_type:
            plt.pie(y, labels=my_labels, startangle=90, colors=create_RGB_list(len(y)))
            plot_title = course + ' ' + exam.replace('_',' ') + ' ' + mykey
        plt.title(plot_title)


def get_total_exam_time(mydict):
    total_exam_time = {}
    for course in list_courses(mydict):
        total_exam_time[course] = {}
        for exam in list_exams(mydict, course):
            total_exam_time[course][exam] = 0
            for question in list_questions(mydict, course, exam):
                total_exam_time[course][exam] += mydict[course][exam][question]['avg_time']
        for courses in total_exam_time.keys():
            if not total_exam_time[courses]:
                del total_exam_time[courses]
    return total_exam_time


def print_total_exam_time(total_exam_time, course):
    y = []
    my_label = []
    for exam in total_exam_time[course]:
        #remove exams where total time was less than threshold (in s)
        if 10*60 > total_exam_time[course][exam]:
            continue
        y.append(float(total_exam_time[course][exam])/60)
        my_label.append(exam.replace('_',' '))
    y = np.asarray(y)
    plt.bar(range(len(y)), y, align='center', color=create_RGB_list(len(y)))
    plt.gca().set_xticks(range(len(y)))
    plt.gca().set_xticklabels(my_label,size='small')
    plt.xticks(rotation='80',size='small')
    plt.ylabel('Total time per exam (min)\n based on average \n for each question',size='small')
    plt.title(course)

def load_delta_t(filename):

    import csv
    with open(filename,'r') as delt:
            reader = csv.reader(delt, delimiter=',')
            row = reader.next()
            while len(row) <= 1:
                row = reader.next()
            num_cols = len(row)
            labels = row;
            row = reader.next();
            delta_t = [];
            while len(row) == num_cols:
                try:
                        delta_t.extend([int(row[0])]*int(row[1]))
                        row = reader.next()
                except ValueError:
                        row = reader.next()
    return delta_t
    
# Plot a pie chart showing the relative amount of time spent on pages related to a course
def plot_pie_chart_time_spent_on_course(my_dict,thres,colors):
    labels = []
    total_time = np.zeros(len(list_courses(my_dict)))
    for num,course in enumerate(list_courses(my_dict)):
        try:
            total_time[num] = my_dict[course]['visit_duration']
        except:
            pass
        for exam in list_exams(my_dict,course):
            try:
                total_time[num] += my_dict[course][exam]['visit_duration']
            except:
                pass
            for question in list_questions(my_dict,course,exam):
                total_time[num] += my_dict[course][exam][question]['visit_duration']            
        labels.append(course + " [" + str(round(total_time[num]/60.0/60.0/1000,1)) + " kh]")
    
    thres = thres*sum(total_time)

    inds = [];
    for time in total_time:
        if time < thres:
            inds.append(np.where(total_time == time)[0][0])
    other_labels = [labels[i] for i in inds];
    other_time = sum(total_time[inds]);

    tt = np.delete(total_time,inds)
    for lab in other_labels:
        labels.remove(lab)
    labels.append('OTHER [' + str(round(other_time/60.0/60.0/1000,1)) + ' kh]')
    tt = np.append(tt,other_time)
        
    plt.pie(tt, labels = labels, shadow = False, autopct = '%.1f%%',pctdistance=0.6, labeldistance=1.2, colors=colors )
    plt.title('Total time users spent on all wiki pages by course ' + " [" + str(round(np.sum(total_time)/60.0/60.0/1000,1)) + " kh]",size='26')

# Plot the number of clicks per day in time
def plot_total_clicks_time_series(date_list, num_clicks, logarithmic,showExamLabels):
    x_axis=[]
    x_axis.append(date_list.index('1/1/12'))
    x_axis.append(date_list.index('5/1/12'))
    x_axis.append(date_list.index('9/1/12'))
    x_axis.append(date_list.index('1/1/13'))
    x_axis.append(date_list.index('5/1/13'))
    x_axis.append(date_list.index('9/1/13'))
    x_axis.append(date_list.index('1/1/14'))

    myarray = np.asarray(num_clicks)

    if logarithmic:
        plt.semilogy(myarray,linewidth=2)
        plt.ylabel('Number of clicks', size='x-large')
    else:
        plt.plot(myarray,linewidth=2)
        plt.gca().set_yticklabels(['0','10','20','30','40','50','60','70'],size='x-large')
        plt.ylabel('Number of clicks (in thousands)', size='x-large')
    
    plt.grid(b=True, which='major', color='0.85',linestyle='-')
    plt.xlabel('Date', size='x-large')
    plt.title('Total number of clicks: ' + str(np.sum(myarray)), size='x-large')
    plt.gca().set_xticks(x_axis)
    plt.gca().set_xticklabels(['Jan 12','May 12','Sep 12','Jan 13','May 13','Sep 13','Jan 14'],size='x-large')

    ## Exams  ##
    # APR 2014
    index = date_list.index('4/25/14')
    plt.plot([index,index],[1,70000],'g:')
    if showExamLabels:
        plt.text(index+5, 65000, 'Math 101', size='x-large')

    index = date_list.index('4/24/14')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 50000, 'Math 103', size='x-large')

    index = date_list.index('4/24/14')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 35000, 'Math 105', size='x-large')

    index = date_list.index('4/24/14')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 20000, 'Math 110', size='x-large')

    index = date_list.index('4/16/14')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 42500, 'Math 152', size='x-large')

    index = date_list.index('4/16/14')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 27500, 'Math 215', size='x-large')

    # DEC 2013
    index = date_list.index('12/10/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 65000, 'Math 100', size='x-large')

    index = date_list.index('12/11/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 50000, 'Math 102', size='x-large')

    index = date_list.index('12/11/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 35000, 'Math 104', size='x-large')

    index = date_list.index('12/11/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 20000, 'Math 110', size='x-large')

    # APR 2013
    index = date_list.index('4/15/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 40000, 'Math 152', size='x-large')

    index = date_list.index('4/19/13')
    plt.plot([index,index],[1,70000],'g:')
    if showExamLabels:
        plt.text(index+5, 65000, 'Math 103', size='x-large')

    index = date_list.index('4/22/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 50000, 'Math 101', size='x-large')

    index = date_list.index('4/22/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 35000, 'Math 105', size='x-large')

    index = date_list.index('4/22/13')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 20000, 'Math 110', size='x-large')

    # DEC 2012
    index = date_list.index('12/14/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 65000, 'Math 102', size='x-large')

    index = date_list.index('12/5/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 50000, 'Math 100', size='x-large')

    index 
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 35000, 'Math 104', size='x-large')

    index = date_list.index('12/5/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 20000, 'Math 110', size='x-large')

    # APR 2012
    index = date_list.index('4/16/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index+5, 65000, 'Math 152', size='x-large')

    index = date_list.index('4/11/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 50000, 'Math 101', size='x-large')

    index = date_list.index('4/11/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 35000, 'Math 103', size='x-large')

    index = date_list.index('4/11/12')
    plt.plot([index,index],[1,70000],'k:')
    if showExamLabels:
        plt.text(index-65, 20000, 'Math 105', size='x-large')
