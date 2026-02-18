
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS experiment_runs (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'running'
);

CREATE TABLE IF NOT EXISTS parameters (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES experiment_runs(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES experiment_runs(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS artifacts (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES experiment_runs(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    type VARCHAR(50)
);
