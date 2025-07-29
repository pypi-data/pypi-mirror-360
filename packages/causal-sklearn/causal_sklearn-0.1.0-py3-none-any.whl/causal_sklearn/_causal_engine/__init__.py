"""
CausalEngine Core Module

因果推理引擎的核心实现，包含四阶段架构：
1. Perception: 感知网络 (原始数据 -> 高级表征)
2. Abduction: 归因网络 (高级表征 -> 个体因果表征)
3. Action: 行动网络 (个体因果表征 -> 决策得分)
4. Decision: 决断头 (决策得分 -> 任务输出)

以及完整的CausalEngine实现和数学工具。
"""

from .engine import (
    CausalEngine,
    create_causal_regressor,
    create_causal_classifier
)

from .networks import (
    Perception,
    Abduction,
    Action
)

from .heads import (
    DecisionHead,
    RegressionHead,
    ClassificationHead,
    TaskType,
    create_decision_head
)

from .math_utils import (
    CauchyMath,
    CauchyMathNumpy
)

__all__ = [
    # Core Engine
    'CausalEngine',
    'create_causal_regressor', 
    'create_causal_classifier',
    
    # Networks
    'Perception',
    'Abduction',
    'Action',
    
    # Decision Heads
    'DecisionHead',
    'RegressionHead',
    'ClassificationHead',
    'TaskType',
    'create_decision_head',
    
    # Math Utils
    'CauchyMath',
    'CauchyMathNumpy'
]