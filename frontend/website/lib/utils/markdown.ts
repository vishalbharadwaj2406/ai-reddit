// Very small, conservative markdown-to-plain converter for copy purposes.
export function markdownToPlain(md: string): string {
  let out = md;
  // Code fences -> code content only
  out = out.replace(/```[\s\S]*?```/g, (block) => block.replace(/```[a-zA-Z0-9\-]*\n?/, '').replace(/```$/, ''));
  // Inline code
  out = out.replace(/`([^`]+)`/g, '$1');
  // Bold/italic/strike
  out = out.replace(/\*\*([^*]+)\*\*/g, '$1');
  out = out.replace(/\*([^*]+)\*/g, '$1');
  out = out.replace(/_([^_]+)_/g, '$1');
  out = out.replace(/~~([^~]+)~~/g, '$1');
  // Links [text](url) -> text (url)
  out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)');
  // Headings: remove hashes
  out = out.replace(/^#{1,6}\s*/gm, '');
  // Lists: remove markers
  out = out.replace(/^\s*[-*+]\s+/gm, '- ');
  out = out.replace(/^\s*\d+\.\s+/gm, (m) => m.replace(/\d+\./, '1.'));
  // Blockquotes: remove '>'
  out = out.replace(/^>\s?/gm, '');
  // Trim extra blank lines
  out = out.replace(/\n{3,}/g, '\n\n');
  return out.trim();
}
