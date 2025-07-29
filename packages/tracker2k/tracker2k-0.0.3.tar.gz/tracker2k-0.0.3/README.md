A log tracking client integration code for OpenAI agents sdk


### Quick Start

1. 安装client lib sdk

```
pip install tracker2k
```

2. 集成agent服务代码

```
import tracker2k

# 注：
#   1.app_name：指服务的应用名字，例如：chuxing-assistant, travel-assistant
#   2.env_name：指服务应用的环境名称，例如：dev, pre, prod
#   3.endpoint：指链路远端服务地址
#       - 测试环境：https://ainlp-offline.xiaojukeji.com/asst/logagent/xuanji
#       - 线上环境：http://10.88.151.15:22323/logagent/xuanji
tracker2k.init(app_name="chuxing-assistant", env_name="dev", endpoint="https://ainlp-offline.xiaojukeji.com/asst/logagent/xuanji")


# 注：
#   1 trace_id 对应链路的trace_id
#   2. metadata中的query和uid，对应用户请求query和用户id

with trace(
        workflow_name=f"LPY Agent ({session_id})",
        group_id=f'Lpy Agent',
        trace_id=trace_id,
        metadata={"query": user_input, "uid": uid}
    ):
    ...your code...
```

3. 查看追踪数据

界面地址（测试环境）：https://yunzhi-dev.intra.xiaojukeji.com/#/traceOverview
