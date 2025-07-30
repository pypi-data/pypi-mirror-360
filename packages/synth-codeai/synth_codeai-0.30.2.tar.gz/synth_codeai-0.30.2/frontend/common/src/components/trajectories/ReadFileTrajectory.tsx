import React from 'react';
import { Trajectory } from '../../models/trajectory';
import {
  Card,
  CardHeader,
} from '../ui/card';
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the button

interface ReadFileTrajectoryProps {
  trajectory: Trajectory;
}

export const ReadFileTrajectory: React.FC<ReadFileTrajectoryProps> = ({
  trajectory,
}) => {
  // Extract data, including the content for copying
  const { line_count, total_bytes, filepath } = trajectory.stepData || {}; // Removed content extraction
  const timestamp = trajectory.created; // Use created timestamp

  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { // Format time consistently
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Invalid Date';

  const displayPath = filepath || 'Unknown file';
  const displayLineCount = line_count !== undefined ? line_count : '?';
  const displayTotalBytes = total_bytes !== undefined ? total_bytes : '?';

  // Construct the summary string for display and copying
  const summaryText = `Read ${displayLineCount} lines (${displayTotalBytes} bytes) from ${displayPath}`;

  return (
    <Card>
      {/* Updated CardHeader layout */}
      <CardHeader className="py-3 px-4">
        <div className="flex justify-between items-start"> {/* Changed to items-start for better alignment with button */}
          {/* Group icon and descriptive text */}
          <div className="flex items-center space-x-2 flex-grow mr-2"> {/* Added flex-grow and margin */}
            <span className="mr-1">📄</span> {/* Icon */}
            {/* Descriptive text */}
            <span className="text-sm"> {/* Adjusted text size slightly */}
              Read <strong className="font-semibold">{displayLineCount}</strong> lines (<strong className="font-semibold">{displayTotalBytes}</strong> bytes) from <em className="italic">{displayPath}</em>
            </span>
          </div>
          {/* Timestamp and Copy Button */}
          <div className="flex items-center space-x-2 flex-shrink-0"> {/* Container for timestamp and button */}
            {/* Updated textToCopy to use the summary string */}
            <CopyToClipboardButton textToCopy={summaryText} /> {/* Moved button before timestamp */}
            <div className="text-xs text-muted-foreground mt-0.5"> {/* Adjusted margin slightly */}
              {formattedTime}
            </div>
          </div>
        </div>
      </CardHeader>
      {/* CardContent removed */}
    </Card>
  );
};
