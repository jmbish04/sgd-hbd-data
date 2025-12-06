
import { drizzle } from 'drizzle-orm/d1';
import { eq, sql, and } from 'drizzle-orm';
import * as schema from '../schema_enriched';
import { rawHdbPropertyInfo } from '../schema';

import { AiService } from './ai';

// OneMap API Constants
const ONEMAP_THEMES_URL = 'https://www.onemap.gov.sg/api/public/themesvc';

// Types for OneMap Responses
interface OneMapThemeResult {
    Theme_Name: string;
    LatLng: string; // "1.345,103.876"
    NAME: string;
    [key: string]: any;
}

export class HDBEnrichmentService {
    private db;
    private aiService: AiService;

    constructor(private env: Env) {
        this.db = drizzle(env.DB, { schema });
        this.aiService = new AiService(env.AI);
    }

    /**
     * Main Orchestrator: Enriches a single block
     */
    async enrichBlock(blockId: number): Promise<void> {
        // 1. Fetch Block Data
        const block = await this.db.query.enrichedHdbBlocks.findFirst({
            where: eq(schema.enrichedHdbBlocks.id, blockId),
        });

        if (!block || !block.latitude || !block.longitude) {
            console.error(`Block ${blockId} not found or missing geocoordinates.`);
            return;
        }

        const lat = block.latitude;
        const long = block.longitude;

        // 2. Score-Lah! Calculation (OneMap + Internal)
        const scores = await this.calculateScoreLah(lat, long);

        // 3. Valuation Breakdown (Internal Logic)
        const valuations = await this.getValuationBreakdown(blockId);

        // 4. Frontend Assets
        const frontendData = await this.generateFrontendAssets(block.block, block.street, lat, long);

        // 5. Database UPSERTs
        await this.saveEnrichmentData(blockId, scores, valuations, frontendData);
    }

    /**
     * Calculates "Score-Lah!" metrics using OneMap + Internal Amenities
     */
    /**
     * Calculates "Score-Lah!" metrics using OneMap + Internal Amenities + AI Insights
     */
    private async calculateScoreLah(lat: number, long: number) {
        // 1. Fetch Raw Amenities from OneMap
        const hawkers = await this.searchOneMapTheme('hawkercentre', lat, long, 1000);
        const supermarkets = await this.searchOneMapTheme('supermarkets', lat, long, 1000);
        const kindergartens = await this.searchOneMapTheme('kindergartens', lat, long, 1000);
        const parks = await this.searchOneMapTheme('nationalparks', lat, long, 2000);

        // Mocking MRT/Bus for now (In prod, fetch 'mrt_station_exit' / 'bus_busstop')
        const mrts = await this.searchOneMapTheme('mrt_station_exit', lat, long, 800) || [];
        const buses = await this.searchOneMapTheme('bus_stop', lat, long, 400) || [];

        // 2. Calculate Quantitative Scores (0-100)
        const foodScore = this.calculateFoodScore(hawkers.length, supermarkets.length);
        const parkScore = this.calculateParkScore(parks.length);
        const educationScore = this.calculateEducationScore(kindergartens.length);
        const transportScore = this.calculateTransportScore(mrts.length, buses.length);
        const walkabilityScore = this.calculateWalkabilityScore(mrts.length, buses.length, hawkers.length + supermarkets.length);

        const overallScore = Math.round((foodScore + parkScore + educationScore + transportScore + walkabilityScore) / 5);

        // 3. AI Generated Insights & Rationales
        const amenitiesContext = {
            hawkers: hawkers.length,
            supermarkets: supermarkets.length,
            parks: parks.length,
            kindergartens: kindergartens.length,
            mrts: mrts.length,
            busStops: buses.length
        };

        const scoresContext = {
            overall: overallScore,
            food: foodScore,
            parks: parkScore,
            education: educationScore,
            transport: transportScore
        };

        // Call the AI (Reasoning + Stucturing)
        const insights = await this.aiService.generateScoreLahInsights(amenitiesContext, scoresContext);

        return {
            scoreLah: overallScore,
            scoreLahRationale: insights.scoreLahRationale,

            foodAccess: foodScore,
            foodAccessRationale: insights.foodAccessRationale,

            parks: parkScore,
            parksRationale: insights.parksRationale,

            education: educationScore,
            educationRationale: insights.educationRationale,

            // New fields
            hawker: Math.min(100, hawkers.length * 20),
            hawkerRationale: `${hawkers.length} hawkers nearby.`, // Simple fallback or could add to AI
            mrt: Math.min(100, mrts.length * 50),
            mrtRationale: `${mrts.length} stations nearby.`,
            bus: Math.min(100, buses.length * 10),
            busRationale: `${buses.length} bus stops nearby.`,

            walkability: walkabilityScore,
            walkabilityRationale: insights.transportRationale, // Reusing transport rationale or could separate

            noiseLevel: insights.noiseLevel,
            noiseLevelRationale: insights.noiseLevelRationale,

            trafficLevel: insights.trafficLevel,
            trafficLevelRationale: insights.trafficLevelRationale
        };
    }

    // --- Scoring Helper Functions ---

    /**
     * Calculates Food Access Score based on variety and count.
     * Heuristic: Hawkers are weighted 3x more than supermarkets for "local flavour".
     */
    private calculateFoodScore(hawkerCount: number, supermarketCount: number): number {
        const score = (hawkerCount * 15) + (supermarketCount * 5);
        return Math.min(100, score);
    }

    /**
     * Calculates Green/Parks Score.
     * Heuristic: Parks are valuable but diminishing returns after 3-4 parks.
     */
    private calculateParkScore(parkCount: number): number {
        return Math.min(100, parkCount * 25);
    }

    /**
     * Calculates Education Score.
     * Heuristic: Based on density of Kindergartens (primary proxy for young family amenities).
     */
    private calculateEducationScore(kindergartenCount: number): number {
        return Math.min(100, kindergartenCount * 10);
    }

    /**
     * Calculates Transport Score.
     * Heuristic: MRTs are king (50pts each), Bus stops support (5pts each).
     */
    private calculateTransportScore(mrtCount: number, busStopCount: number): number {
        return Math.min(100, (mrtCount * 50) + (busStopCount * 5));
    }

    /**
     * Calculates Walkability Score.
     * Implies density of nodes within walking distance.
     */
    private calculateWalkabilityScore(mrtCount: number, busStopCount: number, amenityCount: number): number {
        // More nodes = more walkable destinations
        const nodeScore = (mrtCount * 20) + (busStopCount * 2) + (amenityCount * 5);
        return Math.min(100, nodeScore);
    }

    /**
     * Generates Valuation stubs
     */
    private async getValuationBreakdown(blockId: number) {
        // 1. Get Block Info to match Resale Prices
        const blockInfo = await this.db.query.enrichedHdbBlocks.findFirst({
            where: eq(schema.enrichedHdbBlocks.id, blockId),
            columns: { block: true, street: true }
        });

        if (!blockInfo) return [];

        // 1.5 Fetch Property Info for Unit Counts
        // Note: rawHdbPropertyInfo has columns like 'fourRoomSold', 'fiveRoomSold'
        const [propertyInfo] = await this.db.select().from(rawHdbPropertyInfo)
            .where(and(
                eq(rawHdbPropertyInfo.blkNo, blockInfo.block),
                eq(rawHdbPropertyInfo.street, blockInfo.street)
            ))
            // .limit(1) - D1 select returns array, we take first
            ;

        // 2. Aggregate Resale Prices (Last 2 Years)
        // Note: Joining rawHdbResalePrices on block/street.
        // We use raw SQL for aggregation efficiency.
        const query = sql`
            SELECT 
                flatType,
                MIN(resalePrice) as minPrice,
                AVG(resalePrice) as avgPrice,
                MAX(resalePrice) as maxPrice,
                COUNT(*) as salesVolume,
                MAX(month) as latestTransaction
            FROM rawHdbResalePrices
            WHERE block LIKE ${`%${blockInfo.block}%`}
            AND streetName LIKE ${`%${blockInfo.street}%`}
            AND month >= date('now', '-24 months')
            GROUP BY flatType
        `;

        const results = await this.db.run(query).catch(e => {
            console.error("Valuation Aggregation Failed:", e);
            return { results: [] };
        });

        // Helper to map flatType string to unit count from Property Info
        const getTotalUnits = (flatType: string, info: any): number => {
            if (!info) return 0;
            const type = flatType.toUpperCase();
            if (type.includes('1 ROOM')) return (info.oneRoomSold || 0) + (info.oneRoomRental || 0);
            if (type.includes('2 ROOM')) return (info.twoRoomSold || 0) + (info.twoRoomRental || 0);
            if (type.includes('3 ROOM')) return (info.threeRoomSold || 0) + (info.threeRoomRental || 0);
            if (type.includes('4 ROOM')) return info.fourRoomSold || 0;
            if (type.includes('5 ROOM')) return info.fiveRoomSold || 0;
            if (type.includes('EXECUTIVE')) return info.execSold || 0;
            if (type.includes('MULTI-GENERATION')) return info.multigenSold || 0;
            return 0;
        };

        // 3. Map to HdbValuationData format
        // Note: Rental data is mocked for now as we don't have a clean raw rental table with block-level precision yet.
        return (results.results || []).map((row: any) => ({
            flatType: row.flatType,
            estMinValBuy: row.minPrice,
            estAvgValBuy: row.avgPrice,
            estMaxValBuy: row.maxPrice,

            // Estimates for Rent using centralized logic
            estMinValRent: this.calculateEstimatedMonthlyRent(row.minPrice, 'min'),
            estAvgValRent: this.calculateEstimatedMonthlyRent(row.avgPrice, 'avg'),
            estMaxValRent: this.calculateEstimatedMonthlyRent(row.maxPrice, 'max'),

            totalUnits: getTotalUnits(row.flatType, propertyInfo),
            latestPurchaseDate: row.latestTransaction,
            avgAnnualPurchases: this.calculateAnnualizedVolume(row.salesVolume, 2), // 2 year window
            impliedRentalYield: this.getBenchmarkRentalYield(),
            salesVolumeLastYear: row.salesVolume // approximate
        }));
    }

    /**
     * Calculates estimated monthly rent based on property value and yield benchmarks.
     * Logic:
     * - Min: Conservative 3.5% yield
     * - Avg: Standard 4.0% yield
     * - Max: Optimistic 4.5% yield
     * @param price Property price in SGD
     * @param percentile 'min' | 'avg' | 'max'
     */
    private calculateEstimatedMonthlyRent(price: number, percentile: 'min' | 'avg' | 'max'): number {
        if (!price) return 0;

        // Yield Benchmarks (Annual)
        const YIELD_RATES = {
            min: 0.035, // 3.5%
            avg: 0.040, // 4.0%
            max: 0.045  // 4.5%
        };

        const annualRent = price * YIELD_RATES[percentile];
        return Math.round(annualRent / 12);
    }

    /**
     * Calculates annualized volume from a total over a period.
     */
    private calculateAnnualizedVolume(totalVolume: number, periodYears: number): number {
        if (!totalVolume || !periodYears) return 0;
        return Number((totalVolume / periodYears).toFixed(1));
    }

    /**
     * Returns the benchmark rental yield used for calculations.
     * Can be enhanced to fetch from DB/API in future.
     */
    private getBenchmarkRentalYield(): number {
        return 4.0; // Current market benchmark percentage
    }

    /**
     * Generates URLs
     */
    private async generateFrontendAssets(block: string, street: string, lat: number, long: number) {
        const query = encodeURIComponent(`${block} ${street}`);
        return {
            portalLinks: JSON.stringify({
                propertyGuru: `https://www.propertyguru.com.sg/property-for-sale?market=residential&freetext=${query}`,
                ninetyNine: `https://www.99.co/singapore/sale?query=${query}`
            }),
            googleStreetViewUrl: `https://maps.googleapis.com/maps/api/streetview?size=600x400&location=${lat},${long}&key=${this.env.GOOGLE_MAPS_API_KEY || 'DEMO_KEY'}`
            // Note: In prod, do not expose API Key in DB if possible, or use a signed URL proxy.
            // For now, storing the structure.
        };
    }

    /**
   * Historical Portfolio Analysis (Cron Job)
   * * Calculates Rent/Resale Gaps and Generates Advice.
   * * Inserts incremental records for history.
   */
    async runHistoricalPortfolioAnalysis(): Promise<void> {
        const timestamp = new Date().toISOString();

        // 1. Fetch all portfolio items
        const portfolioItems = await this.db.query.userPortfolio.findMany();

        for (const item of portfolioItems) {
            if (!item.flatType) continue;

            // 2. Get latest valuation for this item
            const valuation = await this.db.query.hdbValuationData.findFirst({
                where: (table, { eq, and }) => and(
                    eq(table.blockId, item.blockId),
                    eq(table.flatType, item.flatType!)
                )
            });

            if (!valuation) continue;

            // 3. Calculate Gaps
            // 3. Calculate Gaps
            let rentGap = 0;

            if (item.currentRent && valuation.estAvgValRent) {
                rentGap = item.currentRent - valuation.estAvgValRent;
            }

            let marketValueGap = 0;

            if (item.acquisitionPrice && valuation.estAvgValBuy) {
                marketValueGap = valuation.estAvgValBuy - item.acquisitionPrice;
            }

            // 4. Fetch Score-Lah for Impact Analysis
            const score = await this.db.query.hdbScoreLah.findFirst({
                where: eq(schema.hdbScoreLah.blockId, item.blockId)
            });

            // 5. AI Analysis (Two-Step Reasoning + Structuring)
            const context = {
                blockId: item.blockId,
                flatType: item.flatType,
                acquisitionPrice: item.acquisitionPrice,
                currentValuation: valuation.estAvgValBuy,
                currentRent: item.currentRent,
                marketRent: valuation.estAvgValRent,
                rentGap: rentGap,
                marketValueGap: marketValueGap,
                scoreLah: score
            };

            const aiInsights = await this.aiService.generatePortfolioInsights(context);

            // 6. Insert New Analysis Record
            const analysisData: schema.NewPortfolioAnalysis = {
                portfolioId: item.id,
                generatedAt: timestamp,
                rentGap: rentGap,
                rentAdvice: aiInsights.rentAdvice,
                marketValueGap: marketValueGap,
                resaleOutlook: aiInsights.resaleOutlook,
                scoreLahImpact: aiInsights.scoreLahImpact,
                aiActionItems: aiInsights.aiActionItems
            };

            await this.db.insert(schema.portfolioAnalysis).values(analysisData);
        }
    }

    /**
     * Helper to fetch OneMap Themes
     */
    private async searchOneMapTheme(theme: string, lat: number, long: number, radiusMeters: number): Promise<OneMapThemeResult[]> {
        // Note: OneMap Theme API usually returns ALL points. 
        // We fetch all and filter by distance locally for efficiency if the dataset is small, 
        // or use their spatial query if available (Themes API is mostly "dump all").
        // Checking OneMap docs: /themesvc/retrieveTheme?queryName={theme}
        // It returns all. We must filter.

        try {
            const resp = await fetch(`${ONEMAP_THEMES_URL}/retrieveTheme?queryName=${theme}`);
            if (!resp.ok) return [];

            const data: any = await resp.json();
            const results: OneMapThemeResult[] = data.SrchResults || [];

            // Filter by radius
            return results.filter(item => {
                const [pLat, pLng] = item.LatLng.split(',').map(Number);
                const dist = this.haversineDistance(lat, long, pLat, pLng);
                return dist <= radiusMeters;
            });
        } catch (e) {
            console.error(`OneMap Fetch Error (${theme}):`, e);
            return [];
        }
    }

    /**
     * Simple Haversine Distance in Meters
     */
    private haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
        const R = 6371e3; // metres
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;

        const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }

    private async saveEnrichmentData(blockId: number, scores: any, valuations: any[], frontend: any) {
        const timestamp = new Date().toISOString();

        // Upsert ScoreLah
        await this.db.insert(schema.hdbScoreLah).values({
            blockId,
            ...scores
        }).onConflictDoUpdate({
            target: schema.hdbScoreLah.blockId,
            set: scores
        });

        // Replace Valuations (Delete + Insert for simplicity with multiple types)
        await this.db.delete(schema.hdbValuationData).where(eq(schema.hdbValuationData.blockId, blockId));
        for (const val of valuations) {
            await this.db.insert(schema.hdbValuationData).values({
                blockId,
                ...val,
                lastEnrichedAt: timestamp
            });
        }

        // Upsert Frontend Data
        await this.db.insert(schema.hdbFrontendData).values({
            blockId,
            ...frontend,
            lastEnrichedAt: timestamp
        }).onConflictDoUpdate({
            target: schema.hdbFrontendData.blockId,
            set: { ...frontend, lastEnrichedAt: timestamp }
        });
    }
}
