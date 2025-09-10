// MongoDB initialization script
db = db.getSiblingDB('fileconverter');

// Create collections
db.createCollection('conversion_jobs');
db.createCollection('uploaded_files');

// Create indexes for better performance
db.conversion_jobs.createIndex({ "created_at": -1 });
db.conversion_jobs.createIndex({ "status": 1 });
db.conversion_jobs.createIndex({ "user_id": 1, "created_at": -1 });

db.uploaded_files.createIndex({ "created_at": -1 });
db.uploaded_files.createIndex({ "file_hash": 1 });

print('Database initialized successfully!');