LAB 01 — THE PRICE OF ONE REQUEST

Provider/model: Google Gemini API — gemini-3.6-flash.
The original lab uses Anthropic, but this run was adapted to Gemini because the instructor allowed the use of a free AI provider.

1. PART 1 PREDICTION VS. PART 2 MEASUREMENT

English: prediction 1.00x; measured complaint = 60 tokens; measured/EN = 1.00x.
Russian: prediction 1.92x; measured complaint = 79 tokens; measured/EN = 1.32x.
Kazakh: prediction 2.13x; measured complaint = 149 tokens; measured/EN = 2.48x.

Prediction basis: UTF-8 bytes. The prediction was based on offline Part 1 measurements, not on a tokenizer. The measured results show that token counts do not follow characters, bytes, or words directly; they depend on the model tokenizer.

2. ANNUAL COST SCENARIO

Volume assumption: 5,000 requests/day × 365 = 1,825,000 requests/year. This is a scenario for the lab's annual-cost calculation, not a measured production workload.

EN: 109 input tokens/request; 198,925,000 input tokens/year; $149.19 input cost/year.
RU: 139 input tokens/request; 253,675,000 input tokens/year; $190.26 input cost/year.
KK: 245 input tokens/request; 447,125,000 input tokens/year; $335.34 input cost/year.

Input-only paid-tier equivalent uses $0.75 per 1M input tokens through Dec. 31, 2026. Gemini's Free Tier is listed as free, but this project was Restricted/Unavailable, so real generation could not be completed.

Output tokens were not measured. An illustrative example of 500 output tokens/request would cost $3,421.88/year at $3.75 per 1M output tokens, but this is an assumption and must not be presented as a measured value.

3. PRODUCTION MODEL FOR A KAZAKH SUPPORT QUEUE

Model: Gemini 3.6 Flash.
Reason: in this experiment it handled Kazakh token counting and produced 149 complaint tokens versus 60 for English. Its published paid-tier input price is $0.75/1M tokens through Dec. 31, 2026, while the Free Tier is listed as free. For production, the quality of Kazakh answers should be validated on a representative support set before deployment; token cost alone is not sufficient.

4. ONE COST LEVER NOT USED

We did not use prompt/context caching; because the system prompt is repeated across requests, caching could reduce repeated input-token cost when supported by the deployment.

AI-USE DECLARATION

I used AI assistance during this lab to adapt the original Anthropic-based measurement script to the Google Gemini API, debug API and token-counting errors, explain the token measurements, and format the final calculations. I ran the commands locally and checked the returned token counts myself. The AI did not generate the measured values: the token counts in this report come from my local execution of the adapted script. The Gemini generation step returned HTTP 403 because my Google AI Studio projects were marked Restricted/Unavailable, so output-token measurements were not available. Any output-cost example is explicitly labeled as an assumption.

Source note: Google Gemini API pricing and model documentation were checked on 19 September 2026.
