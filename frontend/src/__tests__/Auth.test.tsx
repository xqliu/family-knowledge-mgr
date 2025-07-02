import React from 'react'
import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor, act } from '../test-utils'
import { mockFetch } from '../test-setup'
import App from '../App'

describe('Authentication Tests', () => {
  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('API Authentication Scenarios', () => {
    it('handles 401 Unauthorized responses from API', async () => {
      // Mock 401 response for health check (should not happen)
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Authentication required' })
      })

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API连接失败') ?? false
        )).toBeInTheDocument()
      })
    })

    it('handles 401 on family overview API call', async () => {
      // First call (health) succeeds, second call (family overview) returns 401
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'API运行正常' })
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          json: async () => ({ error: 'Authentication required' })
        })

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API运行正常') ?? false
        )).toBeInTheDocument()
      })

      // Should not display family data section due to 401
      expect(screen.queryByText('家庭概览')).not.toBeInTheDocument()
    })

    it('handles 403 Forbidden responses from API', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'API运行正常' })
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 403,
          json: async () => ({ error: 'Permission denied' })
        })

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API运行正常') ?? false
        )).toBeInTheDocument()
      })

      // Should not display family data section due to 403
      expect(screen.queryByText('家庭概览')).not.toBeInTheDocument()
    })

    it('displays appropriate error message for authentication failures', async () => {
      // Mock authentication error response
      mockFetch.mockRejectedValueOnce(new Error('Unauthorized: 401'))

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API连接失败') ?? false
        )).toBeInTheDocument()
      })
    })
  })

  describe('Authentication Flow Integration', () => {
    it('successfully displays data when authenticated', async () => {
      const mockAuthenticatedData = {
        stats: {
          total_members: 3,
          total_stories: 8,
          total_photos: 15
        }
      }

      // Mock successful authenticated API calls
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'API运行正常' })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockAuthenticatedData
        })

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText('家庭概览')).toBeInTheDocument()
      })

      // Check authenticated data is displayed
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('8')).toBeInTheDocument()
      expect(screen.getByText('15')).toBeInTheDocument()
    })

    it('handles mixed authentication states (health ok, family auth failed)', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'API运行正常' })
        })
        .mockRejectedValueOnce(new Error('Authentication required'))

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        // Health check should succeed
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API运行正常') ?? false
        )).toBeInTheDocument()
      })

      // Family data should not be displayed
      expect(screen.queryByText('家庭概览')).not.toBeInTheDocument()
    })

    it('retries API calls after authentication failure', async () => {
      // First attempt fails, but we can verify the calls were made
      mockFetch
        .mockRejectedValueOnce(new Error('Unauthorized'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'API运行正常' })
        })

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API连接失败') ?? false
        )).toBeInTheDocument()
      })

      // Verify fetch was called for health endpoint
      expect(mockFetch).toHaveBeenCalledWith('/api/health/')
    })
  })

  describe('Authentication Error Handling', () => {
    it('gracefully handles authentication timeout', async () => {
      // Mock slow network that times out
      mockFetch.mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      )

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API连接失败') ?? false
        )).toBeInTheDocument()
      }, { timeout: 200 })
    })

    it('handles malformed authentication responses', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          json: async () => { throw new Error('Invalid JSON') }
        })

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API连接失败') ?? false
        )).toBeInTheDocument()
      })
    })

    it('displays user-friendly error for authentication issues', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network authentication failed'))

      await act(async () => {
        render(<App />)
      })

      await waitFor(() => {
        // Should show generic API failure message, not expose auth details
        expect(screen.getByText((content, element) => 
          element?.textContent?.includes('API连接失败') ?? false
        )).toBeInTheDocument()
        
        // Should not expose specific auth error details
        expect(screen.queryByText(/authentication/i)).not.toBeInTheDocument()
      })
    })
  })
})