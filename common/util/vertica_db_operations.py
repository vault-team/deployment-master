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

import logging
import subprocess

import paramiko
import vertica_python

from common import constant
from common.constant import *
from common.models import MPPDB

_DEFAULT_VERTICA_ADMIN = 'dbadmin'
_DEFAULT_VERTICA_DATABASE = 'db_srvr'

logger = logging.getLogger(__name__)

def get_ssh_client(host_ip, key_file):
    """
    Get SSH client.
    By default, the database guest is only accessible through the user ubuntu by key pair.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host_ip, username='ubuntu', key_filename=key_file)
    return ssh_client


def execute_shell_command(host_ip, key_file, command):
    """Execute a shell command."""
    ssh_client = get_ssh_client(host_ip, key_file)
    stdin, stdout, stderr = ssh_client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    return stdout, ssh_client


def get_dbadmin_password(host_ip):
    """
    Retrieve the user dbadmin's password on Vertica database server.
    This password is generated automatically during Vertica database installation process.
    """
    command = 'cat /etc/vertica.cnf'
    stdout, ssh_client = execute_shell_command(host_ip, KEY_FILE_PATH_LOCAL, command)
    dbadmin_password = str()
    for line in stdout:
        if 'dbadmin_password' in line:
            dbadmin_password = str(line.strip('\n')[19:])
    ssh_client.close()
    return dbadmin_password

def test_vertica_connection(host_ip, user=_DEFAULT_VERTICA_ADMIN, password=""):
    try:
        conn = get_database_connection(host_ip=host_ip, user_name=user, user_password=password)
        conn.close()
        return True
    except:
        return False


def get_database_connection(host_ip=None, user_name=None, user_password=None, mppdb=None):
    """Return a connection to Vertica database server."""
    logger.debug("Create vertica connection, IP:%s, user_name:%s, password:%s" % (host_ip,user_name,user_password))

    if host_ip is None:
        host_ip = mppdb.mppdb_ip

    if user_name is None and user_password is None:
        user_name = _DEFAULT_VERTICA_ADMIN
        user_password = mppdb.mppdb_password

    conn_info = {'host': host_ip, 'port': 5433, 'user': user_name, 'password': user_password,
                 'database': _DEFAULT_VERTICA_DATABASE,
                 'read_timeout': 600}
    connection = vertica_python.connect(**conn_info)
    return connection


def execute_vsql_command(host_ip=None, user_name=None, user_password=None, command=None, connection=None):
    """Execute a vsql command on Vertica database server."""
    if connection is None:
        connection = get_database_connection(host_ip, user_name, user_password)
    cur = connection.cursor()
    cur.execute(command)
    return cur, connection


def create_db_user(host_ip, dbadmin_password, user_list=None):
    """Create users on a Vertica database server."""
    logger.info('Start to create db user on %s' % host_ip)
    command = ''

    for user in user_list:
        user_name = user.get_sql_username()
        command += "CREATE USER %s IDENTIFIED BY '%s'; GRANT CREATE ON DATABASE db_srvr TO %s;" % (
            user_name, user.password, user_name)

        logger.debug(command)
    cur, connection = execute_vsql_command(host_ip, _DEFAULT_VERTICA_ADMIN, dbadmin_password, command)

    connection.close()
    return


def export_objects(host_ip, user_name, user_password, source_table_sql_path):
    """Export objects (tables, schemas,etc) of a user into a sql script."""
    logger.info("Start to export objects of %s on %s " % (user_name, host_ip))
    command = "SELECT EXPORT_OBJECTS('','',false);"
    cur, connection = execute_vsql_command(host_ip, user_name, user_password, command)
    with open(source_table_sql_path, 'a') as ff:
        for row in cur.iterate():
            for element in row:
                ff.write(str(element))
    connection.close()
    return


def transfer_file_between_hosts(target_host_ip, source_table_sql_path, source_filename):
    """Transfer sql script to the target Vertica database server."""
    logger.info("Start to transfer file to %s" % target_host_ip)
    subprocess.check_call(['scp', '-i', KEY_FILE_PATH_LOCAL, source_table_sql_path,
                           'ubuntu@%s:%s' % (target_host_ip, TARGET_TABLE_SQL_PATH + source_filename)])
    return


def create_table_from_sql_file(target_host_ip, tenant_mppdb, dest_mppdb, user_name, user_password, filename):
    try:
        """Create tables and schemas of a user on the target Vertica database server."""
        logger.info("Start to create table on %s" % target_host_ip)
        command = "sudo su - dbadmin -c '/opt/vertica/bin/vsql -f %s -U %s -w %s'" % (
            TARGET_TABLE_SQL_PATH + filename, user_name, user_password)
        logger.debug(command)

        ssh_client = execute_shell_command(target_host_ip, KEY_FILE_PATH_LOCAL, command)[1]
        ssh_client.close()

        schemas = get_schemas_by_tenant_mppdb_id(tenant_mppdb.tenant_mppdb_id, dest_mppdb)
        for user in tenant_mppdb.user_list:
            grant_schemas_to_user(schemas=schemas, username=user.get_sql_username(), mppdb=dest_mppdb)


        command = "rm %s" % TARGET_TABLE_SQL_PATH + filename
        ssh_client = execute_shell_command(target_host_ip, KEY_FILE_PATH_LOCAL, command)[1]
        ssh_client.close()
        return
    except Exception as inst:
        logger.exception("failt to create_table_from_sql_file: '")
        raise inst


def get_tables_by_tenant_mppdb(host_ip, dbadmin_password, user_list):
    """Return tables belonging to a TenantMPPDB."""
    try:
        logger.info('Get tables on %s' % host_ip)
        table_list = []
        for user in user_list:
            user_name = user.get_sql_username()
            command = "select table_schema, table_name from v_catalog.tables where owner_name = '%s';" % user_name
            cur, connection = execute_vsql_command(host_ip, _DEFAULT_VERTICA_ADMIN, dbadmin_password, command)
            for row in cur.iterate():
                table_list.append(row[0] + '.' + row[1])
        connection.close()
        return table_list
    except Exception as inst:
        logging.exception("Can't get tables")
        raise inst


def export_table_data(source_host_ip, source_dbadmin_password, target_host_ip, target_dbadmin_password, table_list):
    try:
        """Export table data to the target Vertica database server."""
        logger.info('Start to export table from %s to %s' % (source_host_ip, target_host_ip))
        command = "CONNECT TO VERTICA db_srvr USER dbadmin PASSWORD '%s' ON '%s',5433;" % (
            target_dbadmin_password, target_host_ip)
        for table in table_list:
            command += "EXPORT TO VERTICA db_srvr.%s FROM %s;" % (table, table)
        command += "DISCONNECT db_srvr;"
        connection = execute_vsql_command(source_host_ip, _DEFAULT_VERTICA_ADMIN, source_dbadmin_password, command)[1]
        connection.close()
        return
    except Exception as inst:
        logger.exception("Fail to export data object of a user")


def delete_user(host_ip, dbadmin_password, user_list):
    """Delete a user on a Vertica database server."""
    command = ''
    for user in user_list:
        user_name = user.get_sql_username()
        logger.info('Start to drop user %s from %s' % (user_name, host_ip))
        command += "drop user %s CASCADE;" % user_name
    connection = execute_vsql_command(host_ip, _DEFAULT_VERTICA_ADMIN, dbadmin_password, command)[1]
    connection.close()
    return


def find_users(host_ip, dbadmin_password):
    table_list = []
    command = "select user_name from users;"
    cur, connection = execute_vsql_command(host_ip, _DEFAULT_VERTICA_ADMIN, dbadmin_password, command)

    for row in cur.iterate():
        table_list.append(row[0])

    connection.close()
    return table_list


def move_tenant_mppdb_btw_mppdb(migration_job, source_mppdb, dest_mppdb, tenant_mppdb):
    try:
        create_db_user(dest_mppdb.mppdb_ip, dest_mppdb.mppdb_password, tenant_mppdb.user_list)

        source_host_ip = source_mppdb.mppdb_ip
        source_dbadmin_password = source_mppdb.mppdb_password

        # User's info, schema, table(without data) found here and send to dst database
        for user in tenant_mppdb.user_list:
            user_name = user.get_sql_username()
            source_filename = 'jobQueueId' + str(migration_job.id) + '_' + user_name + '.sql'
            source_table_sql_path = constant.SOURCE_TABLE_SQL_PATH + source_filename
            export_objects(source_host_ip, user_name, user.password, source_table_sql_path)

            # transfer files from source mppdb to target mppdb
            transfer_file_between_hosts(dest_mppdb.mppdb_ip, source_table_sql_path, source_filename)
            # on target mppdb, ask user to execute sql file
            create_table_from_sql_file(dest_mppdb.mppdb_ip, tenant_mppdb, dest_mppdb, user_name, user.password, source_filename)

            subprocess.check_call(['rm', source_table_sql_path])

        # on source mppdb, export table data to target mppdb
        table_list = get_tables_by_tenant_mppdb(source_host_ip, source_dbadmin_password, tenant_mppdb.user_list)
        export_table_data(source_host_ip, source_dbadmin_password, dest_mppdb.mppdb_ip, dest_mppdb.mppdb_password,
                          table_list)

        return
    except Exception as inst:
        logging.exception("Fail to move tenant data")
        raise inst


def create_vertica_schema(host_ip, username, password, schema_name):
    """
    Create schema on destination database
    Tested
    :param host_ip:
    :param username:
    :param password:
    :param schema_name:
    """
    cur, conn = execute_vsql_command(host_ip=host_ip, user_name=username,
                         user_password=password, command="CREATE SCHEMA %s" % schema_name)
    conn.close()


def get_schemas_by_tenant_mppdb_id(tenant_mppdb_id, mppdb):
    if not isinstance(mppdb, MPPDB):
        raise TypeError()
    if not isinstance(tenant_mppdb_id, int):
        raise TypeError()

    cur, conn = execute_vsql_command(host_ip=mppdb.mppdb_ip, user_name=_DEFAULT_VERTICA_ADMIN,
                                     user_password=mppdb.mppdb_password, command="select SCHEMA_NAME from v_catalog.schemata WHERE SCHEMA_NAME like 'tm%d_%%'" % tenant_mppdb_id)

    ret = []
    for row in cur.iterate():
        ret.append(row[0])

    conn.close()
    return ret


def grant_schemas_to_user(schemas = [], username = None, mppdb = None):
    conn = get_database_connection(mppdb=mppdb)
    for schema in schemas:
        cur, conn = execute_vsql_command(connection=conn, command="GRANT ALL ON SCHEMA %s TO %s" % (schema, username))
        cur.close()
    conn.close()







