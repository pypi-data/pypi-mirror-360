import time

from sthg_ontology_base.example.test_utils import session_factory,TGClient
from sthg_ontology_base import BaseModel
from sqlalchemy import and_, or_

def test_query():
    """测试查询功能"""

    api_name = 'business_events'
    ontology_api_name = 'ApiName.ontology.7a4569fa-cbfb-4cbf-ae8f-f343560a65c5'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    obj_name = getattr(client.ontology.objects, api_name)
    result = obj_name.where(or_(agg.id==164,agg.id==160)).group_by(agg.event_type).count().compute()
    print(result)


def test_common_query():
    api_name = 'agg,aggt'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg,aggt = client.models
    results = client.ontology.objects.join([agg, aggt], on_fields_list=[("ad_id", "ad_id")], join_types=["right"]).all()
    print(results)


def test_create():

    """测试创建功能"""
    print("\n测试创建记录:")
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)

    new_item = client.ontology.objects.agg.create(
        ad_id=101,
        clicks = 101
    )
    print(f"创建成功: RID={new_item.ad_id}")

#
def test_update():
    """测试更新功能"""
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    print("\n测试更新操作:")

    # 先创建测试数据
    test_item = client.ontology.objects.agg.create(
                ad_id=102,
                clicks = 102
    )

    # 执行更新
    updated_count = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).update(clicks=103)

    print(f"更新了 {updated_count} 条记录")

    # 验证更新
    result = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).first()
    print(f"更新后数据: {result.__dict__}")
#
#
def test_delete():
    """测试删除功能"""
    api_name = 'agg'
    ontology_api_name = 'ApiName.ontology.dea3d732-f033-45c2-9439-995d1656cdef'
    client = TGClient(api_name, ontology_api_name)
    agg = client.ontology.objects._model_classes.get(api_name)
    print("\n测试删除操作:")

    # 执行删除
    deleted_count = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).delete()

    print(f"删除了 {deleted_count} 条记录")

    # 验证删除
    result = client.ontology.objects.agg.where(
        agg.ad_id == 102
    ).first()
    print(f"删除后查询结果: {'存在' if result else '不存在'}")

#
# def test_bulk_create(session_factory):
#     """测试批量插入功能"""
#     client = FoundryClient(session_factory)
#     print("\n测试批量插入功能:")
#
#
#
#     new_item = client.ontology.objects.OntologyModelWrite.create(
#         rid="test_009",
#         api_name="test_api9",
#         display_name="测试模型39",
#         create_uid="tester9"
#     )
#
#     data_list = []
#
#     for i in range(1, 5):
#         item_dict = {
#             "rid": "test_bulk_create"+str(i),
#             "api_name": "test_bulk_create_api"+str(i),
#             "display_name": "批量模型模型",
#             "create_uid": "tester"
#         }
#         data_list.append(item_dict)
#
#     # 测试批量插入
#     test_item = new_item.bulk_create(
#         data_list
#     )
#
#     print(test_item)
#
#
# def test_batch_delete(session_factory):
#     """测试批量删除功能"""
#     client = FoundryClient(session_factory)
#     print("\n测试删除操作:")
#
#
#
#     # 执行删除
#     deleted_count = client.ontology.objects.OntologyModelWrite.where(
#         OntologyModelWrite.display_name == "批量模型模型"
#     ).delete()
#
#     print(f"删除了 {deleted_count} 条记录")
#
#
#
# def test_batch_update(session_factory):
#     """测试批量更新功能"""
#     client = FoundryClient(session_factory)
#     print("\n测试批量更新功能:")
#
#
#
#     # 测试批量更新功能
#     update_count = client.ontology.objects.OntologyModelWrite.where(
#         OntologyModelWrite.display_name == "批量模型模型"
#     ).update(display_name="已更新模型", new_filed="新增字段值")
#
#     print(f"更新了 {update_count} 条记录")
#


if __name__ == "__main__":


    # 执行测试套件
    BaseModel.set_session_factory(session_factory)
    test_common_query()
    #test_query()
    #test_bulk_create(session_factory)
    # test_batch_delete(session_factory)
    # test_batch_update(session_factory)
    #test_create()
    #test_update()
    #test_delete()

