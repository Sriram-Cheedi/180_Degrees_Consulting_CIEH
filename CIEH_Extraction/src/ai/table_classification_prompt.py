
import json


def build_table_classification_prompt(
    table: dict,
    document_context: str
) -> str:

    rows = table["rows"]

    table_preview = {
        "table_index": table["table_index"],
        "column_count": len(rows[0]),
        "headers": [
            {"column_index": index, "text": header}
            for index, header in enumerate(rows[0])
        ],
        "sample_rows": rows[1:4]
    }

    return f"""
You are interpreting tables from UK local authority
Freedom of Information responses.

Your task is to classify table columns and identify
what type of measurement the table reports.

You must NOT extract or generate numerical counts.

COLUMN CATEGORIES:
- tattoo_premises: tattoo premises only
- tattoo_practitioners: tattoo practitioners only
- combined_premises_and_practitioners:
  premises and practitioners combined
- other: totals, dates, years, unrelated categories,
  or different mixed categories
- unknown: cannot determine the category

METRIC TYPES:
- active_register_total:
  Only an explicitly described snapshot or total
  of currently registered premises/practitioners
- new_registrations:
  Registrations occurring during a specified period
- applications:
  Submitted applications
- other:
  A different clearly described measurement
- unknown:
  Ambiguous measurement

RULES:
1. Return one classification for every column index.
2. Preserve the original zero-based column indices.
3. Do not classify PERS & PREM as premises only.
4. Do not classify PERSON as premises.
5. Do not classify Grand Total as premises.
6. Use surrounding document context when deciding
   the metric type.
7. Do not invent meanings absent from the source.
8. If uncertain, use unknown and request human review.
9. Return only JSON matching the provided schema.

TABLE:
{json.dumps(table_preview, ensure_ascii=False)}

DOCUMENT CONTEXT:
{document_context}
"""


