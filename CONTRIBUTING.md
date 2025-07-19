# 🤝 Contributing to OpenTestability

Thank you for considering contributing to this project! Whether you want to report a bug, suggest a feature, improve the documentation, or contribute code — you're welcome here.

Please follow the guidelines below to help maintain a clean, readable, and efficient development flow.

---

## 🛠️ How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/OpenTestability.git
cd OpenTestability
```

### 2. Create a Branch
```bash
git checkout -b feat/your-feature-name
```

### 3. Commit with Proper Format _(see below)_

### 4. Push and Open a Pull Request
Make sure your PR clearly describes what it solves. Reference any related issues (e.g., `Closes #12`).

---

## 📝 Commit & Issue Guidelines

### ✅ Commit Message Format

```
<type>[: scope]: <short summary>
```

#### Common Types:

| Type       | Description                                                               |
|------------|---------------------------------------------------------------------------|
| `feat`     | New feature (incomplete or under development)                             |
| `feat_c`   | Completed feature with test coverage                                       |
| `fix`      | Bug fix or patch                                                          |
| `refactor` | Code structure improvement (no new features or fixes)                     |
| `rm`       | Removed features, modules, or code blocks                                 |
| `docs`     | Documentation-only changes                                                |
| `test`     | Adding or modifying unit/integration tests                                |
| `chore`    | Non-code logic changes (e.g., dependencies, CI, formatting)               |
| `perf`     | Performance optimization                                                  |
| `style`    | Formatting, whitespace, lint fixes (no logic changes)                     |

#### Examples:

```
feat: add initial parser for gate-level netlists  
feat_c: implement and test SCOAP CO calculation  
fix: handle empty net fanouts in dag_builder  
rm: remove legacy netlist parser implementation  
docs: update README with architecture diagram  
test: add edge case tests for reconvergence  
chore: add .pre-commit-config.yaml  
```

---

### 🧾 Issue Title Format

Use structured tags to clarify the nature of your issue:

```
[FEATURE]   Describe new capability or enhancement  
[BUG]       Report a reproducible problem  
[DOCS]      Documentation suggestion or fix  
[TEST]      Coverage request or test fix  
[REFACTOR]  Internal code structure change  
[QUESTION]  Ask something or start a discussion  
```

#### Examples:

- `[FEATURE] Add visual representation of DAG`
- `[BUG] Netlist parser crashes on single-pin gates`
- `[DOCS] Clarify usage instructions for SCOAP CLI`
- `[QUESTION] Should sequential metrics be part of SCOAP or separate module?`

---

## 🧪 Testing

If your PR adds or modifies code logic, please add corresponding unit tests in the `tests/` directory. You can run tests locally using:

```bash
pytest tests/
```

---

## 📜 License

By contributing, you agree that your code will be licensed under the **Apache 2.0 License** used by this project.
