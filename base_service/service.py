from data_access.RDSDataTable import RDSDataTable
from utilities.restutils import paginated_rsp, pagination_support


class BaseService:
    def __init__(self, table_name, key_columns=None):
        self._table_name = table_name
        self._data_table = RDSDataTable(self._table_name, key_columns=key_columns)

    def get_all(self, query_params, fields, req_info):
        offset, limit = pagination_support(query_params)
        rsp_data = self._data_table.find_by_template(None, field_list=fields, offset=offset, limit=limit)
        data = rsp_data
        if offset and limit:
            rsp_data = paginated_rsp(self._data_table, req_info, rsp_data, offset, limit)
            data = rsp_data['data']

        rsp_data_and_links = {"data": data}
        if offset and limit:
            rsp_data_and_links['pagination'] = rsp_data['pagination']
        return rsp_data_and_links

    def get_by_id(self, fields, query_id):
        rsp_data = self._data_table.find_by_primary_key(query_id, field_list=fields)
        rsp_data_and_links = {"data": rsp_data}
        return rsp_data_and_links

