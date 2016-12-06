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

import random

from datetime import datetime
from datetime import timedelta

# generate query records used to insert into Query table

insert_command = """INSERT INTO Query VALUES """
tenant_mppdb_list = [1, 2, 3, 4, 5, 6]

current_time = datetime.now()
for i in range(99):
    year = current_time.year
    month = current_time.month
    day = random.randint(12, 15)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    start_time = datetime(year, month, day, hour, minute, second)
    diff = random.randint(0, 10)
    end_time = start_time + timedelta(seconds=diff)
    tenant_mppdb_id = random.choice(tenant_mppdb_list)
    if tenant_mppdb_id == 1:
        user_id = 2
        mppdb_id = '8a1eff86-ec29-4471-8400-a405b0847700'
    elif tenant_mppdb_id == 2:
        user_id = random.randint(1, 3)
        mppdb_id = 'f63af4da-cd7e-4569-a9af-11662ab4c259'
    elif tenant_mppdb_id == 3:
        user_id = 4
        mppdb_id = '8a1eff86-ec29-4471-8400-a405b0847700'
    elif tenant_mppdb_id == 4:
        user_id = 5
        mppdb_id = '48d1aa2a-835d-4997-9ee4-c72f279be259'
    elif tenant_mppdb_id == 5:
        user_id = 7
        mppdb_id = 'f63af4da-cd7e-4569-a9af-11662ab4c259'
    elif tenant_mppdb_id == 6:
        user_id = 5
        mppdb_id = '8a1eff86-ec29-4471-8400-a405b0847700'
    insert_command += """(%s, '%s', '%s', NULL, NULL, %s, %s, NULL, '%s', NULL), """ % (
        i + 1, start_time, end_time, user_id, tenant_mppdb_id, mppdb_id)

insert_command = insert_command[:-2]
insert_command += ';'
print insert_command
