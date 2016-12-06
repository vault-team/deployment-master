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

from datetime import datetime

from common.constant import *
from common.db.db_analyzer import DatabaseAnalyzer
from common.models import TenantMPPDBGroup
from tenant_activity_analyzer import look_for_best_tenant_mppdb, check_service_level


class DeploymentAdvisor():
    """
    Consolidate all TenantMPPDBs and generate a deployment plan.
    A deployment plan is a list of updated TenantMPPDBGroup objects.
    """

    def __init__(self):
        self.database_analyzer = DatabaseAnalyzer(DatabaseAnalyzer.CONSOLIDATION)

    def consolidate(self):
        """Consolidate all TenantMPPDBs into new groups."""
        # put TenantMPPDBs with the same flavor and node quantity into one initial group
        initial_groups = {}
        tenant_mppdb_list = self.database_analyzer.get_tenant_mppdb_list()
        for tenant_mppdb in tenant_mppdb_list:

            initial_group_key = tenant_mppdb.flavor + '+' + str(tenant_mppdb.request_node_quantity)
            if initial_group_key not in initial_groups.keys():
                initial_groups[initial_group_key] = []
            initial_groups[initial_group_key].append(tenant_mppdb)
        least_active_tenant_mppdb = {}
        for initial_group_key in initial_groups.keys():
            minimum_active_ratio = min(
                [tenant_mppdb.active_ratio for tenant_mppdb in initial_groups[initial_group_key]])
            for tenant_mppdb in initial_groups[initial_group_key]:
                group_key = tenant_mppdb.flavor + '+' + str(tenant_mppdb.request_node_quantity)
                if tenant_mppdb.active_ratio == minimum_active_ratio and group_key not in least_active_tenant_mppdb.keys():
                    least_active_tenant_mppdb[group_key] = tenant_mppdb
        # consolidate TenantMPPDBs in every initial group based on their query status in the past consolidation cycle period
        new_groups = {}
        for initial_group_key in initial_groups.keys():
            new_groups[initial_group_key] = []
            new_groups[initial_group_key].append([least_active_tenant_mppdb[initial_group_key]])
            initial_groups[initial_group_key].remove(least_active_tenant_mppdb[initial_group_key])
            index = 0
            while len(initial_groups[initial_group_key]) != 0:
                best_tenant_mppdb = look_for_best_tenant_mppdb(new_groups[initial_group_key][index], initial_groups[initial_group_key], self.database_analyzer.total_epochs)
                new_groups[initial_group_key][index].append(best_tenant_mppdb)
                service_level = check_service_level(new_groups[initial_group_key][index], self.database_analyzer.total_epochs)
                if service_level >= SERVICE_LEVEL_AGREEMENT:
                    initial_groups[initial_group_key].remove(best_tenant_mppdb)
                else:
                    new_groups[initial_group_key][index].remove(best_tenant_mppdb)
                    index += 1
                    new_groups[initial_group_key].append([])
        # get a list of new groups and each new group contains a list of satisfied TenantMPPDBs
        new_group_list = []
        for new_group_set in new_groups.values():
            for new_group in new_group_set:
                new_group_list.append(new_group)
        return new_group_list

    def generate_deployment_plan(self):
        """
        Match new groups with current TenantMPPDBGroups based on the number of common TenantMPPDBs they hold. The more, the better.
        If there is no matching TenantMPPDBGroup for a new group, create a new TenantMPPDBGroup.
        """
        # calculate the number of common TenantMPPDBs between each new group and each current TenantMPPDBGroup
        new_group_list = self.consolidate()
        group_matching = {}
        current_tenant_mppdb_group_list = self.database_analyzer.get_current_tenant_mppdb_group_list()
        for new_group in new_group_list:
            new_group_by_tenant_mppdb_id = [tenant_mppdb.tenant_mppdb_id for tenant_mppdb in new_group]
            for current_tenant_mppdb_group in current_tenant_mppdb_group_list:
                current_tenant_mppdb_group_by_tenant_mppdb_id = [tenant_mppdb.tenant_mppdb_id for tenant_mppdb in
                                                                 current_tenant_mppdb_group.tenant_mppdb_members_list]
                common_tenant_mppdbs = list(
                    set(new_group_by_tenant_mppdb_id) & set(current_tenant_mppdb_group_by_tenant_mppdb_id))
                common_tenant_mppdbs_count = len(common_tenant_mppdbs)
                if common_tenant_mppdbs_count != 0:
                    group_matching[common_tenant_mppdbs[0]] = common_tenant_mppdbs_count
        # Deploy the new group with the maximum number of common TenantMPPDBs to a current TenantMPPDBGroup
        new_tenant_mppdb_group_list = []
        #current_datetime = datetime.now()
        sorted_group_matching = sorted(group_matching, key=group_matching.get, reverse=True)
        for tenant_mppdb_id in sorted_group_matching:
            new_tenant_mppdb_group_list_by_group_id = [tenant_mppdb_group.tenant_mppdb_group_id for tenant_mppdb_group
                                                       in new_tenant_mppdb_group_list]
            new_tenant_mppdb_group_list_by_tenant_mppdb_members = [tenant_mppdb_group.tenant_mppdb_members_list for
                                                                   tenant_mppdb_group in new_tenant_mppdb_group_list]
            for new_group in new_group_list:
                new_group_by_tenant_mppdb_id = [tenant_mppdb.tenant_mppdb_id for tenant_mppdb in new_group]
                for current_tenant_mppdb_group in current_tenant_mppdb_group_list:
                    current_tenant_mppdb_groups_by_tenant_mppdb_id = [tenant_mppdb.tenant_mppdb_id for tenant_mppdb in
                                                                      current_tenant_mppdb_group.tenant_mppdb_members_list]
                    if tenant_mppdb_id in new_group_by_tenant_mppdb_id and tenant_mppdb_id in current_tenant_mppdb_groups_by_tenant_mppdb_id and current_tenant_mppdb_group.tenant_mppdb_group_id not in new_tenant_mppdb_group_list_by_group_id and new_group not in new_tenant_mppdb_group_list_by_tenant_mppdb_members:
                        current_tenant_mppdb_group.group_size = len(new_group)
                        current_tenant_mppdb_group.formation_time = None
                        current_tenant_mppdb_group.node_quantity = new_group[0].request_node_quantity
                        current_tenant_mppdb_group.tenant_mppdb_members_list = new_group
                        new_tenant_mppdb_group_list.append(current_tenant_mppdb_group)
        # Create a new TenantMPPDBGroup for a new group if there is no current TenantMPPDBGroup available for it
        newly_created_tenant_mppdb_group_count = 1
        for new_group in new_group_list:
            if new_group not in [tenant_mppdb_group.tenant_mppdb_members_list for tenant_mppdb_group in
                                 new_tenant_mppdb_group_list]:
                new_tenant_mppdb_group_id = max([tenant_mppdb_group.tenant_mppdb_group_id for tenant_mppdb_group in
                                                 current_tenant_mppdb_group_list]) + newly_created_tenant_mppdb_group_count
                new_tenant_mppdb_group_list.append(
                    TenantMPPDBGroup(tenant_mppdb_group_id=new_tenant_mppdb_group_id, group_size=len(new_group),
                                     formation_time=None, node_quantity=new_group[0].request_node_quantity,
                                     flavor=new_group[0].flavor, tenant_mppdb_members_list=new_group))
                newly_created_tenant_mppdb_group_count += 1
        return new_tenant_mppdb_group_list
