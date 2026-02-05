# AI Orchestrator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

Automated refactoring pipeline using Gemini and Codex with Semgrep validation.

## 🚀 İki Farklı Araç

### 1. `orchestrator_improved.py` - Refactoring Pipeline

Mevcut projeleri analiz edip iyileştirir.

### 2. `project_generator.py` - Project Generator ⭐ YENİ

Sıfırdan proje oluşturur! [Detaylı döküman →](GENERATOR_README.md)

```bash
python project_generator.py \
  --name "MyWebsite" \
  --description "Modern portfolyo sitesi" \
  --tech "React, TypeScript, TailwindCSS"
```

---

## AI Orchestrator (Refactoring)

## Features

✅ **Error Handling** - Graceful error handling and recovery  
✅ **Configuration** - JSON-based configuration file  
✅ **Logging** - File and console logging with timestamps  
✅ **Output Tracking** - All intermediate results saved with timestamps  
✅ **CLI Arguments** - Skip steps, dry run mode  
✅ **Validation** - Pre-flight checks for all required files  
✅ **Modular** - Clean class-based architecture

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your project in `config.json`:

```json
{
  "project_root": "/path/to/your/project"
}
```

## Usage

### Basic usage:

```bash
python orchestrator_improved.py
```

### Dry run (analysis only):

```bash
python orchestrator_improved.py --dry-run
```

### Skip specific steps:

```bash
python orchestrator_improved.py --skip-semgrep
python orchestrator_improved.py --skip-refactor
```

### Custom config:

```bash
python orchestrator_improved.py --config custom_config.json
```

## Configuration

Edit `config.json` to customize:

- `project_root` - Target project path
- `output_dir` - Where to save results
- `steps` - Enable/disable pipeline steps
- `prompts` - Custom prompt file paths

## Output

Results are saved in `output/` directory with timestamps:

- `YYYYMMDD_HHMMSS_analysis.txt` - Gemini analysis
- `YYYYMMDD_HHMMSS_semgrep_findings.json` - Semgrep results
- `YYYYMMDD_HHMMSS_tasks.json` - Decided tasks
- `YYYYMMDD_HHMMSS_final_scan.txt` - Final validation

Logs are saved to `orchestrator.log`.

## Pipeline Steps

1. **Analysis** - Gemini analyzes project for refactoring opportunities
2. **Semgrep** - Static analysis to find concrete issues
3. **Decision** - Gemini decides safe, actionable tasks
4. **Refactor** - Codex applies the refactors
5. **Validation** - Final Semgrep scan to verify improvements

## Error Handling

- Pre-flight validation of all files
- Graceful error messages
- Non-zero exit codes on failure
- Detailed logging for debugging

## Original vs Improved

| Feature         | Original   | Improved             |
| --------------- | ---------- | -------------------- |
| Error handling  | ❌         | ✅                   |
| Configuration   | Hardcoded  | JSON file            |
| Logging         | Print only | File + Console       |
| CLI arguments   | ❌         | ✅                   |
| Output tracking | ❌         | ✅ Timestamped       |
| Validation      | ❌         | ✅ Pre-flight checks |
| Structure       | Script     | Class-based          |
| Documentation   | ❌         | ✅                   |

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

- Fork the repository
- Create your feature branch (`git checkout -b feature/AmazingFeature`)
- Commit your changes (`git commit -m 'feat: add amazing feature'`)
- Push to the branch (`git push origin feature/AmazingFeature`)
- Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Gemini](https://gemini.google.com/) for AI analysis
- [Codex](https://openai.com/codex) for code generation
- [Semgrep](https://semgrep.dev/) for static analysis
- All contributors who help improve this project

---

## 👤 Author

**Oğuzhan Dede**
- GitHub: [@oguzhandede](https://github.com/oguzhandede)
- Email: oguzhandede@gmail.com

---

**Made with ❤️ by the community**
