帮我写一个计算 etf 的 pe 的 python 工具

查询 etf 持仓的接口为

https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=517180&month=3,6,9,12

结果格式为 html，具体在我上传的文件里。

你需要从 html 提取出有用的信息（最近的一次持仓）。使用 `request`，`bs4` 和 正则来解析。

接着，你需要获取个股的市盈率数据，接口如下：

#### 实时行情数据-雪球[](https://akshare.akfamily.xyz/data/stock/stock.html#id21)

接口: stock_individual_spot_xq

目标地址: https://xueqiu.com/S/SH513520

描述: 雪球-行情中心-个股

限量: 单次获取指定 symbol 的最新行情数据

输入参数

| 名称    | 类型  | 描述                                                         |
| ------- | ----- | ------------------------------------------------------------ |
| symbol  | str   | symbol="SH600000"; 证券代码，可以是 A 股个股代码，A 股场内基金代码，A 股指数，美股代码, 美股指数 |
| token   | float | token=None; 默认不设置token                                  |
| timeout | float | timeout=None; 默认不设置超时参数                             |

输出参数

| 名称  | 类型   | 描述 |
| ----- | ------ | ---- |
| item  | object | -    |
| value | object | -    |

接口示例

```
import akshare as ak

stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol="SPY")
print(stock_individual_spot_xq_df.dtypes)
```

数据示例

```
        item                value
0         代码                  SPY
1      52周最高               562.33
2         均价           558.103271
3         涨幅              -0.8623
4        流通股                 None
5         振幅                 1.16
6         现价               556.48
7         最高               562.33
8     今年以来涨幅                17.82
9        流通值                 None
10      发行日期         727632000000
11        最低               555.83
12  资产净值/总市值       541528495360.0
13   股息(TTM)               6.8432
14  股息率(TTM)               1.2297
15        货币                  USD
16    最小交易单位                    1
17     每股净资产                 None
18    市盈率(静)                 None
19       成交额        29610471457.0
20        涨跌                -4.84
21      每股收益                 None
22        昨收               561.32
23       成交量             53054184
24       市净率                 None
25       周转率                 5.45
26     52周最低               409.21
27        名称       标普500 ETF-SPDR
28  市盈率(TTM)             7461.489
29       交易所                 ARCA
30        时间  2024-07-12 04:10:00
31  基金份额/总股本            973132000
32        今开               561.44
```

最后将 个股的 PE 按权重加权调和平均输出即可。