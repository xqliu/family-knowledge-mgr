import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '../test-utils'
import userEvent from '@testing-library/user-event'
import App from '../App'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('App Component', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('renders main heading and subtitle', () => {
    // Mock successful API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: { total_members: 5, total_stories: 10, total_photos: 25 }
        })
      })

    render(<App />)
    
    expect(screen.getByText('🏠 家庭知识库')).toBeInTheDocument()
    expect(screen.getByText('Family Knowledge Hub')).toBeInTheDocument()
  })

  it('displays initial API status as checking', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: { total_members: 0, total_stories: 0, total_photos: 0 }
        })
      })

    render(<App />)
    
    expect(screen.getByText(/检测中.../)).toBeInTheDocument()
  })

  it('displays API status after successful health check', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: { total_members: 0, total_stories: 0, total_photos: 0 }
        })
      })

    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText(/API运行正常/)).toBeInTheDocument()
    })
    
    expect(mockFetch).toHaveBeenCalledWith('/api/health/')
    expect(mockFetch).toHaveBeenCalledWith('/api/family/overview/')
  })

  it('displays family data when API returns data', async () => {
    const mockFamilyData = {
      stats: {
        total_members: 5,
        total_stories: 10,
        total_photos: 25
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockFamilyData
      })

    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('家庭概览')).toBeInTheDocument()
    })

    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
    expect(screen.getByText('家庭成员')).toBeInTheDocument()
    expect(screen.getByText('家庭故事')).toBeInTheDocument()
    expect(screen.getByText('家庭照片')).toBeInTheDocument()
  })

  it('handles API connection failure', async () => {
    mockFetch.mockRejectedValue(new Error('Network error'))

    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText(/API连接失败/)).toBeInTheDocument()
    })
  })

  it('displays zero values when family data stats are missing', async () => {
    const mockFamilyData = {
      stats: {} // Empty stats
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockFamilyData
      })

    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText('家庭概览')).toBeInTheDocument()
    })

    // Should display 0 for missing stats
    const zeros = screen.getAllByText('0')
    expect(zeros).toHaveLength(3) // Should have 3 zeros for members, stories, photos
  })

  it('displays system status information', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: { total_members: 0, total_stories: 0, total_photos: 0 }
        })
      })

    render(<App />)
    
    expect(screen.getByText('系统状态')).toBeInTheDocument()
    expect(screen.getByText(/React \+ TypeScript \+ Vite/)).toBeInTheDocument()
    expect(screen.getByText(/Django \+ API/)).toBeInTheDocument()
  })

  it('displays quick access links', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: { total_members: 0, total_stories: 0, total_photos: 0 }
        })
      })

    render(<App />)
    
    expect(screen.getByText('快速访问')).toBeInTheDocument()
    
    const adminLink = screen.getByText('📊 Django Admin')
    const healthLink = screen.getByText('🔍 API健康检查')
    const familyLink = screen.getByText('👨‍👩‍👧‍👦 家庭数据API')
    
    expect(adminLink.closest('a')).toHaveAttribute('href', '/admin/')
    expect(healthLink.closest('a')).toHaveAttribute('href', '/api/health/')
    expect(familyLink.closest('a')).toHaveAttribute('href', '/api/family/overview/')
  })

  it('displays footer text', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          stats: { total_members: 0, total_stories: 0, total_photos: 0 }
        })
      })

    render(<App />)
    
    expect(screen.getByText(/单体部署架构演示/)).toBeInTheDocument()
  })

  it('does not render family data section when no data is available', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockRejectedValueOnce(new Error('Family data fetch failed'))

    render(<App />)
    
    expect(screen.queryByText('家庭概览')).not.toBeInTheDocument()
  })

  it('handles partial API failure gracefully', async () => {
    // First API call succeeds, second fails
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'API运行正常' })
      })
      .mockRejectedValueOnce(new Error('Family overview failed'))

    render(<App />)
    
    await waitFor(() => {
      expect(screen.getByText(/API运行正常/)).toBeInTheDocument()
    })
    
    // Should not show family data section
    expect(screen.queryByText('家庭概览')).not.toBeInTheDocument()
  })
})