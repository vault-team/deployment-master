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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from common import constant


class SQLalchemyUtil(object):
    engine = None
    Session = None

    @classmethod
    def init_engine(cls):
        cls.engine = create_engine('mysql+mysqlconnector://%s:%s@%s:%d/%s' % (
            constant.DB_USER, constant.DB_PASSWORD, constant.DB_HOST, constant.DB_PORT, constant.DB_SCHEMA),
                                   isolation_level="READ COMMITTED", poolclass=NullPool, connect_args={'time_zone': '+0:00'})

    @classmethod
    def get_session(cls):
        if cls.engine is None:
            cls.init_engine()
        cls.Session = sessionmaker(bind=cls.engine, autocommit=False, autoflush=False)
        session = cls.Session()
        return session

    @classmethod
    def close(cls):
        cls.engine.dispose()
        cls.engine = None
