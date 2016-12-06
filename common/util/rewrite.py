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

def rewrite_user_name(tenant_mppdb_id, user_name):
    """
    Rewrite mppdb username to "tm{id}_{username}"
    Tested
    :param tenant_mppdb_id:
    :param user_name:
    :return:
    """
    return "tm%d_%s" % (tenant_mppdb_id, user_name)


def rewrite_schema_name(tenant_mppdb_id, schema_name):
    """
    Rewrite mppdb schema to "tm{id}_{username}"\
    Tested
    :param tenant_mppdb_id:
    :param schema_name:
    :return:
    """
    return "tm%d_%s" % (tenant_mppdb_id, schema_name)
