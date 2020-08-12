"""
交易策略模型
起码几十种
但是还没想好
怎么对接进去
先不管了睡觉
"""
from Entity import User,Stock
import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import leastsq
from datetime import datetime, timedelta
from Data import get_stock_basics, get_hist_data
from Neo4j import get_Graph
from Mysql import get_all_columns_with_label


def hist_predict(stock='600196'):
    # all_hist = get_all_columns_with_label('p_change')
    # for x in all_hist.keys():
    #     for idx in range(len(all_hist[x])):
    #         all_hist[x][idx] = round(all_hist[x][idx], 0)
    # with open("cache/all_hist_p_price.txt", 'w', encoding='utf8') as o:
    #     o.write(str(all_hist))
    with open("cache/all_hist_p_price.txt", 'r', encoding='utf8') as i:
        all_hist = eval(i.read())
    target = all_hist[stock]
    alen = len(all_hist)
    count = 0
    for length in range(3, 6):
        nihe = []
        print("\n\n 复星医药最近%s天的走势"%length)
        print(target[-length:])
        for x in all_hist.keys():
            count += 1
            # if count % (alen//20) == 0:
            #     print("[","="*(count // (alen//20)),'>',' '*(20 - (count // (alen//20))), ']')
            data = all_hist[x]
            d_len = len(data)
            if d_len < 10:
                continue
            if x != stock:
                fu = target[-length:]
                for window in range(d_len - length):
                    comp = data[window:window + length]
                    if len(comp) != length:
                        continue
                    flag = True
                    for index in range(length):
                        try:
                            if -1 <= comp[index] - fu[index] and comp[index] - fu[index] <= 1:
                                continue
                            else:
                                flag = False
                        except Exception as e:
                            flag = False
                            continue
                    if flag:
                        print("拟合到股票数据接近，STOCK: %s" % x, "Index: %s, PRICE_CHANGE:"%(d_len - window))
                        try:
                            if d_len > 2 * length + window:
                                print(data[window:window + length * 2])
                                nihe.append(data[window + length])
                            else:
                                print(data[window, d_len])
                                nihe.append(data[window + length])
                        except Exception as e:
                            continue
        print("%s天内，拟合的平均趋势为%s"%(length, sum(nihe)/len(nihe)))




class simulation_User():
    balance = {
                       '资金余额': 100,
                       '可用金额': 4000,
                       '可取金额': 30,
                       '总资产': 5100,
              }
    position = [{
        '证券代码': '600100',
        '可用股份': 400,
        '冻结股份': 200,
        '成本价格': 19.40,
        '市场价': 17.88
    },
        {
            '证券代码': '600220',
            '可用股份': 400,
            '冻结股份': 400,
            '成本价格': 11.79,
            '市场价': 11.28
        }
    ]
    def __index__(self):
        print("初始化一个模拟器")


def residuals(p, y, x, fun):
    """
    实验数据x, y和拟合函数之间的差，p为拟合需要找到的系数
    """
    return y - fun(x, p)


#直线方程
def f_1(x, a, b):
    return a * x +b

# 二次曲线方程
def f_2(x, A, B, C):
    return A * x * x + B * x + C

# 三次曲线方程
def f_3(x, A, B, C, D ):
    return A * x * x * x + B * x * x + C * x + D

def func_sin(x, A, k, theta):
    """
    数据拟合所用的函数: A*cos(2*pi*k*x + theta)
    """
    return A * np.sin(k * x + theta)


def nihe(data):
    if type(data[0]) == str:
        data = [float(x) for x in data]
    x0 = np.linspace(0, len(data), len(data))
    y0 = data
    func = [f_2, f_3, func_sin]
    offset_min = 10000000
    func_min_offset = -1
    para_min_offset = []
    for f in range(len(func)):
        x2 = np.arange(0, len(data), len(data))
        try:
            para = curve_fit(func[f], x0, y0)[0]
        except Exception as e:
            # print(e)
            return 0,0,-1
        if f == 0:
            A, B, C = para
            y2 = func[f](x2, A, B, C)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
        elif f == 1:
            A, B, C, D = para
            y2 = func[f](x2, A, B, C, D)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
        elif f == 2:
            try:
                A, B, C = para
            except Exception as e:
                print("!!!!!",para,e)
            y2 = func[f](x2, A, B, C)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
        elif f == 3:
            A, B = para
            y2 = func[f](x2, A, B)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
    return para_min_offset, func[func_min_offset], func_min_offset


def filter():
    para = ['open',
             'high',
             'close',
             'low',
             'volume',
             'price_change',
             'p_change',
             'ma5',
             'ma10',
             'ma20',
             'v_ma5',
             'v_ma10',
             'v_ma20',
             'turnover']
    graph = get_Graph()
    roe = graph.run("MATCH (n) WHERE EXISTS(n.`净资产收益率(ROE)`) RETURN n.stock_id,n.name, n.`净资产收益率(ROE)`").data()
    code_roe = { x['n.stock_id']:x for x in roe }
    codes = list(get_stock_basics().index)
    names = get_stock_basics()['name'].tolist()
    for c in codes:
        try:
            if c[0]=='3':
                continue
            x = get_hist_data(c, '2020-07-28','2020-07-29')
            if x.at['2020-07-29','close'] < x.at['2020-07-29','ma20'] and \
                    float(x.at['2020-07-29','p_change']) < 3 and \
                    float(code_roe[c]['n.`净资产收益率(ROE)`']) > 1:
                print("%s, 二十日线：%s, 今日价格：%s, 今日涨幅：%s, ROE:%s" %
                      (names[codes.index(c)], x.at['2020-07-29','ma20'],
                       x.at['2020-07-29','close'], x.at['2020-07-29','p_change'],
                       code_roe[c]['n.`净资产收益率(ROE)`'] ))
        except Exception as e:
                continue

def main():
    # su = simulation_User()
    # user = User(su)
    # pro = ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
    # all_data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # ts_code = list(all_data.ts_code)
    # symbol = list(all_data.symbol)


    realtime_Price = [
                      17.70, 17.92, 17.71, 17.84, 17.97,
                      17.91, 17.96, 18.06, 18.11, 18.12,
                      18.18, 18.28, 18.47, 18.45, 18.36,
                      18.45, 18.48, 18.64, 18.69, 18.67,
                      18.56, 18.60, 18.46, 18.46, 18.44,
                      18.35, 18.38, 18.39, 18.31, 18.16,
                      18.16, 18.10, 18.17, 18.29, 18.14,
                      18.23, 18.15, 18.17, 18.24, 18.16,
                      17.99, 17.91, 17.86, 17.89, 17.88,
                    17.70, 17.92, 17.71, 17.84, 17.97,
                    17.91, 17.96, 18.06, 18.11, 18.12,
                    18.18, 18.28, 18.47, 18.45, 18.36,
                    18.45, 18.48, 18.64, 18.69, 18.67,
                    18.56, 18.60, 18.46, 18.46, 18.44,
                    18.35, 18.38, 18.39, 18.31, 18.16,
                    18.16, 18.10, 18.17, 18.29, 18.14,
                    18.23, 18.15, 18.17, 18.24, 18.16,
                    17.99, 17.91, 17.86, 17.89, 17.88
                      ]
    # print(su.position)
    data = realtime_Price[:20]
    para, func, func_min_offset = nihe(data)
    if para == 0:
        return
    x2 = np.arange(0, len(data) + 20)
    y2 = None
    print(para, func_min_offset)
    if func_min_offset == 0:
        A, B, C = para
        y2 = func(x2, A, B, C)
    elif func_min_offset == 1:
        A, B, C, D = para
        y2 = func(x2, A, B, C, D)
    elif func_min_offset == 2:
        A, B, C = para
        y2 = func(x2, A, B, C)

    if max(y2) != y2[-1]:
        max_y2 = max(y2)
        print("Max_y2:%s" % max_y2)
        for x in range(len(y2[-20:])):
            if y2[-20 + x] == max_y2:
                print("卖出点在：%s, 时间为：%s" % (max_y2, datetime.now() + timedelta(minutes=2 * x)))
    elif min(y2) != y2[-1]:
        min_y2 = min(y2)
        print("Min_y2:%s"%min_y2)
        for x in range(len(y2[-20:])):
            if y2[-20 + x] == min_y2:
                print("买入点在：%s, 时间为：%s" % (min_y2, datetime.now() + timedelta(minutes=2 * x)))
    else:
        if max(y2) < y2[len(data)]:
            print("持续下行中！！")
        else:
            print("持续上升中！！")

if __name__ == '__main__':
    # main()
    # filter()
    hist_predict()