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

from common.models import MigrationJob
from deployment_master.action.mppdb_creation import MPPDBCreation
from deployment_master.action.tenant_mppdb_group_creation import TenantMPPDBGroupCreation


class MigrationPlan(object):
    def __init__(self, action_list):
        self.actions = []
        self.actions += action_list

    def getActions(self):
        return self.actions

    # Function to get all creation actions
    def getMppdbCreations(self):
        ret = []
        for action in self.actions:
            if isinstance(action, MPPDBCreation):
                ret.append(action)
        return ret

    def getCopyAndMoveMPPDBAction(self):
        ret = []
        for action in self.actions:
            if isinstance(action, MigrationJob):
                ret.append(action)
        return ret

    def getTenantMppdbGroupCreations(self):
        ret = []
        for action in self.actions:
            if isinstance(action, TenantMPPDBGroupCreation):
                ret.append(action)
        return ret

    def __eq__(self, other):
        found_list = []
        unfound_list = []

        if (len(self.actions) != len(self.actions)):
            return False

        for item in self.actions:
            for compare_item in other.actions:
                found_flag = False
                if item == compare_item:
                    found_list.append(item)
                    found_flag = True
                    break
            if not found_flag:
                unfound_list.append(item)

        if len(found_list) == len(self.actions):
            return True
        else:
            return False
