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

from common.models import TenantMPPDBGroup
from deployment_master.action import Action


class TenantMPPDBGroupCreation(Action):
    def __init__(self, newly_created_tenant_mppdb_group):
        self.newly_created_tenant_mppdb_group = newly_created_tenant_mppdb_group

    def run(self, session):
        new_tenant_mppdb_group = TenantMPPDBGroup(group_size=0,
                                                  node_quantity=self.newly_created_tenant_mppdb_group.node_quantity,
                                                  flavor=self.newly_created_tenant_mppdb_group.flavor)
        session.add(new_tenant_mppdb_group)
        session.commit()


    def __eq__(self, other):
        if isinstance(other,
                      TenantMPPDBGroupCreation) and self.newly_created_tenant_mppdb_group.node_quantity == other.newly_created_tenant_mppdb_group.node_quantity:
            return True
        else:
            return False
