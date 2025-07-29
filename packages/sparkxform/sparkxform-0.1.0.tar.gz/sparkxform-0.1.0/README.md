# sparkxform

**sparkxform** is a lightweight and reusable PySpark transformation utility library designed for scalable and modular data engineering pipelines. It contains a growing collection of transformation functions for Spark DataFrames including ID generation, string cleaning, date parsing, and more.

---

## 📦 Features

- 🔢 Dynamic ID generation from existing tables
- ✂️ String cleaning (trimming, lowercasing, etc.)
- 📅 Date column parsing and standardization
- 🔄 Easily extendable with your own transformations
- 💼 Production-friendly Python packaging

---

## 📚 Installation

Clone the repository and install locally:

```bash
git clone https://github.com/RanjitM007/sparkxform.git
cd sparkxform
pip install -e .
```

Or

```python
pip install sparkxform
```

### 🔢 assign_next_id

```python
from sparkxform import assign_next_id

df = assign_next_id(spark, df, table_name='existing_table', column_name='storage_id')
```
### 📝 Description

`assign_next_id()` assigns a **uniform incremental ID** to all rows in the given DataFrame by:

- Querying the max ID from an external table via Spark SQL.
- Incrementing it by one.
- Creating (or overwriting) a column with that next ID value.

---

### ✅ Advantages

- Simple and fast for batch inserts with uniform IDs.
- Useful for tracking ingestion batches.
- Easily integrates with Hive/Spark SQL tables.
- Eliminates race conditions in single-threaded batch ETL flows.

---

### ⚠️ Disadvantages

- All rows get the same ID, so it is not suitable for row-level uniqueness.
- Requires the external table (`table_name`) to exist and be readable.
- Not thread-safe or atomic in distributed writes — use with care in concurrent workloads.
- Cannot assign unique row IDs (e.g., for primary keys) — for that use `monotonically_increasing_id()` or UUIDs.

---

### 🧠 Best For

- Appending batch metadata.
- Managing incremental inserts.
- Logging ingestion batches with shared identifiers.

---

### 🔁 Related Functions (coming soon)

- `assign_partitioned_ids()`
- `assign_uuid_column()`
- `generate_sequential_ids_by_group()`

---

Let me know if you'd like me to help you implement the **row-level unique ID generator**, **partition-aware version**, or add automated tests for this function.

### 📆 convert_to_date

```python
from sparkxform import convert_to_date

df = convert_to_date(df, col_name='order_date', fmt='MM/dd/yyyy')
```

### 📝 Description
`convert_to_date()` transforms a string-based date column into a Spark SQL `DateType` using the format you specify.

- Uses to_date() internally to parse and cast values.

- Overwrites the existing column with parsed date values.

### ✅ Advantages

- Simplifies date parsing using consistent Spark syntax.  
- Supports custom date formats (e.g., `'MM/dd/yyyy'`, `'dd-MM-yyyy'`, etc.).  
- Avoids manual casting and parsing logic.

---

### ⚠️ Disadvantages

- If the input format is incorrect or mismatched, `null` values will be produced.  
- It overwrites the existing column; to preserve it, the function must be extended to use a `new_col` parameter.  
- Works only with string columns containing valid date strings.

---

### 🧠 Best For

- Standardizing date columns from CSV, JSON, or unstructured sources.  
- Preparing data for time-based operations (e.g., filtering, grouping by date).  
- Quick date conversion in ETL pipelines.

---

### 🔁 Related Functions (coming soon)

- `convert_to_timestamp()`  
- `add_date_part_columns()` *(e.g., year, month, day)*  
- `format_date_column()`

____

### ✂️ clean_string_column

```python
from sparkxform import clean_string_column

df = clean_string_column(df, col_name='Name', new_col='cleaned_name')
```

#### 📝 Description
`clean_string_column()` cleans a string column by:

- Removing leading and trailing whitespace using `trim()`.

- Converting all characters to lowercase using `lower()`.

- Optionally writing the cleaned result to a new column `(new_col)` or replacing the original.


#### ✅ Advantages

- Simplifies standard string cleaning operations.  
- Helps maintain consistency across categorical or textual data.  
- Non-destructive if `new_col` is specified — preserves original column.

---

#### ⚠️ Disadvantages

- Assumes the input column is of string type; other types may raise errors.  
- Only performs basic cleaning (`trim` + `lower`) — not full normalization or regex cleaning.

---

#### 🧠 Best For

- Preprocessing name, city, email, or category columns.  
- Normalizing textual data for comparison, deduplication, or joins.  
- Cleaning incoming data from CSV/Excel/JSON sources.

---

#### 🔁 Related Functions (coming soon)

- `remove_special_chars()`  
- `normalize_whitespace()`  
- `standardize_column_case()`




