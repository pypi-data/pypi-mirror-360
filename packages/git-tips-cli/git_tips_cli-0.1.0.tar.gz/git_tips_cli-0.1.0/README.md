# git-tips-cli
A simple CLI tool that shows you random useful Git tips to improve your daily Git workflow.

# git-tips-cli

🧠 A simple CLI tool that shows you random useful Git tips  
📘 Great for learning Git little by little every day!

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 🚀 Features

- 📌 Shows a random Git tip every time you run `git-tips`
- 🗂️ Tip list stored in `JSON` (easy to edit/extend)
- 🌐 Supports Japanese descriptions
- 🧩 Easy to install & use

---

## 📦 Installation

```bash
pip install git-tips-cli
```

Or if you're developing locally:

```bash
git clone https://github.com/your-username/git-tips-cli.git
cd git-tips-cli
pip install -e .
```

---

## 🔧 Usage

```bash
git-tips
```

Example output:

```
📌 git log --oneline
ログを1行ずつ簡潔に表示します。
```

---

## 📁 Example Tip Data (`tips.json`)

```json
[
  {
    "command": "git diff --staged",
    "description": "ステージングされた変更の差分を表示します。"
  },
  {
    "command": "git restore .",
    "description": "作業ツリーの変更をすべて元に戻します。"
  }
]
```

---

## 📥 Contributing

Got a favorite Git tip? PRs welcome!

1. Fork this repo
2. Add your tip to `tips.json`
3. Submit a Pull Request 🙌

---

## 🪪 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.