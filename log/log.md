# 理论部分进展

## 2017/10/5 董建耕

进展：阅读《多视图几何》，初步理解over-estimated solution

细节：几种常见的代价函数

1. algebric distance

    if H is denoted as follows

    $$
     H=\left[
        \begin{matrix}
        h^{1T} \\
        h^{2T} \\
        h^{3T} \end{matrix}
        \right] 
    $$

    the eqution $x'=Hx$ can be written in the form (detail ignored)

    $$ Ah=0 $$

    where $h=\left[\begin{matrix} h^1 \\ h^2 \\ h^3 \end{matrix}\right]$.

    if there are more than four point correspondence, $Ah=\epsilon\neq0$, can be used as cost function.


2. geometric distance

    When x can be considered as exact, 

    $$ \sum_{i=1}^{\infty}{d(x',Hx)^2 }$$

    otherwise, 

    $$ \sum_{i=1}^{\infty}{d(x',Hx)^2+d(x, H^{-1}x')^2}$$


3. reprojection distance

    Combining $x$ and $x'$ into a point in a 4-D space, it is obvious that $x'=Hx$ represent a supersurface $\nu_H$ in the 4-D space. It is possible to find a $(\hat{x}, \hat{x}')$ on 
    $\nu_H$ that is closest to $(x, x')$. Thus, another cost function is as follows

    $$\sum_{i=1}^{\infty}{d[(x, x'), (\hat{x}, \hat{x}')]}$$