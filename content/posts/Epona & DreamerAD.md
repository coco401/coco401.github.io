

##  World Model with Latent Reward Modeling

![[Pasted image 20260407160120.png|697]]

---
### EPONA介绍
由于**DreamerAD**是基于Epona的,我们先来看一下**Epona**结构:
**Epona**是一个自回归的扩散世界模型,其网络核心概念分为3个部分.
- **Multimodal Spatiotemporal Transformer (MST)**, 用与将历史上下文编码成潜空间表示.
- **Trajectory Planning Diffusion Transformer (TrajDiT)**
- **Next-frame Prediction Diffusion Transformer (VisDiT)**
可以看到Epona 是一个多模态生成的网络
---
#### MST
MST的输入: 过去的latent状态$\{Z_t\}∈\mathbb{R}^{B\times T\times L\times C}$ + 历史轨迹 $\{a_t\}∈\mathbb{R}^{B \times T \times 3}$ 
将他们投影到一个潜空间中然后沿着空间维度,添加位置嵌入结合成$\{E_t\}∈\mathbb{R}^{B\times T\times (L+3)\times D}$ 
$B$ is the batch size, $T$ is the number of condition ing frames, $L = H ×W$ is the number of flattened latents in an image, $C$ is the image latent channel dimension, $D$ is the embedding dimension


然后MST具体会重复12次下面的运算:
1. **时间维度对齐：** `E ← rearrange(E, (b t) l c → (b l) t c))`
    - **作用：** 这是一个维度重排操作。它把批次（b）和空间/模态维度（l）打包，把**时间维度（t**暴露在前面。这就像是把每个空间位置在不同时间点的像素单独抽出来排成一列，为下一步的时间交互做准备。
2. **因果时间注意力运算：** `E ← CausalTemporalLayer(E, CausalMask)`
    - **作用：** 在暴露出的时间维度上做自注意力机制（Self-attention）。关键在于这里加了一个**三角形因果掩码（CausalMask）**。这迫使网络在计算第 t 帧的特征时，只能看到 ≤t 的历史帧，不能看未来的帧。正是这一步，让前面 1 到 T−1 帧的历史信息如流水一般“注入”并累积到了第 T 帧的特征中。
3. **空间维度对齐：** `E ← rearrange(E, (b l) t c → (b t) l c))`
    - **作用：** 再次进行维度重排，把批次（b）和时间（t）打包，把**空间/模态维度l**暴露出来。这意味着现在网络把注意力转回了“单帧画面内部”。
4. **多模态空间注意力运算：** `E ← MultimodalSpatialLayer(E)`
    - **作用：** 在单帧的内部，让视觉的 Token（画面内容）和动作的 Token（驾驶意图）互相进行注意力交互，从而实现多模态信息的深度融合。
在执行完多次这样的block后
- **切片提取：** 此时，模型直接在时间维度 $T$ 上进行切片，**只取出最后一帧（the last frame）的潜空间嵌入**。
- **得到结果：** 这个被切出来的末帧特征就是最终的 $F$，其维度为 $B×(L+3)×D$

#### TrajDiT & VisDiT

本质是 flow matching 的轨迹生成器,使用rectified flow loss $L_{traj}​=E_{a,ϵ,t}​∥v_{traj}​(a(t),t)−(a−ϵ)∥^2$
visdit结构和trjadit结构相似但是使用trajdit生成action作为condition.

#### Chain-of-Forward Training

具体来说,因为epona是一帧帧生成的自回归网络,实际推理中, 真实历史是不存在的，模型只能依赖**它自己之前生成的、带有微小瑕疵的预测帧**来继续往下推演。这种训练和推理环境的不一致会导致微小的误差在循环中像滚雪球一样迅速累积，最终造成长视频的画面质量急剧下降.
**epona使用前推链训练来缓解这个问题:**
训练时就连续推理多步来模拟推理时的噪声,在训练时让他消除这些误差.(因为训练时完整步数降噪推理很慢所以这里也用了单步降噪估算)


![[Pasted image 20260407155912.png]]

### Shortcut Forcing World Model (SF-WM)

原始数据集在10hz的nuplan上, dreamerAD作者首先迁移到了2hz的Navsim上.
一种采样方式:将100步的diffsuion 采样到 1-4步, 从而获得80x的推理速度.
灵感来源于shortcut model. [[2410.12557] One Step Diffusion via Shortcut Models](https://arxiv.org/abs/2410.12557)需要明确的是仅对VisDiT做shortcut,对TrajDiT依然是固定步长20步.

具体思想,是使用一个教师模型走更多的步数,学生模型走更少的步数.学生用d/2步数来拟合老师d步的结果.通过不断蒸馏最终获得1步出结果的效果.
![[Pasted image 20260408112604.png]]
### Autoregressive Dense Reward Modeling

##### Reward Annotation and Labeling.

世界模型在探索OOD数据分布时会产生很大的幻觉,因此作者**构建了一个空间受限的探索轨迹词表（Vocabulary）** 这里和EPONA很不一样,因为epona 的轨迹是一个连续的坐标空间非离散的.

针对每一个场景, 从8192条轨迹筛选出256条:
- **空间邻域约束**: 只有落在人类轨迹“邻域”内的候选者才会被保留。具体必须满足严苛的物理限制：纵向偏差 ∣Δx∣≤10m，横向偏差 ∣Δy∣≤5m，以及航向角偏差 Δθ≤20∘。
- **横向均匀采样：** 为了防止筛选出的候选轨迹在某个区域过于密集，系统会根据横向偏差 ∣Δy∣ 对过滤后的轨迹进行排序，并进行等距的均匀采样，最终精确提取出 256 条具有代表性的轨迹，构成最终的探索词表 Γ。
剩下的256条轨迹会丢尽navsim pdm 仿真器每隔0.5s 一共4s来做一个8指标的8次打分具体类别是:
##### 八大指标

1. **无碰撞 (no collisions, NC)**：对应 $R_{nc}$
2. **可行驶区域依从性 (drivable area compliance, DAC)**：对应 $R_{dac}$​。
3. **行驶方向依从性 (driving direction compliance, DDC)**：对应 $R_{ddc}$​。
4. **交通信号灯依从性 (traffic light compliance, TLC)**：对应 $R_{tlc}$
5. **自车进度/轨迹进度 (ego progress, EP)**：对应 $R_{ep}$​。 
6. **碰撞时间 (time-to-collision, TTC)**：对应 $R_{ttc}$​。 
7. **车道保持 (lane keeping, LK)**：对应 $R_{lk}$​。 
8. **历史舒适度 (history comfort, HC)**：对应 $R_{hc}$​。


##### Reward Model Training.
这个相当于是用navsim 仿真器输出了一个分数真值. 输入预测8帧预测轨迹,
$$ r^t_{pred} = RewardModel(traj_{0:t}, his_{-3:t})$$
$$r^t_{pred} = MLP(CrossAttention(Q_r, his_{-3:t}))$$ 其中$$his_{-3:t} = his\_enc(concat[z_{-3},z_{-2},...,z^p_t]) $$
$$Q_r=Q_{base}+C_{cyn}$$
系统为 8 个奖励维度初始化了 8 个独立的可学习基向量 $Q_{base}$​。同时，将轨迹特征和当前的时间步信息相加，得到动态上下文 $C_{cyn}$​。两者结合构成最终的查询向量$Q_r=Q_{base}+C_{cyn}$
最后，利用交叉注意力机制（Cross-Attention），让查询向量去提取潜空间上下文中的关键信息，再经过 MLP 输出这一步的 8 维预测分数
注意0时刻前是3帧真值,0时刻后的z是自回归预测出来的

**Loss**
$$L_{sup} = \sum^8_{k=1}w_k  y(t) BCEWithLogits(r_{pred},r)$$
where ωk and γ(t) denote reward-type and temporal weighting factors respectively.

**本质上是带有动态权重的二元交叉熵损失函数（BCEWithLogits），强迫网络输出的 r​ 去无限逼近 PDM 模拟器给出的真值 r** 通过这个拟合训练，DreamerAD 成功让 AD-RM 学会了**直接看“抽象的潜空间特征”就能猜出 PDM 会打多少分**
## Reinforcement Learning with Vocabulary Sampling

##### Reward Design for RL

最终强化学习reward分为安全项和任务项,
$$ r^t_{total} = L+S = log(\prod_i r^{w_i}_i \times \sum_j w_jr_j)$$

$$ r_{final} = \sum^8_{t=1}w_t \cdot r^t_{total} $$
注意这里是带时间权重的8帧reward相加.
##### 高斯词汇表采样
1. 模型先生成一条基准轨迹 $\tau_{act}$ ，并以此为均值构建一个高斯分布,其中方差固定值$\sigma^2$
2. 计算这些候选轨迹词汇表和基准的马氏距离,将马氏距离转成softmax 概率
3. 最终输入给 GRPO 的这组候选轨迹（共 G 条）分为两部分：$g_1$​ 条根据 Softmax 概率从真实词表中抽取（保证判别性与物理合理性），$g_2$​ 条从基准轨迹的高斯邻域中抽取（用于局部探索）,最终得到每个轨迹的奖励$r^i_{final}$

##### 策略优化与Loss



**LOSS**

$$ L_{total} = L_{actor} + L_{bc} + L_{kl}$$
其中, 行为克隆loss是$\tau_{act}$ 和 真值轨迹的L1 loss; KLloss是计算原始策略分布和更新策略分布的KL散度;
该aactor损失是ppo风格的
$$ L_{actor} = [max(-A_iρ, - A_iclip(ρ,1-e,1+e)])]$$
其中$A_i$ 按照grpo的做法算组优势:
$$ A_i = \frac{r^{i...g}_{final} - mean(r^{i...g}_{final})}{\sqrt{var(r^{i...g}_{final})}} $$
以及为防止每次策略变化太多系统会计算新策略（πθ​）和旧策略（πold​）生成当前轨迹的概率比率: $ρ=exp(\log π _\theta− \log π_{old}​)$
## 指标

### 像素级
(dreamerAD未给出像素重建指标,借用epona的指标)
主要看FID和FVD俩大指标.


|       | FID 2-40 曲线 |     | FVD40 |
| ----- | ----------- | --- | ----- |
| epona |             |     |       |


### 任务级

| ID  | SF-WM | AD-RM | Vocab Sampling | WorldRFT | Flow-GRPO | EPDMS↑   |
| --- | ----- | ----- | -------------- | -------- | --------- | -------- |
| 1   |       |       |                |          |           | 85.1     |
| 2   |       | √     | √              |          |           | 86.4     |
| 3   | √     |       | √              |          |           | 87.0     |
| 4   | √     | √     | √              |          |           | **87.7** |
| 5   | √     | √     |                | √        |           | 86.8     |
| 6   | √     | √     |                |          | √         | 87.0     |
|     |       |       |                |          |           |          |





## 消融实验设计

高亮为预计要做的实验方向.

**实验方向1** VAE 方向.
目前所有看到的 VAE based world model 都未解冻过vae encoder 但部分方法会动decoder部分.

| ID              | encoder |     |
| --------------- | ------- | --- |
| epona           | DCAE    |     |
| dreamerAD       | DCAE    |     |
| ==wan 2.1==     |         |     |
| ==LTX==         | ==LTX== |     |
| ==video dc-ae== |         |     |


**实验方向2** 加速diffusion方向. 对比sf-wm
对强化学习来说快速rollout是必要的.

何凯明团队近期提出了meanflow, drifting model 等单步模型.号称单步sota,可以尝试使用看看.

| ID                    | EPDMS↑ | FVD40 | FID 2-40曲线 |
| --------------------- | ------ | ----- | ---------- |
| dreamerAD(SF-WM)      |        |       |            |
| ==improve mean flow== |        |       |            |
| ==drifting model==    |        |       |            |
| Epona baseline        | 85.1   | 74.88 | 9.05-18.54 |

**实验方向3** 强化学习的reward

1. **思路来源**：文献中的 **AD-R1** 提出了世界模型普遍存在的“乐观偏差（Optimistic Bias）”——因为训练数据都是安全的人类驾驶，模型遇到危险动作时，往往会在潜空间里“脑补”出安全的未来，导致给危险动作打高分
**实验设计**：

- **当前做法**：DreamerAD 依赖过滤后的 256 条高质量/合理的轨迹词表来训练奖励模型。
- **改进**：在训练 AD-RM 时，故意合成一批**反事实的失败轨迹（Counterfactual Negative Samples，如冲出路面、追尾）**喂给世界模型。强制 AD-RM 在潜空间中学习识别这些“灾难性隐状态”，并赋予极高的惩罚分数。
- **预期验证**：设计一个“危险场景召回率”指标。验证加入反事实数据后，模型在极端长尾场景下（如前方急刹车）是否能更准确地给出低分，从而提升整体的防撞率（NC）

1. **思路**:文献 **AdaWM** 强调了对齐和自适应的重要性。DreamerAD 目前是将 8 个维度的奖励通过固定的对数（log）和 sigmoid 函数硬编码加权聚合（Safety 乘积，Task 求和),
- **实验设计**：
    - **当前做法**：无论在直行、转弯还是红绿灯路口，wcoll​,woffroad​ 等聚合权重是固定的超参数。
    - **改进**：利用 AD-RM 提取的隐空间历史上下文特征 his−3:t​，额外训练一个**注意力门控模块（Attention Gating Module）**。让模型根据当前场景的潜空间语义自动输出这 8 个奖励维度的权重。例如：潜特征识别到当前是十字路口，自动调高交通灯依从性（TLC）和防撞（NC）的权重；如果在空旷高速，则自动调高进度（EP）的权重。
    - **预期验证**：在 NavSim 评测中，分析模型是否在特定复杂场景（如无保护左转）下表现得更加智能，且各项子指标的短板得到弥补。

| ID               | EPDMS |     |
| ---------------- | ----- | --- |
| dreamerAD(ad-rm) |       |     |
| ==自适应条件惩罚权重==    |       |     |
| ==反事实失败惩罚==      |       |     |

