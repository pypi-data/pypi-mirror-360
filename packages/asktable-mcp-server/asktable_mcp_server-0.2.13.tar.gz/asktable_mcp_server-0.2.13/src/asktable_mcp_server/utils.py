import json
from asktable import Asktable

class AskTableHelper:
    def __init__(self, api_key, base_url=None):
        self.asktable_client = Asktable(base_url=base_url, api_key=api_key)

    def get_datasource_ids_by_role(self, role_id):
        """
        根据 role_id 获取该角色下所有 policy 涉及的 datasource_id 列表
        :param role_id: 角色ID
        :return: list, 包含所有 datasource_id
        """
        role_source = self.asktable_client.roles.get_polices(role_id=role_id)
        datasource_ids = set()
        for policy in role_source:
            if hasattr(policy, 'dataset_config') and hasattr(policy.dataset_config, 'datasource_ids'):
                datasource_ids.update(policy.dataset_config.datasource_ids)
        return list(datasource_ids)

    def get_role_name_by_role(self, role_id):
        """
        根据 role_id 获取角色名称
        :param role_id: 角色ID
        :return: 角色名称字符串
        """
        role_source = self.asktable_client.roles.retrieve(role_id=role_id)
        return role_source.name

    def get_datasources_info(self):
        """
        返回当前 API KEY 下所有数据库 meta data
        :return: dict, {status, data}
        """
        meta_data_list = self.asktable_client.datasources.list()
        if not meta_data_list.items:
            return {
                "status": "failure",
                "data": "该用户还没有创建任何数据库"
            }
        result = [
            {
                "datasource_id": ds.id,
                "数据库引擎": ds.engine,
                "数据库描述": ds.desc,
            }
            for ds in meta_data_list.items
        ]
        return {
            "status": "success",
            "data": json.dumps(result, ensure_ascii=False, indent=2)
        }

    def get_datasources_info_by_role(self, role_id):
        """
        输入 role_id，返回该角色可访问的数据源的描述、引擎和id
        :param role_id: 角色ID
        :return: dict, {status, data}
        """
        # 1. 获取所有数据源
        meta_data_list = self.asktable_client.datasources.list()
        if not meta_data_list.items:
            return {
                "status": "failure",
                "data": "该用户还没有创建任何数据库"
            }

        # 2. 获取该角色可访问的数据源ID
        datasource_ids = set(self.get_datasource_ids_by_role(role_id))

        # 3. 只保留属于该 role 的数据源
        result = [
            {
                "datasource_id": ds.id,
                "数据库引擎": ds.engine,
                "数据库描述": ds.desc,
            }
            for ds in meta_data_list.items if ds.id in datasource_ids
        ]

        if not result:
            return {
                "status": "failure",
                "data": "该角色没有可访问的数据库"
            }

        return {
            "status": "success",
            "data": json.dumps(result, ensure_ascii=False, indent=2)
        }