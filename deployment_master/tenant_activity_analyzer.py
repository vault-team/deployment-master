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

from common.constant import REPLICATON_FACTOR, EPOCH_SIZE
from common.string_constant import QueryLogStatus_FAILURE
from common.db.db_util import SQLalchemyUtil
from common.models import MPPDB, TenantMPPDB, TenantMPPDBGroup, User


def get_tenant_mppdb_list_in_certain_period(session, analysis_start_time, analysis_end_time):
    """
    Read data about TenantMPPDB, User, and Query from database either in the consolidation or service level checking cycle period.
    Analyze TenantMPPDBs' individual query status on each epoch.
    Return a list of TenantMPPDB object.
    """
    tenant_mppdb_list = session.query(TenantMPPDB).all()
    for tenant_mppdb in tenant_mppdb_list:
        cmd = "Select value from TempTenantMPPDBActivity where TempTenantMPPDBActivity.tenant_mppdb_id=" + str(tenant_mppdb.tenant_mppdb_id) + " and TempTenantMPPDBActivity.time > '" + str(analysis_start_time) + "' and TempTenantMPPDBActivity.time <='" + str(analysis_end_time) + "' group by TempTenantMPPDBActivity.time"
        resultset = session.execute(cmd)

        query_status_list = []
        for value in resultset:
            if value[0] == 0:
                query_status_list.append(0)
            else:
                query_status_list.append(1)

        tenant_mppdb.query_status_list = query_status_list

        if len(query_status_list) != 0:
            tenant_mppdb.active_ratio = float(query_status_list.count(1)) / float(len(query_status_list))
        else:
            tenant_mppdb.active_ratio = 0
        tenant_mppdb.user_list = session.query(User).filter(User.tenant_mppdb_id == tenant_mppdb.tenant_mppdb_id).all()
    return tenant_mppdb_list

def get_tenant_mppdb_list_in_one_epoch(session, analysis_start_time, analysis_end_time):
    try:
        tenant_mppdb_list = session.query(TenantMPPDB).all()

        session = SQLalchemyUtil.get_session()

        analysis_start_time_str = str(analysis_start_time)
        analysis_end_time_str = str(analysis_end_time)

        cmd = "Select Query.tenant_mppdb_id, count(Query.tenant_mppdb_id) from Query where (Query.query_body regexp '[[:blank:]]*create[[:blank:]]+table.*select' or Query.query_body regexp '[[:blank:]]*select')" \
              "and ((Query.start_time > '" + analysis_start_time_str + "' and Query.start_time <= '" + analysis_end_time_str + "') or Query.end_time = null) and Query.query_status != '"+ QueryLogStatus_FAILURE +"' group by Query.tenant_mppdb_id"

        resultset = session.execute(cmd)

        #Initiate the query_status_list
        for tenant_mppdb in tenant_mppdb_list:
            tenant_mppdb.query_status_list = [0]


        for result in resultset:
            for tenant_mppdb in tenant_mppdb_list:
                if tenant_mppdb.tenant_mppdb_id == result[0]:
                    tenant_mppdb.query_status_list = [1]


        return tenant_mppdb_list
    except Exception as e:
        logging.exception("Fail to get_tenant_mppdb_list_in_one_epoch")
        raise e

def identify_tenant_mppdb_group_for_tenant(session, tenant_mppdb_list):
    """Find out TenantMPPDBGroups for TenantMPPDBs"""
    current_tenant_mppdb_group_list = session.query(TenantMPPDBGroup).all()
    for current_tenant_mppdb_group in current_tenant_mppdb_group_list:
        matching_tenant_mppdbs = []
        for tenant_mppdb in tenant_mppdb_list:
            if current_tenant_mppdb_group.tenant_mppdb_group_id == tenant_mppdb.tenant_mppdb_group_id:
                matching_tenant_mppdbs.append(tenant_mppdb)
        current_tenant_mppdb_group.tenant_mppdb_members_list = matching_tenant_mppdbs
        current_tenant_mppdb_group.mppdb_list = session.query(MPPDB).filter(
            MPPDB.tenant_mppdb_group_id == current_tenant_mppdb_group.tenant_mppdb_group_id).all()
    return current_tenant_mppdb_group_list


def calculate_overlap_info(tenant_mppdb_set, total_epochs):
    """Calculate overlap info of query status of TenantMPPDBs"""
    active_tenant_mppdbs_count_at_each_epoch = {}
    for epoch in range(total_epochs):
        active_tenant_mppdbs_count_at_each_epoch[epoch] = 0
        for tenant_mppdb in tenant_mppdb_set:
            if tenant_mppdb.query_status_list[epoch] == 1:
                active_tenant_mppdbs_count_at_each_epoch[epoch] += 1
    return active_tenant_mppdbs_count_at_each_epoch

def calculate_active_tenant_mppdbs_count_in_one_epoch(tenant_mppdb_set):
    active_tenant_mppdbs_count_at_each_epoch = 0
    for tenant_mppdb in tenant_mppdb_set:
        if tenant_mppdb.query_status_list[0] == 1:
            active_tenant_mppdbs_count_at_each_epoch += 1
    return active_tenant_mppdbs_count_at_each_epoch

def look_for_best_tenant_mppdb(existing_tenant_mppdbs, candidate_tenant_mppdbs, total_epochs):
    """Find out the best TenantMPPDB that can be put in a group"""
    candidate_tenant_mppdb_overlap_info = {}
    for candidate in candidate_tenant_mppdbs:
        active_tenant_mppdbs_count_at_each_epoch = calculate_overlap_info(existing_tenant_mppdbs + [candidate],
                                                                          total_epochs)
        maximum_active_tenant_mppdbs_no = active_tenant_mppdbs_count_at_each_epoch[
            max(active_tenant_mppdbs_count_at_each_epoch, key=lambda i: active_tenant_mppdbs_count_at_each_epoch[i])]
        time_percentage_with_maximum_active_tenant_mppdbs = float(
            active_tenant_mppdbs_count_at_each_epoch.values().count(maximum_active_tenant_mppdbs_no)) / float(
            total_epochs)
        candidate_tenant_mppdb_overlap_info[candidate] = [maximum_active_tenant_mppdbs_no,
                                                          time_percentage_with_maximum_active_tenant_mppdbs]
    min_maximum_active_tenant_mppdbs_no = min(
        [overlap_info[0] for overlap_info in candidate_tenant_mppdb_overlap_info.values()])
    better_candidate = {}
    for candidate in candidate_tenant_mppdb_overlap_info.keys():
        if candidate_tenant_mppdb_overlap_info[candidate][0] == min_maximum_active_tenant_mppdbs_no:
            better_candidate[candidate] = candidate_tenant_mppdb_overlap_info[candidate]
    min_time_percentage_with_maximum_active_tenant_mppdbs = min(
        [overlap_info[1] for overlap_info in better_candidate.values()])
    best_candidate = {}
    if len(existing_tenant_mppdbs) != 0:
        for candidate, overlap_info in better_candidate.items():
            if overlap_info[1] == min_time_percentage_with_maximum_active_tenant_mppdbs:
                for tenant_mppdb in existing_tenant_mppdbs:
                    if candidate.tenant_mppdb_group_id == tenant_mppdb.tenant_mppdb_group_id:
                        best_candidate[candidate] = best_candidate.get(candidate, 0) + 1
                    else:
                        best_candidate[candidate] = 0
        best_tenant_mppdb = max(best_candidate, key=best_candidate.get)
    else:
        for candidate, overlap_info in better_candidate.items():
            if overlap_info[1] == min_time_percentage_with_maximum_active_tenant_mppdbs:
                best_tenant_mppdb = candidate
    return best_tenant_mppdb


def check_service_level(tenant_mppdb_set, total_epochs, quota=REPLICATON_FACTOR):
    """Check service level."""
    active_tenant_mppdbs_count_at_each_epoch = calculate_overlap_info(tenant_mppdb_set, total_epochs)
    good_epochs_count = 0
    for active_tenant_mppdbs_count in active_tenant_mppdbs_count_at_each_epoch.values():
        if active_tenant_mppdbs_count <= quota:
            good_epochs_count += 1
    service_level = float(good_epochs_count) / float(total_epochs)
    return service_level

def check_service_level_in_one_epoch(tenant_mppdb_set, quota=REPLICATON_FACTOR):
    active_tenant_mppdbs_count_in_one_epoch = calculate_active_tenant_mppdbs_count_in_one_epoch(tenant_mppdb_set)