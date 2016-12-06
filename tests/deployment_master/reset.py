# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
from datetime import datetime
from datetime import timedelta
from warnings import filterwarnings

import MySQLdb

from common.util.vertica_db_operations import execute_vsql_command

filterwarnings('ignore', category=MySQLdb.Warning)

# generate query records used to insert into Query table
insert_command = """INSERT INTO Query VALUES """
tenant_mppdb_list = [1, 2, 3, 4, 5, 6]

current_time = datetime.now()
for i in range(99):
    year = current_time.year
    month = current_time.month
    # modify day
    day = random.randint(13, 20)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    start_time = datetime(year, month, day, hour, minute, second)
    diff = random.randint(0, 10)
    end_time = start_time + timedelta(seconds=diff)
    tenant_mppdb_id = random.choice(tenant_mppdb_list)
    # modify all the mppdb_id (modify this section)
    if tenant_mppdb_id == 1:
        user_id = 2
        mppdb_id = 'ffae3bc8-572a-4a10-aeae-048bd4e9f9f2'
    elif tenant_mppdb_id == 2:
        user_id = random.randint(1, 3)
        mppdb_id = '8b029e34-55c4-4b84-b336-8ac7fe60e6df'
    elif tenant_mppdb_id == 3:
        user_id = 4
        mppdb_id = 'ffae3bc8-572a-4a10-aeae-048bd4e9f9f2'
    elif tenant_mppdb_id == 4:
        user_id = 5
        mppdb_id = 'e6e53153-336f-4030-bd33-10f99bd159e5'
    elif tenant_mppdb_id == 5:
        user_id = 7
        mppdb_id = '8b029e34-55c4-4b84-b336-8ac7fe60e6df'
    elif tenant_mppdb_id == 6:
        user_id = 5
        mppdb_id = 'ffae3bc8-572a-4a10-aeae-048bd4e9f9f2'
    insert_command += """(%s, '%s', '%s', NULL, NULL, %s, %s, NULL, '%s', NULL), """ % (
        i + 1, start_time, end_time, user_id, tenant_mppdb_id, mppdb_id)
insert_command = insert_command[:-2]
insert_command += ';'

# Data for testing
# modify this section
tenant_list = ['43aad64fa7c244e69246b596b6c19128', '7d060ae439ad469a9729cfaedfe264d6']
tenant_mppdb_group_id_list = [1, 2, 3]
tenant_mppdb_list = [1, 2, 3, 4, 5, 6]
user_in_tmg1 = {'John': 'john123', 'Mary': 'mary123', 'Billy': 'billy123'}
# {ip address:password}
mppdb_in_tmg1 = {'192.168.1.220': ''}
user_in_tmg2 = {'Peter': 'peter123', 'Sally': 'sally123', 'Michael': 'michael123'}
mppdb_in_tmg2 = {'192.168.1.213': ''}
user_in_tmg3 = {'Henry': 'henry123'}
mppdb_in_tmg3 = {'192.168.1.210': ''}
user_list = user_in_tmg1.keys() + user_in_tmg2.keys() + user_in_tmg3.keys()
mppdb_list = mppdb_in_tmg1.keys() + mppdb_in_tmg2.keys() + mppdb_in_tmg3.keys()

# Part 1: Add or reset the testing data on database
# connection = MySQLdb.connect(user='vault', passwd='vault', host='192.168.1.138', db='vault')
connection = MySQLdb.connect(user='root', passwd='', host='127.0.0.1', db='vault')
cur = connection.cursor()

for tenant_mppdb_group_id in tenant_mppdb_group_id_list:
    cur.execute("""delete from TenantMPPDBGroup where tenant_mppdb_group_id = %s""", (tenant_mppdb_group_id,))
    cur.execute("""delete from MPPDB where tenant_mppdb_group_id = %s""", (tenant_mppdb_group_id,))
for tenant_mppdb_id in tenant_mppdb_list:
    cur.execute("""delete from TenantMPPDB where tenant_mppdb_id = %s""", (tenant_mppdb_id,))
for user_name in user_list:
    cur.execute("""delete from User where user_name = %s""", (user_name,))
for mppdb_ip in mppdb_list:
    cur.execute("""delete from MPPDB where mppdb_ip = %s""", (mppdb_ip,))
for tenant_mppdb_id in tenant_mppdb_list:
    cur.execute("""delete from Query where tenant_mppdb_id = %s""", (tenant_mppdb_id,))

cur.execute("""delete from TenantMPPDBGroup""")
cur.execute("""delete from MPPDB""")
cur.execute("""delete from JobQueue""")

connection.commit()

# modify the INSERT INTO MPPDB VALUES(mppdb_id of the tenant group, ip address, tenant_group_id, mppdb_password)
# modify this section
cur.execute(
    """INSERT INTO MPPDB VALUES ('ffae3bc8-572a-4a10-aeae-048bd4e9f9f2','192.168.1.220',1,''),('8b029e34-55c4-4b84-b336-8ac7fe60e6df ','192.168.1.213',2,''),('e6e53153-336f-4030-bd33-10f99bd159e5','192.168.1.210',3,'')
          ,('26211c60-c617-4132-9df9-cd40b307caca','192.168.1.205','3',''),('530807a9-d428-4d69-83b2-9fad30189d7b','192.168.1.203','1',''),('aff1849f-6cc8-491c-aca5-8e6ef97cf075','192.168.1.226','2',''),('dd669e86-2593-4d7b-b515-52a043824b3a','192.168.1.218','4','');""")
cur.execute(
    """INSERT INTO TenantMPPDB VALUES (1,1,1,'7','43aad64fa7c244e69246b596b6c19128','Computing'),(2,2,1,'8','43aad64fa7c244e69246b596b6c19128','Engineering'),(3,1,1,'7','43aad64fa7c244e69246b596b6c19128','Statistics'),(4,3,2,'7','7d060ae439ad469a9729cfaedfe264d6','Chemistry'),(5,2,1,'8','7d060ae439ad469a9729cfaedfe264d6','Math'),(6,1,1,'7', '7d060ae439ad469a9729cfaedfe264d6','Physics');""")
cur.execute(
    """INSERT INTO TenantMPPDBGroup VALUES (1,3,'2016-04-29 13:11:21',1,'7'),(2,2,'2016-04-29 14:12:31',1,'8'),(3,1,'2016-04-29 14:12:31',2,'7');""")
cur.execute(
    """INSERT INTO User VALUES (1,'Peter','admin','peter123',2),(2,'John','admin','john123',1),(3,'Sally','admin','sally123',2),(4,'Mary','admin','mary123',3),(5,'Billy','admin','billy123',6),(6,'Henry','admin','henry123',4),(7,'Michael','admin','michael123',5);""")
cur.execute(""" %s """ % insert_command)

connection.commit()
cur.close()

# Part 2: Prepare MPPDBs based on the testing data

# dbadmin: clean all users' data on all MPPDBs
combined_mppdb = mppdb_in_tmg1.copy()
combined_mppdb.update(mppdb_in_tmg2)
combined_mppdb.update(mppdb_in_tmg3)

command_clean_user = ''
for user in user_list:
    command_clean_user += "DROP USER if exists %s CASCADE;" % user

for host_ip, dbadmin_password in combined_mppdb.items():
    connection = execute_vsql_command(host_ip, 'dbadmin', dbadmin_password, command_clean_user)[1]
    connection.close()

# dbadmin: create user and grant create privilega
command_create_user_in_tmg1 = ''
for user, password in user_in_tmg1.items():
    command_create_user_in_tmg1 += "CREATE USER %s IDENTIFIED BY '%s'; GRANT CREATE ON DATABASE db_srvr TO %s;" % (
        user, password, user)

for host_ip, dbadmin_password in mppdb_in_tmg1.items():
    cur, connection = execute_vsql_command(host_ip, 'dbadmin', dbadmin_password, command_create_user_in_tmg1)
    connection.close()

command_create_user_in_tmg2 = ''
for user, password in user_in_tmg2.items():
    command_create_user_in_tmg2 += "CREATE USER %s IDENTIFIED BY '%s'; GRANT CREATE ON DATABASE db_srvr TO %s;" % (
        user, password, user)

for host_ip, dbadmin_password in mppdb_in_tmg2.items():
    cur, connection = execute_vsql_command(host_ip, 'dbadmin', dbadmin_password, command_create_user_in_tmg2)
    connection.close()

command_create_user_in_tmg3 = ''
for user, password in user_in_tmg3.items():
    command_create_user_in_tmg3 += "CREATE USER %s IDENTIFIED BY '%s'; GRANT CREATE ON DATABASE db_srvr TO %s;" % (
        user, password, user)

for host_ip, dbadmin_password in mppdb_in_tmg3.items():
    cur, connection = execute_vsql_command(host_ip, 'dbadmin', dbadmin_password, command_create_user_in_tmg3)
    connection.close()

# users: create schema, create table, and load table data
# modify this section
# modify the ip address of the cluster which is used to transfer data to other user
for user, password in user_in_tmg1.items():
    command_create_user_data = "CREATE SCHEMA %s; CREATE TABLE %s (Date timestamp NOT NULL, Name varchar(32) NOT NULL, PTID int DEFAULT NULL::int, LBMP float DEFAULT NULL::float, Marginal_cost_losses float DEFAULT NULL::float, Marginal_cost_congestion float);" % (
        user + '_schema', user + '_schema.' + user + '_table')
    for host_ip_in_tmg1 in mppdb_in_tmg1.keys():
        cur, connection = execute_vsql_command(host_ip_in_tmg1, user, password, command_create_user_data)
        connection.close()
        command_export_user_data = "CONNECT TO VERTICA db_srvr USER %s PASSWORD '%s' ON '%s',5433;" % (
            user, password, host_ip_in_tmg1)
        command_export_user_data += "EXPORT TO VERTICA db_srvr.%s FROM %s;" % (
            user + '_schema.' + user + '_table', 'sample.sample')
        command_export_user_data += "DISCONNECT db_srvr;"
        cur, connection = execute_vsql_command('192.168.1.219', 'dbadmin', '', command_export_user_data)
        connection.close()

for user, password in user_in_tmg2.items():
    command_create_user_data = "CREATE SCHEMA %s; CREATE TABLE %s (Date timestamp NOT NULL, Name varchar(32) NOT NULL, PTID int DEFAULT NULL::int, LBMP float DEFAULT NULL::float, Marginal_cost_losses float DEFAULT NULL::float, Marginal_cost_congestion float);" % (
        user + '_schema', user + '_schema.' + user + '_table')
    for host_ip_in_tmg2 in mppdb_in_tmg2.keys():
        cur, connection = execute_vsql_command(host_ip_in_tmg2, user, password, command_create_user_data)
        connection.close()
        command_export_user_data = "CONNECT TO VERTICA db_srvr USER %s PASSWORD '%s' ON '%s',5433;" % (
            user, password, host_ip_in_tmg2)
        command_export_user_data += "EXPORT TO VERTICA db_srvr.%s FROM %s;" % (
            user + '_schema.' + user + '_table', 'sample.sample')
        command_export_user_data += "DISCONNECT db_srvr;"
        cur, connection = execute_vsql_command('192.168.1.219', 'dbadmin', '', command_export_user_data)
        connection.close()

for user, password in user_in_tmg3.items():
    command_create_user_data = "CREATE SCHEMA %s; CREATE TABLE %s (Date timestamp NOT NULL, Name varchar(32) NOT NULL, PTID int DEFAULT NULL::int, LBMP float DEFAULT NULL::float, Marginal_cost_losses float DEFAULT NULL::float, Marginal_cost_congestion float);" % (
        user + '_schema', user + '_schema.' + user + '_table')
    for host_ip_in_tmg3 in mppdb_in_tmg3.keys():
        cur, connection = execute_vsql_command(host_ip_in_tmg3, user, password, command_create_user_data)
        connection.close()
        command_export_user_data = "CONNECT TO VERTICA db_srvr USER %s PASSWORD '%s' ON '%s',5433;" % (
            user, password, host_ip_in_tmg3)
        command_export_user_data += "EXPORT TO VERTICA db_srvr.%s FROM %s;" % (
            user + '_schema.' + user + '_table', 'sample.sample')
        command_export_user_data += "DISCONNECT db_srvr;"
        cur, connection = execute_vsql_command('192.168.1.219', 'dbadmin', '', command_export_user_data)
        connection.close()
