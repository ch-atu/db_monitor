
# DB monitor监控平台

## 特性
- **构建**: 前后端分离架构，Python+Django+restframework提供后台API，celery定制数据采集策略，Iview作为前端展示
- **UI**: 开箱即用的高质量前端设计，提供丰富的图表、指标展示，核心数据形成趋势图分析
- **深度定制**: 提供完整可用的数据监控方案，告别冗长的SQL脚本、常用手册，复杂数据通过web页面即可轻易浏览

## 功能简介

- 资源管理
    - MySQL/Redis/Linux资源信息录入
    - 资源管理中各类设备信息作为采集设备来源，支持动态加入实例监控列表
- 实例列表
    - 查看各监控实例列表及详细信息
- 监控告警
    - 告警配置及告警信息查看
    
## 环境

- Python 3.9
    - Django 2.2
    - Django Rest Framework 3.1
    
- Vue.js 2.9
    - iview 3.4
    

## 安装部署
### 1. 安装python3.6以上(建议)

### 2. 安装mysql5.7

注意字符集：utf-8

create database db_monitor; 

### 3. 安装redis3.2

### 4. 项目配置

#### 5. 安装依赖包
pip install -r requirements.txt

#### 6.settings配置
--MySQL数据库：

>DATABASES = {  
    'default': {  
        'ENGINE': 'django.db.backends.mysql',  
		'NAME': 'db_monitor',  
		'USER': 'root',  
		'PASSWORD': 'mysqld',  
        'HOST':'127.0.0.1',  
		'PORT': '3306',  
    }
}

--Redis：

>CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

>CELERY_BROKER_URL = 'redis://localhost:6379/2'


#### 7.创建数据库
>python manage.py makemigrations

>python manage.py migrate

>python manage.py createsuperuser(创建登录用户)

#### 8.执行数据库脚本

>@install/initdata.sql

### 9.启动/停止
>python manage.py runserver 0.0.0.0:8000 #建议使用固定IP地址启动

### 10.celery的启动
参考celery_run.txt

注：也可以使用脚本启动/关闭[不推荐]：

celery: sh celery_start[shutdown].sh

django: sh web_start[shutdown].sh

### 11.关于日志：

celery日志：logs/celery-worker.log & logs/celery-beat.log

web日志： logs/django-web.log

采集数据异常主要查看celery日志！

注：使用shell脚本启停时如遇到“/r command not found”，为linux与windows换行符格式差异导致，在Linux凭条可以在vim下执行:set ff=unix解决


