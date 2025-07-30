import React, { useState, useCallback, useEffect } from 'react';
import { Clipboard, Check } from 'lucide-react';
import { cn } from '../../utils'; // Assuming cn utility exists for class merging

interface CopyToClipboardButtonProps {
  textToCopy: string;
  className?: string;
  tooltipText?: string; // Optional tooltip text
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'; // Optional size for tooltip
  variant?: string;
  tooltipSide?: string;
}

export const CopyToClipboardButton: React.FC<CopyToClipboardButtonProps> = ({
  textToCopy,
  className,
}) => {
  const [isCopied, setIsCopied] = useState(false);

  // Modified function signature to accept the event
  const copyToClipboard = useCallback(async (event: React.MouseEvent) => {
    // Stop the event from bubbling up to parent elements (like Collapsible trigger)
    event.stopPropagation();

    try {
      await navigator.clipboard.writeText(textToCopy);
      setIsCopied(true);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      // Optionally: Add user feedback for error
    }
  }, [textToCopy]);

  useEffect(() => {
    if (isCopied) {
      const timer = setTimeout(() => {
        setIsCopied(false);
      }, 2000); // Reset icon after 2 seconds

      return () => clearTimeout(timer); // Cleanup timer on unmount or if isCopied changes
    }
  }, [isCopied]);

  return (
    <button
      type="button"
      // Updated onClick handler to pass the event object
      onClick={(e) => copyToClipboard(e)}
      className={cn(
        'inline-flex items-center justify-center p-1 border border-muted rounded-md text-muted-foreground',
        'hover:bg-muted hover:scale-105 active:scale-100',
        'transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        className // Merge custom classes
      )}
      aria-label="Copy to clipboard"
    >
      {isCopied ? (
        <Check className="h-4 w-4 text-green-500" />
      ) : (
        <Clipboard className="h-4 w-4" />
      )}
    </button>
  );
};
