
import torch
import torch.nn as nn
from transformers import BertModel

class CasrelModel(nn.Module):
    """CasRel 模型: A Novel Cascade Binary Tagging Framework for Relational Triple Extraction"""
    def __init__(self, bert_path, num_rels, dropout_prob=0.1):
        super().__init__()
        self.bert = BertModel.from_pretrained(bert_path)
        self.bert_dim = self.bert.config.hidden_size
        self.num_rels = num_rels

        # 主语识别模块 (Subject Tagger)
        self.subject_tagger = nn.Linear(self.bert_dim, 2)

        # 关系-宾语联合识别模块 (Relation-specific Object Taggers)
        self.object_tagger = nn.Linear(self.bert_dim, self.num_rels * 2)
        
        self.dropout = nn.Dropout(dropout_prob)

    def forward(self, input_ids, attention_mask, subject_ids=None):
        """
        Args:
            input_ids: (batch_size, seq_len)
            attention_mask: (batch_size, seq_len)
            subject_ids: (batch_size, seq_len) - 训练时提供，用于获取特定主语的表示
        """
        # 1. BERT 编码
        # (batch_size, seq_len, bert_dim)
        encoder_outputs = self.bert(input_ids, attention_mask=attention_mask)[0]
        encoder_outputs = self.dropout(encoder_outputs)

        # 2. 主语头/尾预测 (Subject Prediction)
        # (batch_size, seq_len, 2)
        pred_sub_heads_logits = self.subject_tagger(encoder_outputs)
        pred_sub_tails_logits = self.subject_tagger(encoder_outputs)
        
        pred_sub_heads = torch.sigmoid(pred_sub_heads_logits)
        pred_sub_tails = torch.sigmoid(pred_sub_tails_logits)

        # 3. 关系-宾语预测 (Object Prediction)
        if subject_ids is not None:
            # 训练模式：使用真实主语来预测宾语
            # (batch_size, 1, bert_dim)
            sub_output = torch.bmm(subject_ids.unsqueeze(1).float(), encoder_outputs)
            # (batch_size, seq_len, bert_dim)
            sub_output_expanded = sub_output.expand_as(encoder_outputs)
            
            # 融合 BERT 输出和主语表示
            # (batch_size, seq_len, bert_dim)
            combined_output = encoder_outputs + sub_output_expanded
        else:
            # 预测模式：直接使用 BERT 输出
            combined_output = encoder_outputs

        # (batch_size, seq_len, num_rels * 2)
        pred_obj_logits = self.object_tagger(combined_output)
        # (batch_size, seq_len, num_rels, 2)
        pred_obj_logits = pred_obj_logits.view(pred_obj_logits.size(0), pred_obj_logits.size(1), self.num_rels, 2)
        
        pred_obj_heads_logits = pred_obj_logits[..., 0]
        pred_obj_tails_logits = pred_obj_logits[..., 1]

        pred_obj_heads = torch.sigmoid(pred_obj_heads_logits)
        pred_obj_tails = torch.sigmoid(pred_obj_tails_logits)

        return {
            'sub_heads': pred_sub_heads, 
            'sub_tails': pred_sub_tails,
            'obj_heads': pred_obj_heads, 
            'obj_tails': pred_obj_tails
        }

    def compute_loss(self, predictions, labels):
        """计算 CasRel 模型的损失"""
        loss_fct = nn.BCEWithLogitsLoss(reduction='none')

        # 主语损失
        sub_heads_loss = loss_fct(predictions['sub_heads'][..., 0], labels['sub_heads'].float())
        sub_tails_loss = loss_fct(predictions['sub_tails'][..., 1], labels['sub_tails'].float())
        sub_loss = (sub_heads_loss + sub_tails_loss).mean()

        # 宾语损失
        obj_heads_loss = loss_fct(predictions['obj_heads'], labels['obj_heads'].float())
        obj_tails_loss = loss_fct(predictions['obj_tails'], labels['obj_tails'].float())
        obj_loss = (obj_heads_loss + obj_tails_loss).mean()

        return sub_loss + obj_loss

# --- 使用示例 ---
if __name__ == '__main__':
    BERT_PATH = r"C:/Lucky_dt/2_bj/BJ_AI23_KG/12days/KG_code/chapter4_code/CasRel_RE/bert-base-chinese"
    NUM_RELS = 19 # 根据你的 relation.json 文件
    
    # 1. 实例化模型
    model = CasrelModel(bert_path=BERT_PATH, num_rels=NUM_RELS)
    
    # 2. 模拟输入
    batch_size = 2
    seq_len = 64
    input_ids = torch.randint(0, 21128, (batch_size, seq_len)) # 假设 vocab_size 为 21128
    attention_mask = torch.ones(batch_size, seq_len, dtype=torch.long)
    subject_ids = torch.zeros(batch_size, seq_len) # 模拟一个主语
    subject_ids[:, 5] = 1

    # 3. 前向传播
    outputs = model(input_ids, attention_mask, subject_ids=subject_ids)

    print("模型实例化和前向传播成功！")
    print(f"预测的主语头形状: {outputs['sub_heads'].shape}")
    print(f"预测的宾语头形状: {outputs['obj_heads'].shape}")
