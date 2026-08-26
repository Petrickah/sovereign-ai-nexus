import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// RTL's automatic afterEach-cleanup only self-registers when it detects
// global test-framework hooks; vitest.config.ts intentionally runs without
// `globals: true` (explicit imports in test files instead), so it has to be
// wired up here or every test after the first sees leftover DOM nodes.
afterEach(cleanup)
