# Theory

任意MIMO系统可以视为多个MISO系统的组合，故只考虑MISO系统。

如果不存在误差，则两个坐标系之间的关系如下，其中$X$为齐次坐标$\left[x_1, x_2, x_3, 1\right]^T$，$y$为标量，$W_{real}$为行向量：

$$ y=W_{real}X $$

考虑测量误差

$$ \widetilde{y}=
    y+\varepsilon_y,
    \widetilde{X}=
    X+\varepsilon_X
$$

$$ \widetilde{y}=
    W_{real}\widetilde{X}
    -W_{real}\varepsilon_X
    +\varepsilon_y
$$

其中

$$ \varepsilon_y\sim
    \mathcal{N}\left(
        \bold{0}, \sigma_y
    \right),
    \varepsilon_X\sim
    \mathcal{N}\left(
        \bold{0}, \Sigma_X
    \right)
$$

于是有：

$$ \widetilde{y}\sim
    \mathcal{N}\left(
        W_{real}\widetilde{X}, \sigma_d
    \right)
$$

其中$\sigma_d=W_{real}\Sigma_XW_{real}^T+\sigma_y$

采用贝叶斯线性回归，记第$i$次迭代后$W$分布为

$$ W\sim\mathcal{N}\left(\bar{\mu_i}, \Sigma_i\right) $$

则贝叶斯线性回归公式为：

$$ p\left(
        W|D_i
    \right)
    \propto
    p\left(
        \widetilde{y}_i\vert\widetilde{X}_i, W
    \right)
    p\left(
        W|D_{i-1}
    \right)
$$

$$ \propto
    \exp{
        \left[
            -\frac{1}{2}
            \left(
                \widetilde{y}_i-W\widetilde{X}_i
            \right)
            \sigma_d^{-1}
            \left(
                \widetilde{y}_i-W\widetilde{X}_i
            \right)^T
        \right]
    }
    \exp{
        \left[
            -\frac{1}{2}
            \left(
                W-\bar{\mu}_{i-1}
            \right)
            \Sigma_{i-1}^{-1}
            \left(
                W-\bar{\mu}_{i-1}
            \right)^T
        \right]
    }
$$

$$ \propto
    \exp{
        \left[
            -\frac{1}{2}
            \left(
                -W\widetilde{X}_i\sigma_d^{-1}\widetilde{y}_i
                -\widetilde{y}_i\sigma_d^{-1}\widetilde{X}_i^TW^T
                -\bar{\mu}_{i-1}\Sigma_{i-1}^{-1}W^T
                -W\Sigma_{i-1}^{-1}\bar{\mu}_{i-1}
                +W\widetilde{X}_i\sigma_d^{-1}\widetilde{X}_i^TW^T
                +W\Sigma_{i-1}^{-1}W^T
            \right)
        \right]
    }
$$

整理可以得到：

$$ \Sigma_i=
    \left(
        \widetilde{X}_i\sigma_d^{-1}\widetilde{X}_i^T
        +\Sigma_{i-1}^{-1}
    \right)^{-1}
$$

$$ \bar{\mu}_i=
    \left(
        \widetilde{y}_i\sigma_d^{-1}\widetilde{X}_i^T
        +\bar{\mu}_{i-1}\Sigma_{i-1}^{-1}
    \right)
    \Sigma_i
$$

对于接收到的第一组数据，根据极大似然估计有

$$ W=
    \widetilde{y}_1\sigma_d^{-1}\widetilde{X}_1^T
    \left(
        \widetilde{X}_1\sigma_d^{-1}\widetilde{X}_1^T
    \right)^{-1}
$$

所以假设$\Sigma_0^{-1}=\bold{0}$，使极大似然估计与贝叶斯回归的参数期望一致。

综上，贝叶斯线性回归过程如下：

$$ initial: \Sigma_0^{-1}=\bold{0},\ \Sigma_X,\ \sigma_y $$

$$ iterative:
    \Sigma_i=
    \left(
        \widetilde{X}_i\sigma_d^{-1}\widetilde{X}_i^T
        +\Sigma_{i-1}^{-1}
    \right)^{-1},\
    \bar{\mu}_i=
    \left(
        \widetilde{y}_i\sigma_d^{-1}\widetilde{X}_i^T
        +\bar{\mu}_{i-1}\Sigma_{i-1}^{-1}
    \right)
    \Sigma_i
$$