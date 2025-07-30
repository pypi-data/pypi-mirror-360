
CREATE TABLE resource_type (
    name TEXT PRIMARY KEY
);

CREATE TABLE event_type (
    name TEXT PRIMARY KEY,
    template TEXT
);

INSERT INTO resource_type (name) VALUES
    ('playbook'),
    ('workflow'),
    ('target'),
    ('step'),
    ('task'),
    ('action');

INSERT INTO event_type (name, template) VALUES
    ('REGISTERED', 'Resource {{ resource_path }} version {{ resource_version }} was registered.'),
    ('UPDATED', 'Resource {{ resource_path }} version {{ resource_version }} was updated.'),
    ('UNCHANGED', 'Resource {{ resource_path }} already registered.'),
    ('EXECUTION_STARTED', 'Execution started for {{ resource_path }}.'),
    ('EXECUTION_FAILED', 'Execution failed for {{ resource_path }}.'),
    ('EXECUTION_COMPLETED', 'Execution completed for {{ resource_path }}.');
