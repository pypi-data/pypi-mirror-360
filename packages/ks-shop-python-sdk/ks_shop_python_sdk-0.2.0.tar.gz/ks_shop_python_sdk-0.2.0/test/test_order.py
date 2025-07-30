import sys
from pathlib import Path
# 将项目根目录添加到 sys.path
root_dir = Path(__file__).parent.parent  # 根据文件位置调整层级
sys.path.insert(0, str(root_dir))

from ks_shop_api.order import request
from ks_shop_api.order import schema
from test.test_base import base_request, base_dict


def test_cursor_list():
    """
    Test function for CursorListRequest.
    """
    params = schema.OpenOrderCursorListSchema()
    params.orderViewStatus = 1
    params.pageSize = 1
    params.beginTime = 1751731200000  # Example timestamp
    params.endTime = 1751854000000  # Example timestamp
    params.cursor = ''
    response = base_request(request.OpenOrderCursorListRequest, params=params)
    print(response)
test_cursor_list()

def demo_dict():
    params = {
        "orderViewStatus": 1,
        "pageSize": 1,
        "beginTime": 1751731200000,  # Example timestamp
        "endTime": 1751854000000,  # Example timestamp
        "cursor": ''
    }
    response = base_request(request.OpenOrderCursorListRequest, params=params)
    print(response)
# demo_dict()

if __name__ == "__main__":
    pass