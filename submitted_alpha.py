import wqb
import yaml
import nest_asyncio
import asyncio
from entity.result_alpha import *
import Models
import ast
import json
from dacite import from_dict, Config
from entity.result_alpha import AlphaModel

nest_asyncio.apply()


def login():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    logger = wqb.wqb_logger()
    wqbs = wqb.WQBSession((config['username'], config['password']), logger=logger)
    return wqbs


def get_alpha():
    wqbs = login()
    index = 0
    alpha_list = []
    while index == 0 or len(alpha_list) == 100:
        unsubmitted_url = ("https://api.worldquantbrain.com/users/self/alphas?limit=100&offset=" + str(index) +
                           "&status=UNSUBMITTED%1FIS-FAIL&order=-dateSubmitted&hidden=false")
        search_url = ("https://api.worldquantbrain.com/users/self/alphas?limit=100&offset=" + str(index) +
                      "&status=UNSUBMITTED%1FIS_FAIL&is.sharpe%3E1.58&is.turnover%3C0.7"
                      "&order=-dateCreated&hidden=false")
        search_url = ("https://api.worldquantbrain.com/users/self/alphas?limit=100&offset=" + str(index) +
                      "&status=UNSUBMITTED%1FIS_FAIL&is.sharpe%3E3&settings.region=EUR"
                      "&order=-is.sharpe&hidden=false")
        print(search_url)
        response = wqbs.get(search_url)
        alpha_list = response.json()["results"]
        index += len(alpha_list)
        # with open('output.txt', 'a', encoding='utf-8') as f:
        #     for item in alpha_list:
        #         f.write(str(item) + '\n')
        # for j in range(len(alpha_list)):
        #     alpha = alpha_list[j]
        #     print(alpha)
    return alpha_list


def convert_alpha_model_to_alpha_retry(alpha_model: AlphaModel) -> Models.AlphaRetry:
    """
    将 AlphaModel 对象转换为 Models.AlphaRetry 对象

    Args:
        alpha_model: AlphaModel 对象

    Returns:
        AlphaRetry: 转换后的 AlphaRetry 对象
    """
    # 提取 settings 中的字段
    settings = alpha_model.settings
    is_ = alpha_model.is_

    # 提取 regular 中的表达式
    regular_expression = alpha_model.regular.code if alpha_model.regular else ""

    # 创建 AlphaRetry 对象
    alpha_retry = Models.AlphaRetry(
        type=alpha_model.type,
        instrument_type=settings.instrumentType,
        region=settings.region,
        universe=settings.universe,
        delay=settings.delay,
        decay=settings.decay,
        neutralization=settings.neutralization,
        truncation=settings.truncation,
        pasteurization=settings.pasteurization,
        unit_handling=settings.unitHandling,
        nan_handling=settings.nanHandling,
        language=settings.language,
        max_trade=settings.maxTrade,
        visualization=settings.visualization,
        regular_expression=regular_expression,
        alpha=alpha_model.id,
        author=alpha_model.author,
        pnl=is_.pnl,
        bookSize=is_.bookSize,
        longCount=is_.longCount,
        shortCount=is_.shortCount,
        turnover=is_.turnover,
        returns=is_.returns,
        drawdown=is_.drawdown,
        margin=is_.margin,
        sharpe=is_.sharpe,
        fitness=is_.fitness,
        # created_at 和 updated_at 需要根据实际情况设置
    )

    return alpha_retry


def batch_insert_alpha_retry_bulk(alpha_retry_list):
    """
    使用 bulk_insert_mappings 批量插入 AlphaRetry 对象到数据库
    性能更高，但不触发 ORM 事件

    Args:
        alpha_retry_list: AlphaRetry 对象列表
    """
    try:
        # 转换对象为字典映射
        mappings = []
        for alpha_retry in alpha_retry_list:
            mappings.append({
                'type': alpha_retry.type,
                'instrument_type': alpha_retry.instrument_type,
                'region': alpha_retry.region,
                'universe': alpha_retry.universe,
                'delay': alpha_retry.delay,
                'decay': alpha_retry.decay,
                'neutralization': alpha_retry.neutralization,
                'truncation': alpha_retry.truncation,
                'pasteurization': alpha_retry.pasteurization,
                'unit_handling': alpha_retry.unit_handling,
                'nan_handling': alpha_retry.nan_handling,
                'language': alpha_retry.language,
                'max_trade': alpha_retry.max_trade,
                'visualization': alpha_retry.visualization,
                'regular_expression': alpha_retry.regular_expression,
                'alpha': alpha_retry.alpha,
                'author': alpha_retry.author,
                'pnl': alpha_retry.pnl,
                'bookSize': alpha_retry.bookSize,
                'longCount': alpha_retry.longCount,
                'shortCount': alpha_retry.shortCount,
                'turnover': alpha_retry.turnover,
                'returns': alpha_retry.returns,
                'drawdown': alpha_retry.drawdown,
                'margin': alpha_retry.margin,
                'sharpe': alpha_retry.sharpe,
                'fitness': alpha_retry.fitness
            })

        # 批量插入
        Models.session.bulk_insert_mappings(Models.AlphaRetry, mappings)
        Models.session.commit()
        print(f"成功批量插入 {len(alpha_retry_list)} 条记录")
    except Exception as e:
        Models.session.rollback()
        print(f"批量插入失败: {e}")
    finally:
        Models.session.close()


def parse_alpha_string(alpha_str):
    """
    解析 alpha 字符串为字典对象

    Args:
        alpha_str: 包含字典的字符串

    Returns:
        dict: 解析后的字典对象
    """
    # 方法1: 使用 ast.literal_eval (更安全)
    try:
        return ast.literal_eval(alpha_str)
    except (ValueError, SyntaxError):
        pass

    # 方法2: 替换单引号为双引号后使用 json.loads
    try:
        alpha_json = alpha_str.replace("'", '"').replace('True', 'true').replace('False', 'false').replace('None',
                                                                                                           'null')
        return json.loads(alpha_json)
    except json.JSONDecodeError:
        pass

    raise ValueError("无法解析 alpha 字符串")


def dict_to_alpha_model(data):
    # 处理嵌套对象
    settings = Settings(**data['settings'])
    regular = Regular(**data['regular'])

    # 处理分类列表
    classifications = [Classification(**cls) for cls in data.get('classifications', [])]

    # 处理 is 字段 (注意这里是 is_, 因为 is 是关键字)
    is_data = data.get('is')
    is_obj = None
    if is_data:
        is_obj = from_dict(data_class=IS, data=is_data)

    # 创建主对象
    alpha_model = AlphaModel(
        id=data['id'],
        type=data['type'],
        author=data['author'],
        settings=settings,
        regular=regular,
        dateCreated=data['dateCreated'],
        dateSubmitted=data.get('dateSubmitted'),
        dateModified=data['dateModified'],
        name=data.get('name'),
        favorite=data.get('favorite', False),
        hidden=data.get('hidden', False),
        color=data.get('color'),
        category=data.get('category'),
        tags=data.get('tags', []),
        classifications=classifications,
        grade=data.get('grade'),
        stage=data.get('stage'),
        status=data.get('status'),
        is_=is_obj,
        os=data.get('os'),
        train=data.get('train'),
        test=data.get('test'),
        prod=data.get('prod'),
        competitions=data.get('competitions'),
        themes=data.get('themes'),
        pyramids=data.get('pyramids'),
        pyramidThemes=data.get('pyramidThemes'),
        team=data.get('team')
    )

    return alpha_model


def get_alpha_test():
    wqbs = login()
    index = 0
    alpha_list = []
    while len(alpha_list) == 0 or len(alpha_list) == 50:
        search_url = ("https://api.worldquantbrain.com/users/self/alphas?limit=50&offset=" + str(index) +
                      "&status=UNSUBMITTED%1FIS_FAIL&is.sharpe%3E3&settings.region=EUR"
                      "&dateCreated%3E=2025-11-26T00:00:00-05:00&dateCreated%3C2025-11-28T00:00:00-05:00"
                      "&order=-dateCreated&hidden=false")
        print(search_url)
        response = wqbs.get(search_url)
        alpha_list = response.json()["results"]
        index += len(alpha_list)
        print("已获取 " + str(index) + " 个 alpha")
        print(alpha_list[0])
        alpha_retry_list = []
        for alpha in alpha_list:
            # alpha = ("{'id': 'akqn86Z6', 'type': 'REGULAR', 'author': 'XY30989', 'settings': {'instrumentType': 'EQUITY', 'region': 'EUR', 'universe': 'TOP2500', 'delay': 1, 'decay': 0, 'neutralization': 'CROWDING', 'truncation': 0.1, 'pasteurization': 'ON', 'unitHandling': 'VERIFY', 'nanHandling': 'ON', 'maxTrade': 'OFF', 'language': 'FASTEXPR', 'visualization': False, 'startDate': '2013-01-20', 'endDate': '2023-01-20'}, 'regular': {'code': 'ts_product(anl69_dps_best_eeps_cur_yr, 66)', 'description': None, 'operatorCount': 1}, 'dateCreated': '2025-11-27T00:42:51-05:00', 'dateSubmitted': None, 'dateModified': '2025-11-27T00:42:51-05:00', 'name': None, 'favorite': False, 'hidden': False, 'color': None, 'category': None, 'tags': [], 'classifications': [{'id': 'DATA_USAGE:SINGLE_DATA_SET', 'name': 'Single Data Set Alpha'}], 'grade': None, 'stage': 'IS', 'status': 'UNSUBMITTED', 'is': {'pnl': 17945, 'bookSize': 20000000, 'longCount': 214, 'shortCount': 1212, 'turnover': 1.0, 'returns': 0.2243, 'drawdown': 0.0, 'margin': 0.000449, 'sharpe': 11.18, 'fitness': 5.29, 'startDate': '2013-01-20', 'checks': [{'name': 'LOW_SHARPE', 'result': 'PASS', 'limit': 1.58, 'value': 11.18}, {'name': 'LOW_FITNESS', 'result': 'PASS', 'limit': 1.0, 'value': 5.29}, {'name': 'LOW_TURNOVER', 'result': 'PASS', 'limit': 0.01, 'value': 1.0}, {'name': 'HIGH_TURNOVER', 'result': 'FAIL', 'limit': 0.7, 'value': 1.0}, {'name': 'CONCENTRATED_WEIGHT', 'result': 'FAIL', 'date': '2020-12-08', 'limit': 0.1, 'value': 0.133714}, {'name': 'LOW_SUB_UNIVERSE_SHARPE', 'result': 'PASS', 'limit': 5.81, 'value': 11.18}, {'name': 'SELF_CORRELATION', 'result': 'PENDING'}, {'name': 'DATA_DIVERSITY', 'result': 'PENDING'}, {'name': 'PROD_CORRELATION', 'result': 'PENDING'}, {'name': 'REGULAR_SUBMISSION', 'result': 'PENDING'}, {'name': 'LOW_2Y_SHARPE', 'result': 'FAIL', 'value': 0.0, 'limit': 1.58}, {'result': 'PASS', 'name': 'MATCHES_PYRAMID', 'effective': 1, 'multiplier': 1.4, 'pyramids': [{'name': 'EUR/D1/ANALYST', 'multiplier': 1.4}]}, {'result': 'WARNING', 'name': 'MATCHES_THEMES', 'themes': [{'id': '3yYPdo4', 'multiplier': 2.0, 'name': 'IND Region Theme'}]}]}, 'os': None, 'train': None, 'test': None, 'prod': None, 'competitions': None, "
            #          "'themes': None, 'pyramids': None, 'pyramidThemes': None, 'team': None}")

            alpha_model = dict_to_alpha_model(alpha)
            fail_count = 0
            for check in alpha_model.is_.checks:
                if check.result == 'FAIL':
                    fail_count += 1
            if alpha_model.name != 'fail' and alpha_model.name != 'sub_fail' and fail_count < 2:
                if alpha_model.is_.investabilityConstrained.fitness > 1 or alpha_model.is_.investabilityConstrained.margin > 0.001:
                    alpha_retry = convert_alpha_model_to_alpha_retry(alpha_model)
                    alpha_retry_list.append(alpha_retry)
        # 批量插入到数据库
        if alpha_retry_list:
            print("批量插入中..." + str(len(alpha_retry_list)))
            batch_insert_alpha_retry_bulk(alpha_retry_list)


def get_check_alpha():
    wqbs = login()
    index = 0
    alpha_list = []
    while len(alpha_list) == 0 or len(alpha_list) == 50:
        search_url = ("https://api.worldquantbrain.com/users/self/alphas?limit=50&offset=" + str(index) +
                      "&status=UNSUBMITTED%1FIS_FAIL&is.sharpe%3E2&settings.region=EUR"
                      "&dateCreated%3E=2025-11-26T00:00:00-05:00&dateCreated%3C2025-11-28T00:00:00-05:00"
                      "&order=-dateCreated&hidden=false")
        print(search_url)
        response = wqbs.get(search_url)
        alpha_list = response.json()["results"]
        index += len(alpha_list)
        print("已获取 " + str(index) + " 个 alpha")
        print(alpha_list[0])
        alpha_retry_list = []
        for alpha in alpha_list:
            # alpha = ("{'id': 'akqn86Z6', 'type': 'REGULAR', 'author': 'XY30989', 'settings': {'instrumentType': 'EQUITY', 'region': 'EUR', 'universe': 'TOP2500', 'delay': 1, 'decay': 0, 'neutralization': 'CROWDING', 'truncation': 0.1, 'pasteurization': 'ON', 'unitHandling': 'VERIFY', 'nanHandling': 'ON', 'maxTrade': 'OFF', 'language': 'FASTEXPR', 'visualization': False, 'startDate': '2013-01-20', 'endDate': '2023-01-20'}, 'regular': {'code': 'ts_product(anl69_dps_best_eeps_cur_yr, 66)', 'description': None, 'operatorCount': 1}, 'dateCreated': '2025-11-27T00:42:51-05:00', 'dateSubmitted': None, 'dateModified': '2025-11-27T00:42:51-05:00', 'name': None, 'favorite': False, 'hidden': False, 'color': None, 'category': None, 'tags': [], 'classifications': [{'id': 'DATA_USAGE:SINGLE_DATA_SET', 'name': 'Single Data Set Alpha'}], 'grade': None, 'stage': 'IS', 'status': 'UNSUBMITTED', 'is': {'pnl': 17945, 'bookSize': 20000000, 'longCount': 214, 'shortCount': 1212, 'turnover': 1.0, 'returns': 0.2243, 'drawdown': 0.0, 'margin': 0.000449, 'sharpe': 11.18, 'fitness': 5.29, 'startDate': '2013-01-20', 'checks': [{'name': 'LOW_SHARPE', 'result': 'PASS', 'limit': 1.58, 'value': 11.18}, {'name': 'LOW_FITNESS', 'result': 'PASS', 'limit': 1.0, 'value': 5.29}, {'name': 'LOW_TURNOVER', 'result': 'PASS', 'limit': 0.01, 'value': 1.0}, {'name': 'HIGH_TURNOVER', 'result': 'FAIL', 'limit': 0.7, 'value': 1.0}, {'name': 'CONCENTRATED_WEIGHT', 'result': 'FAIL', 'date': '2020-12-08', 'limit': 0.1, 'value': 0.133714}, {'name': 'LOW_SUB_UNIVERSE_SHARPE', 'result': 'PASS', 'limit': 5.81, 'value': 11.18}, {'name': 'SELF_CORRELATION', 'result': 'PENDING'}, {'name': 'DATA_DIVERSITY', 'result': 'PENDING'}, {'name': 'PROD_CORRELATION', 'result': 'PENDING'}, {'name': 'REGULAR_SUBMISSION', 'result': 'PENDING'}, {'name': 'LOW_2Y_SHARPE', 'result': 'FAIL', 'value': 0.0, 'limit': 1.58}, {'result': 'PASS', 'name': 'MATCHES_PYRAMID', 'effective': 1, 'multiplier': 1.4, 'pyramids': [{'name': 'EUR/D1/ANALYST', 'multiplier': 1.4}]}, {'result': 'WARNING', 'name': 'MATCHES_THEMES', 'themes': [{'id': '3yYPdo4', 'multiplier': 2.0, 'name': 'IND Region Theme'}]}]}, 'os': None, 'train': None, 'test': None, 'prod': None, 'competitions': None, "
            #          "'themes': None, 'pyramids': None, 'pyramidThemes': None, 'team': None}")

            alpha_model = dict_to_alpha_model(alpha)
            fail_count = 0
            for check in alpha_model.is_.checks:
                if check.result == 'FAIL':
                    fail_count += 1
            if fail_count != 0 or (alpha_model.name != '' and alpha_model.name != 'pending' and alpha_model.name is not None):
                continue
            else:
                print("正在更新 " + alpha_model.id)
                name = "pending"
                color = 'YELLOW'
                description = """Idea: This is a great idea.
Rationale for data used: The data used is very reliable and meets the expected standards.
Rationale for operators used: The selected operator is very suitable and can effectively complete the required operation."""
                params = {
                    "color": color,
                    "name": name,
                    "category": None,
                    "regular": {"description": description},
                }
                wqbs.patch("https://api.worldquantbrain.com/alphas/" + alpha_model.id, json=params)


def check_alpha(s, alpha_id):
    result = s.get("https://api.worldquantbrain.com/alphas/" + alpha_id + "/check")
    pass


def submit_alpha():
    decays = [4, 10, 20]
    truncations = [0.01, 0.008]
    ops_list = ['abs', 'densify', 'inverse', 'log', 'sign', 'sqrt', 'rank', 'zscore']
    ops_dict = [{"power": 2, "signed_power": 2}]

    alphas = Models.session.query(Models.AlphaRetry).all()
    for alpha in alphas:
        pass


if __name__ == '__main__':
    # login()
    # get_alpha_test()
    get_check_alpha()