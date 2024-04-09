from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
from pymongo.common import ServerApi
from typing import List, Dict

# Initialize FastAPI app
app = FastAPI()

# Connect to MongoDB Atlas
uri = "mongodb+srv://cluster0.koikyan.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='C:\\Users\\kunal\\Downloads\\X509-cert-8493993245001309744.pem',
                     server_api=ServerApi('1'))
db = client['LIBRARYMANAGEMENTSYSTEM']
collection = db['students']

# MongoDB Document Schema using Pydantic
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

# Define a new Pydantic model for the simplified student response
class SimplifiedStudent(BaseModel):
    name: str
    age: int

# Create a new student
@app.post("/students", status_code=201, response_model=dict)
def create_student(student: Student):
    """
    API to create a student in the system. All fields are mandatory and required while creating the student in the system.
    """
    inserted_student = collection.insert_one(student.dict())
    return {"id": str(inserted_student.inserted_id)}

# List students with optional filters
@app.get("/students", response_model=Dict[str, List[SimplifiedStudent]])
def list_students(country: str = Query(None, description="To apply filter of country. If not given or empty, this filter should be applied."),
                 age: int = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result. If not given or empty, this filter should be applied.")):
    """
    An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.
    """
    filters = {}
    if country:
        filters["address.country"] = country
    if age is not None:
        filters["age"] = {"$gte": age}
    students = collection.find(filters)
    return {"data": [SimplifiedStudent(name=student["name"], age=student["age"]) for student in students]}

# Fetch a specific student by ID
@app.get("/students/{id}", status_code=200, response_model=Student)
def get_student(id: str):
    """
    Fetch a specific student by ID.
    """
    student = collection.find_one({"_id": ObjectId(id)})
    if student:
        return Student(**student)
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Update a student
@app.patch("/students/{id}", status_code=204)
def update_student(id: str, student: Student):
    """
    API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database.
    """
    updated_student = collection.update_one({"_id": ObjectId(id)}, {"$set": student.dict()})
    if updated_student.modified_count:
        return {}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete a student
@app.delete("/students/{id}", status_code=200)
def delete_student(id: str):
    """
    Delete a student by ID.
    """
    deleted_student = collection.delete_one({"_id": ObjectId(id)})
    if deleted_student.deleted_count:
        return {}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
