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

from datetime import datetime, timedelta

import math

from common import constant
from common.constant import SERVICE_LEVEL_CHECKING_PERIOD, CONSOLIDATION_PERIOD
from common.models import Performance, SlaGuarantee, TenantMPPDBActivity
from common.util.date_converter import DateConverter
from deployment_master.tenant_activity_analyzer import *


class DatabaseAnalyzer(object):
    CONSOLIDATION = 'consolidation'
    SERVICE_LEVEL_CHECKING = 'service_level_checking'
    DASHBOARD_PERFORMANCE_GRAPH_UPDATING = 'dashboard_performance_graph_updating'
    DASHBOARD_SLA_GUARANTEE_GRAPH_UPDATING = 'dashaboard_sla_guarantee_graph_updating'
    DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_UPDATING = 'dashboard_tenant_mppdb_activity_graph_updating'

    """
    Collect and analyze data from database.
    Consolidate and store all info in tenant_mppdb_list and current_tenant_mppdb_group_list.
    tenant_mppdb_list: a list of TenantMPPDB objects.
    current_tenant_mppdb_group_list: a list of TenantMPPDBGroup objects.
    """

    def __init__(self, analysis_type):
        self.session = SQLalchemyUtil.get_session()
        self.analysis_type = analysis_type
        self.total_epochs = 0
        self.analysis_start_time = None
        self.analysis_end_time = None



    def close_db_connection(self):
        self.session.close()

    def get_tenant_mppdb_list(self):
        self.get_start_end_time()
        tenant_mppdb_list = get_tenant_mppdb_list_in_certain_period(self.session, self.analysis_start_time, self.analysis_end_time)
        return tenant_mppdb_list

    def get_tenant_mppdb_list_in_dashboard(self):
        self.get_start_end_time()
        tenant_mppdb_list = get_tenant_mppdb_list_in_one_epoch(self.session, self.analysis_start_time, self.analysis_end_time)
        return tenant_mppdb_list

    def get_sla_analysis_list(self, tenant_mppdb_group_activities):
        self.get_start_end_time()
        activity_dict = {}

        for performance in tenant_mppdb_group_activities:
            # activity_dict[performance.tenant_mppdb_group_id][0]: number of epochs which performance is 1
            # activity_dict[performance.tenant_mppdb_group_id][0]: total number of epochs
            if performance.value == 1:
                if performance.tenant_mppdb_group_id in activity_dict:
                    activity_dict[performance.tenant_mppdb_group_id][0] += 1
                    activity_dict[performance.tenant_mppdb_group_id][1] += 1
                else:
                    activity_dict[performance.tenant_mppdb_group_id] = [1, 1]
            else:
                if performance.tenant_mppdb_group_id in activity_dict:
                    activity_dict[performance.tenant_mppdb_group_id][0] += 0
                    activity_dict[performance.tenant_mppdb_group_id][1] += 1
                else:
                    activity_dict[performance.tenant_mppdb_group_id] = [0, 1]

        return activity_dict

    def get_current_tenant_mppdb_group_list(self):
        """Return a list of TenantMPPDBGroup objects."""
        tenant_mppdb_list = self.get_tenant_mppdb_list()
        current_tenant_mppdb_group_list = identify_tenant_mppdb_group_for_tenant(self.session, tenant_mppdb_list)
        return current_tenant_mppdb_group_list

    def get_current_tenant_mppdb_group_list_in_dashboard(self):
        tenant_mppdb_list = self.get_tenant_mppdb_list_in_dashboard()
        current_tenant_mppdb_group_list = identify_tenant_mppdb_group_for_tenant(self.session, tenant_mppdb_list)
        return current_tenant_mppdb_group_list

    def get_mppdb(self, tenant_mppdb_group_id):
        mppdb_list = self.session.query(MPPDB).filter(MPPDB.tenant_mppdb_group_id==tenant_mppdb_group_id).all()
        return mppdb_list

    def get_start_end_time(self):

        if self.analysis_type == self.CONSOLIDATION:
            try:
                self.total_epochs = int(math.ceil(CONSOLIDATION_PERIOD.total_seconds() / EPOCH_SIZE.total_seconds()))
                self.analysis_end_time = (self.session.query(TenantMPPDBActivity).order_by(TenantMPPDBActivity.time.desc()).first()).time
                self.analysis_start_time = self.analysis_end_time - CONSOLIDATION_PERIOD
            except:
                self.analysis_end_time = DateConverter.local_datetime_to_gmt_datetime(datetime.now())
                self.analysis_start_time = self.analysis_end_time - timedelta(seconds=CONSOLIDATION_PERIOD.total_seconds())


        elif self.analysis_type == self.SERVICE_LEVEL_CHECKING:
            try:
                self.total_epochs = int(math.ceil(SERVICE_LEVEL_CHECKING_PERIOD.total_seconds() / EPOCH_SIZE.total_seconds()))
                self.analysis_end_time = (self.session.query(TenantMPPDBActivity).order_by(TenantMPPDBActivity.time.desc()).first()).time
                self.analysis_start_time = self.analysis_end_time - SERVICE_LEVEL_CHECKING_PERIOD
            except:
                self.analysis_end_time = DateConverter.local_datetime_to_gmt_datetime(datetime.now())
                self.analysis_start_time = self.analysis_end_time - timedelta(
                    seconds=SERVICE_LEVEL_CHECKING_PERIOD)

        elif self.analysis_type == self.DASHBOARD_PERFORMANCE_GRAPH_UPDATING:
            try:
                self.analysis_start_time = (self.session.query(Performance).order_by(Performance.time.desc()).first()).time
                self.analysis_end_time = self.analysis_start_time + timedelta(seconds=constant.DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND)
            except:
                self.analysis_end_time = DateConverter.local_datetime_to_gmt_datetime(datetime.now())
                self.analysis_start_time = self.analysis_end_time - timedelta(seconds=constant.DASHBOARD_PERFORMANCE_GRAPH_INTERVAL_IN_SECOND)

        elif self.analysis_type == self.DASHBOARD_SLA_GUARANTEE_GRAPH_UPDATING:
            try:
                self.analysis_start_time = (self.session.query(SlaGuarantee).order_by(SlaGuarantee.time.desc()).first()).time
                self.analysis_end_time = self.analysis_start_time + timedelta(seconds=constant.DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND)
            except:
                self.analysis_end_time = DateConverter.local_datetime_to_gmt_datetime(datetime.now())
                self.analysis_start_time = self.analysis_end_time - timedelta(seconds=constant.DASHBOARD_SLA_GUARANTEE_GRAPH_INTERVAL_IN_SECOND)

        elif self.analysis_type == self.DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_UPDATING:
            try:
                self.analysis_start_time = (self.session.query(TenantMPPDBActivity).order_by(TenantMPPDBActivity.time.desc()).first()).time
                self.analysis_end_time = self.analysis_start_time + timedelta(seconds=constant.DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND)
            except:
                self.analysis_end_time = DateConverter.local_datetime_to_gmt_datetime(datetime.now())
                self.analysis_start_time = self.analysis_end_time - timedelta(seconds=constant.DASHBOARD_TENANT_MPPDB_ACTIVITY_GRAPH_INTERVAL_IN_SECOND)

