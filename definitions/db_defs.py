# -*- coding: utf-8 -*-

import os

def latest_database_version():
    return '1.8.0'

def extra_datatables_sqlfile():
    """
    >>> os.path.isfile(extra_datatables_sqlfile())
    True
    """
    return os.path.join(os.path.dirname(__file__), 'create_db_extra_data_tables.sql')