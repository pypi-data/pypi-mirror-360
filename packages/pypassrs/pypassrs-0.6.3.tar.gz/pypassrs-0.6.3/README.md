# pypassrs

A Python wrapper around [passrs](https://crates.io/projects/passrs)

## Usage

```py
import pypassrs

# Initialize a new password storage
pypassrs.init(".passrs_storage")

# Generate a new password
password = pypassrs.generate()

# Insert the new password into the storage
pypassrs.insert("path/to/password", password)

# Alternatively, store the password that is generated
pypassrs.generate("path/to/password2")

# Get a password
pypassrs.show("path/to/password")

# Show password directory
print(pypassrs.tree())
```
