"""
Decision Heads for CausalEngine

决断头 (DecisionHead) 负责 CausalEngine 第四阶段 Decision，通过结构方程 τ(S) 
将内部的决策得分分布 S ~ Cauchy(μ_S, γ_S) 转换为特定任务的输出 Y，并计算相应的损失。

数学框架：
给定观测 y_true，通过以下两条路径计算似然：
- 路径A (可逆τ): s_inferred = τ^(-1)(y_true) → PDF计算
- 路径B (不可逆τ): P({s | τ(s) = y_true}) → CDF计算

设计哲学：
- 高内聚：每个 Head 封装与特定任务相关的所有逻辑（前向计算、损失计算）。
- 低耦合：核心引擎通过工厂函数获取 Head 实例，并调用其方法，无需了解任务细节。
- 可扩展：添加新任务只需创建新的 Head 子类并在工厂中注册，引擎代码无需改动。
"""

import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple

from .math_utils import CauchyMath


class TaskType(Enum):
    """任务类型枚举"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"


class DecisionHead(nn.Module, ABC):
    """
    决断头的抽象基类 (Abstract Base Class)。
    
    实现 CausalEngine 第四阶段 Decision，负责通过结构方程 τ(S) 将决策分数 S 
    转换为观测 Y，并计算观测的似然损失。

    所有具体的决断头都应继承此类，并实现其抽象方法。
    """
    def __init__(self, output_size: int, factor=10.0):
        super().__init__()
        self.output_size = output_size
        self.factor = factor  # 默认10.0, 用于调整损失的权重，因为 Cauchy NLL 损失很平坦，所以需要乘以一个较大的数

    @abstractmethod
    def forward(
        self,
        decision_scores: Tuple[torch.Tensor, torch.Tensor],
        mode: str = 'standard'
    ) -> torch.Tensor:
        """
        将决策得分转换为面向用户的预测结果。

        Args:
            decision_scores: 决策得分元组 (mu_S, gamma_S)。
            mode: 当前的推理模式。

        Returns:
            任务特定的预测结果（例如，回归值、类别概率）。
        """
        raise NotImplementedError

    @abstractmethod
    def compute_loss(
        self,
        y_true: torch.Tensor,
        decision_scores: Tuple[torch.Tensor, torch.Tensor],
        mode: str = 'standard',
        reduction: str = 'mean'
    ) -> torch.Tensor:
        """
        根据决策得分和真实标签计算损失。

        Args:
            y_true: 真实标签。
            decision_scores: 模型的原始决策得分元组 (mu_S, gamma_S)。
            mode: 当前的推理模式。

        Returns:
            计算出的损失值 (标量)。
        """
        raise NotImplementedError


class RegressionHead(DecisionHead):
    """回归任务专用决断头
    
    实现结构方程 τ(s) = s (恒等映射)，使用路径A进行似然计算。
    
    TODO: 未来可以考虑加入一些可学习的线性变化，比如加入一个可学习的线性层，将决策得分映射到输出空间。
    """

    def __init__(self, output_size: int, factor=1.0):
        super().__init__(output_size, factor)

    def forward(
        self,
        decision_scores: Tuple[torch.Tensor, torch.Tensor],
        mode: str = 'standard'
    ) -> torch.Tensor:
        """对于回归任务，点预测通常使用位置参数 mu_S。
        
        Args:
            decision_scores: 决策分数元组 (mu_S, gamma_S)
            mode: 推理模式（回归任务中通常忽略，因为都返回位置参数）
        """
        mu_S, _ = decision_scores
        return mu_S

    def compute_loss(
        self,
        y_true: torch.Tensor,
        decision_scores: Tuple[torch.Tensor, torch.Tensor],
        mode: str = 'standard',
        reduction: str = 'mean'
    ) -> torch.Tensor:
        mu_pred, gamma_pred = decision_scores
        if mode == 'deterministic':
            # 确定性模式：使用均方误差 (MSE)
            mse = (y_true - mu_pred) ** 2
            if reduction == 'mean':
                return torch.mean(mse)
            elif reduction == 'sum':
                return torch.sum(mse)
            elif reduction == 'none':
                return mse
            else:
                raise ValueError(f"Unknown reduction: {reduction}")
        else:
            # 分布模式：使用柯西负对数似然 (NLL)
            return CauchyMath.nll_loss(y_true, mu_pred, gamma_pred, reduction=reduction) * self.factor


class ClassificationHead(DecisionHead):
    """分类任务专用决断头 (One-vs-Rest)
    
    实现结构方程 τ_k(s_k) = I(s_k > C_k)，使用路径B进行似然计算。
    """

    def __init__(self, n_classes: int, ovr_threshold: float = 0.0, learnable_threshold: bool = False):
        super().__init__(output_size=n_classes)
        self.n_classes = n_classes

        if learnable_threshold:
            # 注册可学习的 OvR 决策阈值
            self.register_parameter(
                'ovr_threshold',
                nn.Parameter(torch.full((n_classes,), ovr_threshold))
            )
        else:
            # 将阈值注册为非学习参数的 buffer，确保设备同步
            self.register_buffer(
                'ovr_threshold',
                torch.full((n_classes,), ovr_threshold)
            )

    def forward(
        self,
        decision_scores: Tuple[torch.Tensor, torch.Tensor],
        mode: str = 'standard'
    ) -> torch.Tensor:
        mu_S, gamma_S = decision_scores
        if mode == 'deterministic':
            # 确定性模式：输出 Softmax 概率，与传统ML对齐
            return torch.softmax(mu_S, dim=-1)
        else:
            # 分布模式：计算 OvR 概率 P_k = P(S_k > C_k)
            ovr_probs = CauchyMath.survival_function(
                self.ovr_threshold,
                mu_S,
                gamma_S
            )
            return ovr_probs

    def compute_loss(
        self,
        y_true: torch.Tensor,
        decision_scores: Tuple[torch.Tensor, torch.Tensor],
        mode: str = 'standard',
        reduction: str = 'mean'
    ) -> torch.Tensor:
        mu_S, gamma_S = decision_scores
        if mode == 'deterministic':
            # 确定性模式：使用交叉熵损失，输入为原始 logits
            return nn.functional.cross_entropy(mu_S, y_true, reduction=reduction)
        else:
            # 分布模式：使用独立的 OvR 二元交叉熵 (BCE) 损失
            
            # 1. 从决策得分计算 OvR 概率
            ovr_probs = CauchyMath.survival_function(
                self.ovr_threshold,
                mu_S,
                gamma_S
            )

            # 2. 准备 one-hot 真实标签
            if y_true.dim() == 1:
                y_true_onehot = nn.functional.one_hot(
                    y_true, num_classes=self.n_classes
                ).float()
            else: # 已经one-hot编码的多标签分类
                y_true_onehot = y_true.float()

            # 3. 计算 BCE 损失: -[y*log(p) + (1-y)*log(1-p)]
            eps = 1e-8
            ovr_probs = torch.clamp(ovr_probs, eps, 1 - eps)
            
            bce_loss = -(y_true_onehot * torch.log(ovr_probs) +
                         (1 - y_true_onehot) * torch.log(1 - ovr_probs))
            
            # Sum over classes first, then apply reduction
            sample_losses = torch.sum(bce_loss, dim=-1)
            
            if reduction == 'mean':
                return torch.mean(sample_losses)
            elif reduction == 'sum':
                return torch.sum(sample_losses)
            elif reduction == 'none':
                return sample_losses
            else:
                raise ValueError(f"Unknown reduction: {reduction}")


def create_decision_head(
    output_size: int,
    task_type: str,
    **kwargs
) -> DecisionHead:
    """
    决断头工厂函数。

    根据任务类型字符串和参数，创建并返回一个具体的 DecisionHead 实例。

    Args:
        output_size (int): 任务的输出维度 (例如，回归特征数或分类类别数)。
        task_type (str): 任务类型，'regression' 或 'classification'。
        **kwargs: 传递给特定决断头构造函数的额外参数。

    Returns:
        DecisionHead: 一个具体的 DecisionHead 子类实例。
        
    Raises:
        ValueError: 如果提供了未知的 task_type。
    """
    task = TaskType(task_type)
    if task == TaskType.REGRESSION:
        return RegressionHead(output_size=output_size)
    elif task == TaskType.CLASSIFICATION:
        return ClassificationHead(
            n_classes=output_size,
            ovr_threshold=kwargs.get('ovr_threshold', 0.0),
            learnable_threshold=kwargs.get('learnable_threshold', False)
        )
    else:
        # 这段代码理论上不可达，因为 TaskType(task_type) 会在无效时提前失败
        raise ValueError(f"Unknown task type provided: {task_type}")


