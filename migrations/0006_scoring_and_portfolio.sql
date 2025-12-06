CREATE TABLE `hdb_frontend_data` (
	`id` integer PRIMARY KEY NOT NULL,
	`block_id` integer NOT NULL,
	`google_street_view_url` text,
	`last_enriched_at` text,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `hdb_score_lah` (
	`id` integer PRIMARY KEY NOT NULL,
	`block_id` integer NOT NULL,
	`score_lah` integer,
	`score_lah_rationale` text,
	`walkability` integer,
	`walkability_rationale` text,
	`food_access` integer,
	`food_access_rationale` text,
	`hawker` integer,
	`hawker_rationale` text,
	`mrt` integer,
	`mrt_rationale` text,
	`bus` integer,
	`bus_rationale` text,
	`education` integer,
	`education_rationale` text,
	`parks` integer,
	`parks_rationale` text,
	`noise_level` integer,
	`noise_level_rationale` text,
	`traffic_level` integer,
	`traffic_level_rationale` text,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `hdb_valuation_data` (
	`id` integer PRIMARY KEY NOT NULL,
	`block_id` integer NOT NULL,
	`flat_type` text NOT NULL,
	`est_min_val_buy` real,
	`est_avg_val_buy` real,
	`est_max_val_buy` real,
	`est_min_val_rent` real,
	`est_avg_val_rent` real,
	`est_max_val_rent` real,
	`total_units` integer,
	`latest_purchase_date` text,
	`avg_annual_purchases` real,
	`implied_rental_yield` real,
	`sales_volume_last_year` integer,
	`last_enriched_at` text,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `portfolio_analysis` (
	`id` integer PRIMARY KEY NOT NULL,
	`portfolio_id` integer NOT NULL,
	`generated_at` text NOT NULL,
	`rent_gap` real,
	`rent_advice` text,
	`market_value_gap` real,
	`resale_outlook` text,
	`score_lah_impact` text,
	`ai_action_items` text,
	FOREIGN KEY (`portfolio_id`) REFERENCES `user_portfolio`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `user_portfolio` (
	`id` integer PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`block_id` integer NOT NULL,
	`flat_type` text,
	`unit_number` text,
	`ownership_status` text NOT NULL,
	`acquisition_date` text,
	`acquisition_price` real,
	`current_rent` real,
	`created_at` text NOT NULL,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
ALTER TABLE `ai_property_listings` ADD `pro_list` text;--> statement-breakpoint
ALTER TABLE `ai_property_listings` ADD `con_list` text;--> statement-breakpoint
ALTER TABLE `ai_property_listings` DROP COLUMN `overall_score`;--> statement-breakpoint
ALTER TABLE `ai_property_listings` DROP COLUMN `walkability_score`;--> statement-breakpoint
ALTER TABLE `ai_property_listings` DROP COLUMN `food_score`;--> statement-breakpoint
ALTER TABLE `ai_property_listings` DROP COLUMN `transport_score`;--> statement-breakpoint
ALTER TABLE `ai_property_listings` DROP COLUMN `education_score`;--> statement-breakpoint
ALTER TABLE `ai_property_listings` DROP COLUMN `business_score`;--> statement-breakpoint
ALTER TABLE `enriched_hdb_blocks` DROP COLUMN `estimated_value`;--> statement-breakpoint
ALTER TABLE `enriched_hdb_blocks` DROP COLUMN `walkability_score`;--> statement-breakpoint
ALTER TABLE `enriched_hdb_blocks` DROP COLUMN `portal_links`;--> statement-breakpoint
ALTER TABLE `enriched_hdb_blocks` DROP COLUMN `google_street_view_url`;--> statement-breakpoint
ALTER TABLE `enriched_hdb_blocks` DROP COLUMN `last_enriched_at`;
