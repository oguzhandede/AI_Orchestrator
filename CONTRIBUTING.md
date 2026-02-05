# Contributing to AI Orchestrator

🎉 Öncelikle, AI Orchestrator'a katkıda bulunmayı düşündüğünüz için teşekkür ederiz!

## 🌟 Katkıda Bulunma Yolları

- 🐛 Bug bildirme
- 💡 Yeni özellik önerme
- 📖 Dokümantasyon geliştirme
- 🔧 Kod yazma ve PR gönderme
- 🧪 Test yazma
- 🎨 Semgrep kuralları ekleme

## 📋 Geliştirme Ortamı Kurulumu

```bash
# Repo'yu klonlayın
git clone https://github.com/YOUR_USERNAME/ai-orchestrator.git
cd ai-orchestrator

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Test edin
python orchestrator_improved.py --dry-run
```

## 🐛 Bug Bildirme

Bug bildirirken lütfen:
1. **Açık bir başlık** kullanın
2. **Detaylı açıklama** yapın
3. **Yeniden üretme adımları** ekleyin
4. **Beklenen ve gerçekleşen davranış** belirtin
5. **Ortam bilgilerini** paylaşın (OS, Python versiyonu)

[Bug Report Issue Açın](../../issues/new?template=bug_report.md)

## 💡 Özellik Önerme

Yeni özellik önerirken:
1. **Özelliğin faydası**nı açıklayın
2. **Kullanım senaryoları** verin
3. **Olası implementasyon** önerileri sunun

[Feature Request Issue Açın](../../issues/new?template=feature_request.md)

## 🔧 Pull Request Süreci

### 1. Fork ve Branch Oluşturma

```bash
# Fork'u klonlayın
git clone https://github.com/YOUR_USERNAME/ai-orchestrator.git
cd ai-orchestrator

# Yeni branch oluşturun
git checkout -b feature/amazing-feature
# veya
git checkout -b fix/bug-description
```

### 2. Değişikliklerinizi Yapın

- **Kod stiline** uyun (PEP 8 for Python)
- **Anlamlı commit mesajları** yazın
- **Küçük, odaklanmış** PR'lar gönderin

### 3. Test Edin

```bash
# Syntax kontrolü
python -c "from orchestrator_improved import Orchestrator"
python -c "from project_generator import ProjectGenerator"

# Dry run testi
python orchestrator_improved.py --dry-run
```

### 4. Commit ve Push

```bash
git add .
git commit -m "feat: add amazing feature"
git push origin feature/amazing-feature
```

### 5. Pull Request Açın

- **Açıklayıcı başlık** kullanın
- **Değişiklikleri detaylandırın**
- **İlgili issue'ları** bağlayın
- **Screenshot/GIF** ekleyin (UI değişiklikleri için)

## 📝 Commit Mesajı Kuralları

[Conventional Commits](https://www.conventionalcommits.org/) kullanıyoruz:

```
feat: yeni özellik ekle
fix: bug düzelt
docs: dokümantasyon değişikliği
style: kod formatı (kod değişikliği yok)
refactor: kod iyileştirmesi
test: test ekleme/düzeltme
chore: build/config değişiklikleri
```

Örnekler:
```
feat: add progress bar to orchestrator
fix: resolve bare except in line 191
docs: update GENERATOR_README.md
refactor: extract validation logic to helper
test: add unit tests for config loading
```

## 🎨 Semgrep Kuralları Ekleme

Yeni Semgrep kuralı eklerken:

1. `semgrep/semgrep.yml` dosyasını düzenleyin
2. Kural kategorisine uygun yerleştirin
3. Açıklayıcı mesaj yazın
4. Test edin:
   ```bash
   semgrep --config semgrep/semgrep.yml --test
   ```

## 📖 Dokümantasyon

README veya GENERATOR_README güncellerken:
- **Net ve anlaşılır** yazın
- **Örnekler** ekleyin
- **Markdown formatına** dikkat edin

## ✅ Checklist (PR Öncesi)

- [ ] Kod PEP 8 uyumlu
- [ ] Syntax hataları yok
- [ ] Değişiklikler test edildi
- [ ] Dokümantasyon güncellendi
- [ ] Commit mesajları kurallara uygun
- [ ] PR açıklaması detaylı

## 🤝 Code Review Süreci

1. Maintainer'lar PR'ınızı inceleyecek
2. Gerekirse değişiklik isteyecekler
3. Onaylandıktan sonra merge edilecek

## 💬 İletişim

- GitHub Issues
- GitHub Discussions
- E-posta: [maintainer email]

## 📜 Code of Conduct

Lütfen [Code of Conduct](CODE_OF_CONDUCT.md) dosyasını okuyun.

---

**Katkılarınız için teşekkürler! 🙏**
