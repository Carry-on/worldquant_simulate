import Models
import utils


def build_sim_alpha(alpha):
    return build_usual_alpha(alpha=alpha)


def build_usual_alpha(region, universe, delay, decay, neutralization, alpha):
    return build_alpha(region=region, universe=universe, delay=delay, decay=decay, neutralization=neutralization, regular=alpha)


def build_alpha(type: str = 'REGULAR',
                instrument_type: str = 'EQUITY',
                region: str = 'USA',
                universe: str = 'TOP3000',
                delay: int = 1,
                decay: int = 0,
                neutralization: str = 'SUBINDUSTRY',
                truncation: float = 0.08,
                pasteurization: str = 'ON',
                test_period: str = 'P1Y',
                unit_handling: str = 'VERIFY',
                nan_handling: str = 'ON',
                language: str = 'FASTEXPR',
                max_trade: str = 'OFF',
                visualization: bool = False,
                regular: str = ''
                ):
    alpha = {
        'type': type,
        'settings': {
            'instrumentType': instrument_type,
            'region': region,
            'universe': universe,
            'delay': delay,
            'decay': decay,
            'neutralization': neutralization,
            'truncation': truncation,
            'pasteurization': pasteurization,
            'testPeriod': test_period,
            'unitHandling': unit_handling,
            'nanHandling': nan_handling,
            'language': language,
            'maxTrade': max_trade,
            'visualization': visualization
        },
        'regular': regular
    }
    return alpha


def build_fixed_alpha(regular):
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
            'testPeriod': 'P1Y',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR',
            'maxTrade': 'OFF',
            'visualization': False
        },
        'regular': regular
        ## 这个就是表达式
    }
    return alpha


def save_alpha(resp_data, alpha):
    alpha_model = Models.Alpha(
        type=alpha['type'],
        instrument_type=alpha['settings']['instrumentType'],
        region=alpha['settings']['region'],
        universe=alpha['settings']['universe'],
        delay=alpha['settings']['delay'],
        decay=alpha['settings']['decay'],
        neutralization=alpha['settings']['neutralization'],
        truncation=alpha['settings']['truncation'],
        pasteurization=alpha['settings']['pasteurization'],
        unit_handling=alpha['settings']['unitHandling'],
        nan_handling=alpha['settings']['nanHandling'],
        language=alpha['settings']['language'],
        max_trade=alpha['settings']['maxTrade'],
        visualization=alpha['settings']['visualization'],
        regular_expression=alpha['regular'],
        wq_id=resp_data.get('id') if resp_data else None,
        alpha=resp_data.get('alpha') if resp_data else None
    )
    try:
        Models.session.add(alpha_model)
        Models.session.commit()
        print('Alpha saved to database successfully')
    except Exception as e:
        Models.session.rollback()
        print('Error:', e)
    finally:
        Models.session.close()



def submit_alpha():
    wqbs = utils.login()

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
    #     try:
    #         Models.session.add(alpha_model)
    #         Models.session.commit()
    #         print('Alpha saved to database successfully')
    #     except Exception as e:
    #         Models.session.rollback()
    #         print('Error:', e)
    #     finally:
    #         Models.session.close()
    # else:
    #     print('Login Failed')
    # pass


def save_fields():
    wqbs = utils.login()
    datafields_df = utils.get_datafields(wqbs, 'EQUITY', 'USA', 1, 'TOP1000')
    list = [item for sublist in datafields_df for item in sublist]
    print(len(list))
    for field in list:
        data_fields = Models.DataField(
            id=field['id'],
            description=field['description'],
            region=field['region'],
            delay=field['delay'],
            universe=field['universe'],
            type=field['type'],
            coverage=field['coverage'],
            userCount=field['userCount'],
            alphaCount=field['alphaCount'],
            themes=str(field['themes']),
            dataset_id=field['dataset']['id'],
            dataset_name=field['dataset']['name'],
            category_id=field['category']['id'],
            category_name=field['category']['name'],
            subcategory_id=field['subcategory']['id'],
            subcategory_name=field['subcategory']['name']
        )
        try:
            Models.session.add(data_fields)
            Models.session.commit()
            print('Alpha saved to database successfully')
        except Exception as e:
            Models.session.rollback()
            print('Error:', e)
        finally:
            Models.session.close()
    print("finished add to db")


def get_alpha():
    wqbs = utils.login()
    unsubmitted_url = 'https://api.worldquantbrain.com/users/self/alphas?limit=10&offset=0&status!=UNSUBMITTED%1FIS-FAIL&order=-dateSubmitted&hidden=false'
    submitted_url = 'https://api.worldquantbrain.com/users/self/alphas?limit=10&offset=0&status!=UNSUBMITTED%1FIS-FAIL&order=-dateSubmitted&hidden=false'
    response = wqbs.get(submitted_url)
    alpha_list = response.json()["results"]
    print(alpha_list)
    for j in range(len(alpha_list)):
        alpha = alpha_list[j]
        print(alpha)

