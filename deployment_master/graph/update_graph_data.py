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

from common.db.db_analyzer import DatabaseAnalyzer
from common.db.db_util import SQLalchemyUtil
from deployment_master.graph.temp_performance import Performance
from deployment_master.graph.temp_sla_guarantee import SlaGuarantee
from deployment_master.graph.temp_tenant_mppdb_activity import TenantMPPDBActivity


class UpdateGraphData():

    logger = logging.getLogger("UpdateGraphData")

    def __init__(self):
        self.logger.info('UpdateGraphData')
        self.session = None
        self.performance_monitor = Performance()
        self.sla_guarantee_monitor = SlaGuarantee()
        self.tenant_mppdb_activity_monitor = TenantMPPDBActivity()


    def __call__(self):
        self.logger.info('Start to update graph data.')
        try:
            self.session = SQLalchemyUtil.get_session()
            self.performance_monitor.calculate_performance(self.session)
            self.sla_guarantee_monitor.calculate_sla_guarantee(self.session)
            self.tenant_mppdb_activity_monitor.calculate_tenant_mppdb_activity(self.session)
        except:
            self.session.rollback()
            raise


