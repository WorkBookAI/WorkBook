export function formatMessage(text: string) {
  // Split by newlines and filter empty lines
  const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);

  return lines.map((line, idx) => {
    // Handle numbered lists
    if (/^\d+\./.test(line)) {
      return { type: 'list', content: line, key: `list-${idx}` };
    }

    // Handle bullet points
    if (/^[-*•]/.test(line)) {
      return { type: 'bullet', content: line.replace(/^[-*•]\s*/, ''), key: `bullet-${idx}` };
    }

    // Handle bold markers
    if (line.includes('**')) {
      return { type: 'text', content: line, key: `text-${idx}` };
    }

    // Regular text
    return { type: 'text', content: line, key: `text-${idx}` };
  });
}

export function renderFormattedLine(item: any) {
  if (item.type === 'list') {
    return <div className="ml-4 mb-2">{item.content}</div>;
  }

  if (item.type === 'bullet') {
    return (
      <div className="ml-4 mb-1 flex gap-2">
        <span>•</span>
        <span>{item.content}</span>
      </div>
    );
  }

  // Handle bold text
  const parts = item.content.split(/\*\*([^*]+)\*\*/);

  return (
    <p className="mb-2">
      {parts.map((part: string, idx: number) =>
        idx % 2 === 1 ?
          <strong key={idx}>{part}</strong> :
          <span key={idx}>{part}</span>
      )}
    </p>
  );
}
