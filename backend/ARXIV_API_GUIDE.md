# arXiv API 集成文档

## 概述

本模块实现了arXiv论文搜索功能，支持关键词搜索、领域过滤、年份范围过滤和发表场所过滤。

## API端点

### 1. 搜索论文

**端点**: `GET /api/papers/search`

**查询参数**:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| query | string | 是 | 搜索关键词 | "deep learning" |
| field | string | 否 | 领域过滤 | "cs.AI", "cs.CL" |
| year_min | int | 否 | 最小年份 | 2020 |
| year_max | int | 否 | 最大年份 | 2024 |
| venue | string | 否 | 发表场所 | "NeurIPS", "ICML" |
| page | int | 否 | 页码 (从1开始) | 1 |
| page_size | int | 否 | 每页数量 (1-100) | 10 |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "papers": [
      {
        "paper_id": "2401.00001",
        "title": "Attention Is All You Need",
        "authors": ["Vaswani et al."],
        "summary": "论文摘要...",
        "published": "2024-01-01T00:00:00",
        "published_year": 2024,
        "updated": "2024-01-02T00:00:00",
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "pdf_url": "https://arxiv.org/pdf/2401.00001.pdf",
        "arxiv_url": "http://arxiv.org/abs/2401.00001v1"
      }
    ],
    "total": 15234,
    "page": 1,
    "page_size": 10,
    "total_pages": 1524
  }
}
```

### 2. 获取论文详情

**端点**: `GET /api/papers/<paper_id>`

**路径参数**:
- paper_id: arXiv论文ID (如 "2301.00001")

**响应示例**:

```json
{
  "success": true,
  "data": {
    "paper_id": "2301.00001",
    "title": "论文标题",
    "authors": ["作者1", "作者2"],
    "summary": "完整摘要",
    "published": "2023-01-01T00:00:00",
    "categories": ["cs.AI"],
    "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf"
  }
}
```

### 3. 获取PDF下载链接

**端点**: `GET /api/papers/<paper_id>/pdf`

**响应示例**:

```json
{
  "success": true,
  "data": {
    "paper_id": "2301.00001",
    "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf"
  }
}
```

## 常见arXiv分类

| 分类代码 | 说明 |
|---------|------|
| cs.AI | Artificial Intelligence |
| cs.CL | Computation and Language (NLP) |
| cs.CV | Computer Vision |
| cs.LG | Machine Learning |
| cs.NE | Neural and Evolutionary Computing |
| stat.ML | Statistics - Machine Learning |

## 使用示例

### cURL示例

```bash
# 基础搜索
curl "http://localhost:5000/api/papers/search?query=deep+learning&page=1&page_size=5"

# 领域过滤
curl "http://localhost:5000/api/papers/search?query=transformers&field=cs.AI"

# 年份范围
curl "http://localhost:5000/api/papers/search?query=neural+networks&year_min=2023&year_max=2024"

# 获取论文详情
curl "http://localhost:5000/api/papers/2301.00001"

# 获取PDF链接
curl "http://localhost:5000/api/papers/2301.00001/pdf"
```

### JavaScript示例

```javascript
// 搜索论文
async function searchPapers(query) {
  const response = await fetch(
    `/api/papers/search?query=${encodeURIComponent(query)}&page=1&page_size=10`
  );
  const result = await response.json();
  return result;
}

// 获取论文详情
async function getPaperDetails(paperId) {
  const response = await fetch(`/api/papers/${paperId}`);
  const result = await response.json();
  return result;
}
```

## 错误处理

所有API端点都返回统一的错误格式：

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

常见HTTP状态码:
- 400: 请求参数错误
- 404: 论文未找到
- 500: 服务器内部错误

## 实现细节

### ArxivClient类

主要方法:
- `search_papers()`: 搜索论文
- `get_paper_details()`: 获取论文详情
- `get_paper_pdf_url()`: 获取PDF链接

依赖库:
- `feedparser`: 解析arXiv的Atom feed格式响应
- `requests`: HTTP请求

### 查询构建

arXiv API支持丰富的查询语法:
- `all:关键词`: 在标题、摘要、作者中搜索
- `cat:分类`: 按分类过滤
- `submitted_date:[开始 TO 结束]`: 时间范围过滤

更多信息请参考: https://arxiv.org/help/api
