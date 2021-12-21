from celery import shared_task
from check.maincheck import checkall
from utils.mysql_install import MysqlInstall


@shared_task
def main_check():
    checkall()
    return


@shared_task
def mysql_setup(node_info):
    print('MySQL安装已启动！')
    mysql_install = MysqlInstall(node_info)
    mysql_install.do_mysql_install()

