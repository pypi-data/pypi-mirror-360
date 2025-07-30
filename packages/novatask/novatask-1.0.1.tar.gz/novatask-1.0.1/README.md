# README.md
"""
# NovaTask

NovaTask is a plug-and-play AI-powered database management and decision library that allows developers to easily perform CRUD operations and predictions across any database system.

## Installation

```bash
pip install novatask
```

## Usage Example

```python
from novaTask import NovaTask

nt = NovaTask(db_type='mongodb', db_uri='mongodb://localhost:27017/mydb', mode='offline')

# Add
nt.add('users', {'name': 'John'})

# Get
result = nt.get('users', {'name': 'John'})
print(result)

# Predict (only in online mode)
payload = {"action": "register", "data": {"email": "test@example.com"}, "user_context": {}}
prediction = nt.predict(payload)
print(prediction)
```

## License
MIT
"""
