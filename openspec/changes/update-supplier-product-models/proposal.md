## Purpose
根据用户要求，调整供应商和产品模型以符合规范与实际业务需求。

## Supplier Model Changes
- **保留字段**: contact_person, contact_phone, created_by
- **变更字段**: is_active → status (string: enabled/disabled), notes → remark
- **删除字段**: address

## Product Model Changes
- **保留字段**: origin, destination, includes, excludes, cancellation_policy, travel_notice, important_tips, created_by, itinerary_template (JSONB)
- **变更字段**: reference_price → price, notes → remark, status: active/inactive → enabled/disabled
