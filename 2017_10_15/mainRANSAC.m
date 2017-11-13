% data —�? �?��观测数据
% model —�? 适应于数据的模型
% n —�? 适用于模型的�?��数据个数
% k —�? 算法的迭代次�?
% t —�? 用于决定数据是否适应于模型的�??
% d —�? 判定模型是否适用于数据集的数据数�?
% 输出�?
% best_model —�? 跟数据最匹配的模型参数（如果没有找到好的模型，返回null�?
% best_consensus_set —�? 估计出模型的数据�?
% best_error —�? 跟数据相关的估计出的模型错误

% iterations = 0
% best_model = null
% best_consensus_set = null
% best_error = 无穷�?
% while ( iterations < k )
%     maybe_inliers = 从数据集中随机�?择n个点
%     maybe_model = 适合于maybe_inliers的模型参�?
%     consensus_set = maybe_inliers

%     for ( 每个数据集中不属于maybe_inliers的点 �?
%         if ( 如果点�?合于maybe_model，且错误小于t �?
%             将点添加到consensus_set
%     if �?consensus_set中的元素数目大于d �?
%         已经找到了好的模型，现在测试该模型到底有多好
%         better_model = 适合于consensus_set中所有点的模型参�?
%         this_error = better_model究竟如何适合这些点的度量
%         if ( this_error < best_error )
%             我们发现了比以前好的模型，保存该模型直到更好的模型出�?
%             best_model =  better_model
%             best_consensus_set = consensus_set
%             best_error =  this_error
%     增加迭代次数
% 返回 best_model, best_consensus_set, best_error
function [x, y, model] = main()
sigma = 0.1;
N = 10;
x = 1 : N;
y = x + normrnd(0, sigma, size(x));
y(3) = y (3) + 0.8;

y(10) = y(10) - 0.5;

% model:
% y = k x + b
model = zeros(1, 2);
resModel = zeros(1, 2);
maxInterNum = 0;

% distance threshold
t = sqrt(3.84 * sigma^2);

%sample param
numSample = 10^8; iter = 0; s = 2; epsilon = 0.5; p = 0.99;


while iter < numSample
    sample1 = floor(N * rand) + 1;
    sample2 = floor(N * rand) + 1;
    while sample1 == sample2
        sample2 = floor(N * rand) + 1;
    end
    model = getLinearParam([x(sample1), y(sample1)], [x(sample2), y(sample2)]);
    interPointNum = getInterPointNum(x, y, model, t);
    if interPointNum > maxInterNum
        maxInterNum = interPointNum
        resModel = model;
    end
    
    epsilon = 1 - maxInterNum/N;
    numSample = log(1-p)/log(1-(1-epsilon)^s);
    iter = iter + 1;
end

model

figure, scatter(x, y)
xx = 0 :0.5 : N;
yy = model(1) * xx + model(2);
hold on
plot(xx, yy)
plot(xx, yy+t, '-g', xx, yy - t, '-g')

%% Robust cost function
robustCostModel = fmincon(@(resModel)robustCosrFun(x, y, t, resModel), resModel,[], [])
yy = robustCostModel(1) * xx + robustCostModel(2);
plot(xx, yy, 'b')


end

function model = getLinearParam(x1, x2)
    % a line determined by point x1 and x2
    model(1) = (x1(2) - x2(2))/(x1(1) - x2(1));
    model(2) = (x2(1) * x1(2) - x1(1) * x2(2)) / (x2(1) - x1(1))^2;
end

function num = getInterPointNum(x, y, model, t)
    num = 0;
    for i = 1 : length(x)
        if (y(i) - (model(1) * x(i) + model(2)))^2 <= t^2
        num = num + 1;
        end
    end
end

function cost = robustCosrFun(x, y, t, resModel)
    cost = 0;
    for i = 1 : length(x)
        temp = (y(i) - (resModel(1) * x(i) + resModel(2)))^2;
        if temp > t ^2
            cost = cost + t^2;
        else
            cost = cost + temp^2;
        end
    end
    cost
end

