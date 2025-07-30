import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '../ui/collapsible';
import { Trajectory } from '../../models/trajectory';
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the button

interface InfoTrajectoryProps {
  trajectory: Trajectory;
}

export const InfoTrajectory: React.FC<InfoTrajectoryProps> = ({ trajectory }) => {
  // Extract relevant data
  const stepData = trajectory.stepData || {};
  const title = stepData.title || 'Information';
  // Ensure message is a string for the copy button and preview
  const message = typeof stepData.message === 'string' ? stepData.message :
                  typeof stepData.content === 'string' ? stepData.content : '';
  const messageObject = typeof stepData.message !== 'string' ? stepData.message :
                        typeof stepData.content !== 'string' ? stepData.content : null;

  const isError = trajectory.isError;

  // Format timestamp
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Determine the content to copy - prioritize string message, fallback to JSON of object
  const contentToCopy = message || (messageObject ? JSON.stringify(messageObject, null, 2) : '');

  return (
    <Collapsible className="w-full border border-border rounded-md overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
      <CollapsibleTrigger className="w-full text-left hover:bg-accent/30 cursor-pointer">
        <CardHeader className="py-3 px-4 relative"> {/* Added relative for potential absolute positioning of button if needed */}
          <div className="flex justify-between items-start"> {/* Changed to items-start */}
            <div className="flex items-center space-x-3 flex-grow mr-2"> {/* Added flex-grow and mr-2 */}
              <div className="flex-shrink-0 text-lg pt-0.5">ℹ️</div> {/* Adjusted icon alignment */}
              <CardTitle className="text-base font-medium">
                {title}
              </CardTitle>
            </div>
            <div className="flex items-center space-x-2 flex-shrink-0"> {/* Container for button and time */}
              {contentToCopy && ( // Only show button if there is content to copy
                 <CopyToClipboardButton textToCopy={contentToCopy} className="p-1 h-6 w-6" />
              )}
              <div className="text-xs text-muted-foreground pt-0.5"> {/* Adjusted time alignment */}
                {formatTime(trajectory.created)}
              </div>
            </div>
          </div>
          {message && ( // Only show string preview if message is a non-empty string
            <div className="text-sm text-muted-foreground mt-1 line-clamp-2">
              {message}
            </div>
          )}
        </CardHeader>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <CardContent className="py-3 px-4 border-t border-border bg-card/50">
          {message && ( // Show string content
            <div className="text-sm whitespace-pre-wrap">
              {message}
            </div>
          )}

          {messageObject && ( // Show object content
            <pre className="text-xs bg-muted p-2 rounded-md overflow-auto max-h-60">
              {JSON.stringify(messageObject, null, 2)}
            </pre>
          )}

          {isError && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold mb-2 text-red-500">Error:</h4>
              <pre className="text-xs bg-red-50 dark:bg-red-900/20 p-2 rounded-md text-red-800 dark:text-red-200 overflow-auto max-h-60">
                {trajectory.errorMessage || 'Unknown error'}
                {trajectory.errorType && ` (${trajectory.errorType})`}
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
            </div>
          )}
        </CardContent>
      </CollapsibleContent>
    </Collapsible>
  );
};
