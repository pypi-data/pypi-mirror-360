CasRel 数据处理工具包

这是一个基于 CasRel 模型的中文关系抽取数据处理工具包，支持 BERT 预训练模型。

## 支持的 BERT 模型

- **bert-base-chinese**: 默认中文 BERT 基础模型，适用于通用中文任务，参数量适中，bert_dim=768。

## 安装

- pip install casrel_datautils

## 使用示例

以下是一个使用 `casrel_datautils` 进行数据加载和单条样本处理的示例代码：

```python
from casrel_datautils.Base_Conf import BaseConfig
from casrel_datautils.data_loader import get_dataloader
from casrel_datautils.process import single_sample_process

# 配置基础参数
baseconf = BaseConfig(
    bert_path=r"C:\Lucky_dt\2_bj\BJ_AI23_KG\12days\KG_code\chapter4_code\CasRel_RE\bert-base-chinese", #模型路径
    train_data=r"本地数据路径train.json",
    test_data=r"本地数据路径test.json",
    rel_data=r"本地关系数据路径relation.json",
    batch_size=2
)

# 获取数据加载器
dataloaders = get_dataloader(baseconf)

# 单条样本处理
sample = {"text": "这是一个测试句子"}
input_tensor, mask_tensor = single_sample_process(baseconf, sample)
print(input_tensor.shape)
print(mask_tensor.shape)
```

### 说明

- **BaseConfig**: 用于设置 BERT 模型路径、数据路径和批次大小等参数。
- **get_dataloader**: 返回训练、验证和测试的数据加载器。
- **single_sample_process**: 处理单条文本样本，返回输入张量和掩码张量。

## 注意事项

- 确保数据文件（如 `train.json`、`test.json`、`relation.json`）路径正确。
- 根据任务需求选择合适的 BERT 模型。