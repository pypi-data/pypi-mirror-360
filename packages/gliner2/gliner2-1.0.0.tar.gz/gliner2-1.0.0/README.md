Here's a refined version of your GLiNER2 documentation that improves clarity, flow, and formatting while preserving technical depth and usability:

---

# **GLiNER2: Unified Schema-Based Information Extraction**

> *Next-gen extraction for text, structured data, and classification—powered by [Fastino AI](https://fastino.ai)*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Fastino](https://img.shields.io/badge/Powered%20by-Fastino-blue)](https://fastino.ai)

GLiNER2 is the successor to [GLiNER](https://github.com/urchade/GLiNER), introducing a schema-driven framework to consolidate entity extraction, classification, and structured parsing—all within a unified API.

---

## ✨ What Makes GLiNER2 Unique?

| Capability              | Traditional Tools | **GLiNER2** |
| ----------------------- | ----------------- | ----------- |
| Entity Extraction       | ✅                 | ✅ Enhanced  |
| Text Classification     | ❌                 | ✅ New       |
| Structured Data Parsing | ❌                 | ✅ New       |
| Unified Schema API      | ❌                 | ✅ New       |
| Multi-task Processing   | ❌                 | ✅ New       |

Instead of juggling multiple models, simply define **what** you want and extract it all in **one pass**.

---

## 🚀 Quick Start

### Installation

```bash
pip install gliner2
```

### Basic Usage

```python
from gliner2 import GLiNER2

extractor = GLiNER2.from_pretrained("fastino/gliner-v2")

results = extractor.extract_entities(
    "Dr. Sarah Johnson from Stanford published groundbreaking AI research.",
    ["person", "organization", "field"]
)
print(results)
# {'entities': {'person': ['Dr. Sarah Johnson'], 'organization': ['Stanford'], 'field': ['AI research']}}
```

---

## 🧠 Schema-Based Extraction

Define a custom schema for **entities**, **classification**, and **structured fields**:

```python
schema = (extractor.create_schema()
    .entities(["person", "company", "location"])
    .classification("sentiment", ["positive", "negative", "neutral"])
    .structure("product")
        .field("name", dtype="str")
        .field("price", dtype="str")
        .field("features", dtype="list")
)

results = extractor.extract("Apple CEO Tim Cook announced iPhone 15 for $999...", schema)
```

---

## 🎯 Entity Extraction

### Flexible & Domain-Aware

```python
text = "Patient took 400mg ibuprofen for severe headache yesterday."
results = extractor.extract_entities(text, ["medication", "dosage", "symptom", "timeframe"])
```

#### With Descriptions

```python
results = extractor.extract_entities(
    "The API endpoint /users/{id} returns 404 when user not found.",
    {
        "endpoint": "API URLs and paths like /users/{id}",
        "http_status": "HTTP status codes like 200, 404, 500",
        "error_condition": "Error scenarios and failure cases"
    }
)
```

> 💡 **Tips**:
>
> * Use clear descriptions for ambiguous terms
> * Prefer specific labels like `"email_address"` over `"email"`

---

## 📊 Text Classification

### Single & Multi-Label Support

```python
results = extractor.classify_text(
    "This product exceeded my expectations!",
    {"sentiment": ["positive", "negative", "neutral"]}
)
```

### Multi-Label with Threshold

```python
results = extractor.classify_text(
    "The camera is excellent but battery life is disappointing.",
    {
        "aspects": {
            "labels": ["camera", "battery", "display", "performance", "design"],
            "multi_label": True,
            "cls_threshold": 0.4
        }
    }
)
```

---

## 🗃️ Structured Data Extraction

### Turn Unstructured Text into JSON

```python
text = """
John Smith (CEO) at TechCorp can be reached at john@techcorp.com or +1-555-0123.
The company, founded in 2010, specializes in AI software with 150 employees.
"""

results = extractor.extract_json(
    text,
    {
        "contact": [
            "name::str::Full name of the person",
            "title::str::Job title or position", 
            "email::str::Email address",
            "phone::str::Phone number"
        ],
        "company": [
            "name::str::Company name",
            "founded::str::Year founded",
            "industry::str::Business sector",
            "size::str::Number of employees"
        ]
    }
)
```

---

## 🧩 Multi-Task Extraction with Schemas

Analyze text with entities, classification, and structured fields—**all at once**.

```python
schema = (extractor.create_schema()
    .entities({
        "person": "Names of people",
        "organization": "Companies and institutions",
        "location": "Geographic locations"
    })
    .classification("category", {
        "business": "Corporate news",
        "technology": "Tech developments",
        "research": "Academic studies"
    })
    .structure("announcement")
        .field("what", dtype="str")
        .field("when", dtype="str")
        .field("impact", dtype="list")
        .field("stakeholders", dtype="list")
)
```

---

## 🧪 Advanced Configuration

### Precision Control per Field

```python
schema = (extractor.create_schema()
    .structure("financial_data")
        .field("amount", dtype="str", threshold=0.95)
        .field("date", dtype="str", threshold=0.8)
        .field("description", dtype="str", threshold=0.6)
)
```

### Data Type & Choices

```python
schema = (extractor.create_schema()
    .structure("product")
        .field("name", dtype="str")
        .field("features", dtype="list")
        .field("category", dtype="str", choices=["electronics", "software", "service"])
        .field("tags", dtype="list", choices=["popular", "new", "discounted", "premium"])
)
```

---

## 🏭 Real-World Applications

### Healthcare

```python
text = "Patient Mary Johnson, age 65, visited Dr. Roberts on March 15th..."
# Extracts patient, doctor, medications, urgency, and prescriptions
```

### Legal Contracts

```python
text = "Employment Agreement between TechCorp Inc. and Jane Doe..."
# Extracts parties, dates, clauses, penalties, obligations
```

### Finance

```python
text = "Transaction ID: TXN-2024-001. Transfer of $5,000..."
# Extracts transaction IDs, parties, amounts, purposes
```

---

## 📚 API Summary

| Component            | Description                   |
| -------------------- | ----------------------------- |
| `GLiNER2`            | Main model class              |
| `create_schema()`    | Schema builder                |
| `extract()`          | Unified extraction method     |
| `extract_entities()` | Fast entity-only extraction   |
| `classify_text()`    | Text classification by schema |
| `extract_json()`     | Structured record parsing     |

---

## 🤝 Contribute

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md):

1. Fork and branch
2. Add your feature + test it
3. Submit a PR

---

## 🙌 Credits

* **GLiNER2** by [Fastino AI](https://fastino.ai)
* **Original GLiNER** by [Urchade Zaratiana](https://github.com/urchade/GLiNER)

---

<div align="center"><strong>Built with ❤️ by the Fastino AI team</strong></div>

---

Let me know if you'd like this turned into a formatted README or a documentation website layout.
