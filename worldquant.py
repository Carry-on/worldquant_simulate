import wqb
import yaml
import nest_asyncio
import asyncio
import Models
import json
import utils

nest_asyncio.apply()


def login():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    logger = wqb.wqb_logger()
    wqbs = wqb.WQBSession((config['username'], config['password']), logger=logger)
    return wqbs

def build_alpha(universe):
    alpha = {
        'type': 'REGULAR',
        'settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'universe': 'TOP3000',
            'delay': 1,
            'decay': 0,
            'neutralization': 'INDUSTRY',
            'truncation': 0.1,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR',
            'maxTrade': 'OFF',
            'visualization': False
        },
        'regular': 'v00=-ts_delta(ts_backfill(anl4_adjusted_netincome_ft, 120), 66);v10=-ts_std_dev(v00,22);'
        ## 这个就是表达式
    }

def submit_alpha():
    wqbs = login()

    # resp = asyncio.run(wqbs.simulate(alpha))
    # resp = asyncio.run()
    # resp = wqbs.locate_alpha('xoLowkW')
    # resp = wqbs.check('xoLowkW')
    # resp = wqbs.locate_dataset('analyst4')
    # resp = wqbs.locate_field("anl4_buy")
    # print(resp.text)
    # if resp.status_code == 200:
    #     print('Login Success')
    #     # # 解析响应数据
    #     # try:
    #     #     resp_data = json.loads(resp.text)
    #     # except json.JSONDecodeError:
    #     #     resp_data = {}
    #     # alpha_model = Models.Alpha(
    #     #     type=alpha['type'],
    #     #     instrument_type=alpha['settings']['instrumentType'],
    #     #     region=alpha['settings']['region'],
    #     #     universe=alpha['settings']['universe'],
    #     #     delay=alpha['settings']['delay'],
    #     #     decay=alpha['settings']['decay'],
    #     #     neutralization=alpha['settings']['neutralization'],
    #     #     truncation=alpha['settings']['truncation'],
    #     #     pasteurization=alpha['settings']['pasteurization'],
    #     #     unit_handling=alpha['settings']['unitHandling'],
    #     #     nan_handling=alpha['settings']['nanHandling'],
    #     #     language=alpha['settings']['language'],
    #     #     max_trade=alpha['settings']['maxTrade'],
    #     #     visualization=alpha['settings']['visualization'],
    #     #     regular_expression=alpha['regular'],
    #     #     wq_id=resp_data.get('id') if resp_data else None,
    #     #     alpha=resp_data.get('alpha') if resp_data else None
    #     # )
    #     # try:
    #     #     Models.session.add(alpha_model)
    #     #     Models.session.commit()
    #     #     print('Alpha saved to database successfully')
    #     # except Exception as e:
    #     #     Models.session.rollback()
    #     #     print('Error:', e)
    #     # finally:
    #     #     Models.session.close()
    # else:
    #     print('Login Failed')
    # pass


def request_alpha():
    wqbs = login()
    datafields_df = utils.get_datafields(wqbs, 'EQUITY', 'USA', 1, 'TOP3000')
    print(datafields_df)


def get_alpha():
    wqbs = login()
    unsubmitted_url = 'https://api.worldquantbrain.com/users/self/alphas?limit=10&offset=0&status!=UNSUBMITTED%1FIS-FAIL&order=-dateSubmitted&hidden=false'
    submitted_url = 'https://api.worldquantbrain.com/users/self/alphas?limit=10&offset=0&status!=UNSUBMITTED%1FIS-FAIL&order=-dateSubmitted&hidden=false'
    response = wqbs.get(submitted_url)
    alpha_list = response.json()["results"]
    print(alpha_list)
    for j in range(len(alpha_list)):
        alpha = alpha_list[j]
        print(alpha)

if __name__ == '__main__':
    # login()
    # get_alpha()
    request_alpha()