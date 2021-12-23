/*
Navicat MySQL Data Transfer

Source Server         : dbmon
Source Server Version : 50717
Source Host           : 192.168.48.50:3306
Source Database       : db_monitor_dev

Target Server Type    : MYSQL
Target Server Version : 50717
File Encoding         : 65001
*/

INSERT INTO `alarm_conf` VALUES (17, 4, 'Linux主机通断告警', '>=', 2, '连续中断次数', 'linux_stat', 'select tags,\n       host url,  \n       concat(tags,\n              \':Linux主机通断告警\',\n              \'\\n 告警时间：\',\n              current_timestamp(),\n              \' \\n 主机IP: \',\n              host\n             ) content\n  from linux_stat\n where status = 1 and 99 > %s\n  and %s', 'linux_list', 'alarm_connect');
INSERT INTO `alarm_conf` VALUES (18, 4, 'Linux主机CPU使用率告警', '>=', 90, '使用百分比', 'linux_stat', 'select tags,\n       host url,\n       concat(tags,\n              \':Linux主机CPU使用率告警\',\n              \'\\n 告警时间：\',\n              current_timestamp(),\n              \' \\n 主机IP: \',\n              host,\n              \'\\n CPU使用率：\',\n              cpu_used,\n              \'%%\') content\n  from linux_stat\n where cpu_used >= %s\n  and %s', 'linux_list', 'alarm_cpu');
INSERT INTO `alarm_conf` VALUES (19, 4, 'Linux主机内存使用率告警', '>=', 90, '使用百分比', 'linux_stat', 'select tags,\n       host url,  \n       concat(tags,\n              \':Linux主机内存使用率告警\',\n              \'\\n 告警时间：\',\n              current_timestamp(),\n              \' \\n 主机IP: \',\n              host,\n              \'\\n 内存使用率：\',\n              mem_used,\n              \'%%\'\n             ) content\n  from linux_stat\n where mem_used >= %s\n  and %s', 'linux_list', 'alarm_mem');
INSERT INTO `alarm_conf` VALUES (20, 4, 'Linux主机文件系统使用率告警', '>=', 95, '使用百分比', 'linux_disk', 'select tags,\n       host url,  \n       concat(tags,\n              \':Linux主机磁盘使用率告警\',\n              \'\\n 告警时间：\',\n              current_timestamp(),\n              \' \\n 主机IP: \',\n              host,\n              \' \\n 目录名称：\',\n              mount_point,\n              \' \\n 目录总大小(GB)：\',\n              round(total_size/1024,2),\n              \'\\n 目录可用大小(GB)\',\n              round(free_size/1024,2),\n              \'\\n 使用率：\',\n              used_percent,\n              \'%%\'\n             ) content\n  from linux_disk\n where used_percent >= %s\n       and free_size < 5\n  and %s', 'linux_list', 'alarm_disk');
INSERT INTO `alarm_conf` VALUES (21, 2, 'MySQL数据库通断告警', '>=', 1, '连续中断次数', 'mysql_stat', 'select tags,\n       concat(host, \':\', port) url,  \n       concat(tags,\n              \':MySQL数据库通断告警\',\n              \'\\n 告警时间：\',\n              current_timestamp(),\n              \' \\n 数据库url: \',\n              host,\n              \':\',\n              port\n             ) content\n  from mysql_stat\n where status = 1 and 99 > %s\n  and %s', 'mysql_list', 'alarm_connect');
INSERT INTO `alarm_conf` VALUES (23, 4, 'Linux主机swap使用率告警', '>=', 10, '使用百分比', 'linux_stat', 'select tags,\n       host url,  \n       concat(tags,\n              \':Linux主机SWAP使用率告警\',\n              \'\\n 告警时间：\',\n              current_timestamp(),\n              \' \\n 主机IP: \',\n              host,\n              \'\\n SWAP使用率：\',\n              round(swap_used*100/(swap_used+swap_free),2),\n              \'%%\'\n             ) content\n  from linux_stat\n where (swap_used+swap_free)>0 and swap_used*100/(swap_used+swap_free) >= %s\n  and %s', 'linux_list', 'alarm_swap');
INSERT INTO `alarm_conf` VALUES (24, 3, 'Redis通断告警', '>=', 1, '连续中断次数', 'redis_stat', 'select tags,\r\n       concat(host, \':\', port) url,  \r\n       concat(tags,\r\n              \':Redis通断告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n Redis url: \',\r\n              host,\r\n              \':\',\r\n              port\r\n             ) content\r\n  from redis_stat\r\n where status = 1 and 99 > %s\r\n  and %s', 'redis_list', 'alarm_connect');
--INSERT INTO `alarm_conf` VALUES (25, 3, 'Redis内存使用率告警', '>=', 80, '使用百分比', NULL, 'select tags,\r\n       concat(host, \':\', port) url,  \r\n       concat(tags,\r\n              \':Redis内存使用率告警\',\r\n              \'\\n 告警时间：\',\r\n              current_timestamp(),\r\n              \' \\n Redis url: \',\r\n              host,\r\n              \':\',\r\n              port,\r\n              \' \\n 最大内存配置(MB)\',\r\n              max_memory,\r\n              \' \\n 使用内存大小(MB)\',\r\n              used_memory,\r\n              \' \\n 内存使用率\',\r\n              used_memory_pct,\r\n              \'%%\'\r\n             ) content\r\n  from redis\r\n where used_memory_pct >= %s\r\n  and %s', 'redis_list', 'alarm_mem');

INSERT INTO `django_celery_beat_intervalschedule` VALUES ('1', '1', 'minutes');

INSERT INTO `django_celery_beat_intervalschedule` VALUES ('2', '10', 'minutes');

INSERT INTO `django_celery_beat_intervalschedule` VALUES ('3', '30', 'minutes');

INSERT INTO `django_celery_beat_periodictask` VALUES ('3', 'maincheck', 'system.tasks.main_check', '[]', '{}', null, null, null, null, '1', now(), '0', now(), '', null, '1', null, '0', null, null, '{}', null);

