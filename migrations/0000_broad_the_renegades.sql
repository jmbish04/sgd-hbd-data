CREATE TABLE `agentChatLogs` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`userId` text NOT NULL,
	`role` text NOT NULL,
	`messageContent` text NOT NULL,
	`insightExtracted` integer DEFAULT false,
	`createdAt` text DEFAULT (datetime('now'))
);
--> statement-breakpoint
CREATE TABLE `buyerPreferences` (
	`id` integer PRIMARY KEY NOT NULL,
	`userId` text NOT NULL,
	`targetTowns` text,
	`flatTypes` text,
	`priceRangeMin` real,
	`priceRangeMax` real,
	`amenities` text,
	`employmentCenters` text,
	`createdAt` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`updatedAt` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE `logs` (
	`id` integer PRIMARY KEY NOT NULL,
	`timestamp` text NOT NULL,
	`level` text NOT NULL,
	`component` text NOT NULL,
	`message` text NOT NULL,
	`traceId` text,
	`userId` text,
	`sessionId` text,
	`requestId` text,
	`error` text,
	`metadata` text,
	`createdAt` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE `marketSnapshots` (
	`id` integer PRIMARY KEY NOT NULL,
	`town` text NOT NULL,
	`flatType` text NOT NULL,
	`price` real NOT NULL,
	`yieldRate` real,
	`createdAt` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `policies` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`category` text NOT NULL,
	`title` text NOT NULL,
	`content` text NOT NULL,
	`sourceUrl` text,
	`lastUpdated` text DEFAULT (datetime('now'))
);
--> statement-breakpoint
CREATE TABLE `propertyInsights` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`propertyId` text NOT NULL,
	`type` text NOT NULL,
	`content` text NOT NULL,
	`confidence` real DEFAULT 1,
	`createdAt` text DEFAULT (datetime('now'))
);
--> statement-breakpoint
CREATE TABLE `rawGovMarketsHawkerCentres` (
	`id` integer PRIMARY KEY NOT NULL,
	`datasetId` text,
	`ingestedAt` text,
	`nameOfCentre` text,
	`locationOfCentre` text,
	`typeOfCentre` text,
	`owner` text,
	`noOfStalls` integer,
	`noOfCookedFoodStalls` integer,
	`noOfMktProduceStalls` integer,
	`isMarket` integer,
	`isHawkerCentre` integer
);
--> statement-breakpoint
CREATE TABLE `rawHawkerCentresGeojson` (
	`id` integer PRIMARY KEY NOT NULL,
	`datasetId` text,
	`ingestedAt` text,
	`name` text,
	`description` text,
	`status` text,
	`addressMyenv` text,
	`addressBuildingName` text,
	`addressPostalCode` text,
	`addressStreetName` text,
	`latitude` real,
	`longitude` real,
	`geometryType` text,
	`numberOfCookedFoodStalls` integer,
	`estOriginalCompletionDate` text,
	`implementationDate` text,
	`awardedDate` text
);
--> statement-breakpoint
CREATE TABLE `rawHawkerStallsAnnual` (
	`id` integer PRIMARY KEY NOT NULL,
	`datasetId` text,
	`ingestedAt` text,
	`year` integer,
	`noHawkerStalls` integer
);
--> statement-breakpoint
CREATE TABLE `rawHdbDemand` (
	`id` integer PRIMARY KEY NOT NULL,
	`startYear` integer,
	`endYear` integer,
	`flatType` text,
	`demandForFlats` integer
);
--> statement-breakpoint
CREATE TABLE `raw_hdb_existing_building` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`BLK_NO` integer,
	`ST_COD` text,
	`ENTITYID` integer,
	`POSTAL_COD` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.AREA` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `rawHdbMedianRent` (
	`id` integer PRIMARY KEY NOT NULL,
	`town` text,
	`flatType` text,
	`flatTypeRaw` text,
	`medianRent` real,
	`medianRentRaw` text,
	`quarter` integer,
	`quarterRaw` text,
	`year` integer,
	`startMonth` integer,
	`endMonth` integer
);
--> statement-breakpoint
CREATE TABLE `rawHdbPropertyInfo` (
	`id` integer PRIMARY KEY NOT NULL,
	`blkNo` text,
	`street` text,
	`maxFloorLvl` integer,
	`yearCompleted` integer,
	`bldgContractTown` text,
	`residential` text,
	`commercial` text,
	`marketHawker` text,
	`miscellaneous` text,
	`multistoreyCarpark` text,
	`precinctPavilion` text,
	`oneRoomSold` integer,
	`twoRoomSold` integer,
	`threeRoomSold` integer,
	`fourRoomSold` integer,
	`fiveRoomSold` integer,
	`execSold` integer,
	`multigenSold` integer,
	`studioApartmentSold` integer,
	`oneRoomRental` integer,
	`twoRoomRental` integer,
	`threeRoomRental` integer,
	`otherRoomRental` integer
);
--> statement-breakpoint
CREATE TABLE `rawHdbRentalPrices` (
	`id` integer PRIMARY KEY NOT NULL,
	`rentApprovalDate` text,
	`town` text,
	`block` text,
	`streetName` text,
	`flatType` text,
	`monthlyRent` real,
	`latitude` real,
	`longitude` real,
	`postalCode` text,
	`isGeocoded` integer DEFAULT false,
	`rentApprovalYear` integer,
	`rentApprovalMonth` integer
);
--> statement-breakpoint
CREATE TABLE `rawHdbResaleIndex` (
	`id` integer PRIMARY KEY NOT NULL,
	`town` text,
	`flatType` text,
	`index` real,
	`quarter` integer,
	`quarterRaw` text,
	`year` integer,
	`datasetId` text,
	`ingestedAt` text
);
--> statement-breakpoint
CREATE TABLE `rawHdbResalePrices` (
	`id` integer PRIMARY KEY NOT NULL,
	`month` text,
	`year` integer,
	`town` text,
	`flatType` text,
	`block` text,
	`streetName` text,
	`storeyRange` text,
	`floorAreaSqm` real,
	`flatModel` text,
	`leaseCommenceDate` integer,
	`remainingLease` text,
	`resalePrice` real,
	`monthRaw` text,
	`remainingLeaseYears` integer,
	`remainingLeaseMonths` integer,
	`leaseExpirationDate` text,
	`latitude` real,
	`longitude` real,
	`postalCode` text,
	`isGeocoded` integer DEFAULT false
);
--> statement-breakpoint
CREATE TABLE `rawLtaBusStops` (
	`busStopCode` text PRIMARY KEY NOT NULL,
	`roadName` text,
	`description` text,
	`latitude` real,
	`longitude` real,
	`ingestedAt` text
);
--> statement-breakpoint
CREATE TABLE `rawLtaMrtStations` (
	`stationCode` text PRIMARY KEY NOT NULL,
	`stationName` text,
	`latitude` real,
	`longitude` real,
	`lineCode` text,
	`ingestedAt` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_bus_stops` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_carpark_hdb` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_carpark_ura` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`UNIQUEID` text,
	`NAME` text,
	`CLASS` text,
	`ADDITIONAL_INFO` text,
	`INC_CRC` text,
	`FMEL_UPD_D` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_chas_clinics` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_community_clubs` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`ADDRESSPOSTALCODE` integer,
	`LANDXADDRESSPOINT` integer,
	`LANDYADDRESSPOINT` integer,
	`ADDRESSBLOCKHOUSENUMBER` integer,
	`ADDRESSBUILDINGNAME` text,
	`ADDRESSFLOORNUMBER` integer,
	`ADDRESSSTREETNAME` text,
	`ADDRESSTYPE` integer,
	`DESCRIPTION` text,
	`NAME` text,
	`HYPERLINK` integer,
	`PHOTOURL` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`ADDRESSUNITNUMBER` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_cycling_network` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_dengue_clusters` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`OID` integer,
	`LU_DESC` text,
	`LU_TEXT` text,
	`GPR` text,
	`WHITE_Q_MX` integer,
	`GPR_B_MIN` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.AREA` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_eating_establishments` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_fire_stations` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`ADDRESSBLOCKHOUSENUMBER` integer,
	`ADDRESSBUILDINGNAME` integer,
	`ADDRESSFLOORNUMBER` integer,
	`ADDRESSPOSTALCODE` integer,
	`ADDRESSSTREETNAME` text,
	`ADDRESSTYPE` integer,
	`DESCRIPTION` integer,
	`HYPERLINK` integer,
	`LANDXADDRESSPOINT` integer,
	`LANDYADDRESSPOINT` integer,
	`NAME` text,
	`PHOTOURL` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`ADDRESSUNITNUMBER` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_infant_care` (
	`id` text PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`DataSeries` text,
	`year` integer,
	`value` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_mrt_station_exits` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID_1` integer,
	`LAST_UPDATED` integer,
	`NAME` text,
	`DESCRIPTION` text,
	`STATUS` text,
	`ESTMT_CNSTRN_CMCMNT` text,
	`ESTMT_CNSTRN_CMPLTN` text,
	`CNSTRN_CMCMNT` integer,
	`IMPLMT_ORG` text,
	`QSM_CONTACT` text,
	`CTRCTR_NAME` integer,
	`CTRCTR_CNTCT` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.AREA` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_museums` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_park_connector` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`PRP_STATUS` text,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_police_establishments` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_preschool_centres` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID_1` integer,
	`L_CODE` text,
	`NAME` text,
	`N_RESERVE` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE_1.AREA` integer,
	`SHAPE_1.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_public_libraries` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`ADDRESSBLOCKHOUSENUMBER` integer,
	`ADDRESSBUILDINGNAME` integer,
	`ADDRESSFLOORNUMBER` integer,
	`ADDRESSPOSTALCODE` integer,
	`ADDRESSSTREETNAME` text,
	`ADDRESSTYPE` integer,
	`DESCRIPTION` text,
	`HYPERLINK` integer,
	`LANDXADDRESSPOINT` integer,
	`LANDYADDRESSPOINT` integer,
	`NAME` text,
	`PHOTOURL` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`ADDRESSUNITNUMBER` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_rainfall_readings` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`LU_DESC` text,
	`LU_TEXT` integer,
	`GPR` text,
	`WHI_Q_MX` integer,
	`GPR_B_MN` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.AREA` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_school_directory` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`VENUE` text,
	`ADDRESSBLOCKHOUSENUMBER` integer,
	`ADDRESSSTREETNAME` text,
	`POSTAL_CODE` integer,
	`DETAILS` text,
	`INC_CRC` text,
	`FMEL_UPD_D` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_sports_facilities` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`HYPERLINK` text,
	`DESCRIPTION` integer,
	`POSTALCODE` integer,
	`KEEPERNAME` text,
	`TOTALROOMS` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`NAME` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_sports_fields` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_student_care_centres` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_supermarkets` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`Name` text,
	`Description` text
);
--> statement-breakpoint
CREATE TABLE `raw_sg_taxi_stands` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`NAME` text,
	`X` integer,
	`Y` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_traffic_incidents` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`GRND_LEVEL` text,
	`RAIL_TYPE` text,
	`NAME` text,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.AREA` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `raw_sg_traffic_speed_bands` (
	`id` integer PRIMARY KEY NOT NULL,
	`dataset_id` text,
	`ingested_at` text,
	`OBJECTID` integer,
	`FEATUREID` integer,
	`ZORDER` integer,
	`ANNOTATIONCLASSID` integer,
	`SYMBOLID` integer,
	`STATUS` integer,
	`TEXTSTRING` text,
	`FONTNAME` text,
	`FONTSIZE` integer,
	`BOLD` integer,
	`ITALIC` integer,
	`UNDERLINE` integer,
	`VERTICALALIGNMENT` integer,
	`HORIZONTALALIGNMENT` integer,
	`XOFFSET` integer,
	`YOFFSET` integer,
	`ANGLE` integer,
	`FONTLEADING` integer,
	`WORDSPACING` integer,
	`CHARACTERWIDTH` integer,
	`CHARACTERSPACING` integer,
	`FLIPANGLE` integer,
	`OVERRIDE` integer,
	`INC_CRC` text,
	`FMEL_UPD_D` integer,
	`SHAPE.AREA` integer,
	`SHAPE.LEN` integer
);
--> statement-breakpoint
CREATE TABLE `traceEvents` (
	`id` integer PRIMARY KEY NOT NULL,
	`traceId` text NOT NULL,
	`eventId` text NOT NULL,
	`timestamp` text NOT NULL,
	`level` text NOT NULL,
	`component` text NOT NULL,
	`action` text NOT NULL,
	`message` text NOT NULL,
	`data` text,
	`codeLocation` text,
	`createdAt` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE `traces` (
	`id` text PRIMARY KEY NOT NULL,
	`traceId` text NOT NULL,
	`parentId` text,
	`name` text NOT NULL,
	`component` text NOT NULL,
	`status` text NOT NULL,
	`startTime` text NOT NULL,
	`endTime` text,
	`duration` integer,
	`metadata` text,
	`createdAt` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE TABLE `trackedProperties` (
	`id` integer PRIMARY KEY NOT NULL,
	`userId` text NOT NULL,
	`block` text NOT NULL,
	`street` text NOT NULL,
	`floorAreaSqm` real NOT NULL,
	`flatType` text NOT NULL,
	`leaseCommenceDate` integer NOT NULL,
	`acquisitionDate` text NOT NULL,
	`notes` text,
	`createdAt` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`datasetId` text,
	`ingestedAt` text
);
--> statement-breakpoint
CREATE TABLE `userFeedbackEvents` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`userId` text NOT NULL,
	`propertyId` text,
	`actionType` text NOT NULL,
	`notes` text,
	`createdAt` text DEFAULT (datetime('now'))
);
--> statement-breakpoint
CREATE TABLE `userInsights` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`userId` text NOT NULL,
	`type` text NOT NULL,
	`content` text NOT NULL,
	`confidence` real DEFAULT 1,
	`createdAt` text DEFAULT (datetime('now'))
);
--> statement-breakpoint
CREATE TABLE `userPortfolio` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`userId` text NOT NULL,
	`propertyId` text,
	`acquisitionDate` text,
	`purchasePrice` real,
	`currentValuation` real,
	`createdAt` text DEFAULT (datetime('now'))
);
--> statement-breakpoint
CREATE TABLE `userPreferenceProfiles` (
	`userId` text PRIMARY KEY NOT NULL,
	`budgetMin` integer,
	`budgetMax` integer,
	`preferredTowns` text,
	`flatTypes` text,
	`amenities` text,
	`weightPrice` real DEFAULT 1.0,
	`weightProximityMrt` real DEFAULT 1.0,
	`weightLeaseLife` real DEFAULT 1.0,
	`lastRunAt` text,
	`createdAt` text DEFAULT (datetime('now')),
	`updatedAt` text DEFAULT (datetime('now'))
);
