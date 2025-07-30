import React, { FC } from 'react';
import { Trajectory } from '../../models/trajectory'; // Assuming '@models' alias is configured
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'; // Assuming '@components' alias
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '../ui/collapsible';
import { CopyToClipboardButton } from '../ui/CopyToClipboardButton'; // Import the copy button

// Define the specific type for this trajectory variant
interface UserQueryTrajectoryProps {
  trajectory: Trajectory;
}

function isUserQueryTrajectory(
  t: Trajectory
): t is Trajectory & { recordType: 'user_query'; stepData?: { query?: string } } {
  return t.recordType === 'user_query';
}

/**
 *
 *
 * Renders a trajectory step representing the initial user query that started the session.
 */
export const UserQueryTrajectory: FC<UserQueryTrajectoryProps> = ({ trajectory }) => {
  // Safely access the query from stepData. Use empty string for copy button if query is missing.

  if (!isUserQueryTrajectory(trajectory)) {
    return null; // or fallback UI
  }

  const query = trajectory.stepData?.query ?? '';
  const displayQuery = query || 'Initial query data not available.'; // Fallback for display
  const formattedTime = new Date(trajectory.created).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (

    <Collapsible
      defaultOpen={true}
      className="w-full border border-border rounded-md overflow-hidden shadow-sm hover:shadow-md transition-all duration-200"
    >
      <CollapsibleTrigger className="w-full text-left hover:bg-accent/30 cursor-pointer">
        <CardHeader className="py-3 px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3 flex-1 min-w-0 mr-2"> {/* Ensure title can truncate */}
              <div className="flex-shrink-0 text-lg">❔</div>
              <CardTitle className="text-base font-medium truncate">{/* Display title in card */}
                Query
              </CardTitle>
            </div>
            <div className="flex items-center space-x-2 flex-shrink-0"> {/* Container for button and time */}
              {/* Use the constructed summary text for copying */}
              <CopyToClipboardButton textToCopy={query} />
              <div className="text-xs text-muted-foreground">
                {formattedTime}
              </div>
            </div>
          </div>
        </CardHeader>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <CardContent className="py-3 px-4 border-t border-border bg-card/50">
          <div className="text-sm space-y-1">
            <pre className="bg-muted/50 p-3 rounded-md overflow-x-auto whitespace-pre-wrap">
              {query}
            </pre>
          </div>
        </CardContent>
      </CollapsibleContent>
    </Collapsible>
  );
};
