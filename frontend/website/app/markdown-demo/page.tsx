"use client";

import { Suspense } from 'react';
import MarkdownRenderer from "../../components/Markdown/MarkdownRenderer";

const sample = `# Markdown Demo\n\n- List item A\n- List item B\n\n## Code\n\nInline: \`inline code\`.\n\n\n\u0060\u0060\u0060ts\nfunction add(a: number, b: number) {\n  return a + b;\n}\nconsole.log(add(2, 3));\n\u0060\u0060\u0060\n\n[External Link](https://example.com)`;

function MarkdownDemoContent() {
  return (
    <div className="max-w-3xl mx-auto p-6">
      <MarkdownRenderer content={sample} />
    </div>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<div>Loading markdown demo...</div>}>
      <MarkdownDemoContent />
    </Suspense>
  );
}
