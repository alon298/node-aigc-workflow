# Node AIGC Workflow · 节点化 AIGC 工作流系统

> 个人开源参考 ComfyUI 节点范式实现的 AIGC 图文视频编排系统。

## 核心特性

- **节点化编排**：Prompt 模板 / 参考图 / 首帧生成 / 图生视频 / 批量输出五类节点
- **一致性锁图**：ConsistencyLock 节点锁定角色种子与参考图，保证多镜头人物/产品一致
- **批量出图出片**：BatchOutput 按模板参数网格批量生成镜头清单
- **素材版本可追溯**：每次执行输出 manifest（含提示词、种子、参考图版本）
- **可插拔后端**：默认 mock 出图出片（写占位与参数），可接入即梦/可灵 API

## 快速开始

```bash
python aigc_nodes.py            # 跑内置电商短视频 5 镜头 demo
python aigc_nodes.py --shots 8  # 自定义镜头数
```

## 示例流

```
PromptTemplate(卖点) → FirstFrame(首帧图) → ConsistencyLock(角色锁)
   → ImageToVideo × N 镜头 → BatchOutput(manifest)
```

## License

MIT
