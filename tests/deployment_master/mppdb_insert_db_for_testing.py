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

import MySQLdb


class TestingUtil(object):
    @classmethod
    def insertMPPDB(cls, test_case):
        connection = MySQLdb.connect(user='vault', passwd='vault', host='192.168.1.138', db='vault')
        cur = connection.cursor()

        if test_case == 1:
            cur.execute(
            """INSERT INTO MPPDB VALUES ('530807a9-d428-4d69-83b2-9fad30189d7b','192.168.1.203','-1',''),('aff1849f-6cc8-491c-aca5-8e6ef97cf075','192.168.1.226','-1',''),('dd669e86-2593-4d7b-b515-52a043824b3a','192.168.1.218','4','');""")

        elif test_case == 2:
            cur.execute(
                """INSERT INTO MPPDB VALUES ('26211c60-c617-4132-9df9-cd40b307caca','192.168.1.205','-1',''),('530807a9-d428-4d69-83b2-9fad30189d7b','192.168.1.203','-1',''),('aff1849f-6cc8-491c-aca5-8e6ef97cf075','192.168.1.226','-1','');""")

        connection.commit()
        cur.close()
