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
import uuid
from datetime import datetime

from common.constant import REPLICATON_FACTOR
from common.constant import SERVICE_LEVEL_AGREEMENT
from common.dao import ConsolidationLogDAO
from common.db.db_analyzer import DatabaseAnalyzer
from common.db.db_util import SQLalchemyUtil
from common.models import MigrationJob, TenantMPPDBGroup
from common.util.date_converter import DateConverter
from deployment_master.action.mppdb_creation import MPPDBCreation
from deployment_master.models import MigrationPlan
from tenant_activity_analyzer import look_for_best_tenant_mppdb, check_service_level


class ServiceLevelMonitor(object):
    """
    Monitor service level of each TenantMPPDBGroup.
    And take actions once the service level of a TenantMPPDGroup is violated.
    """

    def __init__(self):
        self.database_analyzer = DatabaseAnalyzer(DatabaseAnalyzer.SERVICE_LEVEL_CHECKING)
        self.logger = logging.getLogger(__name__)

    def find_unsatisfied_tenant_mppdb_groups(self, current_tenant_mppdb_group_list):
        """Find out TenantMPPDBGroups whose service level agreement are violated."""
        unsatisfied_tenant_mppdb_group_list = []
        for tenant_mppdb_group in current_tenant_mppdb_group_list:
            service_level = check_service_level(tenant_mppdb_group.tenant_mppdb_members_list, self.database_analyzer.total_epochs,
                                                quota=min(REPLICATON_FACTOR,
                                                          len(tenant_mppdb_group.tenant_mppdb_members_list)))
            if service_level < SERVICE_LEVEL_AGREEMENT:
                unsatisfied_tenant_mppdb_group_list.append(tenant_mppdb_group)
        return unsatisfied_tenant_mppdb_group_list

    def fix_unsatisfied_tenant_mppdb_group(self, tenant_mppdb_group, current_tenant_mppdb_group_list):
        """Reconsolidate and redeploy TenantMPPDBs in a violated TenantMPPDBGroup."""
        # reconsolidate TenantMPPDBs
        self.logger.info('Start to reconsoldiate tenant MPPDBs in the tenant MPPDB group %s' % str(tenant_mppdb_group))
        tenant_mppdb_list = tenant_mppdb_group.tenant_mppdb_members_list
        minimum_active_ratio = min([tenant_mppdb.active_ratio for tenant_mppdb in tenant_mppdb_list])
        new_groups = []
        for tenant_mppdb in tenant_mppdb_list:
            if tenant_mppdb.active_ratio == minimum_active_ratio and len(new_groups) == 0:
                new_groups.append([tenant_mppdb])
                tenant_mppdb_list.remove(tenant_mppdb)
        index = 0
        while len(tenant_mppdb_list) != 0:
            best_tenant_mppdb = look_for_best_tenant_mppdb(new_groups[index], tenant_mppdb_list, self.database_analyzer.total_epochs)
            new_groups[index].append(best_tenant_mppdb)
            service_level = check_service_level(new_groups[index], self.database_analyzer.total_epochs)
            if service_level >= SERVICE_LEVEL_AGREEMENT:
                tenant_mppdb_list.remove(best_tenant_mppdb)
            else:
                new_groups[index].remove(best_tenant_mppdb)
                index += 1
                new_groups.append([])

        # redeploy TenantMPPDBs in a violated TenantMPPDBGroup.
        new_group_deployed_on_current_tenant_mppdb_group = None
        maximum_tenant_mppdbs_in_a_new_group = max([len(new_group) for new_group in new_groups])
        for new_group in new_groups:
            if len(new_group) == maximum_tenant_mppdbs_in_a_new_group:
                new_group_deployed_on_current_tenant_mppdb_group = new_group
        new_groups.remove(new_group_deployed_on_current_tenant_mppdb_group)

        #current_datetime = datetime.now()
        newly_created_tenant_mppdb_group_count = 1
        newly_created_tenant_mppdb_group_list = []
        for new_group in new_groups:
            new_tenant_mppdb_group_id = max(
                [current_tenant_mppdb_group.tenant_mppdb_group_id for current_tenant_mppdb_group in
                 current_tenant_mppdb_group_list]) + newly_created_tenant_mppdb_group_count
            newly_created_tenant_mppdb_group_list.append(
                TenantMPPDBGroup(tenant_mppdb_group_id=new_tenant_mppdb_group_id, group_size=len(new_group),
                                 formation_time=None, node_quantity=new_group[0].request_node_quantity,
                                 flavor=new_group[0].flavor, tenant_mppdb_members_list=new_group))
            current_tenant_mppdb_group_list.append(
                TenantMPPDBGroup(tenant_mppdb_group_id=new_tenant_mppdb_group_id, group_size=len(new_group),
                                 formation_time=None, node_quantity=new_group[0].request_node_quantity,
                                 flavor=new_group[0].flavor, tenant_mppdb_members_list=new_group))
            newly_created_tenant_mppdb_group_count += 1
            self.logger.info('Create new tenant MPPDB groups %s ' % str(newly_created_tenant_mppdb_group_list))

        global_action_list = []

        for newly_created_tenant_mppdb_group in newly_created_tenant_mppdb_group_list:
            mppdb_quantity_to_create = min(REPLICATON_FACTOR, len(newly_created_tenant_mppdb_group.tenant_mppdb_members_list))

            action_create = MPPDBCreation(action=MigrationJob._tenant_mppdb_data_movement,
                                             dest_tenant_mppdb_group=newly_created_tenant_mppdb_group,
                                             mppdb_quantity_to_create=mppdb_quantity_to_create)

            global_action_list.append(action_create)


            for tenant_mppdb in newly_created_tenant_mppdb_group.tenant_mppdb_members_list:

                tenant_mppdb_data_movement_uuid = uuid.uuid4()
                action_list = []

                for movement_times in range(0, mppdb_quantity_to_create):
                    action = MigrationJob(action=MigrationJob._tenant_mppdb_data_movement,
                                          source_mppdb_id=tenant_mppdb_group.mppdb_list[0].mppdb_id,
                                          dest_mppdb_id=None,
                                          tenant_mppdb_id=tenant_mppdb.tenant_mppdb_id,
                                          changes_id=tenant_mppdb_data_movement_uuid)

                    global_action_list.append(action)
                    action_list.append(action)

                action_create.addAction(tenant_mppdb_data_movement_uuid, action_list)

        tenant_mppdb_group.tenant_mppdb_members_list = new_group_deployed_on_current_tenant_mppdb_group

        self.logger.info('Take actions %s' % str(action_list))

        migration_plan = MigrationPlan(global_action_list)

        session = SQLalchemyUtil.get_session()

        for action in migration_plan.getMppdbCreations():
            action.run(session)

        for action in migration_plan.getTenantMppdbGroupCreations():
            action.run(session)

        # get Move and Copy and call to add them to db job Queue
        for action in migration_plan.getCopyAndMoveMPPDBAction():
            action.run(session)


    def ensure_service_level(self):
        """Trigger service level checking."""
        try:
            self.session = SQLalchemyUtil.get_session()
            self.logger.info('Start to check service level.')
            current_tenant_mppdb_group_list = self.database_analyzer.get_current_tenant_mppdb_group_list()
            unsatisfied_tenant_mppdb_groups = self.find_unsatisfied_tenant_mppdb_groups(current_tenant_mppdb_group_list)

            if len(unsatisfied_tenant_mppdb_groups) != 0:
                self.logger.info('Find tenant MPPDB groups whose service level agreements are violated %s' % str(unsatisfied_tenant_mppdb_groups))
                for tenant_mppdb_group in unsatisfied_tenant_mppdb_groups:
                    self.fix_unsatisfied_tenant_mppdb_group(tenant_mppdb_group, current_tenant_mppdb_group_list)
                ConsolidationLogDAO.update_consolidation_log_table(self.session, DateConverter.local_datetime_to_gmt_datetime(datetime.now()))
                self.logger.info('All unsatisfied tenant MPPDB groups are fixed.')
            else:
                self.logger.info('The service level of all tenant MPPDB groups are satisfied.')
        except:
            self.logger.exception("Fail to finish sla monitor")
