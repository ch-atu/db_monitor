# encoding:utf-8

from utils.tools import mysql_query, mysql_exec
import check.checklog as checklog
from utils.send_email import my_send_email
from utils.send_ding_msg import send_ding_msg
from datetime import datetime


# from system.models import AlarmInfo,AlarmInfoHis


def check_alarm():
    alarm_time = datetime.now()
    print('开始检查告警，告警时间：{}'.format(alarm_time))

    # checklog.logger.info('初始化告警信息表')

    # todo 不初始化告警信息表
    # mysql_exec('insert into alarm_info_his select * from alarm_info')
    # mysql_exec('delete from alarm_info')

    # # 初始化告警信息表
    # try:
    #     alarm_info_init = AlarmInfo.objects.last()  # 获取最后一条数据
    #     alarm_info_his = AlarmInfoHis()
    #
    #     alarm_info_his.tags = alarm_info_init.tags
    #     alarm_info_his.url = alarm_info_init.url
    #     alarm_info_his.alarm_type = alarm_info_init.alarm_type
    #     alarm_info_his.alarm_header = alarm_info_init.alarm_header
    #     alarm_info_his.alarm_content = alarm_info_init.alarm_content
    #     alarm_info_his.alarm_time = alarm_info_init.alarm_time
    #     alarm_info_his.save()
    # except Exception as e:
    #     print()

    check_list = mysql_query(
        "select name,judge_value,judge_sql,judge_table,conf_table,conf_column "
        "from alarm_conf "
        "where judge_sql is not null and judge_table is not null")
    for each_check in check_list:
        alarm_name, judge_value, judge_sql, judge_table, conf_table, conf_column = each_check
        checklog.logger.info("开始告警检查：{}".format(alarm_name))
        select_sql = "select count(*) from {}".format(judge_table)
        select_res = mysql_query(select_sql)
        if select_res[0][0] == 0:
            checklog.logger.info("%s未采集到数据" % alarm_name)
        else:
            is_judge_sql = 'tags in (select tags from {} where {} =1)'.format(conf_table, conf_column)
            judge_sql = judge_sql % (judge_value, is_judge_sql) if judge_value else judge_sql % is_judge_sql
            check_res = mysql_query(judge_sql)
            if check_res == 0:
                checklog.logger.info("{}:告警检查正常".format(alarm_name))
            else:
                for each in check_res:
                    tags, url, alarm_content = each
                    alarm_title = tags + ':' + alarm_name
                    checklog.logger.warning(alarm_content)

                    # todo 添加告警信息
                    insert_sql_alarm_info = ("insert into alarm_info "
                                             "(tags,url,alarm_type,alarm_header,alarm_content,alarm_time) "
                                             "values('{}','{}','{}','{}','{}','{}') ").format(
                        tags, url, alarm_name, alarm_title, alarm_content, alarm_time
                    )

                    mysql_exec(insert_sql_alarm_info)

                    # todo 添加历史告警表
                    insert_sql_alarm_info_his = ("insert into alarm_info_his "
                                                 "(tags,url,alarm_type,alarm_header,alarm_content,alarm_time)"
                                                 "values('{}','{}','{}','{}','{}','{}')".format(
                        tags, url, alarm_name, alarm_title, alarm_content, alarm_time)
                    )
                    mysql_exec(insert_sql_alarm_info_his)
                    print('添加的告警时间是:{}'.format(alarm_time))

                    # # 添加告警信息
                    # alarm_info_add = AlarmInfo()
                    # alarm_info_add.tags = tags
                    # alarm_info_add.url = url
                    # alarm_info_add.alarm_type = alarm_name
                    # alarm_info_add.alarm_header = alarm_title
                    # alarm_info_add.alarm_content = alarm_content
                    # # print('要添加到数据库的alarm_time为：', alarm_time)
                    # alarm_info_add.alarm_time = alarm_time
                    # alarm_info_add.save()
                    #
                    # alarm_test = AlarmInfo.objects.last()

                    # is_send_email(alarm_name, tags, alarm_url, alarm_title, alarm_content)
                    my_send_email(alarm_title, alarm_content)
                    send_ding_msg(alarm_content)


# if __name__ == '__main__':
#     check_alarm()
