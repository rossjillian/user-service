"""

RDSDataTable class that inherits from BaseDataTable
Contributors: Derek Wacks, Jillian Ross, Donald Ferguson
Advisor: Professor Ferguson, Columbia University

"""

from data_access.BaseDataTable import BaseDataTable, DataTableException
import os
import pymysql
import json
import uuid
import logging
import data_access.dbutils as dbutils
import setcredentials as sc
logger = logging.getLogger()


class RDSDataTable(BaseDataTable):
    def __init__(self, table_name, connect_info=None, key_columns=None, context=None):
        self._table_name = table_name
        self._key_columns = key_columns

        if connect_info is not None:
            self._connect_info = connect_info

        # super().__init__()

        sc.setCred()
        db_user = os.environ.get('DB_USER')
        db_pw = os.environ.get('DB_PW')
        db_host = os.environ.get('DB_HOST')

        self.conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pw,
            db="user_service",  # "user_service",user-rdb  # Reminder that this db name is hard-coded
            cursorclass=pymysql.cursors.DictCursor)

        self.cur = self.conn.cursor()

    def find_by_primary_key(self, key_fields, field_list=None, context=None):
        """
        :param key_fields: The values for the key_columns
        :param field_list: A subset of the fields of records
        :return: None, or dictionary containing columns/values for the row
        """
        kf = {
            self._key_columns : key_fields
        }
        response = self.find_by_template(kf, field_list)
        if response is not None and len(response)>0:
            response = response[0]
        else:
            response = None
        return response

    def find_by_template(self, template, field_list=None, limit=None, offset=None, order_by=None, context=None):
        """
        :param template: dictionary of the form { "field1" : value1, "field2": value2, ...}
        :param field_list: list of requested fields of the form, ['fielda', 'fieldb', ...]
        :return: A derived table containing the computed rows.
        """
        try:
            sql, args = dbutils.create_select(self._table_name, template=template, fields=field_list)
            res, data = dbutils.run_q(sql=sql, args=args, cur=self.cur, conn=self.conn, commit=True, fetch=True)
        except Exception as e:
            print("Exception e = ", e)
            raise e
        return list(data)

    def insert(self, new_entity, context=None):
        """
        :param new_record: A dictionary representing a row to add to the set of records. Raises an exception if this
            creates a duplicate primary key.
        :return: None
        """
        override_uuid = uuid.uuid1().hex
        new_entity['id'] = override_uuid
        sql, args = dbutils.create_insert(self._table_name, new_entity)
        print(sql, "\n")
        res, d = dbutils.run_q(sql, args=args, conn=self.conn)
        return res, override_uuid

    def delete_by_template(self, template, context=None):
        """
        Deletes all records that match the template.
        :param template: A template.
        :return: A count of the rows deleted.
        """
        try:
            sql, args = dbutils.create_select(self._table_name, template=template, is_select=False)
            res, d = dbutils.run_q(sql, args=args, conn=self.conn, commit=True)
            return res
        except Exception as e:
            print("Got exception e = ", e)
            raise e

    def delete_by_key(self, key_fields, Context=None):
        """
        Delete record with corresponding key.
        :param key_fields: List containing the values for the key columns
        :return: A count of the rows deleted.
        """
        template = {
            self._key_columns: key_fields
        }
        # Call delete_by_template (which calls find_by_template).
        result = self.delete_by_template(template)
        return result

    def update_by_template(self, template, new_values, context=None):
        """
        :param template: A template that defines which matching rows to update.
        :param new_values: A dictionary containing fields and the values to set for the corresponding fields
            in the records. This returns an error if the update would create a duplicate primary key. NO ROWS are
            update on this error.
        :return: The number of rows updates.
        """
        sql, args = dbutils.create_update(self._table_name, template=template, changed_cols=new_values)
        res, d = dbutils.run_q(sql, args=args, conn=self.conn, commit=True)
        return res

    def update_by_key(self, key_fields, new_values, context=None):
        """
        :param key_fields: List of values for primary key fields
        :param new_values: A dictionary containing fields and the values to set for the corresponding fields
            in the records. This returns an error if the update would create a duplicate primary key. NO ROWS are
            update on this error.
        :return: The number of rows updates.
        """
        template = {
            self._key_columns : key_fields
        }
        res = self.update_by_template(template=template, new_values=new_values)
        return res

    def query(self, query_statement, args, context=None):
        """
        Passed through/executes a raw query in the native implementation language of the backend.
        :param query_statement: Query statement as a string.
        :param args: Args to insert into query if it is a template
        :param context:
        :return: A JSON object containing the result of the operation.
        """
        pass

    def load(self, rows=None):
        """
        Loads data into the data table.
        :param rows:
        :return: Number of rows loaded.
        """
        pass

    def save(self, context):
        """
        Writes any cached data to a backing store.
        :param context:
        :return:
        """
        pass

    def get_count(self, table_name=None, column=None, value_count=None):
        sql = 'select count(*)'
        if table_name:
            sql += (' from %s' % table_name)
        if value_count:
            sql += (" where %s = '%s'" % (column, value_count))
        res, data = dbutils.run_q(sql=sql, conn=self.conn)
        return data[0]['count(*)']


