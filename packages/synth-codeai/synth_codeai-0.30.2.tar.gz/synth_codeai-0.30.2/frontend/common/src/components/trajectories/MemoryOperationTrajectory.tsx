
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '../ui/collapsible';
import { Trajectory } from '../../models/trajectory';
import { KeyRound, Files } from 'lucide-react'; // Import KeyRound and Files icons
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the copy button

// --- New Imports for Markdown ---

import ReactMarkdown, { Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// Using a common style, adjust if needed

import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
// --- End New Imports ---


interface MemoryOperationTrajectoryProps {
  trajectory: Trajectory;
}

// Helper to format timestamp

const formatTime = (timestamp: string) => {
  try {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (e) {
    console.error("Error formatting time:", e);
    return "Invalid Date";
  }
};

export const MemoryOperationTrajectory: React.FC<MemoryOperationTrajectoryProps> = ({ trajectory }) => {
  // Format memory operation data for display

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') return JSON.stringify(value, null, 2);
    return String(value);
  };

  // Get memory operation type from tool name (only used for non-key-fact ops now)

  const getOperationType = (toolName: string): string => {
    const types: Record<string, string> = {
      // emit_key_facts is handled separately
      // emit_related_files is handled separately

      'emit_key_snippet': 'Store Code Snippet',
      'emit_research_note': 'Store Research Note',
      'read_key_facts': 'Retrieve Key Facts',
      'read_key_snippets': 'Retrieve Code Snippets',
      'read_research_notes': 'Retrieve Research Notes',
    };
    return types[toolName] || toolName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()); // Capitalize title

  };

  // --- Define Custom Components for Markdown (copied & adapted) ---

  const components: Components = {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars

      code({ className, children, ...props }) { // Removed node and inline destructuring

        const match = /language-(\w+)/.exec(className || '');
        // Handle potential array children from parsing, join them, and trim trailing newline

        const codeString = (Array.isArray(children) ? children.join('') : String(children))
                          .replace(/\n$/, '');

        // Check only for match to determine if it's a highlighted block

        if (match) {
          // For block code with language

          return (
            <SyntaxHighlighter
              style={vscDarkPlus} // Apply the chosen style

              language={match[1]}
              PreTag="div"
              // Added basic styling matching typical code blocks

              className="text-sm rounded my-2"
            >
              {codeString}
            </SyntaxHighlighter>
          );
        } else {
          // For inline code or block code without language

          return (
            // Apply basic inline code styling

            <code className={`bg-muted px-1 py-0.5 rounded text-sm font-mono ${className || ''}`}>
              {children}
            </code>
          );
        }
      },
    }
  // --- End Custom Components ---


  // Extract relevant data

  const toolName = trajectory.toolName;
  const toolParameters = trajectory.toolParameters || {};
  const toolResult = trajectory.toolResult || {};
  const stepData = trajectory.stepData || {};
  const isError = trajectory.isError;
  const factText = stepData.fact as string | undefined; // Explicitly type fact text


  // Conditional rendering based on toolName

  if (toolName === 'emit_key_facts') {
    const textToCopy = factText || ""; // Content for key fact copy button

    return (
      <Card className="w-full border border-border rounded-md overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
        <CardHeader className="py-3 px-4"> {/* Use consistent padding */}

          <div className="flex justify-between items-start"> {/* Align items to start for button spacing */}

            <div className="flex items-center space-x-3 mr-2"> {/* Add margin right */}

              <KeyRound className="h-4 w-4 text-muted-foreground flex-shrink-0" /> {/* Key Icon */}

              <CardTitle className="text-base font-medium">
                Key Fact
              </CardTitle>
            </div>
            <div className="flex items-center space-x-2"> {/* Group timestamp and button */}

                {/* Modified textToCopy to prepend heading */}

                <CopyToClipboardButton textToCopy={"# Key Fact\n\n" + textToCopy} />
                <div className="text-xs text-muted-foreground">
                    {formatTime(trajectory.created)}
                </div>
            </div>
          </div>
          {/* --- Updated Rendering for Fact Text using Markdown --- */}

          {factText ? (
            <div className="prose prose-sm dark:prose-invert max-w-none break-words mt-2">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={components} // Use the defined custom components

              >
                {factText}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground mt-2 italic">
              (No fact text available)
            </div>
          )}
          {/* --- End Updated Rendering --- */}

        </CardHeader>
         {/* No CardContent needed as fact is in header/below */}

      </Card>
    );
  } else if (toolName === 'emit_related_files') {
    const operationType = "Emit Related Files";
    let formattedFileList = "(No files listed)";
    let textToCopy = `# ${operationType}\n\n${formattedFileList}`;

    // Extract and format file list
    if (toolParameters && Array.isArray(toolParameters.files)) {
        if (toolParameters.files.length > 0) {
            formattedFileList = toolParameters.files.join('\n');
            textToCopy = `# ${operationType}\n\n${formattedFileList}`;
        }
    } else {
        console.warn("Expected 'files' array in toolParameters for emit_related_files, but found:", toolParameters);
    }

    return (
        <Collapsible className="w-full border border-border rounded-md overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
            <CollapsibleTrigger className="w-full text-left hover:bg-accent/30 cursor-pointer">
                <CardHeader className="py-3 px-4">
                    <div className="flex justify-between items-start">
                        <div className="flex items-center space-x-3 mr-2">
                            <Files className="h-4 w-4 text-muted-foreground flex-shrink-0" /> {/* Files Icon */}
                            <CardTitle className="text-base font-medium">
                                {operationType}
                            </CardTitle>
                        </div>
                        <div className="flex items-center space-x-2">
                            <CopyToClipboardButton textToCopy={textToCopy} />
                            <div className="text-xs text-muted-foreground">
                                {formatTime(trajectory.created)}
                            </div>
                        </div>
                    </div>
                    {/* Display brief summary if available in stepData.display */}
                    {stepData.display && (
                        <div className="text-sm text-muted-foreground mt-1 line-clamp-2 break-words">
                        {typeof stepData.display === 'string' ? stepData.display : JSON.stringify(stepData.display)}
                        </div>
                    )}
                </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
                <CardContent className="py-3 px-4 border-t border-border bg-card/50">
                    {/* Display parameters, including the file list */}
                    {Object.keys(toolParameters).length > 0 && (
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
                    {/* Display result and error as usual */}
                     {(!isError && Object.keys(toolResult).length > 0) && (
                        <div>
                            <h4 className="text-sm font-semibold mb-2">Result:</h4>
                            <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-60">
                                {formatValue(toolResult)}
                            </pre>
                        </div>
                    )}
                    {isError && (
                        <div>
                            <h4 className="text-sm font-semibold mb-2 text-red-500">Error:</h4>
                            <pre className="text-xs bg-red-50 dark:bg-red-900/20 p-2 rounded-md text-red-800 dark:text-red-200 overflow-auto max-h-60">
                                {trajectory.errorMessage || 'Unknown error'}
                                {trajectory.errorType && ` (${trajectory.errorType})`}
                            </pre>
                        </div>
                    )}
                    {/* Cost Display */}
                    {trajectory.currentCost !== null && trajectory.currentCost !== undefined && (
                        <div className="mt-3 pt-3 border-t border-border/50 text-xs text-muted-foreground">
                        <span className="flex items-center">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Cost: ${trajectory.currentCost.toFixed(6)}
                        </span>
                        </div>
                    )}
                </CardContent>
            </CollapsibleContent>
        </Collapsible>
    );
  } else {
    // --- Default rendering for OTHER memory operations (existing collapsible structure) ---
    const operationType = getOperationType(toolName);
    // Construct the text to copy for other operations
    const rawTextToCopy = (typeof stepData.display === 'string' ? stepData.display : '') || operationType || "";

    return (
      <Collapsible className="testtt w-full border border-border rounded-md overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
        <CollapsibleTrigger className="w-full text-left hover:bg-accent/30 cursor-pointer">
          <CardHeader className="py-3 px-4">
            <div className="flex justify-between items-start"> {/* Align items to start */}
              <div className="flex items-center space-x-3 mr-2"> {/* Add margin right */}
                {/* Generic Icon for other ops */}
                <div className="flex-shrink-0 text-lg">💾</div>
                <CardTitle className="text-base font-medium">
                  {operationType}
                </CardTitle>
              </div>
              <div className="flex items-center space-x-2"> {/* Group timestamp and button */}
                  {/* Modified textToCopy to prepend heading */}
                  <CopyToClipboardButton textToCopy={"# " + operationType + "\n\n" + rawTextToCopy} />
                  <div className="text-xs text-muted-foreground">
                      {formatTime(trajectory.created)}
                  </div>
              </div>
            </div>
            {/* Display brief summary if available in stepData.display */}
            {stepData.display && (
              <div className="text-sm text-muted-foreground mt-1 line-clamp-2 break-words">
                {typeof stepData.display === 'string' ? stepData.display : JSON.stringify(stepData.display)}
              </div>
            )}
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="py-3 px-4 border-t border-border bg-card/50">
            {Object.keys(toolParameters).length > 0 && (
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

            {(!isError && Object.keys(toolResult).length > 0) && (
              <div>
                <h4 className="text-sm font-semibold mb-2">Result:</h4>
                <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-60">
                  {formatValue(toolResult)}
                </pre>
              </div>
            )}

            {isError && (
              <div>
                <h4 className="text-sm font-semibold mb-2 text-red-500">Error:</h4>
                <pre className="text-xs bg-red-50 dark:bg-red-900/20 p-2 rounded-md text-red-800 dark:text-red-200 overflow-auto max-h-60">
                  {trajectory.errorMessage || 'Unknown error'}
                  {trajectory.errorType && ` (${trajectory.errorType})`}
                </pre>
              </div>
            )}

            {/* Cost Display (Optional) */}
            {trajectory.currentCost !== null && trajectory.currentCost !== undefined && (
              <div className="mt-3 pt-3 border-t border-border/50 text-xs text-muted-foreground">
                <span className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Cost: ${trajectory.currentCost.toFixed(6)}
                </span>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    );
  }
};
