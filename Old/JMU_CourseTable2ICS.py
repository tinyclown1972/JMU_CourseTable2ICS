from hashlib import md5
from datetime import datetime, timedelta
import json

######################################
starterDay = datetime(2021, 9, 6)  # 定义开学时间
######################################


classTime = [None,  (8, 00), (8, 50), (10,  5), (10, 55),  # 早上的上课时间
             (14, 00), (14, 50), (15, 55), (16, 45),  # 中午的上课时间
             (19, 00), (20, 50), (20, 55)]  # 晚上的上课时间


# 用于生成uid，虽然很多日历软件会屏蔽这一项
def uid_generate(key1, key2): return md5(
    f"{key1}{key2}".encode("utf-8")).hexdigest()


def init_start_day(ryear, rmonth, rday):
	global starterDay
	starterDay = datetime(ryear, rmonth, rday)


# 生成上课周，在主函数中被调用
def generate_week(n, stDay):  # n为最大上课周数，stDay为开始上课的日期
    weeks = [None]
    for i in range(1, n):
        singleWeek = [None]
        for d in range(0, 7):
            singleWeek.append(stDay)
            stDay += timedelta(days=1)
        weeks.append(singleWeek)
    return weeks


# 主函数，所有流程都在这里
def generate_ics(get_json, ctl):
    # 下面就是日历最开始固定的字符串，不用修改格式
    calendar_event = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:课表\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:Asia/Shanghai\nEND:VTIMEZONE"
    r_week = generate_week(25, starterDay)
    runtime = datetime.now().strftime('%Y%m%dT%H%M%SZ')  # 文件生成时间

    ############################
    # 处理JSON数据
    schedule_json = json.loads(get_json)
    name = schedule_json['studentTableVm']['name']  # 上课人姓名
    class_name = schedule_json['studentTableVm']['adminclass']  # 上课人班级
    courses = schedule_json['studentTableVm']['activities']  # 课程表列表

    ############################
    for Class in courses:

        ############################
        # 处理JSON,转换为对应参数
        Name = Class['courseName']
        Teacher = '.'.join(Class['teachers'])  # 老师是个列表，所以转成字符串
        Location = Class['room']
        classOrder = [Class['startUnit'], Class['endUnit']]
        classWeek = Class['weekIndexes']
        classWeekday = Class['weekday']
        ############################

        Title = Name + " - " + Location.replace('*', '')  # 将课程名及上课地点作为日历标题
        for timeWeek in classWeek:
            classDate = r_week[timeWeek][classWeekday]
            startTime = classTime[classOrder[0]]
            endTime = classTime[classOrder[-1]]
            classStartTime = classDate + \
                timedelta(minutes=startTime[0] * 60 +
                          startTime[1] - 480)  # 它的代码本身会有8小时的误差
            classEndTime = classDate + \
                timedelta(minutes=endTime[0] * 60 +
                          endTime[1] + 45 - 480)  # 所以减掉480min
            Description = " 任课教师: " + Teacher
            StartTime = classStartTime.strftime('%Y%m%dT%H%M%S')
            EndTime = classEndTime.strftime('%Y%m%dT%H%M%S')

            singleEvent = f"\nBEGIN:VEVENT\nDTSTART;TZID=Asia/Shanghai;VALUE=DATE-TIME:{StartTime}\nDESCRIPTION:{Description}\nUID:CQUPT-{uid_generate(Name, StartTime)}\nDTSTAMP:{runtime}\nSUMMARY:{Title}\nDTEND;TZID=Asia/Shanghai;VALUE=DATE-TIME:{EndTime}\nEND:VEVENT"
            calendar_event += singleEvent

    calendar_event += "\nEND:VCALENDAR"
    if(ctl):
        write_file_name = "{}-{}.ics".format(name, class_name)
        with open(write_file_name, "w", encoding="utf-8") as w:  # 以姓名班级作为文件名输出
            w.write(calendar_event)
        return calendar_event
    else:
        return calendar_event
    # end of main


def test_demo():
    r_json = None
    with open('test.json', 'r', encoding='utf-8') as f:  # 将测试JSON读入进行测试
        r_json = f.read()
    init_start_day(2021, 9, 6)  # 设置上课时间
    res = generate_ics(r_json,1)  # 直接生成文件，并返回课表字符串
    res = generate_ics(r_json,0)

test_demo()