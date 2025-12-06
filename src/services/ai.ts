import { cleanJsonOutput } from '../lib/utils';

export interface PortfolioAnalysisResult {
    resaleOutlook: string;
    rentAdvice: string;
    scoreLahImpact: string;
    aiActionItems: string; // JSON string
}

export interface ScoreLahInsights {
    scoreLahRationale: string;
    foodAccessRationale: string;
    transportRationale: string;
    educationRationale: string;
    parksRationale: string;
    noiseLevel: number;
    noiseLevelRationale: string;
    trafficLevel: number;
    trafficLevelRationale: string;
}

export class AiService {
    constructor(private ai: any) { }

    /**
     * Generates structured portfolio insights using a two-step AI process.
     * 1. Reasoning w/ GPT-OSS-120B
     * 2. Structuring w/ Llama-3.3-70B
     */
    async generatePortfolioInsights(context: any): Promise<PortfolioAnalysisResult> {
        // 1. RAW REASONING (The "Brain")
        const reasoningPrompt = `
You are a top Singapore Property Analyst. Analyze this portfolio item details and market data to provide strategic advice.

Context:
${JSON.stringify(context, null, 2)}

Tasks:
1. Analyze the Gap between Acquisition Price and Current Valuation (Resale Outlook).
2. Analyze the Gap between Current Rent and Market Rent (Rent Advice).
3. Evaluate how the "Score-Lah" (Lifestyle Score) metrics (Walkability, Food, etc.) affect the property's potential.
4. Suggest 2 concrete, actionable items for the owner in "aiActionItems".

Provide a detailed, professional analysis.
        `;

        const analysis = await this.runReasoningModel(reasoningPrompt);

        // 2. STRUCTURED EXTRACTION (The "Formatter")
        const schema = {
            type: "object",
            properties: {
                resaleOutlook: { type: "string", description: "Short outlook (e.g. 'Bullish', 'Stable'). Max 5 words." },
                rentAdvice: { type: "string", description: "Advice on rent (e.g. 'Increase by $200'). Max 10 words." },
                scoreLahImpact: { type: "string", description: "How score metrics affect value. Max 1 sentence." },
                aiActionItems: {
                    type: "array",
                    items: { type: "string" },
                    description: "List of 2 actionable items."
                }
            },
            required: ["resaleOutlook", "rentAdvice", "scoreLahImpact", "aiActionItems"]
        };

        const default_fallback = {
            resaleOutlook: "Stable",
            rentAdvice: "Hold",
            scoreLahImpact: "Neutral",
            aiActionItems: [] // Array for internal raw usage
        };

        const rawResult = await this.runExtractionModel<{
            resaleOutlook: string,
            rentAdvice: string,
            scoreLahImpact: string,
            aiActionItems: string[]
        }>(analysis, schema, default_fallback);

        return {
            ...rawResult,
            aiActionItems: JSON.stringify(rawResult.aiActionItems)
        };
    }

    /**
     * Generates Rationales and Subjective Scores for 'Score-Lah!'.
     */
    async generateScoreLahInsights(amenities: any, quantitativeScores: any): Promise<ScoreLahInsights> {
        // 1. REASONING
        const reasoningPrompt = `
You are a Singapore Lifestyle Expert for HDBs. analyze these amenity counts and standard scores to provide "Vibe Check" rationales.

Amenities:
${JSON.stringify(amenities, null, 2)}

Base Scores (0-100):
${JSON.stringify(quantitativeScores, null, 2)}

Tasks:
1. Write a 1-sentence rationale for the Overall Score (scoreLahRationale).
2. Write 1-sentence rationales for Food, Transport, Education, and Parks based on the data.
3. Estimate Noise Level (1-10) and Traffic Level (1-10) based on amenity density (e.g. many hawkers/MRTs = higher noise/traffic). 
4. Provide rationales for noise and traffic.
        `;

        const analysis = await this.runReasoningModel(reasoningPrompt);

        // 2. EXTRACTION
        const schema = {
            type: "object",
            properties: {
                scoreLahRationale: { type: "string" },
                foodAccessRationale: { type: "string" },
                transportRationale: { type: "string" },
                educationRationale: { type: "string" },
                parksRationale: { type: "string" },
                noiseLevel: { type: "number" },
                noiseLevelRationale: { type: "string" },
                trafficLevel: { type: "number" },
                trafficLevelRationale: { type: "string" }
            },
            required: ["scoreLahRationale", "foodAccessRationale", "noiseLevel", "trafficLevel"]
        };

        return this.runExtractionModel<ScoreLahInsights>(analysis, schema, {
            scoreLahRationale: "Standard analysis.",
            foodAccessRationale: "Standard food access.",
            transportRationale: "Standard transport.",
            educationRationale: "Standard education.",
            parksRationale: "Standard parks.",
            noiseLevel: 5,
            noiseLevelRationale: "Moderate.",
            trafficLevel: 5,
            trafficLevelRationale: "Moderate."
        });
    }

    // --- PRIVATE HELPERS ---

    private async runReasoningModel(prompt: string): Promise<string> {
        try {
            // GPT-OSS-120B uses "input" and "reasoning" schema (Responses API)
            const response = await this.ai.run('@cf/openai/gpt-oss-120b', {
                input: [
                    { role: 'system', content: 'You are an expert analyst.' },
                    { role: 'user', content: prompt }
                ],
                reasoning: {
                    effort: "medium",
                    summary: "detailed"
                }
            });

            // Expected output format check
            // If response is direct string
            if (typeof response === 'string') return response;

            // OpenAI "Responses API" format
            if (response.choices && Array.isArray(response.choices) && response.choices.length > 0) {
                const first = response.choices[0];
                if (first.message && first.message.content) return first.message.content; // Chat Completion
                if (first.text) return first.text; // Text Completion
            }

            // Cloudflare Standard format
            if (response.response) return response.response;
            if (response.result && response.result.response) return response.result.response;

            return JSON.stringify(response);
        } catch (e) {
            console.error("AI Reasoning Step Failed:", e);
            return "Analysis Unavailable.";
        }
    }

    private async runExtractionModel<T>(analysis: string, schema: any, fallback: T): Promise<T> {
        const extractionPrompt = `
Based on the following analysis, extract the exact JSON matching the schema.

ANALYSIS:
${analysis}

Extract into this JSON Schema:
${JSON.stringify(schema, null, 2)}
        `;

        try {
            const response = await this.ai.run('@cf/meta/llama-3.3-70b-instruct-fp8-fast', {
                messages: [
                    { role: 'system', content: 'You are a JSON extractor. Output ONLY valid JSON.' },
                    { role: 'user', content: extractionPrompt }
                ],
                response_format: {
                    type: "json_object",
                    json_schema: schema
                }
            });

            let jsonRaw = "";
            if (typeof response === 'string') jsonRaw = response;
            else if (response.response) jsonRaw = response.response;
            else jsonRaw = JSON.stringify(response);

            jsonRaw = cleanJsonOutput(jsonRaw);
            const parsed = JSON.parse(jsonRaw);

            // Merge with fallback to ensure all keys exist if partial extraction
            return { ...fallback, ...parsed };
        } catch (e) {
            console.error("AI Extraction Step Failed:", e);
            return fallback;
        }
    }
}
