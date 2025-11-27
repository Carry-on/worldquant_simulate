from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Settings:
    instrumentType: str
    region: str
    universe: str
    delay: int
    decay: int
    neutralization: str
    truncation: float
    pasteurization: str
    unitHandling: str
    nanHandling: str
    maxTrade: str
    language: str
    visualization: bool
    startDate: str
    endDate: str


@dataclass
class Regular:
    code: str
    description: Optional[str]
    operatorCount: int


@dataclass
class Classification:
    id: str
    name: str


@dataclass
class Check:
    name: str
    result: str
    limit: Optional[float] = None
    value: Optional[float] = None
    competitions: Optional[List[Dict[str, Any]]] = None
    effective: Optional[int] = None
    multiplier: Optional[float] = None
    pyramids: Optional[List[Dict[str, Any]]] = None
    themes: Optional[List[Dict[str, Any]]] = None


@dataclass
class InvestabilityConstrained:
    pnl: int
    bookSize: int
    longCount: int
    shortCount: int
    turnover: float
    returns: float
    drawdown: float
    margin: float
    fitness: float
    sharpe: float


@dataclass
class IS:
    pnl: int
    bookSize: int
    longCount: int
    shortCount: int
    turnover: float
    returns: float
    drawdown: float
    margin: float
    sharpe: float
    fitness: float
    startDate: str
    investabilityConstrained: Optional[InvestabilityConstrained]
    checks: List[Check]


@dataclass
class Train:
    pnl: int
    bookSize: int
    longCount: int
    shortCount: int
    turnover: float
    returns: float
    drawdown: float
    margin: float
    fitness: float
    sharpe: float
    startDate: str


@dataclass
class Test:
    pnl: int
    bookSize: int
    longCount: int
    shortCount: int
    turnover: float
    returns: float
    drawdown: float
    margin: float
    fitness: float
    sharpe: float
    startDate: str


@dataclass
class AlphaModel:
    id: str
    type: str
    author: str
    settings: Settings
    regular: Regular
    dateCreated: str
    dateSubmitted: Optional[str]
    dateModified: str
    name: Optional[str]
    favorite: bool
    hidden: bool
    color: Optional[str]
    category: Optional[str]
    tags: List[Any]
    classifications: List[Classification]
    grade: Optional[str]
    stage: str
    status: str
    is_: IS
    os: Optional[Any]
    train: Optional[Train]
    test: Optional[Test]
    prod: Optional[Any]
    competitions: Optional[Any]
    themes: Optional[Any]
    pyramids: Optional[Any]
    pyramidThemes: Optional[Any]
    team: Optional[Any]

    # 用于处理字段名映射
    def __post_init__(self):
        if isinstance(self.is_, dict):
            if hasattr(self, 'is_') and self.is_ is not None:
                self.is_ = self.is_
                delattr(self, 'is')
            # 处理 investabilityConstrained
            invest_constrained = self.is_.get('investabilityConstrained')
            if invest_constrained:
                self.is_['investabilityConstrained'] = InvestabilityConstrained(**invest_constrained)

            # 处理 checks
            checks = self.is_.get('checks', [])
            if checks:
                processed_checks = []
                for check in checks:
                    processed_checks.append(Check(**check))
                self.is_['checks'] = processed_checks

            self.is_ = IS(**self.is_)
