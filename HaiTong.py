import easytrader
import time
import tushare as ts
import datetime


user = easytrader.use('htzq_client')
user.connect(r'D:\Program Files\海通证券委托\xiadan.exe') # 类似 r'C:\htzqzyb2\xiadan.exe'
# user.prepare(user='张照博', password='379926', comm_password='379926')
# user.prepare('D:\Program Files\海通证券委托\yh_client.json')  # 配置文件路径

codes = ['600723','002205','002131','002621','002457','600918']

start = time.clock()
# for x in range(10):
#     ti = time.strftime(" %H:%M:%S", time.localtime())
#     names = []
#     price = []
#     for xx in codes:
#         graph_data = ts.get_realtime_quotes(xx)
#         names.append(graph_data.at[0, 'name'])
#         price.append(graph_data.at[0, 'price'])
#     time.sleep(5)
#     print('\n' + ti )
#     print(" | ".join(names))
#     print(" | ".join(price))

# print(time.strftime(" %H:%M:%S", time.localtime()) ,'  ', user.position[0]['市价'])




class User():
    def __init__(self, user):
        self.user = user
        print(user.balance)
        self.zi_jin_yu_e = user.balance['资金余额']
        self.ke_yong_jin_e = user.balance['可用金额']
        self.ke_qu_jin_e = user.balance['可取金额']
        self.zong_zi_chan = user.balance['总资产']
        self.stock = Stock(user.position)

    def buy(self, code, price, amount):
        self.user.buy(code, price, amount)

    def sell(self, code, price, amount):
        self.user.sell(code, price, amount)

    def get_balance(self):
        return self.ke_yong_jin_e

    def user_refresh(self):
        self.user.refresh()

    def get_today_trades(self):
        return self.user.today_trades

    def get_today_entrusts(self):
        return self.user.today_entrusts

    def show(self):
        print("资金余额：%s\n可用资金：%s\n可取金额：%s\n总资产：%s\n"%(self.zi_jin_yu_e, self.ke_yong_jin_e, self.ke_qu_jin_e, self.zong_zi_chan))
        print("当前持仓股票:\n", self.stock.get_position())


class Stock():
    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position


def get_Account():
    return User(user)


if __name__ == '__main__':
    myAccount = User(user)
    myAccount.show()
