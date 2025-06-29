import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

// Custom render function with providers if needed
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return render(ui, {
    // Add any providers here in the future (e.g., ThemeProvider, Router, etc.)
    // wrapper: ({ children }) => <Providers>{children}</Providers>,
    ...options,
  })
}

// Re-export everything from @testing-library/react
export * from '@testing-library/react'

// Override render method
export { customRender as render }