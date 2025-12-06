CREATE TABLE `ai_property_listings` (
	`id` integer PRIMARY KEY NOT NULL,
	`block_id` integer NOT NULL,
	`overall_score` integer,
	`walkability_score` integer,
	`food_score` integer,
	`transport_score` integer,
	`education_score` integer,
	`business_score` integer,
	`overall_reasoning` text,
	`listing_narrative` text,
	`model_name` text,
	`prompt_used` text,
	`generated_at` text NOT NULL,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `analytics_block_metrics` (
	`id` integer PRIMARY KEY NOT NULL,
	`block_id` integer,
	`last_updated` text,
	`median_resale_price` real,
	`median_rent` real,
	`implied_rental_yield` real,
	`price_per_sqm` real,
	`sales_volume_last_year` integer,
	`walkability_score` real,
	`food_access_score` real,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `analytics_neighborhood_scores` (
	`id` integer PRIMARY KEY NOT NULL,
	`town` text NOT NULL,
	`walkability_score` real,
	`food_accessibility_score` real,
	`transport_score` real
);
--> statement-breakpoint
CREATE TABLE `enriched_block_amenities` (
	`id` integer PRIMARY KEY NOT NULL,
	`block_id` integer,
	`amenity_type` text NOT NULL,
	`amenity_name` text NOT NULL,
	`distance_meters` real NOT NULL,
	`is_sheltered` integer,
	FOREIGN KEY (`block_id`) REFERENCES `enriched_hdb_blocks`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `enriched_hdb_blocks` (
	`id` integer PRIMARY KEY NOT NULL,
	`raw_property_id` integer,
	`block` text NOT NULL,
	`street` text NOT NULL,
	`town` text NOT NULL,
	`postal_code` text,
	`latitude` real,
	`longitude` real,
	`year_completed` integer,
	`total_units` integer,
	`has_commercial` integer,
	`estimated_value` real,
	`walkability_score` integer,
	`portal_links` text,
	`google_street_view_url` text,
	`last_enriched_at` text,
	FOREIGN KEY (`raw_property_id`) REFERENCES `rawHdbPropertyInfo`(`id`) ON UPDATE no action ON DELETE no action
);
