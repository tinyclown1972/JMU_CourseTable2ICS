# JMU_CourseTable2ICS
根据课表JSON文件快速生成ICS，方便导入



## 使用方法

首先使用init_start_day(year,month,day) 传入开课时间的年月日

然后调用generate_ics(get_json,ctl)，将压缩的课表json传入，若ctl为1即可生成ics文件，否则将return回课表的字符串

参考test_demo()
