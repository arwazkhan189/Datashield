import pandas as pd
import random
from faker import Faker
from tqdm import tqdm

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# Configuration
num_records = 500_000

# Sample data pools
genders = ['Male', 'Female', 'Other']
diseases = [
    'Diabetes', 'Hypertension', 'Asthma', 'Cancer', 'Arthritis', 
    'Flu', 'Migraine', 'COVID-19', 'Tuberculosis', 'Heart Disease'
]
medications = [
    'Paracetamol', 'Ibuprofen', 'Metformin', 'Amlodipine', 'Lisinopril',
    'Omeprazole', 'Azithromycin', 'Prednisone', 'Atorvastatin', 'Insulin'
]
hospitals = [
    'City Hospital', 'Green Valley Medical Center', 'Sunrise Clinic',
    'Metro Health Institute', 'Apollo Medicals', 'National Care Center'
]

# Generate data
data = []
for _ in tqdm(range(num_records), desc="Generating data"):
    name = fake.name()
    age = random.randint(1, 99)
    gender = random.choice(genders)
    pincode = fake.postcode()
    disease = random.choice(diseases)
    medication = random.choice(medications)
    visit_date = fake.date_between(start_date='-2y', end_date='today')
    doctor = fake.name()
    hospital = random.choice(hospitals)

    data.append([
        name, age, gender, pincode, disease, medication,
        visit_date, doctor, hospital
    ])

# Create DataFrame
columns = [
    'Name', 'Age', 'Gender', 'Pincode', 'Disease',
    'Medication', 'Visit_Date', 'Doctor_Name', 'Hospital_Name'
]
df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv('synthetic_healthcare_dataset.csv', index=False)

print("✅ Dataset generated: 'synthetic_healthcare_dataset.csv'")
