# API文档

## 端点

### 分析对话
```
POST /ai/analyze
```

**请求体**
```json
{
  "conversationId": "string",
  "userNo": "string",
  "conversation": "string",
  "messageNum": "string"
}
```

**响应**
```json
{
  "conversationId": "string",
  "userNo": "string",
  "category": "一级-二级-三级",
  "summary": "结构化摘要",
  "message": "success"
}
```

### 健康检查
```
GET /health
```

**响应**
```json
{
  "status": 200,
  "response": {
    "status": "healthy"
  },
  "message": "success"
}
```

## 分类层级

### 一级分类（10个）
- APP下载和注册
- 额度激活咨询
- 提现申请咨询
- 贷款还款咨询
- **费用异议咨询**（最常用）
- 贷后凭证开具
- 机票分期
- 产品活动咨询
- 催收相关业务
- 其他

### 二级分类（78个）
根据一级分类展开

### 三级分类（7个）
- 飞享会员下的3个分类
- 提额卡下的2个分类
- 新提额卡下的2个分类

## 摘要格式

```
【沟通内容】
用户问题要点

【方案详情】
解决方案和金额

【处理结果】
处理状态和后续
```
