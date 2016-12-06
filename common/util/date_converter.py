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

import time

from datetime import datetime

class DateConverter():

    @staticmethod
    def local_datetime_to_gmt_datetime(datetime):
        linux_timestamp = int(time.mktime(datetime.timetuple()))
        gmt_datetime = DateConverter.linux_timestamp_to_gmt_datetime(linux_timestamp)
        return gmt_datetime

    @staticmethod
    def linux_timestamp_to_gmt_datetime(linux_timestamp):
        gmt_datetimestamp = time.gmtime(linux_timestamp)
        gmt_datetime = datetime.fromtimestamp(time.mktime(gmt_datetimestamp))
        return gmt_datetime

    @staticmethod
    def datetime_to_linux_timestamp(datetime):
        datetime_to_linux_timestamp = int(time.mktime((datetime).timetuple()))
        return datetime_to_linux_timestamp