# Causal-Sklearn - 基于CausalEngine™核心的因果回归和分类

基于突破性CausalEngine™算法的scikit-learn兼容实现 - 将因果推理带入传统机器学习生态系统。

## 核心概念

**传统机器学习**: 从可观测个体特征到结果的映射(from observable individual fetures to outcome)
- 回归: X → Y (数值结果)  
- 分类: X → Y (类别结果)

**因果机器学习**: 从不可观测个体因果表示到结果的推理(from unobservable individual causal representation to outcome)
- 因果回归: U → Y (数值结果)
- 因果分类: U → Y (类别结果)

数学本质: CausalEngine 学习结构方程 **Y = f(U, ε)** 而非学习条件期望 **E[Y|X]**. 

## 项目概述

Causal-Sklearn将强大的因果推理能力引入到熟悉的scikit-learn生态系统中。基于革命性的CausalEngine™算法构建，它提供了传统ML估计器的直接替代品，能够理解因果关系而不仅仅是相关性。

### 🎯 核心突破
- **因果vs相关**: 超越传统模式匹配，实现真正的因果关系理解
- **鲁棒性优势**: 在噪声和异常值存在时表现出色，远超传统方法
- **数学创新**: 以柯西分布为核心的全新数学框架
- **sklearn兼容**: 完美融入现有ML工作流，无需改变使用习惯

## 🌟 核心特性

- **🔧 Scikit-learn兼容**: 完全兼容sklearn接口，可直接替换`MLPRegressor`和`MLPClassifier`
- **🧠 因果推理**: 超越模式匹配，理解数据背后的因果关系
- **🛡️ 鲁棒性卓越**: 在标签噪声和异常值环境下性能远超传统方法
- **📊 分布预测**: 提供完整的分布输出，而非仅点估计
- **⚙️ 多模式推理**: 支持deterministic、standard、sampling等多种推理模式
- **🎯 真实世界验证**: 在加州房价等真实数据集上展现显著优势

## 📊 实验结果亮点

我们在 `quick_test_causal_engine.py` 脚本中进行了严格的基准测试。结果明确展示了 CausalEngine 的 `standard` 模式在含噪数据下的卓越性能，而 `deterministic` 模式作为因果模型的基线，其表现与传统MLP相似。

### 回归任务 (30% 标签噪声)

在回归任务中，CausalEngine 的 `standard` 模式展现出压倒性优势，各项误差指标均远优于传统方法。

| 方法                       | MAE (↓) | MdAE (↓) | RMSE (↓) | R² (↑) |
| :------------------------- | :------ | :------- | :------- | :----- |
| sklearn                    | 47.60   | 39.28    | 59.87    | 0.8972 |
| pytorch                    | 59.70   | 47.25    | 77.36    | 0.8284 |
| Causal (deterministic)     | 58.55   | 45.20    | 78.12    | 0.8249 |
| **Causal (standard)**      | **11.41** | **10.22** | **13.65** | **0.9947** |

*`standard` 模式通过其独特的因果推理机制，在噪声环境下实现了性能的飞跃，证明了其卓越的鲁棒性。*

### 分类任务 (30% 标签噪声)

在3分类任务中，`CausalClassifier (standard)` 模式在所有关键指标上均达到最佳表现，显著优于所有基线模型。

| 方法                       | Accuracy (↑) | Precision (↑) | Recall (↑) | F1-Score (↑) |
| :------------------------- | :----------- | :------------ | :--------- | :----------- |
| sklearn                    | 0.8850       | 0.8847        | 0.8850     | 0.8848       |
| pytorch                    | 0.8950       | 0.8952        | 0.8950     | 0.8951       |
| sklearn_ovr                | 0.8975       | 0.8987        | 0.8974     | 0.8974       |
| Causal (deterministic)     | 0.8888       | 0.8935        | 0.8890     | 0.8884       |
| **Causal (standard)**      | **0.9225**   | **0.9224**    | **0.9225** | **0.9224**   |

*这再次证明了 CausalEngine 的 `standard` 模式不仅在回归中表现优异，在分类任务中同样具有处理标签噪声的领先优势。*

## 安装

### 通过 PyPI 安装（推荐）

```bash
pip install causal-sklearn
```

### 从源代码安装

```bash
# 克隆仓库
git clone https://github.com/1587causalai/causal-sklearn.git
cd causal-sklearn

# 安装依赖并安装包
pip install -e .
```

### 系统要求

- **Python**: >= 3.8
- **核心依赖**: 
  - numpy >= 1.21.0
  - scipy >= 1.7.0  
  - scikit-learn >= 1.0.0
  - torch >= 1.10.0
  - pandas >= 1.3.0

### 验证安装

```python
import causal_sklearn
print(f"Causal-sklearn version: {causal_sklearn.__version__}")
print("安装成功！🎉")
```

## 快速开始

### 基础使用示例

```python
from causal_sklearn import MLPCausalRegressor, MLPCausalClassifier
from sklearn.datasets import make_regression, make_classification
from sklearn.model_selection import train_test_split

# 回归示例
X, y = make_regression(n_samples=1000, n_features=20, noise=0.1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

regressor = MLPCausalRegressor(mode='standard', random_state=42)
regressor.fit(X_train, y_train)
predictions = regressor.predict(X_test)
distributions = regressor.predict_dist(X_test) # 返回完整的Cauchy分布参数

# 分类示例
X, y = make_classification(n_samples=1000, n_features=20, n_classes=3)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

classifier = MLPCausalClassifier(mode='standard', random_state=42)
classifier.fit(X_train, y_train)
predictions = classifier.predict(X_test)
probabilities = classifier.predict_proba(X_test)
```

### 🚀 快速验证测试

运行快速测试脚本，同时验证回归和分类性能：

```bash
# 运行完整的快速测试（回归+分类）
python scripts/quick_test_causal_engine.py

# 这个脚本将：
# 1. 生成合成数据（回归：4000样本×12特征，分类：4000样本×10特征×3类）
# 2. 在30%噪声下比较8种方法性能
# 3. 统一标准化策略确保公平比较
# 4. 生成完整的性能分析报告和可视化图表
```

**快速测试亮点**：
- ⚡ 快速验证：几分钟内完成全面测试
- 🔄 双任务支持：同时测试回归和分类能力
- 🎯 8种方法对比：sklearn/PyTorch基线 + CausalEngine四种模式
- 📊 科学实验设计：无数据泄露的标准化策略
- 🛡️ 噪声鲁棒性：在30%噪声环境下验证优势

### 🏠 真实世界教程 - 加州房价预测

运行完整的真实世界回归教程，展示CausalEngine的强大性能：

```bash
# 运行真实世界回归教程（sklearn-style版本）
python examples/comprehensive_causal_modes_tutorial_sklearn_style.py

# 这个教程将：
# 1. 加载加州房价数据集（20,640个样本）
# 2. 在30%标签噪声下比较13种方法
# 3. 测试CausalEngine所有4种推理模式
# 4. 生成标准版和扩展版性能对比图表
```

**真实世界教程亮点**：
- 🌍 真实数据：加州房价数据集的完整分析
- 🔬 全面对比：13种方法（传统ML + 稳健回归 + CausalEngine四模式）
- 📊 双重可视化：标准版（9种核心方法）+ 扩展版（13种全方法）
- 🎯 CausalEngine专项：四种推理模式的深度对比分析
- 🛡️ 鲁棒性验证：在30%噪声环境下的真实表现

### 📈 鲁棒性测试脚本

测试算法在不同噪声水平下的鲁棒性表现：

```bash
# 回归算法鲁棒性测试（真实数据集）
python scripts/regression_robustness_real_datasets.py

# 分类算法鲁棒性测试（真实数据集）
python scripts/classification_robustness_real_datasets.py

# 这些脚本将：
# 1. 使用sklearn内置真实数据集
# 2. 测试0%-100%噪声梯度（11个级别）
# 3. 比较多种算法的鲁棒性曲线
# 4. 支持多次运行取平均，提高结果稳定性
```



## 📚 文档与理论基础

### 🧮 数学理论基础
- **[🌟 数学基础 (中文)](docs/mathematical_foundation.md)** - **最核心文档** 完整的CausalEngine理论框架
- **[One-Pager Summary](docs/ONE_PAGER.md)** - Executive summary of CausalEngine

## 📄 许可证

本项目采用Apache License 2.0 - 详见[LICENSE](LICENSE)文件。


## 📖 学术引用

如果您在研究中使用了Causal-Sklearn，请引用：

```bibtex
@software{causal_sklearn,
  title={Causal-Sklearn: Scikit-learn Compatible Causal Regression and Classification},
  author={Heyang Gong},
  year={2025},
  url={https://github.com/1587causalai/causal-sklearn},
  note={基于CausalEngine™核心的因果回归和因果分类算法的scikit-learn兼容实现}
}
```

---

<div align="center">

**🌟 CausalEngine™ - 基于归因行动框架的因果推理引擎 🌟**

*从相关性到因果性，从模式匹配到因果理解*

</div>