import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer
from collections import defaultdict
import logging

# --- 配置日志 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_head_idx(source, target):
    """在源 token 列表中查找目标 token 列表的起始索引。"""
    target_len = len(target)
    for i in range(len(source)):
        if source[i: i + target_len] == target:
            return i
    return -1

class CasrelDataset(Dataset):
    """为 CasRel 模型创建的自定义数据集。"""
    def __init__(self, data_path, rel_path, tokenizer, max_length=128):
        super().__init__()
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self._load_data(data_path)
        self.rel2id, self.id2rel = self._load_relations(rel_path)
        self.num_rels = len(self.rel2id)

    def _load_data(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                # 假设数据是 JSON Lines 格式 (每行一个 JSON 对象)
                return [json.loads(line) for line in f]
        except json.JSONDecodeError:
            # 如果不是 JSON Lines，尝试作为单个 JSON 数组读取
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载数据失败: {path}, 错误: {e}")
            return []

    def _load_relations(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                rel_data = json.load(f)
            # 假设 relation.json 的格式是 {"0": "关系1", "1": "关系2", ...}
            id2rel = {int(k): v for k, v in rel_data.items()}
            rel2id = {v: int(k) for k, v in rel_data.items()}
            return rel2id, id2rel
        except Exception as e:
            logger.error(f"加载关系文件失败: {path}, 错误: {e}")
            return {}, {}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        return item['text'], item.get('spo_list', [])

def collate_fn(batch, tokenizer, max_length, rel2id):
    """
    DataLoader 的整理函数，将一批样本转换为模型所需的张量。
    """
    texts, spo_lists = zip(*batch)
    num_rels = len(rel2id)

    # 1. Tokenize
    tokenized = tokenizer(
        list(texts),
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors='pt'
    )
    input_ids = tokenized['input_ids']
    attention_mask = tokenized['attention_mask']
    
    batch_size, seq_len = input_ids.shape

    # 初始化所有标签
    batch_sub_heads = torch.zeros(batch_size, seq_len, dtype=torch.long)
    batch_sub_tails = torch.zeros(batch_size, seq_len, dtype=torch.long)
    batch_obj_heads = torch.zeros(batch_size, seq_len, num_rels, dtype=torch.long)
    batch_obj_tails = torch.zeros(batch_size, seq_len, num_rels, dtype=torch.long)

    for i in range(batch_size):
        text_tokens = tokenizer.convert_ids_to_tokens(input_ids[i])
        current_spo_list = spo_lists[i]
        
        if not current_spo_list:
            continue

        s2ro_map = defaultdict(list)
        for spo in current_spo_list:
            subject_tokens = tokenizer.tokenize(spo['subject'])
            object_tokens = tokenizer.tokenize(spo['object'])
            
            sub_head_idx = find_head_idx(text_tokens, subject_tokens)
            obj_head_idx = find_head_idx(text_tokens, object_tokens)
            
            if sub_head_idx != -1 and obj_head_idx != -1:
                sub_tail_idx = sub_head_idx + len(subject_tokens) - 1
                obj_tail_idx = obj_head_idx + len(object_tokens) - 1
                rel_id = rel2id.get(spo['predicate'])

                if rel_id is not None:
                    subject_span = (sub_head_idx, sub_tail_idx)
                    object_relation_span = (obj_head_idx, obj_tail_idx, rel_id)
                    s2ro_map[subject_span].append(object_relation_span)

        if not s2ro_map:
            continue
            
        for sub_span, ro_list in s2ro_map.items():
            sub_head, sub_tail = sub_span
            if sub_head < seq_len and sub_tail < seq_len:
                batch_sub_heads[i, sub_head] = 1
                batch_sub_tails[i, sub_tail] = 1
                for obj_head, obj_tail, rel_id in ro_list:
                    if obj_head < seq_len and obj_tail < seq_len:
                        batch_obj_heads[i, obj_head, rel_id] = 1
                        batch_obj_tails[i, obj_tail, rel_id] = 1

    inputs = {
        'input_ids': input_ids,
        'attention_mask': attention_mask
    }
    labels = {
        'sub_heads': batch_sub_heads,
        'sub_tails': batch_sub_tails,
        'obj_heads': batch_obj_heads,
        'obj_tails': batch_obj_tails
    }
    
    return inputs, labels

# --- 使用示例 ---
if __name__ == '__main__':
    # 假设你的 BERT 模型和数据文件在以下路径
    BERT_PATH = r"C:/Lucky_dt/2_bj/BJ_AI23_KG/12days/KG_code/chapter4_code/CasRel_RE/bert-base-chinese"
    DATA_DIR = "C:/Lucky_dt/2_bj/BJ_AI23_KG/12days/KG_code/chapter4_code/Casrel_datautils_yu/data"
    
    TRAIN_DATA_PATH = f"{DATA_DIR}/test.json" # 使用 test.json 作为示例
    REL_PATH = f"{DATA_DIR}/relation.json"
    BATCH_SIZE = 2
    MAX_LENGTH = 128

    tokenizer = BertTokenizer.from_pretrained(BERT_PATH)
    
    # 1. 创建 Dataset
    dataset = CasrelDataset(
        data_path=TRAIN_DATA_PATH,
        rel_path=REL_PATH,
        tokenizer=tokenizer,
        max_length=MAX_LENGTH
    )
    
    # 2. 创建 DataLoader
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=lambda batch: collate_fn(batch, tokenizer, MAX_LENGTH, dataset.rel2id)
    )

    # 3. 迭代一个批次查看输出
    try:
        inputs, labels = next(iter(dataloader))
        logger.info("成功从 DataLoader 获取一个批次的数据。")
        logger.info(f"输入 Input IDs 形状: {inputs['input_ids'].shape}")
        logger.info(f"输入 Attention Mask 形状: {inputs['attention_mask'].shape}")
        logger.info(f"标签 Subject Heads 形状: {labels['sub_heads'].shape}")
        logger.info(f"标签 Object Heads 形状: {labels['obj_heads'].shape}")

        print(inputs)
        print(labels)
        
        # 打印第一个样本的详细信息
        print("\n--- 第一个样本详情 ---")
        print("Token IDs:", inputs['input_ids'][0].tolist())
        print("Tokens:", tokenizer.convert_ids_to_tokens(inputs['input_ids'][0].tolist()))
        print("Subject Head 标签:", labels['sub_heads'][0].nonzero().squeeze().tolist())
        print("Subject Tail 标签:", labels['sub_tails'][0].nonzero().squeeze().tolist())
        
    except StopIteration:
        logger.warning("DataLoader 为空，请检查数据文件是否正确或为空。")
    except Exception as e:
        logger.error(f"处理数据时发生错误: {e}")