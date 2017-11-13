
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