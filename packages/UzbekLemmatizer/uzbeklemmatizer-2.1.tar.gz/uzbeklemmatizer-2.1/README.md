# UzbekLemmatizer

**UzbekLemmatizer** is a lemmatization library for word in the Uzbek language.
It automatically reduces words to their canonical (dictionary) forms, which is essential for many NLP (Natural Language Processing) tasks.

### Article: [Development of a Rule-Based Lemmatization Algorithm Through Finite State Machine for Uzbek Language](https://ceur-ws.org/Vol-3315/short01.pdf)
### GitHub link:  https://github.com/MaksudSharipov/UzbekLemmatizer

##  Features

- Lemmatizes Uzbek words to their root forms
- Supports basic rule-based lemmatization
- Simple and lightweight interface for easy integration

## 📌 Installation Note
To install UzbekLemmatizer, make sure you have an up-to-date version of pip and setuptools to avoid installation errors on newer Python versions (e.g. Python 3.12).

✅ Upgrade your build tools (recommended):

```bash
python -m pip install --upgrade pip setuptools wheel
```

✅ Then install the package:

```bash
pip install UzbekLemmatizer
```

## Example 1:
```python

import UzbekLemmatizer as ltz

print(ltz.Lemma('keladiganlarning'))

```

## Result:

```python 

kel

```

## Example 2:
```python

import UzbekLemmatizer as ltz

print(ltz.Lemma('keladiganlarning', full=True))

```

## Result:

```python 

['keladiganlarning', 'kel', ['adigan', 'lar', 'ning'], [5, 5, 3]]

```