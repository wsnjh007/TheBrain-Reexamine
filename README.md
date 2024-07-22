# TheBrain-Reexamine
TB的复盘小工具，就是把每天修改过的节点，定时归集到「复盘」节点下面，方便复盘

### 版本更新日志:
#### v0.01: 初始版本，包含基础的API请求和处理逻辑。
#### v0.02: 添加了通过startTime和endTime进行查询的功能，确保查询的内容为两次复盘之间修改的。
#### v0.03: 修复了时区问题，确保查询时间为UTC时间。
#### v0.04: 美化输出结果，并添加修改时间信息。
#### v0.05: 查询需要添加父节点的ThoughtID的名称信息，并在恰当的地方进行输出。
#### v0.06: 修改逻辑为使用syncUpdateDateTime进行查询，并输出详细信息。
#### v0.07: 查询后，响应内容中'modType': 803的ThoughtID选择extraAId，否则ThoughtID选择sourceId。
#### v0.08: 新增功能，增加'modType'字典的内容输出，并处理log.txt不存在的情况。
#### v0.09: 删除'modType'为102的ThoughtID，并去重处理重复的ThoughtID。
#### v0.10: 去除modType为301的ThoughtID，并处理缺失syncUpdateDateTime的情况。
