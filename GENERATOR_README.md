# AI Project Generator 🚀

Sıfırdan, tam işlevsel projeler oluşturan AI tabanlı proje generatörü.

## Özellikler

- ✅ **Otomatik Planlama** - Gemini ile proje yapısı ve dosya planı oluşturur
- ✅ **Akıllı Yapı Oluşturma** - Klasör ve dosya yapısını otomatik oluşturur
- ✅ **Kod Üretimi** - Codex ile tam işlevsel kod dosyaları üretir
- ✅ **Doğrulama** - Oluşturulan projeyi kontrol eder
- ✅ **İlerleme Takibi** - tqdm ile adım adım ilerleme gösterimi

## Kurulum

```bash
# Gerekli bağımlılıkları yükle
pip install tqdm  # Opsiyonel, progress bar için

# Gemini CLI kurulu olmalı
# Codex CLI kurulu olmalı
```

## Kullanım

### Temel Kullanım

```bash
python project_generator.py \
  --name "MyProject" \
  --description "Proje açıklaması" \
  --tech "React, TypeScript, TailwindCSS"
```

### Örnekler

```bash
# Portfolio sitesi
python project_generator.py \
  --name "MyPortfolio" \
  --description "Kişisel portfolyo sitesi" \
  --tech "HTML, CSS, JavaScript"

# REST API
python project_generator.py \
  --name "BlogAPI" \
  --description "RESTful blog API" \
  --tech "Node.js, Express, MongoDB"

# Full-stack uygulama
python project_generator.py \
  --name "TodoApp" \
  --description "Full-stack todo uygulaması" \
  --tech "React, Node.js, PostgreSQL"
```

### CLI Argümanları

| Argüman | Zorunlu | Açıklama |
|---------|---------|----------|
| `--name` | ✅ | Proje ismi |
| `--description` | ✅ | Proje açıklaması |
| `--tech` | ✅ | Teknoloji stack |
| `--config` | ❌ | Özel config dosyası |
| `--skip-planning` | ❌ | Planlama adımını atla |
| `--skip-validation` | ❌ | Doğrulama adımını atla |

## Konfigürasyon

`generator_config.json` dosyasını düzenleyerek ayarları özelleştirebilirsiniz:

```json
{
  "output_dir": "generated_projects",
  "logs_dir": "logs",
  "templates_dir": "templates",
  "steps": {
    "planning": true,
    "structure": true,
    "implementation": true,
    "validation": true
  }
}
```

## Pipeline Adımları

```
┌─────────────────┐
│   1. PLANNING   │  Gemini ile proje planı oluşturur
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   2. STRUCTURE  │  Klasör ve dosya yapısını oluşturur
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. IMPLEMENTATION│  Codex ile kod dosyalarını üretir
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. VALIDATION  │  Oluşturulan projeyi doğrular
└─────────────────┘
```

## Çıktı

Oluşturulan projeler `generated_projects/` klasörüne kaydedilir.

```
generated_projects/
└── MyProject/
    ├── README.md
    ├── package.json
    ├── .gitignore
    ├── src/
    │   ├── index.js
    │   └── app.js
    └── public/
        ├── index.html
        └── styles.css
```

Log dosyaları `logs/` klasöründe saklanır:
- `YYYYMMDD_HHMMSS_planning_prompt.txt` - Planlama promptu
- `YYYYMMDD_HHMMSS_project_plan.json` - Proje planı
- `YYYYMMDD_HHMMSS_implementation_prompt.txt` - Kod üretim promptu
- `YYYYMMDD_HHMMSS_codex_implementation.txt` - Codex çıktısı

## Gereksinimler

- Python 3.7+
- Gemini CLI (`npm i -g @anthropic-ai/gemini-cli` veya benzeri)
- Codex CLI (`npm i -g @openai/codex-cli` veya benzeri)
- Windows PowerShell (Windows için)

## Notlar

- Proje ismi zaten varsa, timestamp eklenerek yeni klasör oluşturulur
- `tqdm` yüklü değilse, progress bar devre dışı kalır (çalışmaya devam eder)
- Tüm çıktılar UTF-8 encoding ile kaydedilir
