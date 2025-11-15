import { config } from 'dotenv';
config();

import '@/ai/flows/generate-html-from-prompt.ts';
import '@/ai/flows/update-code-with-ai-diff.ts';