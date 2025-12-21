-- Init schema for LMSConnector
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Students
CREATE TABLE IF NOT EXISTS students (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  external_id TEXT UNIQUE NOT NULL,
  email TEXT,
  firstname TEXT,
  lastname TEXT,
  username TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Courses
CREATE TABLE IF NOT EXISTS courses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  external_id TEXT UNIQUE NOT NULL,
  shortname TEXT,
  fullname TEXT,
  category_id TEXT,
  visible BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Enrollments
CREATE TABLE IF NOT EXISTS enrollments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_course ON enrollments(student_id, course_id);

-- Grades
CREATE TABLE IF NOT EXISTS grades (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  grade_item TEXT,
  grade_value NUMERIC,
  grade_max NUMERIC,
  timestamp TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_grades_student_course ON grades(student_id, course_id);

-- Activity logs
CREATE TABLE IF NOT EXISTS activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  student_id UUID REFERENCES students(id) ON DELETE CASCADE,
  course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
  activity_type TEXT NOT NULL,
  resource_id TEXT,
  duration_seconds INTEGER,
  timestamp TIMESTAMP NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_logs(timestamp);

-- Sync logs
CREATE TABLE IF NOT EXISTS sync_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lms_type TEXT NOT NULL,
  sync_type TEXT NOT NULL,
  status TEXT NOT NULL,
  records_processed INTEGER DEFAULT 0,
  error_message TEXT,
  started_at TIMESTAMP NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sync_started_at ON sync_logs(started_at);

-- LMS Sources (to support multiple LMS instances)
CREATE TABLE IF NOT EXISTS lms_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  type TEXT NOT NULL CHECK (type IN ('moodle','canvas','blackboard')),
  base_url TEXT NOT NULL,
  token TEXT,
  oauth_client_id TEXT,
  oauth_client_secret TEXT,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_lms_sources_active_type ON lms_sources(active, type);
