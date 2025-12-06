
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AiService } from '../src/services/ai';

describe('AiService', () => {
    let mockAi: any;
    let service: AiService;

    beforeEach(() => {
        mockAi = {
            run: vi.fn(),
        };
        service = new AiService(mockAi);
    });

    describe('generatePortfolioInsights', () => {
        it('should successfully orchestrate the dual-model pipeline', async () => {
            // Setup Mocks
            const mockReasoning = "Based on the data, the property is doing well. Rent is low.";
            const mockStructured = {
                resaleOutlook: "Bullish",
                rentAdvice: "Increase Rent",
                scoreLahImpact: "High Value",
                aiActionItems: ["Renovate", "List"]
            };

            mockAi.run
                // 1. First call: GPT-OSS-120B (Reasoning)
                .mockResolvedValueOnce({
                    choices: [
                        { message: { content: mockReasoning } }
                    ]
                })
                // 2. Second call: Llama-3.3 (Structure)
                .mockResolvedValueOnce({
                    response: JSON.stringify(mockStructured)
                });

            const context = { blockId: 123, price: 500000 };
            const result = await service.generatePortfolioInsights(context);

            // Verify Reasoning Call
            expect(mockAi.run).toHaveBeenNthCalledWith(1, '@cf/openai/gpt-oss-120b', expect.objectContaining({
                input: expect.any(Array), // Should use 'input' array
                reasoning: expect.any(Object) // Should use 'reasoning' object
            }));

            // Verify Extraction Call
            expect(mockAi.run).toHaveBeenNthCalledWith(2, '@cf/meta/llama-3.3-70b-instruct-fp8-fast', expect.objectContaining({
                messages: expect.any(Array),
                response_format: { type: 'json_object', json_schema: expect.any(Object) }
            }));

            // Verify Result
            expect(result).toEqual({
                ...mockStructured,
                aiActionItems: JSON.stringify(mockStructured.aiActionItems)
            });
        });

        it('should handle OpenAI Text Completion format from GPT-OSS-120B', async () => {
            const mockReasoning = "Analysis: Good.";

            mockAi.run
                .mockResolvedValueOnce({
                    choices: [
                        { text: mockReasoning } // Text completion format
                    ]
                })
                .mockResolvedValueOnce({ response: JSON.stringify({}) }); // Don't care about structure for this test

            await service.generatePortfolioInsights({});

            // The key check is that it didn't crash and processed the text
            expect(mockAi.run).toHaveBeenCalledTimes(2);
        });

        it('should use default fallback on AI failure', async () => {
            // Simulate Error
            mockAi.run.mockRejectedValue(new Error("AI Down"));

            const result = await service.generatePortfolioInsights({});

            expect(result).toEqual({
                resaleOutlook: "Stable",
                rentAdvice: "Hold",
                scoreLahImpact: "Neutral",
                aiActionItems: JSON.stringify([])
            });
        });
    });

    describe('generateScoreLahInsights', () => {
        it('should generate score insights correctly', async () => {
            const mockInsights = {
                scoreLahRationale: "Great place.",
                foodAccessRationale: "Lots of food.",
                noiseLevel: 8,
                trafficLevel: 7,
                transportRationale: "Ok",
                educationRationale: "Ok",
                parksRationale: "Ok",
                noiseLevelRationale: "Loud",
                trafficLevelRationale: "Busy"
            };

            mockAi.run
                .mockResolvedValueOnce({ response: "Reasoning..." }) // Cloudflare format simple
                .mockResolvedValueOnce({ response: JSON.stringify(mockInsights) });

            const result = await service.generateScoreLahInsights({}, {});

            expect(result.noiseLevel).toBe(8);
            expect(result.scoreLahRationale).toBe("Great place.");
        });
    });
});
