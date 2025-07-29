# MSO (Mongo Schema Object Library)

**MSO** is a lightweight **Object-Document Mapper (ODM)** for **MongoDB** that allows Python developers to interact with MongoDB collections in an intuitive and Pythonic way. It offers the flexibility of a schema-less database with the convenience of strongly-typed classes, enabling seamless operations on MongoDB collections using familiar Python patterns.

---

## 🚀 Key Features:

- **Dynamic Model Generation**: Automatically generates Python classes from your MongoDB collection’s `$jsonSchema`.
- **Pythonic API**: Use common patterns like `save()`, `find_one()`, `update_one()`, etc.
- **REST API with Swagger**: Automatically generates a REST API for your models with Swagger documentation.
- **Deeply Nested Models**: Supports arbitrarily nested schemas, including arrays of objects.
- **Auto-validation**: Ensures types, enums, and structure match your schema.
- **Recursive Object Serialization**: Works out-of-the-box with nested documents and arrays.
- **Developer Tools**: Includes tree views, schema printers, and class introspection.

---

## 📦 Requirements

- Python 3.12+
- MongoDB with `$jsonSchema` validation on your collections

---

## 🔧 Installation
```bash
pip install mso
```

# Recommended MongoDB Validation Schema Format
```bash
{
  $jsonSchema: {
    bsonType: 'object',
    properties: {
      _id: {
        bsonType: 'objectId'
      },
      # ADD YOUR FIELDS HERE
      last_modified: {
        bsonType: [
          'date',
          'null'
        ]
      },
      created_at: {
        bsonType: [
          'date',
          'null'
        ]
      }
    },
    additionalProperties: false
  }
}
```

# 🛠️ Basic Usage
In this basic example we have already created a $jsonSchema validator for the "People" collection in MongoDB. We create a new person, update some information and save the person MongoDB.

```python
from pymongo import MongoClient
from mso.generator import get_model

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["mydb"]

# Generate a model based on the "people" collection's schema
People = get_model(db, "people")

# Create a new person
person = People(name="Tony Pajama", age=34)

# Add nested data
person.health.primary_physician.name = "Dr. Strange"
person.address.add(type="home", street="123 Elm", city="NY", state="NY", zip="10001")

# Save to the database
person.save()
```

# 🧪 View Your Class Tree
```python
People.print_nested_class_tree()
```
#### Output
```bash
Tree View:
└── people
    ├── name: str
    ├── age: int
    ├── email: str
    ├── gender: enum [Male, Female, Other]
    ├── addresses: List[addresses_item]
    │   ├── type: enum [Home, Business, Other]
    │   ├── street: str
    │   ├── city: str
    │   ├── state: str
    │   └── zip: str
    └── health: Object
        ├── medical_history: Object
        │   ├── conditions: List[conditions_item]
        │   │   ├── name: str
        │   │   ├── diagnosed: str
        │   │   └── medications: List[medications_item]
        │   │       ├── name: str
        │   │       ├── dose: str
        │   │       └── frequency: str
        │   └── allergies: List
        └── primary_physician: Object
            ├── name: str
            └── contact: Object
                ├── phone: str
                └── address: Object
                    ├── street: str
                    ├── city: str
                    ├── state: str
                    └── zip: str
```

# 🔍 Querying the Database
```python
# Find one
person = People.find_one({"name": "Tony Pajama"})

# Find many
person_list = People.find_many(sort=[("created_at", -1)], limit=10)
```

# Document Manipulation
```python
# Delete
person.delete()

# Clone
new_person = person.clone()
```
# 📊 Data Summary & Analysis
MSO includes a powerful .summarize() method to help you quickly explore and understand your MongoDB collection. It performs a field-level summary with support for:

### ⚙️ Options
**sample_size**: Limit the number of documents to analyze (defaults to all)

**top**: Number of top strings to return (default: 5)

### 🔍 Example

```python
import os
from pymongo import MongoClient
from mso.generator import get_model

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "mydb")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Get the model for the "people" collection
People = get_model(db, "people")

print(People.summarize(top=10))
```
### 🧠 Example Output
```bash
{
  "sample_size": 1000,
  "fields": {
    "name": {
      "type": "str",
      "count": 1000,
      "missing": 0,
      "unique": 993,
      "top_5": [
        {
          "value": "Tony Pajama",
          "count": 7,
          "percent": 0.007
        },
        ...
      ]
    },
    "age": {
      "type": "int",
      "count": 978,
      "missing": 22,
      "unique": 43,
      "min": 1,
      "max": 99,
      "mean": 38.6,
      "median": 34,
      "stdev": 19.2
    },
    "health.primary_physician.name": {
      "type": "str",
      "count": 1000,
      "missing": 0,
      "unique": 12,
      "top_5": [
        {
          "value": "Dr. Strange",
          "count": 46,
          "percent": 0.046
        },
        ...
      ]
    }
  }
}

```

# 🔍 Document Comparison
MSO makes it easy to compare two MongoDB documents—either as model instances or dictionaries—using the powerful Model.diff() method. It supports:

- Deep recursive comparison of nested objects and arrays
- Detection of value and type changes
- Flat or nested output formatting
- Optional strict mode (type-sensitive)
- Filtering for specific fields or changes

### Basic Example

```python
from mso.generator import get_model
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["mydb"]
People = get_model(db, "people")

# Create a valid model instance
person1 = People(name="Alice", age=30, gender="Female")

# Use a dictionary with type mismatch (age as string)
person2 = {
    "name": "Alice",
    "age": "30",  # string instead of int
    "gender": "Female"
}

diff = People.diff(person1, person2, strict=True)

from pprint import pprint

pprint(diff)
```
### Example Output
```bash
{
  'age': {
    'old': 30,
    'new': '30',
    'type_changed': True
  }
}
```

# Convert to and from dictionary
```python
person_dict = person.to_dict()
```

# ⏱ Automatic Timestamps
By default, models automatically include created_at and updated_at fields to track when a document is created or modified. These are managed internally and do not need to be defined in your schema.

### 🔧 How it works
created_at is set once, when the document is first saved.

updated_at is updated every time the document is modified and saved.

Both are stored as UTC datetime.datetime objects.

### 🚫 Disabling timestamps
Timestamps are enabled by default. To disable them, set the `timestamps` parameter to `False` when creating a model.

```python
import os
from time import sleep
from pymongo import MongoClient
from mso.generator import get_model

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "mydb")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Get the model for the collection
People = get_model(db, "people")

# Disable timestamps for a specific model or instance
People.timestamps_enabled = False
```




# 🧩 Lifecycle Hooks
You can use decorators like @pre_save, @post_save, @pre_delete, and @post_delete to hook into model lifecycle events. This is useful for setting defaults, cleaning up, triggering logs, or validating conditions.
### Example: Automatically output a message when a document is saved

```python
from mso.base_model import MongoModel, pre_save, post_save
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["mydb"]


# Define the model hooks you would like to use
class People(MongoModel):
    @post_save  # This method will be called after the document is saved
    def confirm_save(self):
        print(f"[+] Document saved: {self.name}")


People = get_model(db, "people")

person = People(name="Jane Doe")
person.save()

# Output:
# [+] Document saved: Jane Doe
```

# 🧪 REST API with Swagger
MSO can automatically generate a REST API for your models, complete with Swagger documentation. This allows you to easily expose your MongoDB collections as RESTful endpoints.
```python
from mso.api import start_api
from pymongo import MongoClient
from mso.generator import get_model

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["mydb"]

start_api(db)
```
This will start a REST API server with Swagger documentation at http://127.0.0.1:8000/docs


## 🔌 Custom API Endpoints

You can extend the auto-generated API with your own custom routes using the extra_routes parameter in start_api.

### ➕ Example

```python
from fastapi import APIRouter
from mso.api import start_api

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["mydb"]

# Define your custom routes
custom_router = APIRouter()

@custom_router.get("/people/stats", tags=["People"])
def get_people_stats():
    return {"message": "Custom stats for the People collection"}

# Start the API with custom routes
start_api(
    db=db,
    collections=["*"],
    extra_routes=custom_router
)
```


# 🔗 Community & Links
PyPi: https://pypi.org/project/MSO/

Reddit: https://www.reddit.com/r/MSO_Mongo_Python_ORM/

Gitlab: https://github.com/chuckbeyor101/MSO-Mongo-Schema-Object-Library.git  


# 🛡 LICENSE & COPYWRIGHT WARNING
MSO Copyright (c) 2025 by Charles L Beyor                                                                           
is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.                          
To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/4.0/                            
                                                                                                                     
Unless required by applicable law or agreed to in writing, software                                                 
distributed under the License is distributed on an **"AS IS" BASIS,                                                   
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND**, either express or implied.

See the License for the specific language governing permissions and limitations under the License.


# 