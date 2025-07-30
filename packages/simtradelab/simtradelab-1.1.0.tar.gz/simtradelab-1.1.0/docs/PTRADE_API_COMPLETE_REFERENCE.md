# 文档已迁移 📚

> **重要提示**: 此文档已整合到新的统一API参考文档中。

请参考最新的完整文档：**[SimTradeLab API 完整参考文档](SIMTRADELAB_API_COMPLETE_REFERENCE.md)**

新文档包含了：
- ✅ 完整的API接口说明
- ✅ PTrade兼容性指南
- ✅ 使用示例和最佳实践
- ✅ 配置和部署说明
- ✅ 故障排除和常见问题

---

## 历史文档内容

以下为原始PTrade API参考内容，已整合到新文档中：

## API文档

### 使用说明

#### 新建策略

开始回测和交易前需要先新建策略，点击下图中左上角标识进行策略添加。可以选择不同的业务类型（比如股票），然后给策略设定一个名称，添加成功后可以在默认策略模板基础上进行策略编写。

#### 新建回测

策略添加完成后就可以开始进行回测操作了。回测之前需要对开始时间、结束时间、回测资金、回测基准、回测频率几个要素进行设定，设定完毕后点击保存。然后再点击回测按键，系统就会开始运行回测，回测的评价指标、收益曲线、日志都会在界面中展现。

#### 新建交易

交易界面点击新增按键进行新增交易操作，策略方案中的对象为所有策略列表中的策略，给本次交易设定名称并点击确定后系统就开始运行交易了。

交易开始运行后，可以实时看到总资产和可用资金情况，同时可以在交易列表查询交易状态。

交易开始运行后，可以点击交易详情，查看策略评价指标、交易明细、持仓明细、交易日志。

#### 策略运行周期

回测支持日线级别、分钟级别运行，详见handle_data方法。

交易支持日线级别、分钟级别、tick级别运行，日线级别和分钟级别详见handle_data方法，tick级别运行详见run_interval和tick_data方法。

频率：日线级别

当选择日线频率时，回测和交易都是每天运行一次，运行时间为每天盘后。

频率：分钟级别

当选择分钟频率时，回测和交易都是每分钟运行一次，运行时间为每根分钟K线结束。

频率：tick级别

当选择tick频率时，交易最小频率可以达到3秒运行一次。

#### 策略运行时间

盘前运行:

9:30分钟之前为盘前运行时间，交易环境支持运行在run_daily中指定交易时间(如time='09:15')运行的函数；回测环境和交易环境支持运行before_trading_start函数

盘中运行:

9:31(回测)/9:30(交易)~15:00分钟为盘中运行时间，分钟级别回测环境和交易环境支持运行在run_daily中指定交易时间(如time='14:30')运行的函数；回测环境和交易环境支持运行handle_data函数；交易环境支持运行run_interval函数

盘后运行:

15:30分钟为盘后运行时间，回测环境和交易环境支持运行after_trading_end函数(该函数为定时运行)；15:00之后交易环境支持运行在run_daily中指定交易时间(如time='15:10')运行的函数，

#### 交易策略委托下单时间

使用order系列接口进行股票委托下单，将直接报单到柜台。

#### 回测支持业务类型

目前所支持的业务类型:

1.普通股票买卖(单位：股)。

2.可转债买卖(单位：张，T+0)。

3.融资融券担保品买卖(单位：股)。

4.期货投机类型交易(单位：手，T+0)。

5.LOF基金买卖(单位：股)。

6.ETF基金买卖(单位：股)。

#### 交易支持业务类型

目前所支持的业务类型:

1.普通股票买卖(单位：股)。

2.可转债买卖(具体单位请咨询券商，T+0)。

3.融资融券交易(单位：股)。

4.ETF申赎、套利(单位：份)。

5.国债逆回购(单位：份)。

6.期货投机类型交易(单位：手，T+0)。

7.LOF基金买卖(单位：股)。

8.ETF基金买卖(单位：股)。

9.期权交易(单位：手)。

### 开始写策略

#### 简单但是完整的策略

先来看一个简单但是完整的策略:

```python
def initialize(context):
    set_universe('600570.SS')

def handle_data(context, data):
    pass
```

一个完整策略只需要两步:

1. set_universe: 设置我们要操作的股票池，上面的例子中，只操作一支股票: '600570.SS'，恒生电子。所有的操作只能对股票池的标的进行。
2. 实现一个函数: handle_data。

这是一个完整的策略，但是我们没有任何交易，下面我们来添加一些交易

#### 添加一些交易

```python
def initialize(context):
    g.security = '600570.SS'
    # 是否创建订单标识
    g.flag = False
    set_universe(g.security)

def handle_data(context, data):
    if not g.flag:
        order(g.security, 1000)
        g.flag = True
```

这个策略里，当我们没有创建订单时就买入1000股'600570.SS'，具体的下单API请看order函数。这里我们有了交易，但是只是无意义的交易，没有依据当前的数据做出合理的分析。

#### 实用的策略

下面我们来看一个真正实用的策略

在这个策略里，我们会根据历史价格做出判断:

- 如果上一时间点价格高出五天平均价1%，则全仓买入
- 如果上一时间点价格低于五天平均价，则空仓卖出

```python
def initialize(context):
    g.security = '600570.SS'
    set_universe(g.security)
    
def handle_data(context, data):
    security = g.security
    sid = g.security
    
    # 取得过去五天的历史价格
    df = get_history(5, '1d', 'close', security, fq=None, include=False)
    
    # 取得过去五天的平均价格
    average_price = round(df['close'][-5:].mean(), 3)

    # 取得上一时间点价格
    current_price = data[sid]['close']
    
    # 取得当前的现金
    cash = context.portfolio.cash
    
    # 如果上一时间点价格高出五天平均价1%, 则全仓买入
    if current_price > 1.01*average_price:
        # 用所有 cash 买入股票
        order_value(g.security, cash)
        log.info('buy %s' % g.security)
    # 如果上一时间点价格低于五天平均价, 则空仓卖出
    elif current_price < average_price and get_position(security).amount > 0:
        # 卖出所有股票,使这只股票的最终持有量为0
        order_target(g.security, 0)
        log.info('sell %s' % g.security)
```

#### 模拟盘和实盘注意事项

##### 关于持久化

###### 为什么要做持久化处理

服务器异常、策略优化等诸多场景，都会使得正在进行的模拟盘和实盘策略存在中断后再重启的需求，但是一旦交易中止后，策略中存储在内存中的全局变量就清空了，因此通过持久化处理为量化交易保驾护航必不可少。

###### 量化框架持久化处理

使用pickle模块保存股票池、账户信息、订单信息、全局变量g定义的变量等内容。

注意事项：

1. 框架会在before_trading_start（隔日开始）、handle_data、after_trading_end事件后触发持久化信息更新及保存操作；
2. 券商升级/环境重启后恢复交易时，框架会先执行策略initialize函数再执行持久化信息恢复操作。如果持久化信息保存有策略定义的全局对象g中的变量，将会以持久化信息中的变量覆盖掉initialize函数中初始化的该变量。
3. 全局变量g中不能被序列化的变量将不会被保存。您可在initialize中初始化该变量时名字以'__'开头；
4. 涉及到IO(打开的文件，实例化的类对象等)的对象是不能被序列化的；
5. 全局变量g中以'__'开头的变量为私有变量，持久化时将不会被保存；

###### 示例

```python
class Test(object):
    count = 5

    def print_info(self):
        self.count += 1
        log.info("a" * self.count)


def initialize(context):
    g.security = "600570.SS"
    set_universe(g.security)
    # 初始化无法被序列化类对象，并赋值为私有变量，落地持久化信息时跳过保存该变量
    g.__test_class = Test()

def handle_data(context, data):
    # 调用私有变量中定义的方法
    g.__test_class.print_info()
```

###### 策略中持久化处理方法

使用pickle模块保存 g 对象(全局变量)。

###### 示例

```python
import pickle
from collections import defaultdict
NOTEBOOK_PATH = '/home/fly/notebook/'
'''
持仓N日后卖出，仓龄变量每日pickle进行保存，重启策略后可以保证逻辑连贯
'''
def initialize(context):
    #尝试启动pickle文件
    try:
        with open(NOTEBOOK_PATH+'hold_days.pkl','rb') as f:
            g.hold_days = pickle.load(f)
    #定义空的全局字典变量
    except:
        g.hold_days = defaultdict(list)
    g.security = '600570.SS'
    set_universe(g.security)

# 仓龄增加一天
def before_trading_start(context, data):
    if g.hold_days:
        g.hold_days[g.security] += 1
        
# 每天将存储仓龄的字典对象进行pickle保存
def handle_data(context, data):
    if g.security not in list(context.portfolio.positions.keys()) and g.security not in g.hold_days:
        order(g.security, 100)
        g.hold_days[g.security] = 1
    if g.hold_days:
        if g.hold_days[g.security] > 5:
            order(g.security, -100)
            del g.hold_days[g.security]
    with open(NOTEBOOK_PATH+'hold_days.pkl','wb') as f:
        pickle.dump(g.hold_days,f,-1)
```

## 策略引擎简介

### 业务流程框架

ptrade量化引擎以事件触发为基础，通过初始化事件（initialize）、盘前事件（before_trading_start）、盘中事件（handle_data）、盘后事件（after_trading_end）来完成每个交易日的策略任务。

initialize和handle_data是一个允许运行策略的最基础结构，也就是必选项，before_trading_start和after_trading_end是可以按需运行的。

handle_data仅满足日线和分钟级别的盘中处理，tick级别的盘中处理则需要通过tick_data或者run_interval来实现。

ptrade还支持委托主推事件（on_order_response）、交易主推事件（on_trade_response），可以通过委托和成交的信息来处理策略逻辑，是tick级的一个补充。

除了以上的一些事件以外，ptrade也支持通过定时任务来运行策略逻辑，可以通过run_daily接口实现。

### initialize（必选）

```python
initialize(context)
```

#### 使用场景

该函数仅在回测、交易模块可用

#### 接口说明

该函数用于初始化一些全局变量，是策略运行的唯二必须定义函数之一。

注意事项：

该函数只会在回测和交易启动的时候运行一次

#### 可调用接口

set_universe(回测/交易)

set_benchmark(回测/交易)

set_commission(回测)

set_fixed_slippage(回测)

set_slippage(回测)

set_volume_ratio(回测)

set_limit_mode(回测)

set_yesterday_position(回测)

run_daily(回测/交易)

run_interval(交易)

get_trading_day(研究/回测/交易)

get_all_trades_days(研究/回测/交易)

get_trade_days(交易)

convert_position_from_csv(回测)

get_user_name(回测/交易)

is_trade(回测/交易)

get_research_path(回测/交易)

permission_test(交易)

set_future_commission(回测(期货))

set_margin_rate(回测(期货))

get_margin_rate(回测(期货))

create_dir(回测/交易)

set_parameters(回测/交易)

#### 参数

context: Context对象，存放有当前的账户及持仓信息；

#### 返回

None

#### 示例

```python
def initialize(context):
    #g为全局对象
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    order('600570.SS',100)
```

### before_trading_start（可选）

```python
before_trading_start(context, data)
```

#### 使用场景

该函数仅在回测、交易模块可用

#### 接口说明

该函数在每天开始交易前被调用一次，用于添加每天都要初始化的信息，如无盘前初始化需求，该函数可以在策略中不做定义。

注意事项：

1. 在回测中，该函数在每个回测交易日8:30分执行。
2. 在交易中，该函数在开启交易时立即执行，从隔日开始每天9:10分(默认)执行。
3. 当在9:10前开启交易时，受行情未更新原因在该函数内调用实时行情接口会导致数据有误。可通过在该函数内sleep至9:10分或调用实时行情接口改为run_daily执行等方式进行避免。

#### 可调用接口

set_universe(回测/交易)

get_Ashares(研究/回测/交易)

set_yesterday_position(回测)

get_stock_info(研究/回测/交易)

get_index_stocks(研究/回测/交易)

get_fundamentals(研究/回测/交易)

get_trading_day(回测/交易)

get_all_trades_days(研究/回测/交易)

get_trade_days(研究/回测/交易)

get_history(回测/交易)

get_price(研究/回测/交易)

get_individual_entrust(交易)

get_individual_transaction(交易)

convert_position_from_csv(回测)

get_stock_name(研究/回测/交易)

get_stock_status(研究/回测/交易)

get_stock_exrights(研究/回测/交易)

get_stock_blocks(研究/回测/交易)

get_etf_list(交易)

get_industry_stocks(研究/回测/交易)

get_user_name(回测/交易)

get_cb_list(交易)

get_deliver(交易)

get_fundjour(交易)

get_research_path(回测/交易)

get_market_list(研究/回测/交易)

get_market_detail(研究/回测/交易)

permission_test(交易)

get_trade_name(交易)

set_future_commission(回测(期货))

set_margin_rate(回测(期货))

get_margin_rate(回测(期货))

get_instruments(回测/交易(期货))

get_MACD(回测/交易)

get_KDJ(回测/交易)

get_RSI(回测/交易)

get_CCI(回测/交易)

create_dir(回测/交易)

get_opt_objects(研究/回测/交易(期权))

get_opt_last_dates(研究/回测/交易(期权))

get_opt_contracts(研究/回测/交易(期权))

get_contract_info(研究/回测/交易(期权))

set_parameters(回测/交易)

get_cb_info(研究/交易)

get_enslo_security_info(交易)

get_ipo_stocks(交易)

#### 参数

context: Context对象，存放有当前的账户及持仓信息；

data：保留字段暂无数据；

#### 返回

None

#### 示例

```python
def initialize(context):
    #g为全局变量
    g.security = '600570.SS'
    set_universe(g.security)

def before_trading_start(context, data):
    log.info(g.security)

def handle_data(context, data):
    order('600570.SS',100)
```

### handle_data（必选）

```python
handle_data(context, data)
```

#### 使用场景

该函数仅在回测、交易模块可用

#### 接口说明

该函数在交易时间内按指定的周期频率运行，是用于处理策略交易的主要模块，根据策略保存时的周期参数分为每分钟运行和每天运行，是策略运行的唯二必须定义函数之一。

注意事项：

1. 该函数每个单位周期执行一次
2. 如果是日线级别策略，每天执行一次。股票回测场景下，在15:00执行；股票交易场景下，执行时间为券商实际配置时间。
3. 如果是分钟级别策略，每分钟执行一次，股票回测场景下，执行时间为9:31 -- 15:00，股票交易场景下，执行时间为9:30 -- 14:59。
4. 回测与交易中，handle_data函数不会在非交易日触发（如回测或交易起始日期为2015年12月21日，则策略在2016年1月1日-3日时，handle_data不会运行，4日继续运行）。

#### 可调用接口

get_trading_day(回测/交易)

get_all_trades_days(研究/回测/交易)

get_trade_days(研究/回测/交易)

get_history(回测/交易)

get_price(研究/回测/交易)

get_individual_entrust(交易)

get_individual_transaction(交易)

get_gear_price(交易)

get_stock_name(研究/回测/交易)

get_stock_status(研究/回测/交易)

get_stock_exrights(研究/回测/交易)

get_stock_blocks(研究/回测/交易)

get_index_stocks(研究/回测/交易)

get_industry_stocks(研究/回测/交易)

get_fundamentals(研究/回测/交易)

get_Ashares(研究/回测/交易)

get_snapshot(交易)

convert_position_from_csv(回测)

order(回测/交易)

order_target(回测/交易)

order_value(回测/交易)

order_target_value(回测/交易)

order_market(交易)

ipo_stocks_order(交易)

after_trading_order(交易)

after_trading_cancel_order(交易)

etf_basket_order(交易)

etf_purchase_redemption(交易)

cancel_order(回测/交易)

get_stock_info(研究/回测/交易)

get_order(回测/交易)

get_orders(回测/交易)

get_open_orders(回测/交易)

get_trades(回测/交易)

get_position(回测/交易)

get_positions(回测/交易)

get_etf_info(交易)

get_etf_stock_info(交易)

get_etf_stock_list(交易)

get_etf_list(交易)

get_all_orders(交易)

cancel_order_ex(交易)

debt_to_stock_order(交易)

get_user_name(回测/交易)

get_research_path(回测/交易)

get_marginsec_stocks(交易)

get_margincash_stocks(交易)

debt_to_stock_order(交易)

get_margin_contractreal(交易)

get_margin_contract(交易)

marginsec_direct_refund(交易)

get_margin_entrans_amount(交易)

get_margin_contract(交易)

margincash_direct_refund(交易)

marginsec_open(交易)

marginsec_close(交易)

margincash_open(交易)

margincash_close(交易)

margin_trade(交易)

get_marginsec_close_amount(交易)

get_marginsec_open_amount(交易)

get_margincash_close_amount(交易)

get_margincash_open_amount(交易)

get_cb_list(交易)

get_tick_direction(交易)

get_sort_msg(交易)

get_trade_name(交易)

get_margin_rate(回测(期货))

get_instruments(回测/交易(期货)

buy_open(回测/交易(期货)

sell_close(回测/交易(期货)

sell_close(回测/交易(期货)

buy_close(回测/交易(期货)

get_MACD(回测/交易)

get_KDJ(回测/交易)

get_RSI(回测/交易)

get_CCI(回测/交易)

create_dir(回测/交易)

get_opt_objects(研究/回测/交易(期权))

get_opt_last_dates(研究/回测/交易(期权))

get_opt_contracts(研究/回测/交易(期权))

get_contract_info(研究/回测/交易(期权))

set_parameters(回测/交易)

get_covered_lock_amount(交易(期权))

get_covered_unlock_amount(交易(期权))

buy_open(交易(期权))

sell_close(交易(期权))

sell_open(交易(期权))

buy_close(交易(期权))

open_prepared(交易(期权))

close_prepared(交易(期权))

option_exercise(交易(期权))

option_covered_lock(交易(期权))

option_covered_unlock(交易(期权))

get_cb_info(研究/交易)

get_enslo_security_info(交易)

get_ipo_stocks(交易)

check_limit(回测/研究/交易)

#### 参数

context: Context对象，存放有当前的账户及持仓信息；

data：一个字典(dict)，key是标的代码，value是当时的SecurityUnitData对象，存放当前周期（日线策略，则是当天；分钟策略，则是这一分钟）的数据；

注意：为了加速，data中的数据只包含股票池中所订阅标的的信息，可使用data[security]的方式来获取当前周期对应的标的信息；

#### 返回

None

#### 示例

```python
def initialize(context):
    #g为全局变量
    g.security = '600570.SS'
    set_universe(g.security)

def handle_data(context, data):
    order('600570.SS',100)
```

## 策略API介绍

### 设置函数

#### set_universe - 设置股票池

```python
set_universe(security_list)
```

##### 使用场景

该函数仅在回测、交易模块可用

##### 接口说明

设置股票池，股票池是一个股票代码的列表。

注意事项：

1. 股票池内股票代码数量不能超过100只
2. 股票池内股票代码必须是有效的股票代码

##### 参数

security_list：股票代码列表，list类型或str类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_universe(['600570.SS', '000001.SZ'])
```

#### set_benchmark - 设置基准

```python
set_benchmark(security)
```

##### 使用场景

该函数仅在回测、交易模块可用

##### 接口说明

设置策略基准，用于比较策略收益与基准收益。

注意事项：

无

##### 参数

security：基准代码，str类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_benchmark('000300.SS')
```

#### set_commission - 设置佣金费率

```python
set_commission(type, cost, min_trade_cost, tax)
```

##### 使用场景

该函数仅在回测模块可用

##### 接口说明

设置交易佣金费率。

注意事项：

无

##### 参数

type：交易类型，str类型，支持'stock'、'fund'、'bond'、'LOF'

cost：佣金费率，float类型

min_trade_cost：最小佣金，float类型

tax：印花税费率，float类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_commission(type='stock', cost=0.0003, min_trade_cost=5, tax=0.001)
```

#### set_fixed_slippage - 设置固定滑点

```python
set_fixed_slippage(slippage)
```

##### 使用场景

该函数仅在回测模块可用

##### 接口说明

设置固定滑点。

注意事项：

无

##### 参数

slippage：滑点值，float类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_fixed_slippage(0.01)
```

#### set_slippage - 设置滑点

```python
set_slippage(slippage)
```

##### 使用场景

该函数仅在回测模块可用

##### 接口说明

设置滑点。

注意事项：

无

##### 参数

slippage：滑点比例，float类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_slippage(0.001)
```

#### set_volume_ratio – 设置成交比例

```python
set_volume_ratio(ratio)
```

##### 使用场景

该函数仅在回测模块可用

##### 接口说明

设置成交比例。

注意事项：

无

##### 参数

ratio：成交比例，float类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_volume_ratio(0.25)
```

#### set_limit_mode – 设置回测成交数量限制模式

```python
set_limit_mode(mode)
```

##### 使用场景

该函数仅在回测模块可用

##### 接口说明

设置回测成交数量限制模式。

注意事项：

无

##### 参数

mode：限制模式，str类型

##### 返回

None

##### 示例

```python
def initialize(context):
    set_limit_mode('strict')
```

### 获取信息函数

#### 获取行情信息

##### get_history - 获取历史行情

```python
get_history(count, frequency, field, security_list, fq, include, fill, is_dict)
```

###### 使用场景

该函数在回测、交易模块可用

###### 接口说明

获取历史行情数据。

注意事项：

无

###### 参数

count： K线数量，大于0，返回指定数量的K线行情；必填参数；入参类型：int；

frequency：K线周期，现有支持1分钟线(1m)、5分钟线(5m)、15分钟线(15m)、30分钟线(30m)、60分钟线(60m)、120分钟线(120m)、日线(1d)、周线(1w/weekly)、月线(mo/monthly)、季度线(1q/quarter)和年线(1y/yearly)频率的数据；选填参数，默认为'1d'；入参类型：str；

field：指明数据结果集中所支持输出的行情字段；选填参数，默认为['open','high','low','close','volume','money','price']；入参类型：list[str,str]或str；输出字段包括：

open -- 开盘价，字段返回类型：numpy.float64；
high -- 最高价，字段返回类型：numpy.float64；
low --最低价，字段返回类型：numpy.float64；
close -- 收盘价，字段返回类型：numpy.float64；
volume -- 交易量，字段返回类型：numpy.float64；
money -- 交易金额，字段返回类型：numpy.float64；
price -- 最新价，字段返回类型：numpy.float64；
preclose -- 昨收盘价，字段返回类型：numpy.float64(仅日线返回)；
high_limit -- 涨停价，字段返回类型：numpy.float64(仅日线返回)；
low_limit -- 跌停价，字段返回类型：numpy.float64(仅日线返回)；
unlimited -- 判断查询日是否是无涨跌停限制(1:该日无涨跌停限制;0:该日不是无涨跌停限制)，字段返回类型：numpy.float64(仅日线返回)；

security_list：要获取数据的股票列表；选填参数，None表示在上下文中的universe中选中的所有股票；入参类型：list[str,str]或str；

fq：数据复权选项，支持包括，pre-前复权，post-后复权，dypre-动态前复权，None-不复权；选填参数，默认为None；入参类型：str；

include：是否包含当前周期，True –包含，False-不包含；选填参数，默认为False；入参类型：bool；

fill：行情获取不到某一时刻的分钟数据时，是否用上一分钟的数据进行填充该时刻数据，'pre'–用上一分钟数据填充，'nan'–NaN进行填充(仅交易有效)；选填参数，默认为'nan'；入参类型：str；

is_dict：返回是否是字典(dict)格式{str: array()}，True –是，False-不是；选填参数，默认为False；返回为字典格式取数速度相对较快；入参类型：bool；

###### 返回

DataFrame或dict格式的历史行情数据

###### 示例

```python
def handle_data(context, data):
    # 获取过去5天的收盘价
    df = get_history(5, '1d', 'close', '600570.SS', fq=None, include=False)
    log.info(df)
```

##### get_price - 获取历史数据

```python
get_price(security_list, start_date, end_date, frequency, fields, fq, include)
```

###### 使用场景

该函数在研究、回测、交易模块可用

###### 接口说明

获取指定时间段的历史数据。

注意事项：

无

###### 参数

security_list：股票代码列表，list类型或str类型

start_date：开始日期，str类型，格式为'YYYY-MM-DD'

end_date：结束日期，str类型，格式为'YYYY-MM-DD'

frequency：数据频率，str类型，支持'1d'、'1m'等

fields：字段列表，list类型或str类型

fq：复权类型，str类型

include：是否包含当前周期，bool类型

###### 返回

DataFrame格式的历史数据

###### 示例

```python
def handle_data(context, data):
    # 获取指定时间段的数据
    df = get_price('600570.SS', '2023-01-01', '2023-12-31', '1d', ['open', 'close'])
    log.info(df)
```

### 交易相关函数

#### 股票交易函数

##### order - 按数量买卖

```python
order(security, amount, limit_price, style)
```

###### 使用场景

该函数在回测、交易模块可用

###### 接口说明

按指定数量买卖股票。

注意事项：

无

###### 参数

security：股票代码，str类型

amount：交易数量，int类型，正数为买入，负数为卖出

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 买入1000股
    order('600570.SS', 1000)
    # 卖出500股
    order('600570.SS', -500)
```

##### order_target - 指定目标数量买卖

```python
order_target(security, amount, limit_price, style)
```

###### 使用场景

该函数在回测、交易模块可用

###### 接口说明

调整持仓到指定数量。

注意事项：

无

###### 参数

security：股票代码，str类型

amount：目标持仓数量，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 调整持仓到2000股
    order_target('600570.SS', 2000)
```

##### order_value - 指定目标价值买卖

```python
order_value(security, value, limit_price, style)
```

###### 使用场景

该函数在回测、交易模块可用

###### 接口说明

按指定价值买卖股票。

注意事项：

无

###### 参数

security：股票代码，str类型

value：交易价值，float类型

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 买入价值10000元的股票
    order_value('600570.SS', 10000)
```

### 融资融券专用函数

#### 融资融券交易类

##### margincash_open - 融资买入

```python
margincash_open(security, amount, limit_price, style)
```

###### 使用场景

该函数仅在交易模块可用

###### 接口说明

融资买入股票。

注意事项：

需要开通融资融券权限

###### 参数

security：股票代码，str类型

amount：买入数量，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 融资买入1000股
    margincash_open('600570.SS', 1000, 12.50)
```

##### margincash_close - 卖券还款

```python
margincash_close(security, amount, limit_price, style)
```

###### 使用场景

该函数仅在交易模块可用

###### 接口说明

卖券还款。

注意事项：

需要开通融资融券权限

###### 参数

security：股票代码，str类型

amount：卖出数量，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 卖券还款500股
    margincash_close('600570.SS', 500, 13.00)
```

##### marginsec_open - 融券卖出

```python
marginsec_open(security, amount, limit_price, style)
```

###### 使用场景

该函数仅在交易模块可用

###### 接口说明

融券卖出股票。

注意事项：

需要开通融资融券权限

###### 参数

security：股票代码，str类型

amount：卖出数量，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 融券卖出100股
    marginsec_open('600570.SS', 100, 12.50)
```

##### marginsec_close - 买券还券

```python
marginsec_close(security, amount, limit_price, style)
```

###### 使用场景

该函数仅在交易模块可用

###### 接口说明

买券还券。

注意事项：

需要开通融资融券权限

###### 参数

security：股票代码，str类型

amount：买入数量，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

###### 返回

Order对象

###### 示例

```python
def handle_data(context, data):
    # 买券还券50股
    marginsec_close('600570.SS', 50, 12.00)
```

#### 融资融券查询类

##### get_margincash_stocks - 获取融资标的

```python
get_margincash_stocks()
```

###### 使用场景

该函数仅在交易模块可用

###### 接口说明

获取融资标的列表。

注意事项：

需要开通融资融券权限

###### 参数

无

###### 返回

list格式的融资标的列表

###### 示例

```python
def handle_data(context, data):
    # 获取融资标的
    stocks = get_margincash_stocks()
    log.info(stocks)
```

##### get_marginsec_stocks - 获取融券标的

```python
get_marginsec_stocks()
```

###### 使用场景

该函数仅在交易模块可用

###### 接口说明

获取融券标的列表。

注意事项：

需要开通融资融券权限

###### 参数

无

###### 返回

list格式的融券标的列表

###### 示例

```python
def handle_data(context, data):
    # 获取融券标的
    stocks = get_marginsec_stocks()
    log.info(stocks)
```

### 期货专用函数

#### buy_open - 期货买入开仓

```python
buy_open(security, amount, limit_price, style)
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

期货买入开仓。

注意事项：

仅适用于期货交易

##### 参数

security：期货合约代码，str类型

amount：开仓手数，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

##### 返回

Order对象

##### 示例

```python
def handle_data(context, data):
    # 买入开仓1手
    buy_open('IF2312', 1)
```

#### sell_close - 期货卖出平仓

```python
sell_close(security, amount, limit_price, style)
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

期货卖出平仓。

注意事项：

仅适用于期货交易

##### 参数

security：期货合约代码，str类型

amount：平仓手数，int类型

limit_price：限价，float类型，可选

style：交易方式，可选

##### 返回

Order对象

##### 示例

```python
def handle_data(context, data):
    # 卖出平仓1手
    sell_close('IF2312', 1)
```

### 期权专用函数

#### option_exercise - 期权行权

```python
option_exercise(security, amount)
```

##### 使用场景

该函数仅在交易模块可用

##### 接口说明

期权行权操作。

注意事项：

仅适用于期权交易

##### 参数

security：期权合约代码，str类型

amount：行权数量，int类型

##### 返回

Order对象

##### 示例

```python
def handle_data(context, data):
    # 行权2手期权
    option_exercise('10002334.SH', 2)
```

#### get_opt_contracts - 获取期权合约

```python
get_opt_contracts(underlying_symbol)
```

##### 使用场景

该函数在研究、回测、交易模块可用

##### 接口说明

获取指定标的的期权合约列表。

注意事项：

无

##### 参数

underlying_symbol：标的代码，str类型

##### 返回

list格式的期权合约列表

##### 示例

```python
def handle_data(context, data):
    # 获取50ETF期权合约
    contracts = get_opt_contracts('510050.SH')
    log.info(contracts)
```

### 计算函数

#### get_MACD - 获取MACD指标

```python
get_MACD(security, timeperiod)
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

计算MACD技术指标。

注意事项：

无

##### 参数

security：股票代码，str类型

timeperiod：时间周期，int类型

##### 返回

dict格式的MACD指标数据

##### 示例

```python
def handle_data(context, data):
    # 计算MACD指标
    macd = get_MACD('600570.SS', 20)
    log.info(macd)
```

#### get_KDJ - 获取KDJ指标

```python
get_KDJ(security, timeperiod)
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

计算KDJ技术指标。

注意事项：

无

##### 参数

security：股票代码，str类型

timeperiod：时间周期，int类型

##### 返回

dict格式的KDJ指标数据

##### 示例

```python
def handle_data(context, data):
    # 计算KDJ指标
    kdj = get_KDJ('600570.SS', 20)
    log.info(kdj)
```

### 其他函数

#### log - 日志记录

```python
log.info(message)
log.warning(message)
log.error(message)
log.debug(message)
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

记录日志信息。

注意事项：

无

##### 参数

message：日志消息，str类型

##### 返回

None

##### 示例

```python
def handle_data(context, data):
    log.info('策略开始执行')
    log.warning('资金不足')
    log.error('下单失败')
```

#### run_daily - 按日周期处理

```python
run_daily(func, time)
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

设置按日执行的定时任务。

注意事项：

无

##### 参数

func：要执行的函数，function类型

time：执行时间，str类型，格式为'HH:MM'

##### 返回

None

##### 示例

```python
def initialize(context):
    run_daily(before_market_open, time='09:15')

def before_market_open(context):
    log.info('盘前准备')
```

#### run_interval - 按间隔周期处理

```python
run_interval(func, seconds)
```

##### 使用场景

该函数仅在交易模块可用

##### 接口说明

设置按间隔执行的定时任务。

注意事项：

无

##### 参数

func：要执行的函数，function类型

seconds：间隔秒数，int类型

##### 返回

None

##### 示例

```python
def initialize(context):
    run_interval(check_market, 60)

def check_market(context):
    log.info('市场检查')
```

#### is_trade - 业务代码场景判断

```python
is_trade()
```

##### 使用场景

该函数在回测、交易模块可用

##### 接口说明

判断当前是否为交易时间。

注意事项：

无

##### 参数

无

##### 返回

bool类型，True表示交易时间，False表示非交易时间

##### 示例

```python
def handle_data(context, data):
    if is_trade():
        log.info('当前为交易时间')
    else:
        log.info('当前为非交易时间')
```

#### check_limit - 代码涨跌停状态判断

```python
check_limit(security)
```

##### 使用场景

该函数在回测、研究、交易模块可用

##### 接口说明

检查股票是否涨跌停。

注意事项：

无

##### 参数

security：股票代码，str类型

##### 返回

dict格式的涨跌停状态信息

##### 示例

```python
def handle_data(context, data):
    # 检查涨跌停状态
    limit_info = check_limit('600570.SS')
    log.info(limit_info)
```

## 数据结构

### Context对象

Context对象包含当前的账户信息和持仓信息。

#### 属性

portfolio：Portfolio对象，包含账户和持仓信息

#### 示例

```python
def handle_data(context, data):
    # 获取总资产
    total_value = context.portfolio.total_value
    # 获取可用资金
    cash = context.portfolio.cash
    # 获取持仓
    positions = context.portfolio.positions
```

### Portfolio对象

Portfolio对象包含账户的资产和持仓信息。

#### 属性

total_value：总资产，float类型

cash：可用资金，float类型

positions：持仓字典，dict类型

market_value：持仓市值，float类型

#### 示例

```python
def handle_data(context, data):
    portfolio = context.portfolio
    log.info(f'总资产: {portfolio.total_value}')
    log.info(f'可用资金: {portfolio.cash}')
    log.info(f'持仓市值: {portfolio.market_value}')
```

### Position对象

Position对象包含单个股票的持仓信息。

#### 属性

security：股票代码，str类型

amount：持仓数量，int类型

avg_cost：平均成本，float类型

price：当前价格，float类型

market_value：持仓市值，float类型

#### 示例

```python
def handle_data(context, data):
    position = get_position('600570.SS')
    log.info(f'持仓数量: {position.amount}')
    log.info(f'平均成本: {position.avg_cost}')
    log.info(f'当前价格: {position.price}')
```

### Order对象

Order对象包含订单信息。

#### 属性

security：股票代码，str类型

amount：订单数量，int类型

price：订单价格，float类型

status：订单状态，str类型

order_id：订单ID，str类型

#### 示例

```python
def handle_data(context, data):
    order_obj = order('600570.SS', 1000)
    log.info(f'订单ID: {order_obj.order_id}')
    log.info(f'订单状态: {order_obj.status}')
```

## 注意事项

1. 所有股票代码必须使用标准格式，如'600570.SS'、'000001.SZ'
2. 交易函数只能在交易时间内调用
3. 回测和交易环境下某些函数的行为可能有所不同
4. 期货和期权交易需要相应的权限
5. 融资融券交易需要开通相应权限
6. 数据获取函数可能受到网络和数据源限制
7. 技术指标计算需要足够的历史数据
8. 定时任务的执行时间可能受到系统负载影响

## 版本信息

本文档基于PTrade API官方文档编写，版本信息请参考官方网站。

文档最后更新时间：2025年7月6日
