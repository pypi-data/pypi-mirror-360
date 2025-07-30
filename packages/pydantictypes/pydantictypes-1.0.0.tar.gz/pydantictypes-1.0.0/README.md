# Pydantic Types

[![Test](https://github.com/yukihiko-shinoda/pydantic-types/workflows/Test/badge.svg)](https://github.com/yukihiko-shinoda/pydantic-types/actions?query=workflow%3ATest)
[![CodeQL](https://github.com/yukihiko-shinoda/pydantic-types/workflows/CodeQL/badge.svg)](https://github.com/yukihiko-shinoda/pydantic-types/actions?query=workflow%3ACodeQL)
[![Code Coverage](https://qlty.sh/gh/yukihiko-shinoda/projects/pydantic-types/coverage.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/pydantic-types)
[![Maintainability](https://qlty.sh/badges/11a7c146-f6ee-4d74-8b63-2d2e963ef988/maintainability.svg)](https://qlty.sh/gh/yukihiko-shinoda/projects/pydantic-types)
[![Dependabot](https://flat.badgen.net/github/dependabot/yukihiko-shinoda/pydantic-types?icon=dependabot)](https://github.com/yukihiko-shinoda/pydantic-types/security/dependabot)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantictypes)](https://pypi.org/project/pydantictypes)
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fyukihiko-shinoda%2Fpydantic-types)](http://twitter.com/share?text=Pydantic%20Types&url=https://pypi.org/project/pydantictypes/&hashtags=python)

Common used type definitions with Pydantic.

## Advantage

- Out of the box

### Out of the box

You don't need to define customized types for common use cases. This package provides a set of commonly used types that can be directly imported and used in your Pydantic models.

## Quickstart

```bash
pip install pydantictypes
```

## API

### StrictKanjiYenStringToInt

```python
from pydantictypes import StrictKanjiYenStringToInt
from pydantic import BaseModel, ValidationError

class MyModel(BaseModel):
    price: StrictKanjiYenStringToInt

# Successful conversions:
model1 = MyModel(price="1円")           # Result: model1.price = 1
model2 = MyModel(price="1,000円")       # Result: model2.price = 1000  
model3 = MyModel(price="1,000,000円")   # Result: model3.price = 1000000

# These inputs raise ValidationError:
try:
    MyModel(price="1.0円")      # ❌ Decimals not supported
except ValidationError:
    pass

try:
    MyModel(price="1000")       # ❌ Missing 円 character
except ValidationError:
    pass
```
This type converts a string representing a price in Japanese yen, written in kanji, to an integer. It raises a `ValueError` if the input is not a valid kanji yen string.

### StringSlashMonthDayOnlyToDatetime

```python
from pydantictypes import StringSlashMonthDayOnlyToDatetime
from pydantic import BaseModel, ValidationError
import datetime

class MyModel(BaseModel):
    date: StringSlashMonthDayOnlyToDatetime

# Successful conversions:
model1 = MyModel(date="01/01")    # Result: model1.date = datetime.datetime(1904, 1, 1, 0, 0)
model2 = MyModel(date="12/31")    # Result: model2.date = datetime.datetime(1904, 12, 31, 0, 0)  
model3 = MyModel(date="02/29")    # Result: model3.date = datetime.datetime(1904, 2, 29, 0, 0)

# These inputs raise ValidationError:
try:
    MyModel(date="01/32")         # ❌ Invalid day
except ValidationError:
    pass

try:
    MyModel(date="2020/01/01")    # ❌ Wrong format (includes year)
except ValidationError:
    pass
```
This type converts a string in the format "MM/DD" to a `datetime` object, using the year 1904. It raises a `ValueError` if the input is not in the correct format.

### StringSlashToDateTime

```python
from pydantictypes import StringSlashToDateTime
from pydantic import BaseModel, ValidationError
import datetime

class MyModel(BaseModel):
    date: StringSlashToDateTime

# Successful conversions:
model1 = MyModel(date="2020/01/01")   # Result: model1.date = datetime.datetime(2020, 1, 1, 0, 0)
model2 = MyModel(date="2020/12/31")   # Result: model2.date = datetime.datetime(2020, 12, 31, 0, 0)
model3 = MyModel(date="2020/02/29")   # Result: model3.date = datetime.datetime(2020, 2, 29, 0, 0)

# These inputs raise ValidationError:
try:
    MyModel(date="2020/02/30")        # ❌ Invalid date
except ValidationError:
    pass

try:
    MyModel(date="2020-01-01")        # ❌ Wrong format (uses hyphens)
except ValidationError:
    pass
```
This type converts a string in the format "YYYY/MM/DD" to a `datetime` object. It raises a `ValueError` if the input is not in the correct format.

### ConstrainedStringToOptionalInt

```python
from pydantictypes import ConstrainedStringToOptionalInt
from pydantic import BaseModel, ValidationError

class MyModel(BaseModel):
    optional_int: ConstrainedStringToOptionalInt

# Successful conversions:
model1 = MyModel(optional_int="123")     # Result: model1.optional_int = 123
model2 = MyModel(optional_int="0")       # Result: model2.optional_int = 0
model3 = MyModel(optional_int="")        # Result: model3.optional_int = None

# These inputs raise ValidationError:
try:
    MyModel(optional_int="1,000")        # ❌ Commas not supported
except ValidationError:
    pass

try:
    MyModel(optional_int="abc")          # ❌ Not a valid integer
except ValidationError:
    pass
```
This type converts a string to an optional integer. If the string is empty, it returns `None`. If the string is not a valid integer, it raises a `ValueError`.

### StrictStringWithCommaToInt

```python
from pydantictypes import StrictStringWithCommaToInt
from pydantic import BaseModel, ValidationError

class MyModel(BaseModel):
    number: StrictStringWithCommaToInt

# Successful conversions:
model1 = MyModel(number="1")             # Result: model1.number = 1
model2 = MyModel(number="1,000")         # Result: model2.number = 1000
model3 = MyModel(number="1,000,000")     # Result: model3.number = 1000000

# These inputs raise ValidationError:
try:
    MyModel(number="1.0")                # ❌ Decimals not supported
except ValidationError:
    pass

try:
    MyModel(number="1,000円")            # ❌ Currency symbols not supported
except ValidationError:
    pass
```
This type converts a string with commas (e.g., "1,000") to an integer. It raises a `ValueError` if the input is not a valid string with commas.

### StrictStringWithCommaToOptionalInt

```python
from pydantictypes import StrictStringWithCommaToOptionalInt
from pydantic import BaseModel, ValidationError

class MyModel(BaseModel):
    optional_number: StrictStringWithCommaToOptionalInt

# Successful conversions:
model1 = MyModel(optional_number="1")           # Result: model1.optional_number = 1
model2 = MyModel(optional_number="1,000")       # Result: model2.optional_number = 1000
model3 = MyModel(optional_number="")            # Result: model3.optional_number = None

# These inputs raise ValidationError:
try:
    MyModel(optional_number="1.0")              # ❌ Decimals not supported
except ValidationError:
    pass

try:
    MyModel(optional_number="$1,000")           # ❌ Currency symbols not supported
except ValidationError:
    pass
```
This type converts a string with commas to an optional integer. If the string is empty, it returns `None`. If the string is not a valid string with commas, it raises a `ValueError`.

### StrictSymbolYenStringToInt

```python
from pydantictypes import StrictSymbolYenStringToInt
from pydantic import BaseModel, ValidationError

class MyModel(BaseModel):
    price: StrictSymbolYenStringToInt

# Successful conversions:
model1 = MyModel(price=r"\1")           # Result: model1.price = 1
model2 = MyModel(price=r"\1,000")       # Result: model2.price = 1000
model3 = MyModel(price=r"\1,000,000")   # Result: model3.price = 1000000

# These inputs raise ValidationError:
try:
    MyModel(price=r"\1.0")              # ❌ Decimals not supported
except ValidationError:
    pass

try:
    MyModel(price="$1")                 # ❌ Dollar symbol not supported
except ValidationError:
    pass
```
This type converts a string representing a price with backslash symbol (e.g., "\\1,000") to an integer. It raises a `ValueError` if the input is not a valid backslash-prefixed number string.

## Credits

This package was created with [Cookiecutter] and the [yukihiko-shinoda/cookiecutter-pypackage] project template.

[Cookiecutter]: https://github.com/audreyr/cookiecutter
[yukihiko-shinoda/cookiecutter-pypackage]: https://github.com/audreyr/cookiecutter-pypackage
