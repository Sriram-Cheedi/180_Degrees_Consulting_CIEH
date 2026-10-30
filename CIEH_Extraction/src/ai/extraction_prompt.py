
def build_extraction_prompt(document_text: str) -> str:
    return f"""
You are a careful data extraction assistant working with
UK local authority Freedom of Information responses.

Extract numerical information concerning tattoo registrations.

IMPORTANT:
Your job is to copy and classify evidence, not estimate,
calculate, or invent figures.

CATEGORY CLASSIFICATION:
- tattoo_premises:
  Figures explicitly referring to tattoo premises only.
- tattoo_practitioners:
  Figures explicitly referring to individual tattoo practitioners.
- combined_premises_and_practitioners:
  Figures explicitly covering both premises and practitioners.
- other:
  Figures covering other or mixed categories, such as
  tattoo and piercing premises together.
- unknown:
  Figures whose category cannot be established.

Never classify "PERS & PREM" as tattoo_premises.
"PERS & PREM" means combined persons and premises.

Never classify "PERSON" as tattoo_premises.
"PREMISES" is a separate category.

METRIC CLASSIFICATION:
- active_register_total:
  Only when the source explicitly describes a snapshot
  of the total premises or practitioners on the register.
- new_registrations:
  Only when the source clearly describes registrations
  occurring during a particular period.
- applications:
  Only when the source reports applications.
- other:
  A different explicitly described measure.
- unknown:
  The measure cannot be confidently determined.

EXTRACTION RULES:
1. Preserve the exact values from the document.
2. Match every number to its correct row and column.
3. Keep different registration categories separate.
4. Never treat a blank cell as zero.
5. Never infer or calculate missing counts.
6. Do not extract grand totals as yearly records.
7. Preserve financial-year labels exactly as written.
8. Include meaningful evidence with the relevant count,
   column heading, and row label.
9. Use source_location only for a real identifiable
   document location, such as "Table 1, row 2023,
   PREMISES column".
10. Do not invent council names.
11. If the metric or category is ambiguous, use
    "unknown" and set review_required to true.
12. If the document includes combined or potentially
    unsuitable data, request human review.
13. Return an empty records list if no relevant
    figures are available.
14. Return only JSON matching the required schema.

DOCUMENT:
<document>
{document_text}
</document>
"""
