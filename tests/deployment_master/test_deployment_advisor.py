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

from unittest import TestCase

from deployment_master.deployment_advisor import DeploymentAdvisor
import test_deploymentmaster_reset


#######################################Unit Test 1#####################################

##########################################Aim##########################################
# To check whether the deployment advisor can get the current_tenant_mppdb_group_list
# and new_tenant_mppdb_group_list from the backend-database
######################################Prerequisite#####################################
# 1. Create a cluster (192.168.10.144) for data transferring to other user in different cluster (prepare other user's data)
# 2. Upload the sample.txt file to the cluster in step 1
# 3. Create the schema and table in cluster in step 1
#   =>create schema tm9_default(by default when creating the cluster);
#   =>create table tm9_default.Market(Date Date, Name varchar(64), PTID integer, LBMP numeric, Marginal_cost_losses numeric, Marginal_cost_congestion integer);
# 4. Load the data from text file to the table
#   =>copy sample.sample from local '/home/ubuntu/sample.txt' delimiter E'\t' skip 1;
# 5. Modify the test_deployment_reset.py
#   The part needed to be modified is signified by "modify this section"
#   The details is specified in Lili's Development Notes Section 11.2
#####################################Expected Output###################################
# The backend-database contains the MPPDB, TenantMPPDB, TenantMPPDBGroup and User records
# If the deploment advisor can run properly, it can form the current and new tennat mppdb group lists
#######################################################################################


class DeploymentAdvisorTests(TestCase):
    def test_deployment_advisor(self):
        test_deploymentmaster_reset.reset()
        da = DeploymentAdvisor()
        new_tenant_mppdb_group_list = da.generate_deployment_plan()
        print new_tenant_mppdb_group_list
