import yaml
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime, Enum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 读取数据库配置
with open('db.yaml', 'r') as f:
    db_config = yaml.safe_load(f)

# 创建数据库连接
engine_url = db_config['mysql_url']
engine = create_engine(engine_url)
Session = sessionmaker(bind=engine)
session = Session()

# 创建基类
Base = declarative_base()


# t_alpha 表模型
class Alpha(Base):
    __tablename__ = 't_alpha'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)
    instrument_type = Column(String(50), nullable=False)
    region = Column(String(10), nullable=False)
    universe = Column(String(50), nullable=False)
    delay = Column(Integer, nullable=False)
    decay = Column(Numeric(10, 2), default=0.00)
    neutralization = Column(String(20), nullable=False)
    truncation = Column(Numeric(5, 2), default=0.10)
    pasteurization = Column(Enum('ON', 'OFF'), default='ON')
    unit_handling = Column(String(20), default='VERIFY')
    nan_handling = Column(Enum('ON', 'OFF'), default='ON')
    language = Column(String(20), default='FASTEXPR')
    max_trade = Column(Enum('ON', 'OFF'), default='OFF')
    visualization = Column(Boolean, default=False)
    regular_expression = Column(String(2000), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    wq_id = Column(String(128))
    alpha = Column(String(128))


# t_checks 表模型
class Check(Base):
    __tablename__ = 't_checks'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alpha_id = Column(String(128))
    LOW_SHARPE = Column(Float)
    LOW_FITNESS = Column(Float)
    LOW_TURNOVER = Column(Float)
    HIGH_TURNOVER = Column(Float)
    LOW_SUB_UNIVERSE_SHARPE = Column(Float)


# t_datafields 表模型
class DataField(Base):
    __tablename__ = 't_datafields'

    idx_id = Column(BigInteger, primary_key=True, autoincrement=True)
    type_id = Column(String(255))
    id = Column(String(255))
    description = Column(String(1000))
    region = Column(String(255))
    delay = Column(Integer)
    universe = Column(String(255))
    type = Column(String(255))
    coverage = Column(Numeric(18, 6))
    userCount = Column(Integer)
    alphaCount = Column(Integer)
    themes = Column(String(255))
    dataset_id = Column(String(255))
    dataset_name = Column(String(255))
    category_id = Column(String(255))
    category_name = Column(String(255))
    subcategory_id = Column(String(255))
    subcategory_name = Column(String(255))


# t_operators 表模型
class Operator(Base):
    __tablename__ = 't_operators'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255))
    category = Column(String(255))
    scope = Column(String(255))
    definition = Column(String(255))
    description = Column(String(3000))
    documentation = Column(String(255))
    level = Column(String(255))
    details = Column(String(3000))
    content = Column(Text)
    last_modified = Column(String(255))


# t_yearly_stats 表模型
class YearlyStat(Base):
    __tablename__ = 't_yearly_stats'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    index_id = Column(String(128))
    year = Column(String(32))
    pnl = Column(Float)
    bookSize = Column(BigInteger)
    longCount = Column(Integer)
    shortCount = Column(Integer)
    turnover = Column(Float)
    sharpe = Column(Float)
    returns = Column(Float)
    drawdown = Column(Float)
    margin = Column(Float)
    fitness = Column(Float)
    stage = Column(String(64))
