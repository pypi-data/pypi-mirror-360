
import React from 'react';
import { ClipboardCheck } from 'lucide-react'; // Import ClipboardCheck
import ReactMarkdown, { Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { Trajectory } from '../../models/trajectory';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../ui/collapsible';
import { MarkdownCodeBlock } from '../ui/MarkdownCodeBlock'; // Import shared code block component
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the copy button

interface PlanCompletedTrajectoryProps {
  trajectory: Trajectory;
}

export const PlanCompletedTrajectory: React.FC<PlanCompletedTrajectoryProps> = ({ trajectory }) => {
  const { stepData, created } = trajectory;
  // Extract the message from stepData.message, falling back if necessary
  const message = stepData?.message ?? stepData?.completion_message ?? '(No plan completion message)';
  const [isOpen, setIsOpen] = React.useState(true);

  const formattedTime = created
    ? new Date(created).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : 'Invalid Date';

  const components: Components = {
    code: MarkdownCodeBlock,
  };

  return (
    <Card className="mb-4">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CardHeader className="py-3 px-4 cursor-pointer hover:bg-muted/50">
          <CollapsibleTrigger asChild>
            <div className="flex justify-between items-center">
              {/* Left side: Icon and title */}
              <div className="flex items-center space-x-3">
                <ClipboardCheck className="h-4 w-4 text-blue-500" />
                <span>Plan Completed</span> {/* Adjusted title based on context */}
              </div>
              {/* Right side: Copy Button and Timestamp */}
              <div className="flex items-center space-x-2">
                {/* Moved Copy Button Here and Removed Absolute Positioning Wrapper */}
                <CopyToClipboardButton textToCopy={"# Plan Completed\n\n" + message} />
                <div className="text-xs text-muted-foreground">
                  {formattedTime}
                </div>
              </div>
            </div>
          </CollapsibleTrigger>
        </CardHeader>
        <CollapsibleContent>
          <CardContent className="pt-0 pb-3 px-4">
            <div className="prose prose-sm dark:prose-invert max-w-none break-words">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={components}
              >
                {message}
              </ReactMarkdown>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};
