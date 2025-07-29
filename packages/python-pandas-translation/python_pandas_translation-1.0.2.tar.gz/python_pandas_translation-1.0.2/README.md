# Python JIRA Plus
A lightweight Python wrapper around `pandas` that simplifies its syntax and makes common DataFrame operations easier to understand and use. <br>
This library is perfect for beginners, educators, or anyone who finds traditional pandas syntax too complex or verbose. Think of it as a "translation layer" — turning hard-to-read code into intuitive and readable commands.


---

## Installation
```bash
pip install pytho-pandas-translation
```

---

## Examples

### Creating an Issue with Custom Fields
```python
import pandas as pd

from python_pandas_translation import pandas_row

sample_df = pd.DataFrame(
        {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [30, 25, 35]
        }
    )

print(pandas_row.get_rows(sample_df, start=0, end=1))
```

---

## 🤝 Contributing
If you have a helpful tool, pattern, or improvement to suggest:
Fork the repo <br>
Create a new branch <br>
Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

---

## 🙏 Thanks
Thanks for exploring this repository! <br>
Happy coding! <br>
