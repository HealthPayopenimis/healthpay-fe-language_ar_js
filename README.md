# HealthPay Payer System — Arabic Language Pack (`@healthpay/fe-language_ar`)

Arabic (Egypt, `ar` / `ar-EG`) translations for all HealthPay Payer System frontend
modules. Built on the openIMIS language-pack pattern (see `fe-language_fr_js`).

**HealthPay Payer System is built on [openIMIS](https://openimis.org), a Digital Public Good. License: AGPL-3.0.**

## Status

- ✅ First drop: core, admin, insuree, claim, claim_batch, policy, contribution,
  payment, product, medical, pricelist, payer, invoice, policyholder, contract,
  tools, locations (~250 keys)
- ⏳ Remaining keys (~3,100 total across all modules): pending professional
  medical-insurance translator review — see `TRANSLATION_STATUS.md`
- All terminology is locked against the UHIA / Law 2/2018 glossary below.
  **No string ships without glossary compliance.**

## UHIA Terminology Glossary (locked — القاموس المعتمد)

| English | العربية |
|---|---|
| Insuree | المؤمَّن عليه |
| Policy | وثيقة التأمين / التغطية |
| Claim | المطالبة |
| Contribution | الاشتراك |
| Prior authorization | الموافقة المسبقة |
| Health facility | المنشأة الصحية |
| Copay / Deductible | المساهمة / نسبة التحمل |
| Beneficiary | المستفيد |
| Batch run | التسوية الدورية |
| National ID | الرقم القومي |
| Product (benefit package) | برنامج التغطية |
| Enrollment officer | مسؤول التسجيل |
| Claim administrator | مسؤول المطالبات |
| Payer | جهة الدفع |
| Premium | قسط / اشتراك |
| Governorate | المحافظة |
| Markaz | المركز |

## Usage (assembly `openimis.json`)

```json
{
  "modules": [
    { "npm": "@healthpay/fe-language_ar", "cameo": "LanguageArModule" }
  ]
}
```

## RTL Integration Checklist (fe-core)

1. Theme: `direction: "rtl"` when active language is `ar`; set `dir="rtl"` on `<html>`.
2. MUI v7: wrap style engine with RTL cache (`stylis-plugin-rtl` via `@mui/stylis-plugin-rtl`).
3. Fonts: Arabic-first stack — `"IBM Plex Sans Arabic", "Cairo", "Tajawal", "Roboto", sans-serif`.
4. Mirror directional icons (back/forward arrows, tree expanders).
5. **Bidi hygiene**: wrap ICD-10 codes, drug codes, emails, and other Latin
   identifiers in `dir="ltr"` isolation spans (`<bdi>` / `unicode-bidi: isolate`).
6. Numbers policy: **Western digits (0-9)** for all identifiers, amounts, and codes
   (claims-data integrity + UHIA reporting compatibility). Gregorian calendar,
   `ar-EG` locale formatting, currency **EGP / ج.م**.
7. DB: `Language` register row `ar` with the right-to-left flag set (see
   `healthpay-be-egypt` migration).

## Continuous localization

Wire this repo to Weblate/Crowdin. On every upstream openIMIS release, run the
key-diff script to flag new/changed keys for translation.
