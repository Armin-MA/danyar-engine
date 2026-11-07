# ساختار شکست کار و شناسنامه وظایف (Work Breakdown Structure - WBS)

**پروژه:** موتور مشاور هوشمند دانیار (Danyar Engine)  
**نسخه:** 1.0.0  
**وضعیت:** مصوب فاز ۳ (Gate 3 Ready)  
**نقطه عطف مرتبط در گیت‌هاب:** [Milestone 4: Core Implementation & Verification](https://github.com/Armin-MA/danyar-engine/milestone/4)  

---

## ۱. ماتریس جامع شکست کار (WBS Execution Matrix)

| کد تسک | عنوان وظیفه | لایه معماری | مسیر فایل هدف | ایشیو گیت‌هاب | وضعیت |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **TASK-001** | پیکربندی متغیرهای محیطی و Neo4j | `config` | `src/config/app_config.py` | [#1](https://github.com/Armin-MA/danyar-engine/issues/1) | ⏳ در انتظار |
| **TASK-002** | نرمال‌ساز متون و نیم‌فاصله‌های فارسی | `utils` | `src/utils/text_normalizer.py` | [#2](https://github.com/Armin-MA/danyar-engine/issues/2) | ⏳ در انتظار |
| **TASK-003** | اعتبارسنج سخت‌گیرانه خروجی JSON | `utils` | `src/utils/schema_validator.py` | [#3](https://github.com/Armin-MA/danyar-engine/issues/3) | ⏳ در انتظار |
| **TASK-004** | موجودیت‌های دامنه خالص (Domain Entities) | `entities` | `src/entities/domain_entities.py` | [#4](https://github.com/Armin-MA/danyar-engine/issues/4) | ⏳ در انتظار |
| **TASK-005** | قراردادها و واسط‌های انتزاعی سیستم | `contracts` | `src/contracts/engine_contracts.py` | [#5](https://github.com/Armin-MA/danyar-engine/issues/5) | ⏳ در انتظار |
| **TASK-006** | الگوریتم محاسبه اعتبار پویا (FitScore) | `mechanics` | `src/mechanics/calculate_dynamic_credibility.py` | [#6](https://github.com/Armin-MA/danyar-engine/issues/6) | ⏳ در انتظار |
| **TASK-007** | پرامپت و منطق استخراج اتمیک گزاره‌ها | `mechanics` | `src/mechanics/extract_atomic_claims.py` | [#7](https://github.com/Armin-MA/danyar-engine/issues/7) | ⏳ در انتظار |
| **TASK-008** | موتور تحلیل و سنتز تعارض دیالکتیکی | `mechanics` | `src/mechanics/evaluate_dialectical_conflict.py` | [#8](https://github.com/Armin-MA/danyar-engine/issues/8) | ⏳ در انتظار |
| **TASK-009** | فرموله‌ساز سوالات تشخیصی سقراطی | `mechanics` | `src/mechanics/formulate_socratic_inquiry.py` | [#9](https://github.com/Armin-MA/danyar-engine/issues/9) | ⏳ در انتظار |
| **TASK-010** | کامپایلر کانتکست ساختاریافته برای مدل سبک | `mechanics` | `src/mechanics/compile_structured_context.py` | [#10](https://github.com/Armin-MA/danyar-engine/issues/10) | ⏳ در انتظار |
| **TASK-011** | اشیاء انتقال داده گرافی (DTOs) | `database` | `src/database/dto/graph_dtos.py` | [#11](https://github.com/Armin-MA/danyar-engine/issues/11) | ⏳ در انتظار |
| **TASK-012** | کوئری‌های پارامتری‌شده Cypher | `database` | `src/database/queries/cypher_statements.py` | [#12](https://github.com/Armin-MA/danyar-engine/issues/12) | ⏳ در انتظار |
| **TASK-013** | ریپازیتوری عملیات گراف Neo4j | `database` | `src/database/repositories/neo4j_graph_repository.py` | [#13](https://github.com/Armin-MA/danyar-engine/issues/13) | ⏳ در انتظار |
| **TASK-014** | ریپازیتوری کامنت‌ها و نوت‌های انسانی | `database` | `src/database/repositories/neo4j_annotation_repository.py` | [#14](https://github.com/Armin-MA/danyar-engine/issues/14) | ⏳ در انتظار |
| **TASK-015** | ارائه‌دهنده پاسخ‌های سقراطی و نقل‌قول‌ها | `ui` | `src/ui/presenters/socratic_presenter.py` | [#15](https://github.com/Armin-MA/danyar-engine/issues/15) | ⏳ در انتظار |
| **TASK-016** | روت‌های وب و اندپوینت‌های FastAPI | `ui` | `src/ui/api/routes.py` | [#16](https://github.com/Armin-MA/danyar-engine/issues/16) | ⏳ در انتظار |
| **TASK-017** | داشبورد وب تلفیقی (3D Graph + Milkdown) | `ui` | `src/ui/static/index.html` | [#17](https://github.com/Armin-MA/danyar-engine/issues/17) | ⏳ در انتظار |
| **TASK-018** | ارکستراتور بوت‌استرپ و کانتینر IoC | `core` | `src/core/orchestrator.py` | [#18](https://github.com/Armin-MA/danyar-engine/issues/18) | ⏳ در انتظار |

---

## ۲. قانون عدم شروع پیش از موعد (Strict Implementation Gate)

طبق قرارداد معماری:
> **شروع پیاده‌سازی فاز ۴ منحصراً پس از تایید Gate 3 و صدور دستور صریح `START_IMPLEMENTATION` از سوی کاربر مجاز است.**
