import React from 'react';
import { Trajectory } from '../../models/trajectory';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { FileText } from 'lucide-react'; // Or another suitable icon
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the button

interface FileWriteTrajectoryProps {
  trajectory: Trajectory;
}

export const FileWriteTrajectory: React.FC<FileWriteTrajectoryProps> = ({ trajectory }) => {
  const filepath = trajectory.stepData?.filepath || 'N/A';
  const bytesWritten = trajectory.stepData?.bytes_written;
  const timestamp = trajectory.created;

  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { // Format time consistently
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Invalid Date';

  // Construct the summary string for display and copying
  let summaryText = `Wrote file: ${filepath}`;
  if (bytesWritten !== undefined) {
      summaryText = `Wrote ${bytesWritten} bytes to file: ${filepath}`;
  }

  return (
    <Card className="mb-4">
       {/* Updated header structure */}
      <CardHeader className="py-3 px-4">
        <div className="flex justify-between items-center">
          {/* Left Side: Icon and Title */}
          <div className="flex items-center space-x-2 flex-1 min-w-0 mr-2">
            <FileText className="h-4 w-4 text-green-500 flex-shrink-0" />
            <CardTitle className="text-sm font-medium truncate">{summaryText}</CardTitle>
          </div>
          {/* Right Side: Copy Button and Timestamp */}
          <div className="flex items-center space-x-2 flex-shrink-0">
            <CopyToClipboardButton textToCopy={summaryText} />
            <div className="text-xs text-muted-foreground">
              {formattedTime}
            </div>
          </div>
        </div>
      </CardHeader>
      {/* Content can be removed or simplified as info is in header */}
      <CardContent className="pt-0 pb-3 px-4 text-xs text-muted-foreground"> {/* Adjusted padding */}
        <p>File: <Badge variant="secondary" className="ml-1">{filepath}</Badge></p>
        {bytesWritten !== undefined && (
          <p>Bytes Written: <span className="font-semibold">{bytesWritten}</span></p>
        )}
      </CardContent>
    </Card>
  );
};
