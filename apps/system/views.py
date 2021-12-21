import json
import logging
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.shortcuts import HttpResponse
from django.contrib.auth.backends import ModelBackend
from system.models import Users
from django.db.models import Q
from system.models import AlertLog, AlarmConf, AlarmInfo
from rest_framework import permissions
from rest_framework import generics
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.system.serializers import AlertLogSerializer, AlarmConfSerializer, AlarmInfoSerializer, SetupLogSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from utils.tools import mysql_django_query
from rest_framework.renderers import JSONRenderer
from system.tasks import oracle_rac_setup, oracle_rac_onenode_setup, oracle_onenode_setup, mysql_setup

logger = logging.getLogger('system')


class UserInfo(APIView):
    """
    获取用户信息
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        token = (json.loads(request.body))['token']
        obj = Token.objects.get(key=token).user
        result = {
            'name': obj.username,
            'user_id': obj.id,
            'access': list(obj.get_all_permissions()) + ['admin'] if obj.is_superuser else list(
                obj.get_all_permissions()),
            # 'access':['hello'],
            'token': token,
            'avatar': 'https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png'
        }
        print(result)
        return HttpResponse(json.dumps(result))


class UserLogout(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        token = (json.loads(request.body))['token']
        obj = Token.objects.get(key=token)
        obj.delete()
        result = {
            "status": True
        }
        return HttpResponse(json.dumps(result))


class CustomBackend(ModelBackend):
    """
    用户名字/邮箱名字 登录
    :param request:
    :return:
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Users.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            logger.error(e)
            return None


class Menu(APIView):

    def post(self, request):
        result = [
            # 资源管理
            {
                "path": '/assets',
                "name": 'assets',
                "meta": {
                    "icon": 'ios-cloud',
                    "title": '资源管理'
                },
                "component": 'Main',
                "children": [
                    # Oracle数据库
                    {
                        'path': 'oracle-list',
                        'name': 'oracle-list',
                        'meta': {
                            'access': ['assets.view_oraclelist'],
                            'icon': 'ios-menu',
                            'title': 'Oracle数据库',
                            'hideInMenu': 'true'
                        },
                        'component': 'assets/oracle-list'
                    },
                    # MySQL数据库
                    {
                        'path': 'mysql-list',
                        'name': 'mysql-list',
                        'meta': {
                            'access': ['assets.view_mysqllist'],
                            'icon': 'ios-menu',
                            'title': 'MySQL数据库'
                        },
                        'component': 'assets/mysql-list'
                    },
                    # Linux主机
                    {
                        'path': 'linux-list',
                        'name': 'linux-list',
                        'meta': {
                            'access': ['assets.view_linuxlist'],
                            'icon': 'ios-menu',
                            'title': 'Linux主机'
                        },
                        'component': 'assets/linux-list'
                    },
                    # Redis
                    {
                        'path': 'redis-list',
                        'name': 'redis-list',
                        'meta': {
                            'access': ['assets.view_redislist'],
                            'icon': 'ios-menu',
                            'title': 'Redis'
                        },
                        'component': 'assets/redis-list'
                    }
                ]
            },
            # 实例列表
            {
                "path": '/monlist',
                "name": '实例列表',
                "meta": {
                    "icon": 'ios-apps',
                    "title": '实例列表'
                },
                "component": 'Main',
                "children": [
                    # Oracle列表
                    {
                        'path': 'oracle',
                        'name': 'oracle',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'Oracle列表',
                            'access': ['oracle.view_oraclestat'],
                            'hideInMenu': 'true',
                        },
                        'component': 'oracle/stat-list'
                    },
                    # MySQL列表
                    {
                        'path': 'mysql',
                        'name': 'mysql',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'MySQL列表',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/stat-list'
                    },
                    # Redis列表
                    {
                        'path': 'redis',
                        'name': 'redis',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'Redis列表',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/stat-list'
                    },
                    # Linux列表
                    {
                        'path': 'linux',
                        'name': 'linux',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'Linux列表',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'linux/stat-list'
                    }
                ],

            },
            # 监控告警
            {
                "path": '/alarm',
                "name": 'alarm',
                "meta": {
                    "icon": 'ios-warning',
                    "title": '监控告警'
                },
                "component": 'Main',
                "children": [
                    # 告警记录
                    {
                        'path': 'alarm-info',
                        'name': 'alarm-info',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': '告警记录'
                        },
                        'component': 'system/alarm-info'
                    },
                    # 告警配置
                    {
                        'path': 'alarm-conf',
                        'name': 'alarm-conf',
                        'meta': {
                            'access': ['system.view_alarmconf'],
                            'icon': 'ios-menu',
                            'title': '告警配置'
                        },
                        'component': 'system/alarm-conf'
                    }
                ]
            },
            # 数据库部署
            {
                "path": '/setup',
                "name": 'setup',
                "meta": {
                    "icon": 'ios-build',
                    "title": '数据库部署',
                    'hideInMenu': 'true',
                },
                "component": 'Main',
                "children": [
                    # Oracle One Node
                    {
                        'path': 'oracle-onenode',
                        'name': 'oracle-oennode',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': 'Oracle One Node'
                        },
                        'component': 'system/oracle-onenode-setup'
                    },
                    # Oracle RAC
                    {
                        'path': 'oracle-rac',
                        'name': 'oracle-rac',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': 'Oracle RAC'
                        },
                        'component': 'system/oracle-rac-setup'
                    },
                    # Oracle RAC One Node
                    {
                        'path': 'oracle-rac-onenode',
                        'name': 'oracle-rac-onenode',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': 'Oracle RAC One Node'
                        },
                        'component': 'system/oracle-rac-onenode-setup'
                    },
                    # MySQL
                    {
                        'path': 'MySQL',
                        'name': 'MySQL',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': 'MySQL'
                        },
                        'component': 'system/mysql-setup'
                    }
                ]
            },
            # oracle数据库监控
            {
                "path": '/oracle',
                "name": 'Oracle',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'Oracle数据库监控'
                },
                "component": 'Main',
                "children": [
                    # Oracle概览
                    {
                        'path': ':tags/view',
                        'name': 'oracle-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Oracle概览',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'oracle/view'
                    },
                    # 资源
                    {
                        'path': ':tags/resource',
                        'name': 'oracle-resource',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '资源',
                            'access': ['oracle.view_oracletablespace'],
                        },
                        'component': 'oracle/resource'
                    },
                    # 表空间
                    {
                        'path': ':tags/resource/tablespace/:tablespace_name',
                        'name': 'oracle-tablespace',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '表空间',
                            'access': ['oracle.view_oracletablespace'],
                        },
                        'component': 'oracle/tablespace'
                    },
                    # 临时表空间
                    {
                        'path': ':tags/resource/temptablespace/:tablespace_name',
                        'name': 'oracle-temptablespace',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '临时表空间',
                            'access': ['oracle.view_oracletablespace'],
                        },
                        'component': 'oracle/temp-tablespace'
                    },
                    # UNDO表空间
                    {
                        'path': ':tags/resource/undotablespace/:tablespace_name',
                        'name': 'oracle-undotablespace',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'UNDO表空间',
                            'access': ['oracle.view_oracletablespace'],
                        },
                        'component': 'oracle/undo-tablespace'
                    },
                    # 活动会话
                    {
                        'path': ':tags/active-session',
                        'name': 'oracle-active-session',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '活动会话',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'oracle/active-session'
                    },
                    # 性能图
                    {
                        'path': ':tags/performance',
                        'name': 'oracle-performance',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '性能图',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'oracle/performance'
                    },
                    # TOP SQL
                    {
                        'path': ':tags/top-sql',
                        'name': 'oracle-top-sql',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'TOP SQL',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'oracle/top-sql'
                    },
                    # 日志解析
                    {
                        'path': ':tags/alert-log',
                        'name': 'oracle-alertlog',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '日志解析',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'oracle/alert-log'
                    },
                    # 统计信息
                    {
                        'path': ':tags/table-stats',
                        'name': 'oracle-tablestats',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '统计信息',
                            'access': ['oracle.view_oraclestat'],
                        },
                        'component': 'oracle/table-stats'
                    }

                ],

            },
            # Linux主机监控
            {
                "path": '/linux',
                "name": 'Linux',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'Linux主机监控'
                },
                "component": 'Main',
                "children": [
                    # Linux概览
                    {
                        'path': ':tags/view',
                        'name': 'linux-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Linux概览',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/view'
                    },
                    # 磁盘IO
                    {
                        'path': ':tags/io',
                        'name': 'linux-io',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '磁盘IO',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/io'
                    },
                    # 内存 & 虚拟内存
                    {
                        'path': ':tags/memory',
                        'name': 'linux-memory',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '内存&虚拟内存',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/memory'
                    }
                ]
            },
            # MySQL数据库监控
            {
                "path": '/mysql',
                "name": 'MySQL',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'MySQL数据库监控'
                },
                "component": 'Main',
                "children": [
                    # MySQL概览
                    {
                        'path': ':tags/view',
                        'name': 'mysql-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'MySQL概览',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/view'
                    },
                    # MyISAM
                    {
                        'path': ':tags/myisam',
                        'name': 'mysql-myisam',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'MyISAM',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/myisam'
                    },
                    # Innodb
                    {
                        'path': ':tags/innodb',
                        'name': 'mysql-innodb',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Innodb',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/innodb'
                    },
                    # 后台日志
                    {
                        'path': ':tags/alert-log',
                        'name': 'mysql-alert-log',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '后台日志',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/alert-log'
                    },
                    # 慢查询
                    {
                        'path': ':tags/slowquery-log',
                        'name': 'mysql-slowquery-log',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '慢查询',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/slowquery-log'
                    }
                ]

            },
            # Redis数据库监控
            {
                "path": '/redis',
                "name": 'Redis',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'Redis监控'
                },
                "component": 'Main',
                "children": [
                    # Redis概览
                    {
                        'path': ':tags/view',
                        'name': 'redis-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Redis概览',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/view'
                    },
                    # Redis实时状态
                    {
                        'path': ':tags/immediate-stats',
                        'name': 'redis-immediate-stats',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Redis实时状态',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/immediate-stats'
                    },
                    # Redis配置项
                    {
                        'path': ':tags/config',
                        'name': 'redis-config',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Redis配置项',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/config'
                    },
                    # 慢查询分析
                    {
                        'path': ':tags/slowlog',
                        'name': 'redis-slowlog',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '慢查询分析',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/slowlog'
                    },
                    # 连接信息
                    {
                        'path': ':tags/clientlist',
                        'name': 'redis-clientlist',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '连接信息',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/clientlist'
                    },
                    # 命令曲线
                    {
                        'path': ':tags/commandstats',
                        'name': 'redis-commandstats',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '命令曲线',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/command-stats'
                    },
                    # 后台日志
                    {
                        'path': ':tags/alert-log',
                        'name': 'redis-alert-log',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '后台日志',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/alert-log'
                    },
                ]

            }
            # 多级菜单
            # {
            #     "path": '/multilevel',
            #     "name": 'multilevel',
            #     "meta": {
            #         "icon": 'md-menu',
            #         "title": '多级菜单'
            #     },
            #     "component": 'Main',
            #     "children": [
            #         {
            #             "path": '/level_2_1',
            #             "name": 'level_2_1',
            #             "meta": {
            #                 "icon": 'md-funnel',
            #                 "title": '二级-1'
            #             },
            #             "component": 'multilevel/level-2-1'
            #         },
            #
            #     ]
            # },
        ]
        return HttpResponse(json.dumps(result))


class ApiAlertLog(generics.ListAPIView):
    queryset = AlertLog.objects.all().order_by('-log_time')
    serializer_class = AlertLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_fields = ['tags', 'log_level']
    search_fields = ['log_content']
    permission_classes = (permissions.DjangoModelPermissions,)


class ApiAlarmConf(generics.ListCreateAPIView):
    queryset = AlarmConf.objects.get_queryset().order_by('-type')
    serializer_class = AlarmConfSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('type', 'name',)
    search_fields = ('type', 'name',)
    permission_classes = (permissions.DjangoModelPermissions,)


class ApiAlarmConfDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AlarmConf.objects.get_queryset().order_by('id')
    serializer_class = AlarmConfSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class ApiAlarmInfo(generics.ListCreateAPIView):
    def get_queryset(self):
        tags = self.request.query_params.get('tags', None)
        if tags:
            result = AlarmInfo.objects.filter(tags=tags).order_by('-id')
            return AlarmInfo.objects.filter(tags=tags).order_by('-id')  # 倒序
        else:
            return AlarmInfo.objects.all().order_by('-id')  # 倒序

    serializer_class = AlarmInfoSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class ApiAlarmInfoHis(generics.ListCreateAPIView):
    queryset = AlarmInfo.objects.get_queryset().order_by('-id')
    serializer_class = AlarmInfoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('tags',)
    search_fields = ('tags', 'alarm_content',)
    permission_classes = (permissions.DjangoModelPermissions,)


@api_view(['POST'])
def ApiOracleRacSetup(request):
    postBody = request.body
    json_result = json.loads(postBody)
    rac_info = json_result
    node_list = [
        {
            'node_id': str(json_result['node1_id']),
            'hostname': json_result['hostname'] + str(json_result['node1_id']),
            'ip': json_result['node1_ip'],
            'ip_vip': json_result['node1_vip'],
            'ip_priv': json_result['node1_priv_ip'],
            'password': json_result['node1_password']
        },
        {
            'node_id': str(json_result['node2_id']),
            'hostname': json_result['hostname'] + str(json_result['node2_id']),
            'ip': json_result['node2_ip'],
            'ip_vip': json_result['node2_vip'],
            'ip_priv': json_result['node2_priv_ip'],
            'password': json_result['node2_password']
        },
    ]
    module = json_result['module']
    oracle_rac_setup.delay(rac_info, node_list, module)
    # oracleracinstall = OracleRacInstall(rac_info, node_list)
    # oracleracinstall.do_rac_install(module)
    return HttpResponse('success!')


@api_view(['POST'])
def ApiOracleRacOneNodeSetup(request):
    postBody = request.body
    json_result = json.loads(postBody)
    node_info = json_result
    # print(json_result)
    module = json_result['module']
    oracle_rac_onenode_setup.delay(node_info, module)
    # oracleracinstall = OracleRacInstall(rac_info, node_list)
    # oracleracinstall.do_rac_install(module)
    return HttpResponse('success!')


@api_view(['POST'])
def ApiOracleOneNodeSetup(request):
    postBody = request.body
    json_result = json.loads(postBody)
    node_info = json_result
    # print(json_result)
    module = json_result['module']
    oracle_onenode_setup.delay(node_info, module)
    return HttpResponse('success!')


@api_view(['POST'])
def ApiMysqlSetup(request):
    postBody = request.body
    json_result = json.loads(postBody)
    node_info = json_result
    print(json_result)
    mysql_setup.delay(node_info)
    return HttpResponse('success!')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiSetupLog(request):
    sql = "select id,log_type,log_time,log_level,log_content from setup_log"
    setup_log_list = mysql_django_query(sql)
    serializer = SetupLogSerializer(setup_log_list, many=True)
    json = JSONRenderer().render(serializer.data)
    return HttpResponse(json)


# 日志导出
from system.models import AlarmInfo
from django.http import JsonResponse

from datetime import timedelta

from utils.tools import get_zero_time


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def ExportAlarmInfo(request):
    export_alarm_info = []
    alarm_info = []
    day_field = request.query_params.get('day', None)
    if day_field and day_field != 'undefined':
        if day_field == '0':
            zero_today, now = get_zero_time(int(day_field))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_today, alarm_time__lte=now)
        if day_field == '1':
            # 获取昨天的00:00:00点到23:59:59
            zero_yesterday, now = get_zero_time(int(day_field))
            last_yesterday = zero_yesterday + timedelta(hours=23, minutes=59, seconds=59)

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_yesterday, alarm_time__lte=last_yesterday)
        elif day_field == '7':
            # 获取7天前的00:00:00
            zero_seven, now = get_zero_time(int(day_field))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_seven, alarm_time__lte=now)
        elif day_field == '30':
            # 获取30天前的00:00:00
            zero_thirty, now = get_zero_time(int(day_field))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_thirty, alarm_time__lte=now)
        elif day_field == '365':
            # 获取一年前的00:00:00
            zero_before_year, now = get_zero_time(int(day_field))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_before_year, alarm_time__lte=now)
    else:
        zero_today, now = get_zero_time(0)

        alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_today, alarm_time__lte=now)
    for each_alarm_info in alarm_info:
        export_alarm_info.append(
            {
                'tags': each_alarm_info.tags,
                'url': each_alarm_info.url,
                'alarm_type': each_alarm_info.alarm_type,
                'alarm_header': each_alarm_info.alarm_header,
                'alarm_content': each_alarm_info.alarm_content,
                'alarm_time': each_alarm_info.alarm_time
            }
        )
    return JsonResponse(export_alarm_info, safe=False)
