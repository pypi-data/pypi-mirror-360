
from casrel_datautils_yu.Base_Conf import BaseConfig
from casrel_datautils_yu.data_loader import get_dataloader
from casrel_datautils_yu.process import single_sample_process
baseconf = BaseConfig(bert_path=r"C:\Lucky_dt\2_bj\bj_23AI_KGCode\chapter4_code\CasRel_RE\bert-base-chinese",
                      train_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\test.json",
                      test_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\one_Sample.json",
                      rel_data=r"C:\Users\lidat\PycharmProjects\Casrel_datautils\data\relation.json",batch_size=2)
dataloaders = get_dataloader(baseconf)
print(dataloaders)
print(dataloaders.items())
for batch_idx, (inputs, labels) in enumerate(dataloaders["dev"]):
    print(f"Batch {batch_idx}:")
    print(f"Inputs: {inputs}")
    print(f"Labels: {labels}")
    print("---")


sample={"text": "这是一个测试句子"}
input_tensor, mask_tensor=single_sample_process(baseconf,sample)
print(input_tensor.shape)
print(mask_tensor.shape)
