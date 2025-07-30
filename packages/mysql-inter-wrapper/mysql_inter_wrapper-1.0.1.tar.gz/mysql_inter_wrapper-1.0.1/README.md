# mysql_wrapper

This is a lightweight Python utility that wraps common MySQL operations (CRUD) using mysql-connector-python. It provides clean, reusable methods for SELECT, INSERT, UPDATE, DELETE, and parameterized queries, with support for Pandas DataFrames and error handling. ✅ Features Easy-to-use CRUD operations, Parameterized query support &amp; error handling

# MySQL DB Helper for Python 🐍🛠️

This is a lightweight Python utility that wraps common MySQL operations (CRUD) using `mysql-connector-python`. It provides clean, reusable methods for `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and parameterized queries, with support for Pandas DataFrames and error handling.

---

## ✅ Features

- Easy-to-use CRUD operations
- Parameterized query support
- Built-in error handling
- Clean connection management
- Returns query results as Pandas DataFrames

---

## 📦 Installation

```bash
pip install mysql-connector-python pandas
```

---

---

## 🔧 Usage Example

```python
from mysql_helper import DatabaseConnection

# database connection
mydb = DatabaseConnection(
    host='localhost',
    user='root',
    password='password',
    database='db'
)

# update data
query = "UPDATE user SET name= 'karmal Rayan' WHERE user_id = 1;"
mydb.execute_update(query)

# insert user
query = "INSERT INTO user(name, email) VALUES('Gift Franklyne', 'franklyne@example.com')"
mydb.execute_update(query)

# Reading data
query= 'SELECT * FROM user;'
users = mydb.execute_read(query)
print(users)

# delete user
query = 'DELETE FROM user WHERE user_id = 10'
mydb.execute_delete(query)

# Reading data
query= 'SELECT * FROM user;'
users = mydb.execute_read(query)
print(users)
```

---

## 📚 Stored Procedure Examples

### 1. Stored Procedure to Update User

**MySQL Stored Procedure:**

```sql
DELIMITER //
CREATE PROCEDURE updateUser(IN userId INT, IN newEmail VARCHAR(100))
BEGIN
    UPDATE users SET email = newEmail WHERE id = userId;
END //
DELIMITER ;
```

**Python Usage:**

```python
# Calling the stored procedure to update email
update_proc = "CALL updateUser(1, 'updated@example.com')"
mydb.execute_update(update_proc)
```

---

### 2. Stored Procedure to Handle Transaction

**MySQL Stored Procedure:**

```sql
DELIMITER //
CREATE PROCEDURE transferAmount(
    IN senderId INT,
    IN receiverId INT,
    IN amount DECIMAL(10,2)
)
BEGIN
    START TRANSACTION;
    UPDATE accounts SET balance = balance - amount WHERE id = senderId;
    UPDATE accounts SET balance = balance + amount WHERE id = receiverId;
    COMMIT;
END //
DELIMITER ;
```

**Python Usage:**

```python
# Transfer 100.00 from user 1 to user 2
transfer_proc = "CALL transferAmount(1, 2, 100.00)"
mydb.execute_update(transfer_proc)
```

## 🧪 Dependencies

- `mysql-connector-python`
- `pandas`

---
