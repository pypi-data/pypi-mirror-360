import pytest

from ey_commerce_lib.dxm.constant.order import ORDER_SEARCH_APPROVAL_BASE_FORM, \
    ORDER_SEARCH_PENDING_PROCESSING_BASE_FORM, ORDER_SEARCH_SELF_WAREHOUSE_BASE_FORM, \
    ORDER_SEARCH_OUT_OF_STOCK_BASE_FORM
from ey_commerce_lib.dxm.main import DxmClient
from ey_commerce_lib.dxm.schemas.warehouse import WarehouseProductQuery
from ey_commerce_lib.dxm.utils.mark import get_custom_mark_content_list_by_data_custom_mark, \
    generate_add_or_update_user_comment_data_by_content_list
from ey_commerce_lib.four_seller.main import FourSellerClient
from ey_commerce_lib.four_seller.schemas.query.order import FourSellerOrderQueryModel


async def login_success(user_token: str):
    print(f'user_token: {user_token}')
    pass


@pytest.mark.asyncio
async def test_auto_login_4seller():
    # user_token = await auto_login_4seller(user_name="sky@eeyoung.com", password="ey010203@@")
    # print(user_token)
    async with FourSellerClient(
            user_name="xxxxx",
            password="xxxxxx",
            login_success_call_back=login_success,
            user_token="xxxxxx") as four_seller_client:
        await four_seller_client.list_history_order(FourSellerOrderQueryModel())


cookies = {

}

headers = {

}


@pytest.mark.asyncio
async def test_dxm_api():
    async with (DxmClient(headers=headers, cookies=cookies) as dxm_client):
        pass


@pytest.mark.asyncio
async def test_warehouse():
    async with (DxmClient(headers=headers, cookies=cookies) as dxm_client):
        print(await dxm_client.page_warehouse_product(WarehouseProductQuery()))
