[改进方向]
1. 从多线程改成多进程。
    EventEngine用线程写；
    写一个BaseEngine继承于Process，其他引擎继承于BaseEngine；
    MainEngine管理所有引擎。

2. gateway存放位置
    目前gateway放在TradeEngine里面

3. 交易部分缺少 `价格` 部件