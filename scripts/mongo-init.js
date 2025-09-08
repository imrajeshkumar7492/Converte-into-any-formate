// MongoDB initialization script for Converte Pro
db = db.getSiblingDB('converte_pro');

// Create collections with proper indexes
db.createCollection('jobs');
db.createCollection('users');
db.createCollection('files');
db.createCollection('stats');

// Create indexes for better performance
db.jobs.createIndex({ "id": 1 }, { unique: true });
db.jobs.createIndex({ "status": 1 });
db.jobs.createIndex({ "created_at": -1 });
db.jobs.createIndex({ "priority": 1 });
db.jobs.createIndex({ "conversion_type": 1 });

db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": -1 });

db.files.createIndex({ "job_id": 1 });
db.files.createIndex({ "created_at": -1 });
db.files.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

// Insert initial stats document
db.stats.insertOne({
  total_jobs: 0,
  completed_jobs: 0,
  failed_jobs: 0,
  total_files_processed: 0,
  total_data_processed: 0,
  last_updated: new Date()
});

print('Converte Pro database initialized successfully!');