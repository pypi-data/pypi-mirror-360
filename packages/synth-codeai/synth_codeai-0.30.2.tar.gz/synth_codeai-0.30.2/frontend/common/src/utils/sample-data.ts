/**
 * Sample data utility for agent UI components demonstration
 */

// Import AgentStep from types (if still needed, otherwise remove)
// Assuming AgentStep might still be relevant for sample data structure
import {Trajectory} from "../models/trajectory";

// Import AgentSession from the correct location
import { AgentSession } from '../models/session';

/**
 * Returns an array of sample agent steps
 */
export function getSampleAgentSteps(): Trajectory[] {
  return [
    {
      id: 1,
      created: (new Date(Date.now() - 30 * 60000)).toISOString(), // 30 minutes ago
      updated: (new Date(Date.now() - 25 * 60000)).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'project_status',
      sessionId: 1,
    },
    {
      id: 2,
      created: (new Date(Date.now() - 25 * 60000)).toISOString(), // 25 minutes ago
      updated: (new Date(Date.now() - 20 * 60000)).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'project_status',
      sessionId: 1,
    },
    {
      id: 3,
      created: (new Date(Date.now() - 20 * 60000)).toISOString(),// 20 minutes ago
      updated: (new Date(Date.now() - 15 * 60000)).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'stage_transition',
      sessionId: 1,
    },
    {
      id: 4,
      created: (new Date(Date.now() - 15 * 60000)).toISOString(),// 15 minutes ago
      updated: (new Date(Date.now() - 10 * 60000)).toISOString(),
      toolName: '',
      isError: true,
      recordType: 'error',
      errorMessage: 'Encountered ResourceExhausted: 429 Gemini 2.5 Pro Preview doesn\'t have a free quota tier. Please use Gemini 2.5 Pro Experimental (models/gemini-2.5-pro-exp-03-25) instead. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. [violations {\n' +
        '  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"\n' +
        '  quota_id: "GenerateContentInputTokensPerModelPerDay-FreeTier"\n' +
        '  quota_dimensions {\n' +
        '    key: "model"\n' +
        '    value: "gemini-2.5-pro-exp"\n' +
        '  }\n' +
        '  quota_dimensions {\n' +
        '    key: "location"\n' +
        '    value: "global"\n' +
        '  }\n' +
        '}\n' +
        'violations {\n' +
        '  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"\n' +
        '  quota_id: "GenerateContentInputTokensPerModelPerMinute-FreeTier"\n' +
        '  quota_dimensions {\n' +
        '    key: "model"\n' +
        '    value: "gemini-2.5-pro-exp"\n' +
        '  }\n' +
        '  quota_dimensions {\n' +
        '    key: "location"\n' +
        '    value: "global"\n' +
        '  }\n' +
        '}\n' +
        'violations {\n' +
        '  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"\n' +
        '  quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"\n' +
        '  quota_dimensions {\n' +
        '    key: "model"\n' +
        '    value: "gemini-2.5-pro-exp"\n' +
        '  }\n' +
        '  quota_dimensions {\n' +
        '    key: "location"\n' +
        '    value: "global"\n' +
        '  }\n' +
        '}\n' +
        'violations {\n' +
        '  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"\n' +
        '  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"\n' +
        '  quota_dimensions {\n' +
        '    key: "model"\n' +
        '    value: "gemini-2.5-pro-exp"\n' +
        '  }\n' +
        '  quota_dimensions {\n' +
        '    key: "location"\n' +
        '    value: "global"\n' +
        '  }\n' +
        '}\n' +
        ', links {\n' +
        '  description: "Learn more about Gemini API quotas"\n' +
        '  url: "https://ai.google.dev/gemini-api/docs/rate-limits"\n' +
        '}\n' +
        ', retry_delay {\n' +
        '  seconds: 41\n' +
        '}\n' +
        ']. Retrying in 1s... (Attempt 1/20)',
      sessionId: 2,
    },
    {
      id: 5,
      created: (new Date(Date.now() - 10 * 60000)).toISOString(), // 10 minutes ago
      updated: (new Date(Date.now() - 5 * 60000)).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'project_status',
      sessionId: 3,
    },
    {
      id: 6,
      created: (new Date(Date.now() - 5 * 60000)).toISOString(), // 5 minutes ago
      updated: (new Date(Date.now() - 2 * 60000)).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'stage_transition',
      sessionId: 3,
    },
    {
      id: 7,
      created: (new Date(Date.now() - 2 * 60000)).toISOString(), // 2 minutes ago
      updated: (new Date(Date.now() - 1 * 60000)).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'stage_transition',
      sessionId: 3,
    },
    {
      id: 8,
      created: (new Date()).toISOString(), // Now
      updated: (new Date()).toISOString(),
      toolName: '',
      isError: false,
      recordType: 'project_status',
      sessionId: 3,
    }
  ];
}

/**
 * Returns an array of sample agent sessions
 * NOTE: This sample data might be incompatible with the current AgentSession model
 * from `../models/session`. It still uses `steps` and string IDs.
 * Use with caution or update the structure to match the model.
 */
// export function getSampleAgentSessions(): AgentSession[] {
//   const steps = getSampleAgentSteps();

//   // The structure below is based on the OLD AgentSession from utils/types
//   // and might cause issues if used where the new model is expected.
//   const sampleSessions = [
//     {
//       id: "session-1",
//       name: "UI Component Implementation",
//       created: new Date(Date.now() - 35 * 60000),
//       updated: new Date(),
//       status: 'active', // This status might not align with SessionStatus enum
//       steps: steps
//     },
//     {
//       id: "session-2",
//       name: "API Integration",
//       created: new Date(Date.now() - 2 * 3600000),
//       updated: new Date(Date.now() - 30 * 60000),
//       status: 'completed',
//       steps: [
//         {
//           id: "other-step-1",
//           timestamp: new Date(Date.now() - 2 * 3600000),
//           status: 'completed',
//           type: 'planning',
//           title: 'API Integration Planning',
//           content: 'Planning the integration with the backend API...',
//           duration: 4500
//         },
//         // ... other steps
//       ]
//     },
//     {
//       id: "session-3",
//       name: "Bug Fixes",
//       created: new Date(Date.now() - 5 * 3600000),
//       updated: new Date(Date.now() - 4 * 3600000),
//       status: 'error',
//       steps: [
//         {
//           id: "bug-step-1",
//           timestamp: new Date(Date.now() - 5 * 3600000),
//           status: 'completed',
//           type: 'planning',
//           title: 'Bug Analysis',
//           content: 'Analyzing reported bugs from issue tracker...',
//           duration: 3600
//         },
//         // ... other steps
//       ]
//     }
//   ];

//   // We need to cast this to the imported AgentSession type, but it's structurally different.
//   // This function is likely broken/deprecated due to model changes.
//   return sampleSessions as any; // Use 'any' to bypass type checking, but this is unsafe.
// }


// Provide an empty function or a correctly typed one if sample data is truly needed.
// For now, let's provide an empty array generator to satisfy the export need without errors.
export function getSampleAgentSessions(): AgentSession[] {
  console.warn("getSampleAgentSessions is deprecated due to model changes and returns an empty array.");
  return [];
}