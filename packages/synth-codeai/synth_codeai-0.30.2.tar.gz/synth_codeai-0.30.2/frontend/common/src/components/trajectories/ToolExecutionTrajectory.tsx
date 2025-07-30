
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '../ui/collapsible';
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the button
import { Trajectory } from '../../models/trajectory';
import ReactMarkdown from 'react-markdown'; // Added import
import remarkGfm from 'remark-gfm'; // Added import
import { MarkdownCodeBlock } from '../ui/MarkdownCodeBlock'; // Added import


interface ToolExecutionTrajectoryProps {
  trajectory: Trajectory;
}

export const ToolExecutionTrajectory: React.FC<ToolExecutionTrajectoryProps> = ({ trajectory }) => {
  // Format tool parameters for display
  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  // Get the display name of the tool
  const getToolDisplayName = (trajectory: Trajectory) => {
    const toolName =  trajectory.toolName;
    if(toolName === 'ask_expert'){
      if(typeof trajectory?.stepData?.response_content === 'string'){
        return 'Expert Response'
      } else {
        return 'Ask Expert'
      }
    }
    return toolName
      .replace(/_/g, ' ')
      .replace(/\btool\b/gi, '')
      .trim()
      .replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()); // Convert to Title Case
  };

  // Extract relevant data
  const toolName = trajectory.toolName;
  const toolParameters = trajectory.toolParameters || {};
  const toolResult = trajectory.toolResult; // Keep original type for logic
  const stepData = trajectory.stepData || {};
  const displayName = getToolDisplayName(trajectory);
  const isError = trajectory.isError;

  // Prepare text for clipboard (for non-shell tools)
  const getResultTextToCopy = (): string => {
    if (toolName === 'run_shell_command') {
      // For shell commands, copy the output if available, otherwise the command
      return toolResult?.output ?? toolParameters?.command ?? '';
    } else if (toolName === 'web_search_tavily') {
      return toolParameters?.query || '';
    } else if (toolName === 'ask_expert') {
      // For expert, format question and response together
      const question = toolParameters?.question ?? '';
      const response = stepData?.response_content ?? '';
      return `# Parameters:\n\n${question}\n\n---\n\n# Expert Response:\n\n${response}`;
    }
    // Ensure result is a non-empty object before stringifying
    if (typeof toolResult === 'object' && toolResult !== null && Object.keys(toolResult).length > 0) {
      return JSON.stringify(toolResult, null, 2);
    }
    // Handle strings and potentially other primitives (convert to string)
    if (toolResult !== null && toolResult !== undefined && typeof toolResult !== 'object') {
        return String(toolResult);
    }
    // Fallback to parameters if no result
    if (typeof toolParameters === 'object' && Object.keys(toolParameters).length > 0) {
      return JSON.stringify(toolParameters, null, 2);
    }
    // Handle empty objects or cases not caught above
    return '';
  };

  // Check if there's actually a result to display (handles null/undefined/empty object)
  // Treat empty strings as valid results for display
  const hasResultData = toolResult !== null && toolResult !== undefined && (typeof toolResult !== 'object' || Object.keys(toolResult).length > 0);

  // Determine if the copy button should be rendered and what text it should copy
  let rawTextToCopy: string | null = null;
  let shouldRenderButton = false;
  let finalFormattedTextToCopy: string | null = null;

  // For tools, copy error message if error, otherwise copy result/content if available
  if (isError && trajectory.errorMessage) {
    rawTextToCopy = trajectory.errorMessage;
    shouldRenderButton = true;
  } else {
    rawTextToCopy = getResultTextToCopy();
    // Only render button if there's actually text to copy (handles empty string result from getResultTextToCopy)
    if (rawTextToCopy !== '') {
        shouldRenderButton = true;
    }
  }

  // Prepend heading if we have text to copy
  if (shouldRenderButton && rawTextToCopy !== null) {
      const heading = `# ${displayName}\n\n`;
      // For specific tools, just copy the raw content without the heading
      if(['web_search_tavily', 'run_shell_command', 'ask_expert'].includes(toolName)) {
          finalFormattedTextToCopy = rawTextToCopy;
      } else {
          finalFormattedTextToCopy = heading + rawTextToCopy;
      }
  }

  return (
    <Collapsible className="w-full border border-border rounded-md overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
      <CollapsibleTrigger className="w-full text-left hover:bg-accent/30 cursor-pointer">
        <CardHeader className="py-3 px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3 mr-2 overflow-hidden"> {/* Added overflow-hidden */}
              <div className="flex-shrink-0 text-lg">🛠️</div>
              <CardTitle className="text-base font-medium truncate"> {/* Added truncate */}
                {displayName}
              </CardTitle>
            </div>
            {/* Container for timestamp and copy button */}
            <div className="flex items-center space-x-2 flex-shrink-0">
              {/* --- BUTTON POSITIONING (BEFORE TIMESTAMP) --- */}
              {/* Render the copy button conditionally with the formatted text */}
              {shouldRenderButton && finalFormattedTextToCopy !== null && (
                 <CopyToClipboardButton textToCopy={finalFormattedTextToCopy} className="p-1 h-6 w-6" tooltipSide="left" />
              )}
              {/* Timestamp */}
              <div className="text-xs text-muted-foreground">
              {trajectory.created
                ? new Date(trajectory.created).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : 'Invalid Date'}
            </div>
              {/* --- END BUTTON POSITIONING --- */}
            </div>
          </div>
          {stepData.display && (
            <div className="text-sm text-muted-foreground mt-1 line-clamp-2 break-words">
              {typeof stepData.display === 'string' ? stepData.display : JSON.stringify(stepData.display)}
            </div>
          )}
        </CardHeader>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <CardContent className="py-3 px-4 border-t border-border bg-card/50">
          {/* --- Parameters (excluding ask_expert) --- */}
          {Object.keys(toolParameters).length > 0 && toolName !== 'ask_expert' && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold mb-2">Parameters:</h4>
              <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-60">
                {Object.entries(toolParameters).map(([key, value]) => (
                  <div key={key} className="mb-1">
                    <span className="text-blue-600 dark:text-blue-400">{key}:</span> {formatValue(value)}
                  </div>
                ))}
              </pre>
            </div>
          )}

          {/* Display Result for non-shell, non-expert tools */}
          {(!isError && hasResultData && toolName !== 'run_shell_command' && toolName !== 'ask_expert') && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold mb-2">Result:</h4>
              <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-60">
                {formatValue(toolResult)}
              </pre>
            </div>
          )}

          {/* Display Shell Command Output */}
          {(!isError && toolName === 'run_shell_command' && typeof toolResult?.output === 'string' && toolResult.output.length > 0) && (
            <div className="mb-4">
                <h4 className="text-sm font-semibold mb-2">Output:</h4>
                <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-96">
                    {toolResult.output}
                </pre>
            </div>
          )}

          {/* --- START ASK_EXPERT SPECIFIC BLOCK --- */}
          {toolName === 'ask_expert' && (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              {/* Render Response */}
              {typeof stepData?.response_content === 'string' ?
                stepData.response_content.length > 0 && (
                <>
                  <h4 className="text-sm font-semibold mb-2">Expert Response:</h4> {/* Ensure heading styling aligns */}                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{ code: MarkdownCodeBlock }}
                  >
                    {stepData.response_content}
                  </ReactMarkdown>
                </>
                ) : (
                <>
                  <h4 className="text-sm font-semibold mb-2 !mt-0">Parameters:</h4> {/* Ensure heading styling aligns */}                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{ code: MarkdownCodeBlock }}
                  >
                    {toolParameters.question}
                  </ReactMarkdown>
                </>
              )}
            </div>
          )}
          {/* --- END ASK_EXPERT SPECIFIC BLOCK --- */}

          {isError && (
            <div className="mt-4 pt-4 border-t border-border/50">
              <h4 className="text-sm font-semibold mb-2 text-red-500">Error:</h4>
              <pre className="text-xs bg-red-50 dark:bg-red-900/20 p-2 rounded-md text-red-800 dark:text-red-200 overflow-auto max-h-60">
                {trajectory.errorMessage || 'Unknown error'}
                {trajectory.errorType && ` (${trajectory.errorType})`}
                {trajectory.errorDetails && `\nDetails: ${trajectory.errorDetails}`}
              </pre>
            </div>
          )}

          {trajectory.currentCost !== null && trajectory.currentCost !== undefined && (
            <div className="mt-3 pt-3 border-t border-border/50 text-xs text-muted-foreground">
              <span className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Cost: ${trajectory.currentCost.toFixed(6)}
              </span>
              {(trajectory.inputTokens || trajectory.outputTokens) && (
                <span className="flex items-center mt-1">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                  Tokens: {trajectory.inputTokens || 0} in / {trajectory.outputTokens || 0} out
                </span>
              )}
            </div>
          )}
        </CardContent>
      </CollapsibleContent>
    </Collapsible>
  );
};
