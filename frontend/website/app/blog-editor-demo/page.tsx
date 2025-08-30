'use client';

import { Suspense } from 'react';

// Demo editor disabled in production build.
function BlogEditorDemoContent() {
  return (
    <div className="p-8 text-center">
      <h1 className="text-2xl font-bold mb-4">Blog Editor Demo</h1>
      <p className="text-gray-600">This feature is disabled in production builds.</p>
    </div>
  );
}

export default function BlogEditorDemo() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <BlogEditorDemoContent />
    </Suspense>
  );
}
