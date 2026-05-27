# Contributing to lfed-course-recommender

Thank you for your interest in contributing!

## How to contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/lfed-course-recommender.git
   cd lfed-course-recommender
   ```
3. **Add upstream** remote:
   ```bash
   git remote add upstream https://github.com/pkaranje/lfed-course-recommender.git
   ```
4. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
5. **Make your changes**, following the code conventions in `CLAUDE.md`.
6. **Run checks** before pushing:
   ```bash
   make lint
   make typecheck
   make test
   ```
7. **Push** your branch and open a **Pull Request** against `upstream/main`.

## Keeping your fork up to date

```bash
git fetch upstream
git rebase upstream/main
```

## Pull request guidelines

- Keep PRs focused — one logical change per PR.
- Write a clear description of what changed and why.
- All CI checks must pass before review.
- Be respectful and constructive in review discussions.
