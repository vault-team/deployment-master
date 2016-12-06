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

import abc
import logging

from common.db.db_util import SQLalchemyUtil
import thread

from common.models import MPPDB
from common.util.trove_cluster_operations import create_trove_cluster, get_trove_client
from common.util.vertica_db_operations import get_dbadmin_password, create_vertica_schema, create_db_user
from common.constant import *


class TroveClusterCreationManager(object):

    logger = logging.getLogger("TroveClusterCreationManager")

    @classmethod
    def trove_cluster_creation(cls, mppdb_id, tenant_mppdb_group_id, cluster, post_func=[]):

        session = SQLalchemyUtil.get_session()
        try:

            mppdb_ip = create_trove_cluster(cluster)

            mppdb_password = get_dbadmin_password(mppdb_ip)
            mppdb = session.query(MPPDB).filter_by(mppdb_id=mppdb_id).one()
            mppdb.mppdb_password = mppdb_password
            mppdb.mppdb_ip = mppdb_ip
            mppdb.tenant_mppdb_group_id = tenant_mppdb_group_id

            # execute post action
            for func in post_func:
                if isinstance(func, PostMPPDBCreateAction):
                    func.run(mppdb=mppdb, session=session)
                else:
                    raise TypeError()

            session.add(mppdb)
            session.commit()

        except Exception as e:
            logging.exception("Fail to create trove cluster")
            raise e
        finally:
            session.close()

    @classmethod
    def trove_cluster_creation_thread(cls, session, request_node_quantity, flavor, tenant_mppdb_group_id, post_func=[]):

        """Create a MPPDB by requesting Trove to create a cluster."""
        cluster_instances = []
        for i in range(request_node_quantity):
            cluster_instances.append({'flavorRef': flavor, 'volume': {'size': CLUSTER_VOLUME_SIZE},
                                      'availability_zone': CLUSTER_AVAILABILITY_ZONE})
            i += 1
        trove = get_trove_client()
        cluster = trove.clusters.create(CLUSTER_NAME, CLUSTER_DATASTORE, CLUSTER_DATASTORE_VERSION, instances=cluster_instances)

        mppdb_id = cluster.id

        mppdb = MPPDB(mppdb_id=mppdb_id, mppdb_ip="", tenant_mppdb_group_id=tenant_mppdb_group_id, mppdb_password="")
        session.add(mppdb)
        session.commit()

        thread.start_new_thread(cls.trove_cluster_creation, (mppdb_id, tenant_mppdb_group_id, cluster, post_func))


class PostMPPDBCreateAction:

    def __init__(self):
        pass

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self, mppdb, session):
        if not isinstance(mppdb, MPPDB):
            raise TypeError()
        logging.info("Start execute post trove creation action for mppdb_id: "+mppdb.mppdb_id)
        pass






