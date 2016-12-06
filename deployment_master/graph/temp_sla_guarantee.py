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


from common import log
from common import constant
from common.dao import SlaGuaranteeDAO
from common.db.db_analyzer import DatabaseAnalyzer
from common.models import Performance, ConsolidationLog
from service_management_api.api import ExceptionResponse

LOG = log.getLogger(__name__)

class SlaGuarantee:


    def __init__(self):
        self.service_level_checker = DatabaseAnalyzer(DatabaseAnalyzer.DASHBOARD_SLA_GUARANTEE_GRAPH_UPDATING)

    def calculate_sla_guarantee(self, session):

        try:
            try:
                last_consolidation_time = (session.query(ConsolidationLog).order_by(ConsolidationLog.last_timestamp.desc()).first()).last_timestamp
                tenant_mppdb_group_activities = session.query(Performance).filter(Performance.time > last_consolidation_time).all()
            except:
                tenant_mppdb_group_activities = session.query(Performance).all()

            activity_dict = self.service_level_checker.get_sla_analysis_list(tenant_mppdb_group_activities)

            for key in activity_dict.keys():
                tenant_mppdb_group_id = key
                value = activity_dict[key][0]/float(activity_dict[key][1]) * 100
                # update the TempSlaGuarantee table in the backend database
                SlaGuaranteeDAO.update_temp_sla_guarantee_table(session, self.service_level_checker.analysis_end_time, tenant_mppdb_group_id, value)

        except Exception as e:
            LOG.exception(e)
            raise ExceptionResponse(e)
        finally:
            session.close()

