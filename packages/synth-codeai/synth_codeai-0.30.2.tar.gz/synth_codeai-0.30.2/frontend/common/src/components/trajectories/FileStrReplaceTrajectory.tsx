import React from 'react';
import { Trajectory } from '../../models/trajectory';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Replace } from 'lucide-react'; // Using Replace icon as suggested
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the button

export const FileStrReplaceTrajectory: React.FC<{ trajectory: Trajectory }> = ({ trajectory }) => {
  // Destructure stepData safely, providing default values
  const { filepath = 'N/A', old_str = '', new_str = '', count = 0, diff = '' } = trajectory.stepData || {};
  const displayTitle = trajectory.displayTitle || `Replaced string in ${filepath}`;

  // Use a shortened version or placeholder if strings are too long for display
  const shortOldStr = old_str.length > 50 ? old_str.substring(0, 47) + '...' : old_str;
  const shortNewStr = new_str.length > 50 ? new_str.substring(0, 47) + '...' : new_str;

  // Determine text to copy - use the display title
  const textToCopy = displayTitle;
  const timestamp = trajectory.created;
  const formattedTime = timestamp
  ? new Date(timestamp).toLocaleTimeString([], { // Format time consistently
      hour: '2-digit',
      minute: '2-digit',
    })
  : 'Invalid Date';

  return (
    <Card>
      <CardHeader className="py-3 px-4"> {/* Use standard padding */} 
        <div className="flex justify-between items-center">
           {/* Left Side: Icon and Title */}
          <div className="flex items-center space-x-2 flex-1 min-w-0 mr-2"> {/* Ensure title can truncate */}
            <Replace className="h-4 w-4 text-blue-500 flex-shrink-0" />
            <CardTitle className="text-sm font-medium truncate">{/* Apply truncate */}
              {displayTitle}
            </CardTitle>
          </div>
          {/* Right Side: Copy Button and Timestamp */}
          <div className="flex items-center space-x-2 flex-shrink-0">
             <CopyToClipboardButton textToCopy={textToCopy} />
              <div className="text-xs text-muted-foreground">
                {formattedTime}
              </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0 pb-3 px-4"> {/* Adjust padding */}
        <div className="text-xs text-muted-foreground space-y-1">
            {/* Display Filepath */}
            <p>File: <span className="font-mono">{filepath}</span></p>

            {/* Display Old and New Strings (potentially truncated) */}
            <p>Old: <span className="font-mono bg-muted px-1 rounded">{shortOldStr}</span></p>
            <p>New: <span className="font-mono bg-muted px-1 rounded">{shortNewStr}</span></p>

            {/* Display Replacement Count */}
            <Badge variant="secondary">{count} replacement(s)</Badge>

            {/* Display Diff if available */}
            {diff && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs">Show Diff</summary>
                <pre className="mt-1 p-2 text-xs bg-muted rounded text-foreground overflow-x-auto">
                  <code>{diff}</code>
                </pre>
              </details>
            )}
        </div>
      </CardContent>
    </Card>
  );
};

export default FileStrReplaceTrajectory;
