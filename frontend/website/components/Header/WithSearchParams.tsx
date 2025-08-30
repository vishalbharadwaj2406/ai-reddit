'use client'

import React, { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'

function SearchParamsContent({ children }: { children: (searchParams: URLSearchParams) => React.ReactNode }) {
  const searchParams = useSearchParams()
  return <>{children(searchParams)}</>
}

export function WithSearchParams({ children }: { children: (searchParams: URLSearchParams) => React.ReactNode }) {
  return (
    <Suspense fallback={<>{children(new URLSearchParams())}</>}>
      <SearchParamsContent>{children}</SearchParamsContent>
    </Suspense>
  )
}
