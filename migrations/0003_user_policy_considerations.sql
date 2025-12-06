-- Migration for user_policy_considerations

CREATE TABLE "user_policy_considerations" (
	"id" integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	"user_profile_id" integer NOT NULL,
	"notes" text,
	"created_at" text NOT NULL,
	"updated_at" text NOT NULL,
	FOREIGN KEY ("user_profile_id") REFERENCES "user_profiles" ("id") ON UPDATE no action ON DELETE no action
);
