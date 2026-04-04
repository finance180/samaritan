-- Samaritan LMS — Supabase Database Schema
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor > New Query)

-- ============================================
-- Tasks Table
-- ============================================
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  task_id TEXT UNIQUE,
  title TEXT NOT NULL,
  business TEXT NOT NULL DEFAULT 'Personal',
  project TEXT DEFAULT '',
  priority TEXT NOT NULL DEFAULT 'Medium',
  due_date DATE,
  assigned_to TEXT NOT NULL DEFAULT 'Brian',
  notes TEXT DEFAULT '',
  recurrence TEXT NOT NULL DEFAULT 'None',
  recurrence_next_date DATE,
  status TEXT NOT NULL DEFAULT 'Active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

-- Auto-generate task_id (T-001, T-002, ...) from serial id
CREATE OR REPLACE FUNCTION generate_task_id()
RETURNS TRIGGER AS $$
BEGIN
  NEW.task_id := 'T-' || LPAD(NEW.id::TEXT, 3, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_task_id
  BEFORE INSERT ON tasks
  FOR EACH ROW
  EXECUTE FUNCTION generate_task_id();

-- ============================================
-- Projects Table
-- ============================================
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  project_id TEXT UNIQUE,
  name TEXT NOT NULL,
  business TEXT NOT NULL DEFAULT 'Personal',
  description TEXT DEFAULT ''
);

-- Auto-generate project_id (P-001, P-002, ...) from serial id
CREATE OR REPLACE FUNCTION generate_project_id()
RETURNS TRIGGER AS $$
BEGIN
  NEW.project_id := 'P-' || LPAD(NEW.id::TEXT, 3, '0');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_project_id
  BEFORE INSERT ON projects
  FOR EACH ROW
  EXECUTE FUNCTION generate_project_id();

-- ============================================
-- Row Level Security (RLS)
-- ============================================
-- Enable RLS but allow all operations via anon key
-- (single-user system, no multi-tenant restrictions needed)

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all task operations" ON tasks
  FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all project operations" ON projects
  FOR ALL USING (true) WITH CHECK (true);

-- ============================================
-- Indexes for common query patterns
-- ============================================
CREATE INDEX idx_tasks_due_date ON tasks (due_date);
CREATE INDEX idx_tasks_business ON tasks (business);
CREATE INDEX idx_tasks_status ON tasks (status);
CREATE INDEX idx_tasks_assigned_to ON tasks (assigned_to);
CREATE INDEX idx_tasks_completed_at ON tasks (completed_at);
CREATE INDEX idx_projects_business ON projects (business);
