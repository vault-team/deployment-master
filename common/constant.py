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
from datetime import timedelta

import configs


################# Configuration for database #################
#  specifies the ip address of the host which containing the back-end database.
DB_HOST = configs.CONF.get(configs.KEY_BACKEND_DB_HOST)
# specifies the port number of the host which containing the back-end database.
DB_PORT = configs.CONF.get(configs.KEY_BACKEND_DB_PORT)
# specifies the user name of the back-end database.
DB_USER = configs.CONF.get(configs.KEY_BACKEND_DB_USERNAME)
# specifies the password of the back-end database
DB_PASSWORD = configs.CONF.get(configs.KEY_BACKEND_DB_PASSWORD)
# specifies the schema of the back-end database
DB_SCHEMA = configs.CONF.get(configs.KEY_BACKEND_DB_SCHEMA)

################# Configuration for OpenStack #################
# the user name in OpenStack.
OPENSTACK_USERNAME = configs.CONF.get(configs.KEY_OPENSTACK_USERNAME)
# the password of the user in OpenStack.
OPENSTACK_PASSWORD = configs.CONF.get(configs.KEY_OPENSTACK_PASSWORD)
# the id of the project you choose.
PROJECT_ID = configs.CONF.get(configs.KEY_OPENSTACK_PROJECT_ID)
# the authentication URL of Identity v2 API.
AUTH_URL = configs.CONF.get(configs.KEY_OPENSTACK_AUTH_URL)
# the name of the cluster you will create.
CLUSTER_NAME = configs.CONF.get(configs.KEY_OPENSTACK_CLUSTER_NAME)
# the name of the datastore your trove image located at.
CLUSTER_DATASTORE = configs.CONF.get(configs.KEY_OPENSTACK_CLUSTER_DATASTORE)
# the version of the datastore your trove image located at.
CLUSTER_DATASTORE_VERSION = configs.CONF.get(configs.KEY_OPENSTACK_CLUSTER_DATASTORE_VERSION)
# specifies the volume size of the cluster you will create.
CLUSTER_VOLUME_SIZE = configs.CONF.get(configs.KEY_OPENSTACK_CLUSTER_VOLUME_SIZE_GB)
# specifies the availability zone of the cluster you will create.
CLUSTER_AVAILABILITY_ZONE = configs.CONF.get(configs.KEY_OPENSTACK_CLUSTER_AVAILABILITY_ZONE)

################# Configuration for Vault RESTful web server #################
# specifies the ip address of the RESTful web server.
REST_HOST = configs.CONF.get(configs.KEY_DM_LISTEN_HOST)
# specifies the port number of the RESTful web server.
REST_PORT = configs.CONF.get(configs.KEY_DM_LISTEN_PORT)

################# Configutation for deployment advisor #################

# specifies the number of replication of MPPDB should be in the cluster.
REPLICATON_FACTOR = configs.CONF.get(configs.KEY_DM_REPLICATON_FACTOR)
# specifies the value of SLA it should meet. If you set 0.99 which means SLA is 99%.
SERVICE_LEVEL_AGREEMENT = configs.CONF.get(configs.KEY_DM_SERVICE_LEVEL_AGREEMENT)
# specifies the time length of the consolidation period cycle.
CONSOLIDATION_PERIOD = timedelta(seconds=configs.CONF.get(configs.KEY_DM_CONSOLIDATION_PERIOD))
# specifies the time length of checking the service level.
SERVICE_LEVEL_CHECKING_PERIOD = timedelta(seconds=configs.CONF.get(configs.KEY_DM_SERVICE_LEVEL_CHECKING_PERIOD))
# specifies the time length of each epoch used in service level checking and consolidation.
EPOCH_SIZE = timedelta(seconds=configs.CONF.get(configs.KEY_DM_EPOCH_SIZE))
# specifies the number of epochs that will be displayed within the area charts in dashboard.
NUM_OF_EPOCH_IN_DASHBOARD = 12

################# Configuration for Vertica #################
# the path of the key pair file used for SSH connection to the database guest machine from local
KEY_FILE_PATH_LOCAL=configs.CONF.get(configs.KEY_DM_INSTANCE_KEY_FILE_PATH_GUEST)

#  specifies the number of thread for migration job.
TENANT_UPDATE_JOB_MAX_NUM_THREAD = configs.CONF.get(configs.KEY_DM_TENANT_UPDATE_JOB_MAX_NUM_THREAD)
# specifies the waiting time length of checking available migration job.
TENANT_UPDATE_JOB_CHECK_INTERVAL_IN_SECOND = configs.CONF.get(configs.KEY_DM_TENANT_UPDATE_JOB_CHECK_INTERVAL_IN_SECOND)

# the destination path of the sql file will be imported to.
TARGET_TABLE_SQL_PATH = configs.CONF.get(configs.KEY_DM_DATA_MIGRATION_TARGET_TABLE_SQL_PATH)
# the source path of the sql file for exporting.
SOURCE_TABLE_SQL_PATH = configs.CONF.get(configs.KEY_DM_DATA_MIGRATION_SOURCE_TABLE_SQL_PATH)

# specifies the time length of performance computation cycle.
DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND = configs.CONF.get(configs.KEY_DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND)
# specifies the time length of SLA guarantee computation cycle.
DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND = configs.CONF.get(configs.KEY_DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND)
# specifies the time length of tenant MPPDB activity computation cycle.
DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND = configs.CONF.get(configs.KEY_DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND)
# specifies the waiting time length of updating the graph data.
DASHBOARD_UPDATE_GRAPH_DATA_CHECK_INTERVAL_IN_SECOND = configs.CONF.get(configs.KEY_DASHBOARD_UPDATE_GRAPH_DATA_CHECK_INTERVAL_IN_SECOND)

################# Configuration for Query Router #################
QUERY_ROUTER_URI = "192.168.1.138:8080"