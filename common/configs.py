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


import getopt
import logging

from common import log
import sys
from oslo_config import cfg

KEY_BACKEND_DB_HOST = 'BACKEND_DB_HOST'
KEY_BACKEND_DB_PORT = 'BACKEND_DB_PORT'
KEY_BACKEND_DB_SCHEMA = 'BACKEND_DB_SCHEMA'
KEY_BACKEND_DB_USERNAME = 'BACKEND_DB_USERNAME'
KEY_BACKEND_DB_PASSWORD = 'BACKEND_DB_PASSWORD'

KEY_OPENSTACK_USERNAME = 'OPENSTACK_USERNAME'
KEY_OPENSTACK_PASSWORD = 'OPENSTACK_PASSWORD'
KEY_OPENSTACK_PROJECT_ID = 'OPENSTACK_PROJECT_ID'
KEY_OPENSTACK_AUTH_URL = 'OPENSTACK_AUTH_URL'
KEY_OPENSTACK_CLUSTER_NAME = 'OPENSTACK_CLUSTER_NAME'
KEY_OPENSTACK_CLUSTER_DATASTORE = 'OPENSTACK_CLUSTER_DATASTORE'
KEY_OPENSTACK_CLUSTER_DATASTORE_VERSION = 'OPENSTACK_CLUSTER_DATASTORE_VERSION'
KEY_OPENSTACK_CLUSTER_VOLUME_SIZE_GB = 'OPENSTACK_CLUSTER_VOLUME_SIZE_GB'
KEY_OPENSTACK_CLUSTER_AVAILABILITY_ZONE = 'OPENSTACK_CLUSTER_AVAILABILITY_ZONE'

KEY_DM_LISTEN_HOST = 'DM_LISTEN_HOST'
KEY_DM_LISTEN_PORT = 'DM_LISTEN_PORT'

KEY_DM_REPLICATON_FACTOR = 'DM_REPLICATON_FACTOR'
KEY_DM_SERVICE_LEVEL_AGREEMENT = 'DM_SERVICE_LEVEL_AGREEMENT'
KEY_DM_CONSOLIDATION_PERIOD = 'DM_CONSOLIDATION_PERIOD_SECOND'
KEY_DM_SERVICE_LEVEL_CHECKING_PERIOD = 'DM_SERVICE_LEVEL_CHECKING_PERIOD_SECOND'
KEY_DM_EPOCH_SIZE = "DM_EPOCH_SIZE_SECOND"

KEY_DM_INSTANCE_KEY_FILE_PATH_GUEST= 'DM_INSTANCE_KEY_FILE_PATH_GUEST'

KEY_DM_TENANT_UPDATE_JOB_MAX_NUM_THREAD = 'DM_TENANT_UPDATE_JOB_MAX_NUM_THREAD'
KEY_DM_TENANT_UPDATE_JOB_CHECK_INTERVAL_IN_SECOND = 'DM_TENANT_UPDATE_JOB_CHECK_INTERVAL_IN_SECOND'

KEY_DM_DATA_MIGRATION_TARGET_TABLE_SQL_PATH = 'DM_DATA_MIGRATION_TARGET_TABLE_SQL_PATH'
KEY_DM_DATA_MIGRATION_SOURCE_TABLE_SQL_PATH = 'DM_DATA_MIGRATION_SOURCE_TABLE_SQL_PATH'

KEY_DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND = 'DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND'
KEY_DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND = 'DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND'
KEY_DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND = 'DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND'
KEY_DASHBOARD_UPDATE_GRAPH_DATA_CHECK_INTERVAL_IN_SECOND = 'DASHBOARD_UPDATE_GRAPH_DATA_CHECK_INTERVAL_IN_SECOND'

def loadConfig(path):
    opts = [
        cfg.StrOpt(KEY_BACKEND_DB_HOST),
        cfg.IntOpt(KEY_BACKEND_DB_PORT),
        cfg.StrOpt(KEY_BACKEND_DB_SCHEMA),
        cfg.StrOpt(KEY_BACKEND_DB_USERNAME),
        cfg.StrOpt(KEY_BACKEND_DB_PASSWORD),

        cfg.StrOpt(KEY_OPENSTACK_USERNAME),
        cfg.StrOpt(KEY_OPENSTACK_PASSWORD),
        cfg.StrOpt(KEY_OPENSTACK_PROJECT_ID),
        cfg.StrOpt(KEY_OPENSTACK_AUTH_URL),
        cfg.StrOpt(KEY_OPENSTACK_CLUSTER_NAME),
        cfg.StrOpt(KEY_OPENSTACK_CLUSTER_DATASTORE),
        cfg.StrOpt(KEY_OPENSTACK_CLUSTER_DATASTORE_VERSION),
        cfg.IntOpt(KEY_OPENSTACK_CLUSTER_VOLUME_SIZE_GB),
        cfg.StrOpt(KEY_OPENSTACK_CLUSTER_AVAILABILITY_ZONE),

        cfg.StrOpt(KEY_DM_LISTEN_HOST, default='0.0.0.0'),
        cfg.IntOpt(KEY_DM_LISTEN_PORT, default=8788),

        cfg.IntOpt(KEY_DM_REPLICATON_FACTOR, default=2),
        cfg.FloatOpt(KEY_DM_SERVICE_LEVEL_AGREEMENT, default=0.99),
        cfg.IntOpt(KEY_DM_CONSOLIDATION_PERIOD, default=300),
        cfg.IntOpt(KEY_DM_SERVICE_LEVEL_CHECKING_PERIOD, default=60),
        cfg.IntOpt(KEY_DM_EPOCH_SIZE, default=20),

        cfg.StrOpt(KEY_DM_INSTANCE_KEY_FILE_PATH_GUEST),

        cfg.IntOpt(KEY_DM_TENANT_UPDATE_JOB_MAX_NUM_THREAD, default=3),
        cfg.IntOpt(KEY_DM_TENANT_UPDATE_JOB_CHECK_INTERVAL_IN_SECOND, default=20),

        cfg.StrOpt(KEY_DM_DATA_MIGRATION_TARGET_TABLE_SQL_PATH, default=''),
        cfg.StrOpt(KEY_DM_DATA_MIGRATION_SOURCE_TABLE_SQL_PATH, default=''),

        cfg.IntOpt(KEY_DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND, default=20),
        cfg.IntOpt(KEY_DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND, default=20),
        cfg.IntOpt(KEY_DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND, default=20),
        cfg.IntOpt(KEY_DASHBOARD_UPDATE_GRAPH_DATA_CHECK_INTERVAL_IN_SECOND, default=20)
    ]
    conf = cfg.CONF
    conf.register_opts(opts)
    conf(["--config-file",path])


def get_home_dir():
    home_dir = "."

    try:
        opts, args = getopt.getopt(sys.argv, "", ["home_dir"])
    except getopt.GetoptError:
        print 'main.py --home_dir <home dir path>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == 'home_dir':
            home_dir = arg
    return home_dir

logger = log.getLogger("configs")

CONF = cfg.CONF
config_ini = get_home_dir()+"/conf/deployment_master.conf"
loadConfig(path=config_ini)
CONF.log_opt_values(logger, logging.INFO)


