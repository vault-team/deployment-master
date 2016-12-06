__author__ = 'chrisliu'


class Action(object):
    """
    Provide actions involved in the migration process.
        create_mppdb: create a new MPPDB
        copy_mppdb: create a new MPPDB and copy data from another MPPDB which belongs to the same TenantMPPDGroup
        move_tenant_mppdb_data: move a TenantMPPDB's data
        update_tenant_mppdb_group_in_db: update the backend database with new TenantMPPDBGroups info
        delete_tenant_mppdb_data: delete a TenantMPPDB's data if it has been migrated to another one
        delete_mppdb: delete a MPPDB if it is not used any more
    """

    def __repr__(self):
        return "<Action()>" % ()

    # abstract function for migration plan execution
    def run(self):
        pass

    # Equal operator should be implement by each Action
    def __eq__(self, other):
        return False
