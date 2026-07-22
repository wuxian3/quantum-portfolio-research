# 退化感知的量子信息递归投资组合选择：初步调研与压力测试

**研究日期：2026-07-22**  
**结论等级：值得推进，但必须定位为“量子贡献归因与基准设计”，不宜定位为当前硬件的量子优势证明。**

## 1. 执行摘要

这轮工作回答了三个最重要的止损问题。

1. **递归归约机制本身是否有效？** 有效。以“仅由最优/次优独立集退化结构产生的 5-shot 理想化采样器”为例，直接采到 MIS 的概率只有 **56.5%**，但经过固定节点与经典归约后，纯递归路径成功率升至 **90.3%**；加入论文算法中的全局 incumbent 后升至 **93.7%**。
2. **这种提升是否具有量子专属性？** 目前没有证据。最低度数这一纯图启发式在同一递归外壳下已达到 **86.0%**；本次强经典可行域局部搜索达到 **100% incumbent 成功率**。原始 qReduMIS 论文也报告过同一框架换成 SA 后，在其 39 个测试实例上全部成功。
3. **退化是否会夸大“冻结节点识别”的容易程度？** 会。本次 73 个核中，平均 **58.9%** 的节点属于“至少一个 MIS”，但平均只有 **13.8%** 属于“所有 MIS”。因此论文使用的 in-set 指标更接近“存在一个最优延拓的安全节点”，并不是通常意义上的强制 backbone。

最值得继续追的不是“qReduMIS 是否比 standalone QAOA 好”，而是：

> 在严格匹配递归外壳、采样预算和经典计算预算后，QAOA 的节点边缘信息能否稳定超过退化空模型、图结构启发式和强经典采样器？

当前证据给出的判断是：**论文方向 GO，量子专属收益主张 NO-GO，先做归因论文最稳。**

## 2. 文献与算法复原

目标工作把股票相关性阈值图转成 MIS：先执行 exposed-corner / simplicial 类型的精确归约，再在剩余 kernel 上采样独立集。每次量子调用只保留观测到的前两档独立集大小，计算节点边缘频率，从最高的 4 个节点中随机选择一个固定为 in-set，然后删除该节点及其邻居并继续归约。系统性测试使用 Nikkei 225 数据、输入规模 26–44、每个规模 20 个随机子集、阈值为子相关矩阵绝对值的均值，并筛出 73 个非平凡 first kernels；模拟实验每次调用 5 shots，硬件实验每次调用 10 shots。

一个容易被遗漏但会显著影响归因的细节是：算法同时维护局部递归路径 `S` 和全局 incumbent `W`。每次调用得到的最大样本独立集都可与此前已固定节点拼接来更新 `W`。因此“最终成功率”同时包含两类作用：

- **节点指导作用**：采样边缘概率是否帮助固定安全节点；
- **直接求解作用**：采样器是否已经在某次调用中直接给出最优残余解。

本测试把这两部分分开报告。

## 3. 测试设计

### 3.1 数据与实例

- 使用公开的 Chang–Meade–Beasley–Sharaiha 投资组合基准中的 Nikkei 225 相关矩阵。
- 按论文公式构图，使用与公开代码一致的 exposed-corner reducer。
- 构造 73 个 first-kernel 实例，**严格匹配论文 Table IV 的核大小分箱数量**：4–5、6–9、10–13、14–15、16、17–18、19–20、21、22 分别为 11、9、9、7、8、9、8、7、5 个。
- 这 73 个实例不是作者的同一组随机种子，因此用于机制复测和消融，不用于逐点复现论文曲线。
- 另按论文硬件表中四个市场的规模与密度反推阈值，重建 DAX、FTSE、S&P、Nikkei 大核。FTSE 得到 46 个节点而论文表为 45 个，其他三个规模一致；因此大核结果是压力测试，不是精确硬件实例复现。

### 3.2 采样器/选择器消融

所有方法共享相同的 top-4 随机固定、删除邻居、精确归约和 incumbent 外壳，只替换信息源：

- `random_vertex`：全核均匀随机节点；
- `min_degree`：最低度数的 4 个节点中随机选一个；
- `random_greedy`：随机顺序构造 maximal IS，按样本边缘频率选择；
- `exact_top2_5shot`：从全部 \(\alpha\) 与 \(\alpha-1\) 独立集按数量加权均匀抽 5/10 个样本；它是**退化结构空模型**，不是物理采样器；
- `exact_top2_rank`：直接使用全部 \(\alpha\) 与 \(\alpha-1\) 集合的精确边缘排名，是结构信号上限；
- `annealed_local_search`：始终保持独立集可行性的加/删/交换式退火局部搜索；它是强经典控制，不是论文 SA 代码的逐行复刻。

### 3.3 退化感知指标

定义：

\[
F_\exists=\{v:\exists I^\star,\;v\in I^\star\},\qquad
F_\forall=\{v:\forall I^\star,\;v\in I^\star\}.
\]

其中 \(F_\exists\) 对应论文的 in-set ground truth，\(F_\forall\) 才是所有最优解共享的 mandatory/backbone 节点。核心指标为：

\[
B_\exists=\frac{|F_\exists|}{|K|},\qquad
L_\exists=\frac{P(v\in F_\exists)-B_\exists}{1-B_\exists}.
\]

另外对每次固定定义一步后悔值：

\[
r_t=\alpha(K_t)-\left[1+\alpha(K_t-N[v_t])\right].
\]

在本实现中有精确恒等式：

\[
\alpha(K_0)-|S_\text{local}|=\sum_t r_t.
\]

这使得“哪一步选择造成了最终损失”可以被直接定位，而不只看最终 PMIS。

## 4. 结果一：退化本身制造了较高的安全节点基线

| 指标 | 均值 | 中位数 |
| --- | --- | --- |
| Existentially safe baseline | 58.9% | 52.9% |
| Mandatory/backbone fraction | 13.8% | 11.1% |
| Min-degree top-4 safe precision | 87.3% | 100.0% |
| Exact top-2 top-4 safe precision | 97.6% | 100.0% |
| Exact top-2 marginal mass on safe vertices | 87.6% | 92.2% |

进一步观察：

- 73 个核的平均规模为 **14.1**，平均密度 **0.599**，平均 \(\alpha\) 为 **4.18**。
- MIS 数量中位数为 **3**，均值 **5.21**，最大 **37**。
- **27/73** 个核没有任何 mandatory 节点；**12/73** 个核中每个节点都属于至少一个 MIS。
- 精确 top-2 边缘排名相对最低度数的 top-4 安全精度平均多 **10.3 个百分点**；有 **26** 个核差距至少 25 个百分点。这些差距与较高 hardness \(H\) 正相关（Spearman \(\rho=0.620\)），与较高的 \(|F_\exists|/|K|\) 负相关（\(\rho=-0.670\)）。真正有采样器辨识价值的实例，通常不是“几乎所有节点都安全”的高度退化实例。

![Structural signal](qfinance_pilot/fig_structural_signal.png)

![Degeneracy gap](qfinance_pilot/fig_degeneracy_gap.png)

## 5. 结果二：73 个小核上的同外壳消融

### 5.1 每次调用 5 个样本

| Selector | Direct hit | First safe | Path success | Incumbent success | Incumbent AR | Calls | One-call end |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Random vertex | — | 58.7% | 57.0% | 57.0% | 0.860 | 1.08 | 92.2% |
| Min degree | — | 87.7% | 86.0% | 86.0% | 0.968 | 1.20 | 82.4% |
| Random greedy | 75.0% | 80.7% | 78.4% | 88.7% | 0.975 | 1.14 | 86.6% |
| Exact top-2 sampled | 56.5% | 91.6% | 90.3% | 93.7% | 0.984 | 1.14 | 87.3% |
| Exact top-2 rank | — | 97.4% | 97.0% | 97.0% | 0.993 | 1.16 | 85.1% |
| Annealed local search | 100.0% | 99.3% | 99.1% | 100.0% | 1.000 | 1.14 | 87.0% |

最关键的三段归因是：

- `exact_top2_5shot`：**56.5% 直接命中 → 90.3% 递归路径 → 93.7% incumbent**。递归外壳贡献 +33.8 个百分点，incumbent 再救回 +3.4 个百分点。
- `random_greedy`：**75.0% 直接命中 → 78.4% 路径 → 88.7% incumbent**。它说明直接样本质量、节点指导质量和 incumbent 救援可以方向不同，不能合并成一个 PMIS 解读。
- `min_degree` 无任何采样，仍达到 **86.0%**；强经典局部搜索达到 **100% incumbent**。

按实例配对 bootstrap，`exact_top2_5shot` 相对 `min_degree` 的 incumbent 优势为 **7.7 个百分点**，95% CI **[4.8, 10.9]**；精确排名上限相对最低度数为 **11.1 个百分点**，95% CI **[7.8, 14.7]**。因此结构边缘信息确有附加价值，但它并不等于量子专属价值。

![Small ablation](qfinance_pilot/fig_small_ablation_5shot.png)

### 5.2 每次调用 10 个样本

| Selector | Direct hit | First safe | Path success | Incumbent success | Incumbent AR | Calls | One-call end |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Random vertex | — | 58.5% | 56.5% | 56.5% | 0.858 | 1.08 | 92.0% |
| Min degree | — | 87.4% | 85.5% | 85.5% | 0.967 | 1.20 | 82.9% |
| Random greedy | 87.2% | 87.0% | 85.4% | 95.0% | 0.990 | 1.16 | 85.6% |
| Exact top-2 sampled | 76.1% | 93.9% | 92.9% | 96.7% | 0.992 | 1.15 | 86.4% |
| Exact top-2 rank | — | 97.4% | 97.0% | 97.0% | 0.992 | 1.17 | 84.7% |
| Annealed local search | 100.0% | 99.5% | 99.1% | 100.0% | 1.000 | 1.14 | 86.4% |

把 5 shots 增至 10 shots 后，理想化 top-2 采样器的直接命中由 56.5% 升至 **76.1%**，incumbent 成功由 93.7% 升至 **96.7%**；随机贪心的 incumbent 由 88.7% 升至 **95.0%**。有限 shot 的边缘估计误差是主要变量之一，但增加 shots 同样帮助经典采样器，仍不能单独证明量子信息优势。

## 6. 结果三：刻意筛选“采样器可能有用”的 14 个核

为了避免平均结果被容易实例淹没，我在 250 个 \(N=22\) 阈值扫描实例中预先筛选：核规模至少 10、\(|F_\exists|/|K|\le0.65\)、最低度数 top-4 安全精度不高于 0.75、而精确 top-2 排名安全精度至少 0.75。得到 14 个候选核。

| Selector | Direct hit | First safe | Path success | Incumbent success | Incumbent AR | Calls | One-call end |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Random vertex | — | 30.1% | 29.6% | 29.6% | 0.734 | 1.05 | 94.7% |
| Min degree | — | 74.8% | 74.8% | 74.8% | 0.928 | 1.14 | 86.3% |
| Random greedy | 52.5% | 54.7% | 53.4% | 69.0% | 0.905 | 1.10 | 90.4% |
| Exact top-2 sampled | 36.5% | 68.0% | 66.1% | 75.1% | 0.923 | 1.11 | 89.1% |
| Exact top-2 rank | — | 92.7% | 92.7% | 92.7% | 0.976 | 1.11 | 89.0% |
| Annealed local search | 100.0% | 97.6% | 97.5% | 100.0% | 1.000 | 1.12 | 87.9% |

这里出现了一个非常值得写成论文主线的结果：

- 精确 top-2 **排名上限**达到 **92.7%**，显著高于最低度数的 74.8%，配对差 **17.9 个百分点**，95% CI **[12.1, 24.4]**；
- 但只抽 **5 个** top-2 样本时，incumbent 成功只有 **75.1%**，与最低度数的差仅 **0.4 个百分点**，95% CI **[-6.6, 7.6]**；
- 强经典局部搜索仍达到 100%。

因此必须区分两个问题：

1. **结构信号是否存在？** 存在，精确边缘排名能明显胜过最低度数；
2. **极少 shots 能否可靠估计该信号？** 在这些刻意挑选的实例上，5 shots 通常不能。

这比单纯比较最终 PMIS 更有研究价值，也更可能形成可复现、可否证的论文结论。

![Shortlist ablation](qfinance_pilot/fig_shortlist_ablation_5shot.png)

## 7. 结果四：四个硬件规模市场核的经典压力测试

| Market | K | Density | alpha | Safe frac. | Mandatory frac. | MILP median ms | Anneal direct | Anneal incumbent | Greedy incumbent | Min-degree incumbent | Anneal calls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DAX | 49 | 0.291 | 17 | 55.1% | 18.4% | 3.78 | 100.0% | 100.0% | 94.0% | 82.0% | 2.23 |
| FTSE | 46 | 0.278 | 16 | 47.8% | 21.7% | 2.91 | 100.0% | 100.0% | 94.5% | 85.5% | 1.73 |
| S&P | 68 | 0.200 | 21 | 33.8% | 27.9% | 3.98 | 96.0% | 100.0% | 32.5% | 17.5% | 3.23 |
| Nikkei | 78 | 0.169 | 28 | 46.2% | 25.6% | 4.38 | 100.0% | 100.0% | 79.5% | 70.5% | 3.35 |

在当前机器与 SciPy/HiGHS MILP 表达下，四个核的精确 MIS 中位求解时间为 **2.9–4.4 ms**，每次求解的 MIP node 中位数均为 1。该时间只代表本环境和表达，不应外推为通用复杂度结论；但足以说明这些重建实例目前不适合作为量子优势基准。

可行域局部搜索的单样本成功率随计算量迅速上升：10 sweeps/vertex 时 DAX、FTSE、Nikkei、S&P 分别为 90.4%、93.6%、71.4%、24.4%；20 sweeps/vertex 时分别为 99.8%、99.8%、95.4%、51.4%；40 sweeps/vertex 时 S&P 也升至 82.2%。每次调用取 5 个样本后，20 sweeps/vertex 在四个市场上的 incumbent 成功率均为 100%。

![Large controls](qfinance_pilot/fig_large_classical_controls.png)

![Annealing effort](qfinance_pilot/fig_annealing_effort.png)

一个重要反例是 S&P：最低度数的**第一步安全率为 100%**，但最终路径/incumbent 成功率只有 **17.5%**。这证明第一步 frozen-node precision 不能替代整条轨迹的累计 regret；后续任何一次错误固定都可能破坏最优性。

## 8. 初步科学结论

### 8.1 可以支持的结论

- qReduMIS 的“采样—固定—归约”机制确实能把不完美的直接求解器放大成较高的端到端成功率。
- 最优与次优独立集的边缘分布包含超出最低度数的结构信息，尤其在低安全基线、高 hardness 的核上。
- 退化、经典归约、有限-shot 估计和 incumbent 是四个可独立贡献性能的因素；必须分别消融。
- 当前公开市场核中，强经典方法非常容易饱和，适合机制演示，不适合量子专属收益论证。

### 8.2 目前不能支持的结论

- 不能由“qReduMIS 显著优于 standalone QAOA”推出量子 sampler 提供了不可替代的信息；这首先证明的是递归外壳优于一次性直接采样。
- 不能把“属于至少一个 MIS”当成强冻结/backbone。高度退化时随机节点也可能很容易满足这一标准。
- 不能用 current PMIS 或 approximation ratio 单独区分节点指导作用与 incumbent 的直接样本命中作用。
- 不能用这些 \(K\le22\) 或重建 \(K\approx45\text{--}78\) 市场核主张 classical hardness。

## 9. 推荐的论文定位与最小可行研究计划

### 建议标题

**When Does the Sampler Matter? Degeneracy-Aware Attribution in Quantum-Informed Recursive Portfolio Selection**

### 最小充分实验矩阵

第一阶段只做以下四组，避免无边界探索：

1. **精确归因层**：\(F_\exists\)、\(F_\forall\)、退化数、top-2 精确边缘、逐步 regret、cascade；规模控制在可精确枚举或条件 MILP 的范围。
2. **同外壳采样器层**：QAOA、uniform top-2 null、随机贪心、强 SA/局部搜索、最低度数/一到两个图启发式；所有方法共享 top-M、归约、停止条件和 incumbent。
3. **有限-shot 层**：1、2、5、10、25、50 shots，报告边缘排名稳定性，而不只报告 PMIS。
4. **预算匹配层**：同时报告 samples、objective evaluations、wall-clock、QPU calls；至少提供 shot-matched 和 wall-clock-matched 两种比较。

### 建议预注册的主指标

- first-step 与 all-step 的 safe precision；
- mandatory precision；
- graph-adjusted safe lift；
- cumulative regret \(\sum r_t\)；
- direct sample / local path / incumbent 三套成功率；
- reduction cascade 和 kernel shrink per call；
- time-to-safe-decision，而不仅是 time-to-solution。

## 10. 明确止损线

以下阈值是本项目的建议性 go/no-go 规则，不是普适定理：

1. 若最强匹配预算的经典采样器在超过 80% 的实例上直接成功率高于 0.9，这些实例只保留作机制展示，不投入 QPU 预算。
2. 若 \(|F_\exists|/|K|\ge0.7\) 或图启发式 first-safe precision \(\ge0.8\)，先证明 QAOA 的 graph-adjusted lift 至少高 0.05，且按实例 bootstrap 的 95% CI 排除 0，再进入硬件测试。
3. 若超过 80% 的运行在一次固定后结束，PMIS 不作为主指标，改以 first-choice regret、cascade 和 incumbent 分解为主。
4. 若强经典局部搜索在 5 个样本内已达到 incumbent 成功率 \(\ge0.95\)，不得把同一实例用于量子优势叙事；只能研究 shot efficiency、能耗或更严格预算下的信号质量。
5. 在获得作者的 exact graph seeds、QAOA 参数或 shot-level bitstrings 前，不投入大规模 QAOA 参数优化；否则很容易把实例差异、postprocessing 和参数训练差异混入 sampler 归因。

## 11. 下一步最省探索成本的推进顺序

- **第 1 优先级：** 获取/请求论文 73 个精确 first kernels 与四个硬件 kernel，以及每次调用的 postprocessed shot bitstrings。把真实 QAOA 输出直接灌入本测试外壳，不先重跑参数优化。
- **第 2 优先级：** 在本报告筛出的 14 个“低安全基线、结构边缘有优势、最低度数较弱”实例上做 5–50 shot 曲线。这些实例比随机市场核更能检验 sampler 信息。
- **第 3 优先级：** 只在 QAOA 对强经典匹配预算基线出现稳定正 lift 后，扩大到动态市场图、权重或真实回测；否则第一篇应聚焦方法学与负结果的可靠归因。

## 12. 局限性

- 本轮没有真实 Helios shot-level 数据，因此**没有直接复现或否定论文的 QAOA 边缘信号**。
- 73 个核只匹配论文的核大小分布，不是同一随机种子集合。
- `exact_top2_5shot` 是退化结构理想空模型；`annealed_local_search` 是自建强经典控制，均不等同于论文硬件采样器或其 SA 实现。
- 四个大核的阈值由论文表中四舍五入的 \(\lambda\)、规模与密度反推；FTSE 存在 1 个节点差异。
- MILP 时间高度依赖实现、预处理、机器与计时方式，仅用于当前实例的易解性筛查。
- 当前结果没有金融回测含义；这里只测试图优化层的算法归因。

## 13. 复现环境与文件

环境：Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, NetworkX 3.6.1, Matplotlib 3.10.8, sortedcontainers 2.4.0；Linux x86_64，5 个可见 AMD EPYC 9V74 vCPU。

核心输出：

- `qfinance_pilot/structural_audit.csv`：73 个核的精确退化与安全节点审计；
- `qfinance_pilot/small_ablation_summary.csv`：5/10-shot 小核消融摘要；
- `qfinance_pilot/large_ablation_summary.csv`：四个大核的经典控制摘要；
- `qfinance_pilot/shortlist_ablation_summary.csv`：14 个 sampler-relevant 核的摘要；
- `qfinance_pilot/instances.json`、`large_kernel_graphs.json`、`hardness_sweep_shortlist_graphs.json`：图记录；
- 逐 trial CSV 与 Python 源码收录在压缩包中。

## 14. 主要参考文献

1. *Quantum-Informed Portfolio Selection: An End-to-End Pipeline Validated on Trapped-Ion Hardware with Real Market Data*, arXiv:2607.01037v2, 2026.
2. *qReduMIS: A Quantum-Informed Reduction Algorithm for the Maximum Independent Set Problem*, arXiv:2503.12551v3, 2026.
3. T.-J. Chang, N. Meade, J. E. Beasley, Y. M. Sharaiha, *Heuristics for cardinality constrained portfolio optimisation*, Computers & Operations Research 27, 2000.

---

**最终判断：** 第一篇值得推进，而且初步结果已经形成明确、可发表的核心矛盾——**结构边缘信号存在，但少量 shots 未必可估；递归放大真实存在，但并不具有量子专属性；市场图退化会显著抬高“安全冻结”基线。** 后续应把有限-shot 信息增益和 matched-classical attribution 作为主问题，而不是继续堆更多普通 market-graph QAOA 实验。
