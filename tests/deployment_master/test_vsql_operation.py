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

from common.db.db_util import SQLalchemyUtil
from common.models import MPPDB, User
from common.util.vertica_db_operations import get_schemas_by_tenant_mppdb_id, grant_schemas_to_user


class TestVSQLOperation(TestCase):

    def testListSchema(self):
        session = SQLalchemyUtil.get_session()
        mppdb = session.query(MPPDB).get("051366a1-a9d6-4984-82b6-8add5df7cb51")
        print get_schemas_by_tenant_mppdb_id(30, mppdb)
        session.close()

    def test_grant_schemas_to_user(self):
        session = SQLalchemyUtil.get_session()
        mppdb = session.query(MPPDB).get("051366a1-a9d6-4984-82b6-8add5df7cb51")
        users = session.query(User).filter(User.tenant_mppdb_id == 30)
        schemas = get_schemas_by_tenant_mppdb_id(30, mppdb)

        print "MPPDB: "+mppdb.mppdb_ip

        for user in users:
            grant_schemas_to_user(schemas=schemas, username=user.get_sql_username(), mppdb=mppdb)
        session.close
