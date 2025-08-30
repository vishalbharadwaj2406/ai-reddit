'use client';

import { Suspense } from 'react';

// This demo page has been intentionally removed from production build.
// Keeping a minimal stub to avoid broken links during transition.
function DesignSystemDemoContent() {
  return (
    <div className="p-8 text-center">
      <h1 className="text-2xl font-bold mb-4">Design System Demo</h1>
      <p className="text-gray-600">This feature has been removed from production builds.</p>
    </div>
  );
}

export default function DesignSystemDemo() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DesignSystemDemoContent />
    </Suspense>
  );
}