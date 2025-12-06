CREATE TABLE `system_health_tests` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`run_id` text NOT NULL,
	`test_name` text NOT NULL,
	`status` text NOT NULL,
	`duration_ms` integer,
	`metadata` text,
	`result_json` text,
	`error` text,
	`executed_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
