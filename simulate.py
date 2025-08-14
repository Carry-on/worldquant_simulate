import pandas as pd
import yaml
import wqb
import random
import nest_asyncio
import asyncio


region = "USA" ##地区，美股
delay = 1 ##延迟，默认1
universe = "TOP3000" ##股票池，流动性最强的3000只股票
universes = ["TOP3000","TOP1000","TOP500","TOP200","TOPSP500"]


## 获取数据，已通过脚本爬取，放入data文件夹
file_name = '_'.join(["datafields", region, str(delay), universe])
df = pd.read_csv('data/' + file_name + '.csv')


df.head()

# dateset_ids = ["","","","","","","","","","",""]
## 筛选数据, 可自定义筛选条件
dt = df.loc[(df['dataset.id'] == 'fundamental6') &
        (df['coverage']) > 0.6
]


## 数据预处理，主要处理matrix 和 vector 类型的数据
def process_datafields(df):
    raw_fields = []
    if df[df['type'] == "MATRIX"].shape[0] > 0:
        raw_fields.extend(df[df['type'] == "MATRIX"]["id"].tolist())
    if df[df['type'] == "VECTOR"].shape[0] > 0:
        vec_fields = df[df['type'] == "VECTOR"]["id"].tolist()
        raw_fields.extend(get_vec_fields(vec_fields))
    result = []
    for field in raw_fields:
        # result.append("ts_backfill(%s, 120)"%(field,))
        # result.append("winsorize(ts_backfill(%s, 60), std=4)"%field) ts_backfill，时间序列回填，处理缺失值
        result.append(field)
        # result.append("ts_backfill(%s, 60)"%field)
        result.append("ts_backfill(%s, 120)"%field)
    return result

def get_vec_fields(fields):
    vec_ops = ['vec_sum','vec_avg'] ## vector类型的字段需要vec操作符进行降维处理，依据自己的操作符修改
    result = []
    for op in vec_ops:
        for field in fields:
            result.append("%s(%s)"%(op,field))
    return result


pc_fields = process_datafields(dt)


pc_fields[-5]
# 'ts_backfill(vec_avg(fnd6_xidos), 120)'


# 生成alpha表达式
# alpha表达式由操作符及字段组成

## time series
def ts_factory(ts_op, field, day):
    return "%s(%s, %d)" % (ts_op, field, day)


## transform operater
def trans_factory(trans_op, field):
    return "%s(%s)" % (trans_op, field)


## group operater
def group_factory(gp_op, filed, gp):
    return "%s(%s,%s)" % (gp_op, field, gp)


## 一阶alpha,一般由ts 和 trans组合而成

def get_first_order(fields):
    ts_ops = ["ts_zscore","ts_std_dev","ts_av_diff","ts_mean",
              "ts_arg_max","ts_delta","ts_rank","ts_delay"] ## 依据自己的操作符修改
    trans_ops = ["rank","zscore","log","sqrt"] ## 依据自己的操作符修改
    days = [5,22,120,252] ## 分别对应周、月、半年、一年、两年交易日

    trans_res = []
    for trans_op in trans_ops:
        for field in fields:
            trans_res.append(trans_factory(trans_op, field))

    ts_res = []
    for ts_op in ts_ops:
        for field in fields:
            for day in days:
                ts_res.append(ts_factory(ts_op, field, day))
    # trans_ts_res = []
    # for trans_op in trans_ops:
    #     for field in ts_res:
    #         trans_ts_res.append(trans_factory(trans_op, field))
    ts_trans_res = []
    for ts_op in ts_ops:
        for field in trans_res:
            for day in days:
                ts_trans_res.append(ts_factory(ts_op, field, day))

    return fields+trans_res+ts_res+ts_trans_res


regulars = get_first_order(pc_fields)


len(regulars)
# 395340


regulars[-1]
# 'ts_delay(sqrt(ts_backfill(vec_avg(fnd6_xsgas), 120)), 252)'



# alpha setting
alphas = []
init_decay = 0
neut  = "INDUSTRY" ## MARKET INDUSTRY SECTOR SUBINDUSTRY
for regular in regulars:
    alpha = {
        'type': 'REGULAR',
        'settings': {
            'instrumentType': 'EQUITY',
            'region': region,
            'universe': universe,
            'delay': delay,
            'decay': init_decay,
            'neutralization': neut,
            'truncation': 0.1,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR',
            'maxTrade':'OFF',
            'visualization': False
    },
        'regular': regular  ## 这个就是表达式
    }
    alphas.append(alpha)


# 模块回测，基于wqb模块

## 登录

with open('config.yaml', 'r') as f: ## 这个文件存储用户名和密码
    config = yaml.safe_load(f)



logger = wqb.wqb_logger()
wqbs = wqb.WQBSession((config['username'], config['password']), logger=logger)



random.seed(603)
random.shuffle(alphas)  ## 随机打乱顺序，相似表达式相关性过高



nest_asyncio.apply()


## 模拟回测

idx = 1 ## 初始为0
for idx, alpha in enumerate(alphas[idx:]):
    try:
        resp =  asyncio.run(
            wqbs.simulate(
                alpha,  # `alpha` or `multi_alpha`
            )
        )
    except:
        print(idx) ## 这个idx出错，之后可以从这个开始跑
        print(resp.text)
        break

