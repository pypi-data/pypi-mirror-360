# Agent Lab SDK

Набор утилит и обёрток для работы с LLM, AGW и метриками в проектах Agent Lab.

---

1. Установка twine

```
pip install --upgrade build twine
```

2. Собрать и загрузить в pypi

перед обновлением сборки нужно не забыть поменять версию в pyproject.toml
```
python -m build && python -m twine upload dist/*
```

3. Ссылка на проект pypi

> https://pypi.org/project/agent-lab-sdk/

4. установка локально
```
pip install -e .
```

5. установка из интернета
```
pip install agent-lab-sdk
```

# Примеры использования

TBD