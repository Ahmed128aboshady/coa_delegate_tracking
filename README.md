# coa delegate_tracking (`coa_delegate_tracking`)

## 📌 الوصف العام (Overview)
Live location tracking and dashboard for sales delegates in the field.

### التفاصيل الوظيفية:

This module tracks the locations of sales delegates, updates their last known coordinates,
and displays their live and historical positions on an interactive OpenStreetMap map.
    

---

## 🛠️ معلومات الموديول (Module Metadata)
- **الاسم الفني (Technical Name):** `coa_delegate_tracking`
- **التصنيف (Category):** `Sales`
- **الإصدار (Version):** `1.0`
- **الاعتماديات (Dependencies):** `base`, `web`, `sale`

---

## 📦 النماذج البرمجية (Models & Backend)
- **الملف:** `models\coa_delegate.py`
  - **النماذج الجديدة (`_name`):** `coa.delegate`
  - **الوصف:** COA Sales Delegate
- **الملف:** `models\delegate_location.py`
  - **النماذج الجديدة (`_name`):** `delegate.location.log`
  - **النماذج المعدلة (`_inherit`):** `res.partner`, `product.product`, `sale.order`
  - **الوصف:** Delegate GPS Location Log
- **الملف:** `models\delegate_visit.py`
  - **النماذج الجديدة (`_name`):** `delegate.route.plan`, `delegate.visit`
  - **الوصف:** Delegate Route Plan

---

## 🖥️ الواجهات والتقارير (Views & Reports)
- **ملفات الواجهات (`Views`):** `views\coa_delegate_views.xml`, `views\delegate_location_views.xml`, `views\delegate_visit_views.xml`

---

## 🚀 كيفية الاستخدام والتثبيت (Installation & Usage)
1. قُم بإضافة مجلد الموديول إلى مسار `addons_path` الخاص بالسيرفر.
2. قُم بتحديث قائمة الموديولات في أودو (Update Apps List).
3. البحث عن `coa delegate_tracking` أو `coa_delegate_tracking` والضغط على **تثبيت (Install)**.
