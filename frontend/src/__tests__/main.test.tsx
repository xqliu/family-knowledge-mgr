import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock ReactDOM
const mockRender = vi.fn()
const mockCreateRoot = vi.fn(() => ({
  render: mockRender
}))

vi.mock('react-dom/client', () => ({
  createRoot: mockCreateRoot
}))

// Mock the App component
vi.mock('../App.tsx', () => ({
  default: () => React.createElement('div', { 'data-testid': 'app' }, 'Mocked App')
}))

describe('main.tsx', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.resetModules()
    
    // Mock document.getElementById
    const mockElement = document.createElement('div')
    mockElement.id = 'root'
    vi.spyOn(document, 'getElementById').mockReturnValue(mockElement)
  })

  it('should create root and render App in StrictMode', async () => {
    // Import main.tsx to execute the code
    await import('../main.tsx')
    
    // Verify createRoot was called with the root element
    expect(document.getElementById).toHaveBeenCalledWith('root')
    expect(mockCreateRoot).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'root' })
    )
    
    // Verify render was called
    expect(mockRender).toHaveBeenCalledTimes(1)
    
    // Check that render was called with a React element
    expect(mockRender).toHaveBeenCalledWith(
      expect.objectContaining({
        type: React.StrictMode,
        props: expect.objectContaining({
          children: expect.any(Object)
        })
      })
    )
  })

  it('should call createRoot with root element', async () => {
    const mockElement = document.createElement('div')
    mockElement.id = 'root'
    vi.spyOn(document, 'getElementById').mockReturnValue(mockElement)
    
    await import('../main.tsx')
    
    expect(mockCreateRoot).toHaveBeenCalledWith(mockElement)
  })
})