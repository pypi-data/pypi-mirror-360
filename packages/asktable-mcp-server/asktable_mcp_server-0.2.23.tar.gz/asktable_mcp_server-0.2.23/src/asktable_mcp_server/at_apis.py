from asktable import Asktable
import logging

async def get_asktable_answer(
    api_key, datasource_id, question, base_url=None, role_id: str=None, role_variables: dict = None
) -> dict:
    """
    获取asktable数据
    :param api_key:
    :param datasource_id:
    :param question:
    :param base_url:
    :param role_id:
    :param role_variables:
    :return:
    """

    asktable_client = Asktable(api_key=api_key, base_url=base_url)
    logging.info(f"api_key: {api_key}")
    logging.info(f"base_url: {base_url}")
    answer_response = asktable_client.answers.create(
        datasource_id=datasource_id, 
        question=question, 
        role_id=role_id,
        role_variables=role_variables
    )
    return {
        "status": "success" if answer_response.answer else "failure",
        "data": answer_response.answer.text if answer_response.answer else None
    }


async def get_asktable_sql(
    api_key, datasource_id, question, base_url=None, role_id: str=None, role_variables: dict = None
) -> dict:

    asktable_client = Asktable(api_key=api_key, base_url=base_url)
    query_response = asktable_client.sqls.create(
        datasource_id=datasource_id, 
        question=question, 
        role_id=role_id,
        role_variables=role_variables
    )
    return {
        "status": "success" if query_response.query else "failure",
        "data": query_response.query.sql if query_response.query else None
    }


