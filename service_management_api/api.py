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

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from sqlalchemy import desc

import re
from datetime import datetime
from datetime import timedelta

import common
from common import constant
from common.constant import REST_HOST, REST_PORT
from common.models import Performance, Flavor
from common import log
from common.models import Performance, SlaGuarantee
from common.trove_cluster_creation_manager import TroveClusterCreationManager, PostMPPDBCreateAction
from common.util import common_util
from common.util import rewrite
from common.util.vertica_db_operations import create_db_user, delete_user, create_vertica_schema, \
    get_schemas_by_tenant_mppdb_id, grant_schemas_to_user
from deployment_master.action.mppdb_deletion import MPPDBDeletion
from deployment_master.action.tenant_mppdb_data_deletion import TenantMPPDBDataDeletion
from deployment_master.tenant_activity_analyzer import *
from service_management_api.utils import OpenstackUtil

LOG = log.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

DEFAULT_TENANT_SCHEMA_NAME = "default"

_ERROR_MESSAGE = "error_message"
_STATUS = "status"
_OK = "ok"
_ERROR = "error"

class QueryRouterURIAPI(Resource):
    def get(self):
        try:
            return constant.QUERY_ROUTER_URI
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)

class ReplicationFactorAPI(Resource):
    def get(self):
        try:
            return constant.REPLICATON_FACTOR
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)

class ServiceLevelAgreementAPI(Resource):
     def get(self):
        try:
            return constant.SERVICE_LEVEL_AGREEMENT
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)

class ExceptionResponse(Exception):
    status_code = 500

    def __init__(self, error, status_code=None, payload=None):
        Exception.__init__(self)
        if isinstance(error, Exception):
            self.message = error.message
        else:
            self.message = str(error)
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv[_ERROR_MESSAGE] = self.message
        rv[_STATUS] = _ERROR
        return rv

class FlavorAPI(Resource):
    def get(self, flavor_name):
        session = SQLalchemyUtil.get_session()

        try:
            flavor = OpenstackUtil.get_nova_client().flavors.find(name=flavor_name)
            disk = flavor.__getattribute__('disk')
            ephemeral = flavor.__getattribute__('ephemeral')
            ram = flavor.__getattribute__('ram')
            swap = flavor.__getattribute__('swap')
            vcpus = flavor.__getattribute__('vcpus')
            flavor_obj = Flavor(disk=disk, ephemeral=ephemeral, ram=ram, swap=swap, vcpus=vcpus)

            ret = jsonify(flavor=flavor_obj.serialize)
            return ret
        except:
            LOG.exception("Cannot find flaovr")





class UsersAPI(Resource):

    # Get the users list with the same tenant_id
    def get(self, tenant_id):
        session = SQLalchemyUtil.get_session()
        try:
            users = []
            tenant_mppdbs = session.query(TenantMPPDB).filter_by(tenant_id=tenant_id).all()
            ret = None
            if tenant_mppdbs <> None:
                for tenant_mppdb in tenant_mppdbs:
                    users_response = session.query(User).filter_by(tenant_mppdb_id=tenant_mppdb.tenant_mppdb_id).all()
                    for user in users_response:
                        user.user_name = re.sub(r'tm' + str(tenant_mppdb.tenant_mppdb_id) + '_', '', user.user_name)
                        users.append(user)
                ret = jsonify(users=[i.serialize for i in users])
            else:
                ret = jsonify(users=[])

            return ret

        except Exception as e:
            LOG.exception("Fail to get user")
            raise ExceptionResponse(e)
        finally:
            session.close()


    # Create the user in the specified MPPDB
    def post(self, tenant_id):
        session = None
        try:
            session = SQLalchemyUtil.get_session()
            parser = reqparse.RequestParser()
            parser.add_argument('tenant_mppdb_id', type=int, required=True)
            parser.add_argument('user_name', type=str, required=True)
            parser.add_argument('password', type=str, required=True)
            args = parser.parse_args()

            tenant_mppdb_id = args['tenant_mppdb_id']
            user_name = args['user_name']
            password = args['password']

            new_user_in_backend_db = User(user_name=user_name, user_role='Null', password=password, tenant_mppdb_id=tenant_mppdb_id)

            session.add(new_user_in_backend_db)

            #new_user_record = session.query(User).filter_by(user_name=args['user_name']).filter_by(tenant_mppdb_id=tenant_mppdb_id).one()
            tenant_mppdb_record = session.query(TenantMPPDB).filter_by(tenant_mppdb_id=tenant_mppdb_id).one()
            mppdb_records = session.query(MPPDB).filter_by(tenant_mppdb_group_id=tenant_mppdb_record.tenant_mppdb_group_id).all()

            schemas = get_schemas_by_tenant_mppdb_id(tenant_mppdb_id, mppdb_records[0])

            for mppdb_record in mppdb_records:
                create_db_user(mppdb_record.mppdb_ip, mppdb_record.mppdb_password, [new_user_in_backend_db])

                # Grant all corresponding schema to database user
                grant_schemas_to_user(schemas=schemas, username=new_user_in_backend_db.get_sql_username(), mppdb=mppdb_record)

            session.commit()
            return jsonify(user=new_user_in_backend_db.serialize)
        except Exception as e:
            LOG.exception("Fail to create mppdb user")
            try:
                session.rollback()
            except:
                pass

            raise ExceptionResponse(e)
        finally:
            try:
                session.close()
            except:
                pass


class UserAPI(Resource):

    # Show the specified user info.
    def get(self, user_id):
        session = SQLalchemyUtil.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).one()
            ret = jsonify(user=user.serialize)
            return ret
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()


    # Delete a specified user
    def delete(self, user_id):
        session = SQLalchemyUtil.get_session()
        try:
            deleted_user_record = session.query(User).filter_by(user_id=user_id).one()
            tenant_mppdb_record = session.query(TenantMPPDB).filter_by(
                tenant_mppdb_id=deleted_user_record.tenant_mppdb_id).one()
            mppdb_records = session.query(MPPDB).filter_by(
                tenant_mppdb_group_id=tenant_mppdb_record.tenant_mppdb_group_id).all()
            for mppdb_record in mppdb_records:
                delete_user(mppdb_record.mppdb_ip, mppdb_record.mppdb_password, [deleted_user_record])
            session.delete(deleted_user_record)
            session.commit()
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()


class TenantsAPI(Resource):
    # Show list of tenants
    def get(self):
        tenants_list = []
        tenants_object_list = OpenstackUtil.get_keystone_client().users.list()
        for tenant_object in tenants_object_list:
            tenant_list = {}
            tenant_list.__setitem__(u'username', tenant_object.__getattribute__('username'))
            tenant_list.__setitem__(u'id', tenant_object.__getattribute__('id'))
            tenant_list.__setitem__(u'enabled', tenant_object.__getattribute__('enabled'))
            tenant_list.__setitem__(u'name', tenant_object.__getattribute__('name'))
            tenant_list.__setitem__(u'email', tenant_object.__getattribute__('email'))
            tenants_list.append(tenant_list)
        tenants = {}
        tenants.__setitem__(u'tenants', tenants_list)
        return tenants


class TenantAPI(Resource):
    # Show a specified tenant
    def get(self, tenant_name):
        tenants_list = []
        tenants_object_list = OpenstackUtil.get_keystone_client().users.list()
        for tenant_object in tenants_object_list:
            if tenant_object.__getattribute__('username') == tenant_name:
                tenant_list = {}
                tenant_list.__setitem__(u'tenant_name', tenant_object.__getattribute__('username'))
                tenant_list.__setitem__(u'tenant_id', tenant_object.__getattribute__('id'))
                tenant_list.__setitem__(u'enabled', tenant_object.__getattribute__('enabled'))
                tenant_list.__setitem__(u'name', tenant_object.__getattribute__('name'))
                tenant_list.__setitem__(u'email', tenant_object.__getattribute__('email'))
                tenants_list.append(tenant_list)
                break
        tenants = {}
        tenants.__setitem__(u'tenant', tenants_list)
        return tenants


class TenantMPPDBsAPI(Resource):
    # Show list of tenant mppdbs
    def get(self):
        session = SQLalchemyUtil.get_session()
        tenantMppdbs = session.query(TenantMPPDB).all()
        LOG.debug(tenantMppdbs)
        ret = jsonify(tenant_mppdbs=[i.serialize for i in tenantMppdbs])
        session.close()
        return ret

class TenantMPPDBsInSameGroupAPI(Resource):
    # Show Tenant MPPDB List in the same tenant mppdb group
    def get(self, tenant_mppdb_group_id):
        session = SQLalchemyUtil.get_session()
        tenantMppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).all()
        ret = jsonify(tenant_mppdbs=[i.serialize for i in tenantMppdbs])
        session.close()
        return ret

class TenantMPPDBAPI(Resource):
    # Show a specified tenant_mppdb
    def get(self, tenant_mppdb_id):
        session = SQLalchemyUtil.get_session()
        tenantMppdb = session.query(TenantMPPDB).filter_by(tenant_mppdb_id=tenant_mppdb_id).one()
        ret = jsonify(tenant_mppdb=[tenantMppdb.serialize])
        session.close()
        return ret


class TenantMPPDBGroupsAPI(Resource):
    # Show list of tenant mppdb groups
    def get(self):
        session = SQLalchemyUtil.get_session()
        tenantMppdbGroups = session.query(TenantMPPDBGroup).all()
        tenantMppdbs = session.query(TenantMPPDB).all()
        for tenantMppdbGroup in tenantMppdbGroups:
            matching_tenants = []
            for tenantMppdb in tenantMppdbs:
                if tenantMppdbGroup.tenant_mppdb_group_id == tenantMppdb.tenant_mppdb_group_id:
                    matching_tenants.append(tenantMppdb)
            tenantMppdbGroup.tenant_mppdb_members_list = matching_tenants
            tenantMppdbGroup.mppdb_list = session.query(MPPDB).filter(
                MPPDB.tenant_mppdb_group_id == tenantMppdbGroup.tenant_mppdb_group_id).all()
        ret = jsonify(tenant_mppdb_groups=[i.serialize for i in tenantMppdbGroups])
        session.close()
        return ret


class MPPDBsAPI(Resource):

    # Get Tenant MPPDB List
    def get(self, tenant_id):
        session = SQLalchemyUtil.get_session()
        try:
            tenantMppdbs = session.query(TenantMPPDB).filter_by(tenant_id=tenant_id).all()
            return jsonify(tenantMppdbs=[i.serialize for i in tenantMppdbs])
        except Exception as e:
            LOG.exception(e)
        finally:
            session.close()


    # Create Trove Cluster
    def post(self, tenant_id):
        session = SQLalchemyUtil.get_session()
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('request_node_quantity', type=int, required=True)
            parser.add_argument('flavor', type=str, required=True)
            parser.add_argument('tenant_mppdb_name', type=str, required=True)
            args = parser.parse_args()

            tenant_mppdb_group = TenantMPPDBGroup(group_size=1, formation_time=None,
                                                  node_quantity=args['request_node_quantity'], flavor=args['flavor'])
            session.add(tenant_mppdb_group)
            session.flush()

            tenantMppdb = TenantMPPDB(tenant_mppdb_group_id=tenant_mppdb_group.tenant_mppdb_group_id,
                                      request_node_quantity=args['request_node_quantity'], flavor=args['flavor'],
                                      tenant_id=tenant_id, tenant_mppdb_name=args['tenant_mppdb_name'])
            session.add(tenantMppdb)
            session.flush()

            tenant_mppdb_id = tenantMppdb.tenant_mppdb_id

            # Prepare post trove creation action
            # 1. Create default admin user
            # 2. Create default schema
            class PostFunc(PostMPPDBCreateAction):
                def run(self, mppdb, session):

                    # create default admin user for the new Tenant
                    admin = User(user_name="admin",
                                 user_role="Null",
                                 password=common_util.gen_random_password(),
                                 tenant_mppdb_id=tenant_mppdb_id)

                    session.add(admin)

                    create_db_user(host_ip=mppdb.mppdb_ip,
                                   dbadmin_password=mppdb.mppdb_password,
                                   user_list=[admin])

                    # create default schema
                    create_vertica_schema(host_ip=mppdb.mppdb_ip,
                                          username=admin.get_sql_username(),
                                          password=admin.password,
                                          schema_name=rewrite.rewrite_schema_name(tenant_mppdb_id=tenant_mppdb_id,
                                                                                  schema_name=DEFAULT_TENANT_SCHEMA_NAME))

            session.commit()

            TroveClusterCreationManager.trove_cluster_creation_thread(session, args['request_node_quantity'], OpenstackUtil.get_nova_client().flavors.find(
                                                    name=args['flavor']).__getattribute__('id'), tenantMppdb.tenant_mppdb_group_id, post_func=[PostFunc()])
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()


class MPPDBAPI(Resource):
    # Show MPPDB List with the same tenant mppdb group id
    def get(self, tenant_mppdb_group_id):
        session = SQLalchemyUtil.get_session()
        try:
            mppdbs = session.query(MPPDB).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).all()
            ret = jsonify(mppdbs=[i.serialize for i in mppdbs])
            return ret
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()


class DeleteTenantMPPDBsAPI(Resource):
    # Delete the specified Tenant MPPDB in all MPPDBs
    def delete(self, tenant_mppdb_id):
        session = SQLalchemyUtil.get_session()

        delete_action = TenantMPPDBDataDeletion(tenant_mppdb_id=tenant_mppdb_id)
        delete_action.run()

        #Back-end database updation
        #update user records
        deleted_users_record = session.query(User).filter_by(tenant_mppdb_id=tenant_mppdb_id).all()
        for deleted_user in deleted_users_record:
            session.delete(deleted_user)
            session.commit()
        #update tenant mppdb group size
        tenant_mppdb = session.query(TenantMPPDB).filter_by(tenant_mppdb_id=tenant_mppdb_id).one()
        tenant_mppdb_group = session.query(TenantMPPDBGroup).filter_by(tenant_mppdb_group_id=tenant_mppdb.tenant_mppdb_group_id).one()
        tenant_mppdb_group.group_size = tenant_mppdb_group.group_size - 1
        session.add(tenant_mppdb_group)
        session.commit()
        #delete tenant_mppdb
        session.delete(tenant_mppdb)
        session.commit()
        #delete mppdb if mppdb is empty
        action_delete = MPPDBDeletion(tenant_mppdb_group.tenant_mppdb_group_id)
        action_delete.run(session)

class TenantMPPDBActivity(object):
    def __init__(self, epoch, query_status):
        self.epoch = epoch
        self.query_status = query_status

    @property
    def serialize(self):
        return {'epoch': self.epoch, 'query_status': self.query_status}


class TenantMPPDBActivityAPI(Resource):
    # Get the Tenant MPPDB Activity with the format
    def get(self, tenant_mppdb_id):
        #logging.info(str(datetime.now()))
        session = SQLalchemyUtil.get_session()
        try:
            values = session.query(common.models.TenantMPPDBActivity).filter_by(tenant_mppdb_id=tenant_mppdb_id).order_by(desc(common.models.TenantMPPDBActivity.time))[1:constant.NUM_OF_EPOCH_IN_DASHBOARD+1]
            ret = jsonify(tenant_mppdb_activities=[i.serialize for i in values])
            return ret

        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)

        finally:
            session.close()
            #logging.info(str(datetime.now()))

    def post(self, tenant_mppdb_id):

        parser = reqparse.RequestParser()
        parser.add_argument('last_timestamp', type=str, required=True)
        args = parser.parse_args()

        session = SQLalchemyUtil.get_session()
        try:
            gmt_datetime_obj = datetime.strptime(args['last_timestamp'], '%a, %d %b %Y %H:%M:%S %Z')
            start_analysis_time_obj = gmt_datetime_obj + timedelta(seconds=constant.DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND)
            last_timestamp_record = session.query(common.models.TenantMPPDBActivity).filter_by(tenant_mppdb_id=tenant_mppdb_id).filter_by(time=start_analysis_time_obj).one()
            ret = jsonify(tenant_mppdb_activities=[last_timestamp_record.serialize])
            return ret

        except Exception as e:
            return jsonify(tenant_mppdb_activities=[])
        finally:
            session.close()


class TenantMPPDBGroupActivity(object):
    def __init__(self, epoch, performance):
        self.epoch = epoch
        self.performance = performance

    @property
    def serialize(self):
        return {'epoch': self.epoch, 'performance': self.performance}


class TenantMPPDBGroupActivityAPI(Resource):
    # Get the Tenant MPPDB Group Activity with the format
    def get(self, tenant_mppdb_group_id):
        session = SQLalchemyUtil.get_session()
        try:
            values = session.query(Performance).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).order_by(desc(Performance.time))[1:constant.NUM_OF_EPOCH_IN_DASHBOARD+1]
            ret = jsonify(tenant_mppdb_group_activities=[i.serialize for i in values])
            return ret
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()

    def post(self, tenant_mppdb_group_id):

        parser = reqparse.RequestParser()
        parser.add_argument('last_timestamp', type=str, required=True)
        args = parser.parse_args()

        session = SQLalchemyUtil.get_session()
        try:
            gmt_datetime_obj = datetime.strptime(args['last_timestamp'], '%a, %d %b %Y %H:%M:%S %Z')
            start_analysis_time_obj = gmt_datetime_obj + timedelta(seconds=constant.DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND)
            last_timestamp_record = session.query(Performance).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).filter_by(time=start_analysis_time_obj).one()
            ret = jsonify(tenant_mppdb_group_activities=[last_timestamp_record.serialize])
            return ret

        except Exception as e:
            return jsonify(tenant_mppdb_group_activities=[])
        finally:
            session.close()


class TenantMPPDBGroupServiceLevel(object):
    def __init__(self, epoch, service_level):
        self.epoch = epoch
        self.service_level = service_level

    @property
    def serialize(self):
        return {'epoch': self.epoch, 'service_level': self.service_level}


class TenantMPPDBGroupServiceLevelAPI(Resource):
    # Get the Tenant MPPDB Group's Service Level
    def get(self, tenant_mppdb_group_id):
        session = SQLalchemyUtil.get_session()

        try:
            values = session.query(SlaGuarantee).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).order_by(desc(SlaGuarantee.time))[1:constant.NUM_OF_EPOCH_IN_DASHBOARD+1]
            ret = jsonify(tenant_mppdb_group_service_levels=[i.serialize for i in values])
            return ret
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)

    def post(self, tenant_mppdb_group_id):

        parser = reqparse.RequestParser()
        parser.add_argument('last_timestamp', type=str, required=True)
        args = parser.parse_args()

        session = SQLalchemyUtil.get_session()
        try:
            gmt_datetime_obj = datetime.strptime(args['last_timestamp'], '%a, %d %b %Y %H:%M:%S %Z')
            start_analysis_time_obj = gmt_datetime_obj + timedelta(seconds=constant.DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND)
            last_timestamp_record = session.query(SlaGuarantee).filter_by(tenant_mppdb_group_id=tenant_mppdb_group_id).filter_by(time=start_analysis_time_obj).one()
            ret = jsonify(tenant_mppdb_group_service_levels=[last_timestamp_record.serialize])
            return ret

        except Exception as e:
            return jsonify(tenant_mppdb_group_service_levels=[])
        finally:
            session.close()

class UnconsolidatedTenantMPPDBAPI(Resource):
    def get(self):
        session = SQLalchemyUtil.get_session()
        try:
            all_tenant_mppdbs = []
            unconsolidated_tenant_mppdb_groups = session.query(TenantMPPDBGroup).filter_by(group_size=1).all()

            for unconsolidated_tenant_mppdb_group in unconsolidated_tenant_mppdb_groups:
                tenantMppdbs = session.query(TenantMPPDB).filter_by(tenant_mppdb_group_id=unconsolidated_tenant_mppdb_group.tenant_mppdb_group_id).all()
                for tenantMppdb in tenantMppdbs:
                    all_tenant_mppdbs.append(tenantMppdb)

            if(all_tenant_mppdbs.__len__()==0):
                ret = jsonify(unconsolidated_tenant_mppdbs=[])
            else:
                ret = jsonify(unconsolidated_tenant_mppdbs=[i.serialize for i in all_tenant_mppdbs])
            session.close()
            return ret
        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()

# Get Query Router URI
api.add_resource(QueryRouterURIAPI, '/v1.0/queryrouter_uri')

# Get Replication Factor
api.add_resource(ReplicationFactorAPI, '/v1.0/replication_factor')

# Get Service Level Agreement
api.add_resource(ServiceLevelAgreementAPI, '/v1.0/service_level_agreement')

# Get the flavor details
api.add_resource(FlavorAPI, '/v1.0/flavor/<string:flavor_name>')

# Get the users list with the same tenant_id
# Create the user in the specified MPPDB (from dashboard function addUser)
api.add_resource(UsersAPI, '/v1.0/tenants/<string:tenant_id>/users')

# Show the specified user info.
# Delete a specified user (from dashboard function deleteUser)
api.add_resource(UserAPI, '/v1.0/users/<int:user_id>')

# Show list of tenants (from dashboard function getTenants)
api.add_resource(TenantsAPI, '/v1.0/tenants')

# Show a specified tenant (from dashboard function getUsers and addUser)
api.add_resource(TenantAPI, '/v1.0/tenants/<string:tenant_name>')

# Show list of tenant mppdbs (from dashboard window.onload in tenant_mppdb_status file and function getTenantMppdbs)
api.add_resource(TenantMPPDBsAPI, '/v1.0/tenantmppdbs')

# Show Tenant MPPDB List in the same tenant mppdb group (from dashboard function drawTenantsDeployed in tenant_mppdb_group_status file)
api.add_resource(TenantMPPDBsInSameGroupAPI, '/v1.0/tenantmppdbs_in_same_group/<int:tenant_mppdb_group_id>')

# Show a specified tenant_mppdb (from dashboard function getCluster and getUsers)
api.add_resource(TenantMPPDBAPI, '/v1.0/tenantmppdbs/<int:tenant_mppdb_id>')

# Show list of tenant mppdb groups (from dashboard function getTenantMppdbGroups)
api.add_resource(TenantMPPDBGroupsAPI, '/v1.0/tenantmppdbgroups')

# Get Tenant MPPDB List (from dashboard function getClusters)
# Create Trove Cluster (from dashboard function addCluster)
api.add_resource(MPPDBsAPI, '/v1.0/tenantmppdbs/<string:tenant_id>/mppdb')

# Show MPPDB List with the same tenant mppdb group id
api.add_resource(MPPDBAPI, '/v1.0/mppdbs/<int:tenant_mppdb_group_id>/mppdb')

# Delete the specified Tenant MPPDB in all MPPDBs (from dashboard function deleteCluster)
api.add_resource(DeleteTenantMPPDBsAPI, '/v1.0/tenantmppdbs/<int:tenant_mppdb_id>/mppdb')

# Get the Tenant MPPDB Activity with the format (from dashboard function drawChart in tenant_mppdb_status file)
api.add_resource(TenantMPPDBActivityAPI, '/v1.0/tenantmppdbs/<int:tenant_mppdb_id>/activities')

# Get the Tenant MPPDB Group Activity with the format (from dashboard function drawChart in tenant_mppdb_group_status file)
api.add_resource(TenantMPPDBGroupActivityAPI, '/v1.0/tenantmppdbgroups/<int:tenant_mppdb_group_id>/activities')

# Get the Tenant MPPDB Group's Service Level (from dashboard function drawServiceLevelChart in tenant_mppdb_group_status file)
api.add_resource(TenantMPPDBGroupServiceLevelAPI, '/v1.0/tenantmppdbgroups/<int:tenant_mppdb_group_id>/servicelevel')

api.add_resource(UnconsolidatedTenantMPPDBAPI, '/v1.0/tenantmppdbs/unconsolidated_tenantmppdb')

if __name__ == '__main__':
    app.run(host=REST_HOST, port=REST_PORT)
