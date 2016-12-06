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


from sqlalchemy import Column, Integer, TIMESTAMP, String
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import current_timestamp

import common.string_constant
from common import constant
from common.util import rewrite

Base = declarative_base()


class MigrationJob(Base):
    """
    Object raltional mapper mapping to database table JobQueue.
        id: identifier of this job
        action: description of this job
        status: job status (Pending, Processing)
        last_touch_timestamp: the last timestamp that try to execute job
        connection_id: identifier of the connection
        query_id: identifier of the query
        worker_id: uuid of the worker
        type: categorizes the query is sent from queryrouter or deploymentmaster
        tenant_mppdb_id: identifier of tenant mppdb
        source_mppdb_id: identifier of source mppdb
        dest_mppdb_id: identifier of the destination mppdb
        changes_id: identifier for checking all MPPDB of a particular tenant mppdb is already migrated
    """
    __tablename__ = 'JobQueue'

    id = Column(Integer, primary_key=True)
    action = Column(String(50))
    status = Column(String(15))
    last_touch_timestamp = Column(TIMESTAMP(), default=current_timestamp(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    connection_id = Column(String(50))
    query_id = Column(String(50))
    worker_id = Column(String(50))
    type = Column(String(50))
    tenant_mppdb_id = Column(String(50))
    source_mppdb_id = Column(String(50))
    dest_mppdb_id = Column(String(50))
    changes_id = Column(String(50))

    _mppdb_copy = 'mppdb_copy'
    _tenant_mppdb_data_movement = 'tenant_mppdb_data_movement'

    def __init__(self, id=None, action=None, status=None, connection_id=None, query_id=None, worker_id=None, type=None,
                 tenant_mppdb_id=None, source_mppdb_id=None, dest_mppdb_id=None, changes_id=None):

        self.id = id
        self.action = action
        self.status = status
        self.connection_id = connection_id
        self.query_id = query_id
        self.worker_id = worker_id
        self.type = type
        self.tenant_mppdb_id = tenant_mppdb_id
        self.source_mppdb_id = source_mppdb_id
        self.dest_mppdb_id = dest_mppdb_id
        self.changes_id = changes_id

    def setDestMppdb(self, dest_mppdb_id):
        self.dest_mppdb_id = dest_mppdb_id

    def run(self, session):

        migration_job = None

        if self.action == self._mppdb_copy:
            migration_job = MigrationJob(id=self.id, action=self._mppdb_copy, status=common.string_constant.TenantUpdateJobStatus_PENDING,
                                         source_mppdb_id=self.source_mppdb_id,
                                         dest_mppdb_id=self.dest_mppdb_id,
                                         tenant_mppdb_id=self.tenant_mppdb_id, type='deploymentmaster',
                                         changes_id=str(self.changes_id))
        elif self.action == self._tenant_mppdb_data_movement:
            migration_job = MigrationJob(id=self.id, action=self._tenant_mppdb_data_movement, status=common.string_constant.TenantUpdateJobStatus_PENDING,
                                         source_mppdb_id=self.source_mppdb_id, dest_mppdb_id=self.dest_mppdb_id,
                                         tenant_mppdb_id=self.tenant_mppdb_id, type='deploymentmaster',
                                         changes_id=str(self.changes_id))

        session.add(migration_job)
        session.commit()

    def __eq__(self, other):
        if isinstance(other,
                      MigrationJob) and self.source_mppdb_id == other.source_mppdb_id and self.dest_mppdb_id == other.dest_mppdb_id and self.action == other.action:
            return True
        else:
            return False


class MPPDB(Base):
    """
    Object raltional mapper mapping to database table MPPDB.
        mppdb_id: identifier of this MPPDB
        mppdb_ip: ip of a node of this MPPDB
        tenant_mppdb_group_id: identifier of TenantMPPDBGroup this MPPDB serves
        mppdb_password: password of the user dbadmin on this MPPDB
    """
    __tablename__ = 'MPPDB'

    mppdb_id = Column(String(50), primary_key=True)
    mppdb_ip = Column(String(15))
    tenant_mppdb_group_id = Column(Integer)
    mppdb_password = Column(String(200))

    def __init__(self, mppdb_id, mppdb_ip, tenant_mppdb_group_id, mppdb_password):
        self.mppdb_id = mppdb_id
        self.mppdb_ip = mppdb_ip
        self.tenant_mppdb_group_id = tenant_mppdb_group_id
        self.mppdb_password = mppdb_password

    @property
    def serialize(self):
        return {
            'mppdb_id': self.mppdb_id,
            'mppdb_ip': self.mppdb_ip,
            'tenant_mppdb_group_id': self.tenant_mppdb_group_id,
            'mppdb_password': self.mppdb_password,
        }

    def __repr__(self):
        return "MPPDB('%s', '%s','%s', '%s')" % (
            self.mppdb_id, self.mppdb_ip, self.tenant_mppdb_group_id, self.mppdb_password)


class Query(Base):
    """
    Object raltional mapper mapping to database table Query.
        id: identifier of this query
        start_time: start time of the query execution
        end_time: end time of the query execution
        command_type: type of this query (execute, executeUpdate, executeQuery)
        query_body: command content of this query
        user_id: identifier of User that sends this query
        tenant_mppdb_id: identifier of TenantMPPDB this query is sent to
        query_status: status of this query(Success, Failure)
        mppdb_id: identifier of MPPDB on which this query is executed
    """
    __tablename__ = 'Query'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    command_type = Column(String(50))
    query_body = Column(String(255))
    user_id = Column(Integer)
    tenant_mppdb_id = Column(Integer)
    query_status = Column(String(50))
    mppdb_id = Column(String(50))

    def __repr__(self):
        return "Query('%s','%s', '%s', '%s','%s', '%s', '%s', '%s')" % (
            self.id, self.start_time, self.end_time, self.command_type, self.query_body, self.tenant_mppdb_id,
            self.query_status, self.mppdb_id)


class TenantMPPDB(Base):
    """
    Object relational mapper mapping to database table TenantMPPDB along with three additional user-defined attributes.
        tenant_mppdb_id: identifier of this TenantMPPDB
        tenant_mppdb_group_id: identifier of TenantMPPDBGroup this TenantMPPDB belongs to
        request_node_quantity: number of nodes requested by TenantMPPDB
        flavor: flavor
        tenant_id: identifier of Tenant who has requested to create this TenantMPPDB
        tenant_mppdb_name: name
        query_status_list: query status of this TenantMPPDB
        active_ratio: active ratio of this TenantMPPDB
        user_list: users on this TenantMPPDB
    """
    __tablename__ = 'TenantMPPDB'

    tenant_mppdb_id = Column(Integer, primary_key=True)
    tenant_mppdb_group_id = Column(Integer)
    request_node_quantity = Column(Integer)
    flavor = Column(String(50))
    tenant_id = Column(String(50))
    tenant_mppdb_name = Column(String(50))

    query_status_list = []
    active_ratio = float()
    user_list = []

    def __init__(self, tenant_mppdb_id=None, tenant_mppdb_group_id=None, request_node_quantity=None, flavor=None,
                 tenant_id=None, tenant_mppdb_name=None, query_status_list=None, active_ratio=None, user_list=None):
        self.tenant_mppdb_id = tenant_mppdb_id
        self.tenant_mppdb_group_id = tenant_mppdb_group_id
        self.request_node_quantity = request_node_quantity
        self.flavor = flavor
        self.tenant_id = tenant_id
        self.tenant_mppdb_name = tenant_mppdb_name
        self.query_status_list = query_status_list
        self.active_ratio = active_ratio
        self.user_list = user_list

    def __repr__(self):
        return "<TenantMPPDB('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.tenant_mppdb_id, self.tenant_mppdb_group_id, self.request_node_quantity, self.flavor, self.tenant_id,
            self.tenant_mppdb_name, self.query_status_list, self.active_ratio, self.user_list)

    @property
    def serialize(self):
        return {
            'tenant_mppdb_id': self.tenant_mppdb_id,
            'tenant_mppdb_name': self.tenant_mppdb_name,
            'request_node_quantity': self.request_node_quantity,
            'flavor': self.flavor,
            'tenant_id': self.tenant_id,
            'tenant_mppdb_group_id': self.tenant_mppdb_group_id,
        }


class TenantMPPDBGroup(Base):
    """
    Object raltional mapper mapping to database table TenantMPPDBGroup along with two additional user-defined attributes.
        tenant_mppdb_group_id: identifier of this group
        group_size: number of TenantMPPDBs in this group
        formation_time: formation time
        node_quantity: number of nodes in cluster
        flavor: flavor of TenantMPPDBs in this group
        tenant_mppdb_members_list: TenantMPPDB objects that belong to this group
        mppdb_list: MPPDBs that hold this group
    """
    __tablename__ = 'TenantMPPDBGroup'

    tenant_mppdb_group_id = Column(Integer, primary_key=True)
    group_size = Column(Integer)
    formation_time = Column(DateTime)
    node_quantity = Column(Integer)
    flavor = Column(String(50))

    tenant_mppdb_members_list = []
    mppdb_list = []

    def __init__(self, tenant_mppdb_group_id=None, group_size=None, formation_time=None, node_quantity=None,
                 flavor=None, tenant_mppdb_members_list=None, mppdb_list=None):
        self.tenant_mppdb_group_id = tenant_mppdb_group_id
        self.group_size = group_size
        self.formation_time = formation_time
        self.node_quantity = node_quantity
        self.flavor = flavor
        self.tenant_mppdb_members_list = tenant_mppdb_members_list
        self.mppdb_list = mppdb_list

    def __repr__(self):
        return "TenantMPPDBGroup('%s','%s', '%s', '%s', '%s', '%s', '%s')" % (
            self.tenant_mppdb_group_id, self.group_size, self.formation_time, self.node_quantity, self.flavor,
            self.tenant_mppdb_members_list, self.mppdb_list)

    def __eq__(self, other):
        if self.tenant_mppdb_group_id == other.tenant_mppdb_group_id:
            return True
        else:
            return False

    @property
    def serialize(self):
        return {
            'tenant_mppdb_group_id': self.tenant_mppdb_group_id,
            'group_size': self.group_size,
            'node_quantity': self.node_quantity,
            'flavor': self.flavor,
            'formation_time': self.formation_time,
            'tenant_mppdb_members_list': ['#'+str(tenant_mppdb_member.tenant_mppdb_id) for tenant_mppdb_member in
                                          self.tenant_mppdb_members_list],
            'mppdb_list': [mppdb.mppdb_ip for mppdb in self.mppdb_list],
        }


class User(Base):
    """
    Object raltional mapper mapping to database table User.
        user_id: identifier of this user
        user_name: name of this user
        user_role: role of this user
        password: password of this user
        tenant_mppdb_id: identifier of TenantMPPDB this user belongs to
    """
    __tablename__ = 'User'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(50))
    user_role = Column(String(50))
    password = Column(String(50))
    tenant_mppdb_id = Column(Integer)

    def __init__(self, user_id=None, user_name=None, user_role=None, password=None, tenant_mppdb_id=None):
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role
        self.password = password
        self.tenant_mppdb_id = tenant_mppdb_id

    def __repr__(self):
        return "User('%s','%s', '%s', '%s','%s')" % (
            self.user_id, self.user_name, self.user_role, self.password, self.tenant_mppdb_id)

    def get_sql_username(self):
        return rewrite.rewrite_user_name(self.tenant_mppdb_id, self.user_name)

    @property
    def serialize(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'tenant_mppdb_id': self.tenant_mppdb_id,
        }


class Performance(Base):
    """
       Object raltional mapper mapping to database table User.
           time: timestamp of the corresponding performance at the x axis in the graph
           tenant_mppdb_group_id: identifier of the tenant mppdb group
           value: performance of the tenant mppdb group at the y axis in the graph
    """

    __tablename__ = 'TempPerformance'

    time = Column(TIMESTAMP, primary_key=True)
    tenant_mppdb_group_id = Column(Integer, primary_key=True)
    value = Column(Float)

    def __init__(self, time=None, tenant_mppdb_group_id=None, value=None):
        self.time = time
        self.tenant_mppdb_group_id = tenant_mppdb_group_id
        self.value = value


    def __repr__(self):
        return "Performance('%s','%s', '%s')" % (
            self.time, self.tenant_mppdb_group_id, self.value)


    @property
    def serialize(self):
        return {
            'time': self.time,
            'tenant_mppdb_group_id': self.tenant_mppdb_group_id,
            'value': self.value
        }


class SlaGuarantee(Base):
    """
       Object raltional mapper mapping to database table User.
           time: timestamp of the corresponding rt-ttp at the x axis in the graph
           tenant_mppdb_group_id: identifier of the tenant mppdb group
           value: rt-ttp of the tenant mppdb group at the y axis in the graph
    """

    __tablename__ = 'TempSlaGuarantee'

    time = Column(TIMESTAMP, primary_key=True)
    tenant_mppdb_group_id = Column(Integer, primary_key=True)
    value = Column(Float)

    def __init__(self, time=None, tenant_mppdb_group_id=None, value=None):
        self.time = time
        self.tenant_mppdb_group_id = tenant_mppdb_group_id
        self.value = value


    def __repr__(self):
        return "SlaGuarantee('%s','%s', '%s')" % (
            self.time, self.tenant_mppdb_group_id, self.value)


    @property
    def serialize(self):
        return {
            'time': self.time,
            'tenant_mppdb_group_id': self.tenant_mppdb_group_id,
            'value': self.value
        }


class TenantMPPDBActivity(Base):
    """
       Object raltional mapper mapping to database table User.
           time: timestamp of the corresponding activity at the x axis in the graph
           tenant_mppdb_id: identifier of the tenant mppdb
           value: activity of the tenant mppdb at the y axis in the graph
    """

    __tablename__ = 'TempTenantMPPDBActivity'

    time = Column(TIMESTAMP, primary_key=True)
    tenant_mppdb_id = Column(Integer, primary_key=True)
    value = Column(Float)

    def __init__(self, time=None, tenant_mppdb_id=None, value=None):
        self.time = time
        self.tenant_mppdb_id = tenant_mppdb_id
        self.value = value


    def __repr__(self):
        return "TenantMPPDBActivity('%s','%s', '%s')" % (
            self.time, self.tenant_mppdb_id, self.value)


    @property
    def serialize(self):
        return {
            'time': self.time,
            'tenant_mppdb_id': self.tenant_mppdb_id,
            'value': self.value
        }


class ConsolidationLog(Base):
    """
       Object raltional mapper mapping to database table ConsolidationLog.
            last_timestamp: the timestamp of the last consolidation
    """
    __tablename__ = 'ConsolidationLog'

    last_timestamp = Column(TIMESTAMP, primary_key=True)

    def __init__(self, last_timestamp):
        self.last_timestamp = last_timestamp

    def __repr__(self):
        return "ConsolidationLog('%s')" % (
            self.last_timestamp)


    @property
    def serialize(self):
        return {
            'last_timestamp': self.last_timestamp,
        }


class Flavor:
    """
       disk: the volume of the disk
       ephemeral: the volume of the ephemeral disk
       ram: the volume of the ram
       swap: the volume of swap disk
       vcpus: the number of virtual CPU
    """
    def __init__(self, disk, ephemeral, ram, swap, vcpus):
        self.disk = disk
        self.ephemeral = ephemeral
        self.ram = ram
        self.swap = swap
        self.vcpus = vcpus

    @property
    def serialize(self):
        return {
            'disk': self.disk,
            'ephemeral': self.ephemeral,
            'ram': self.ram,
            'swap': self.swap,
            'vcpus': self.vcpus
        }