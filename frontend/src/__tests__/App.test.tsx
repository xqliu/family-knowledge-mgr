import React from 'react'
import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, waitFor, act } from '../test-utils'
import { mockFetch } from '../test-setup'
import App from '../App'

describe('App Component', () => {
  afterEach(() => {
    vi.resetAllMocks()
  })

  it('renders main heading', async () => {
    // Mock successful API response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })
    
    expect(screen.getByText('🏠 家庭知识库')).toBeInTheDocument()
  })

  it('renders header actions', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })
    
    expect(screen.getByText('👤')).toBeInTheDocument()
  })

  it('displays loading state initially', () => {
    // Mock fetch with a promise that never resolves to keep it in loading state
    mockFetch.mockImplementation(() => new Promise(() => {}))
    
    render(<App />)
    
    expect(screen.getByText('加载中...')).toBeInTheDocument()
  })

  it('displays recent activities after successful API call', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })

    await waitFor(() => {
      expect(screen.getByText('今日家庭动态')).toBeInTheDocument()
      expect(screen.getByText('妈妈生日提醒')).toBeInTheDocument()
      expect(screen.getByText('新照片: 家庭聚餐')).toBeInTheDocument()
      expect(screen.getByText('爷爷分享了新故事')).toBeInTheDocument()
    })
  })

  it('displays quick actions section', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })

    await waitFor(() => {
      expect(screen.getByText('快速操作')).toBeInTheDocument()
      expect(screen.getByText('添加内容')).toBeInTheDocument()
      expect(screen.getByText('智能搜索')).toBeInTheDocument()
      expect(screen.getByText('待办事项')).toBeInTheDocument()
      expect(screen.getByText('家庭报告')).toBeInTheDocument()
    })
  })

  it('displays main functions section', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })

    await waitFor(() => {
      expect(screen.getByText('主要功能')).toBeInTheDocument()
      expect(screen.getByText('家庭成员')).toBeInTheDocument()
      expect(screen.getByText('家庭故事')).toBeInTheDocument()
      expect(screen.getByText('重要事件')).toBeInTheDocument()
      expect(screen.getByText('照片回忆')).toBeInTheDocument()
    })
  })

  it('handles API error gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    await act(async () => {
      render(<App />)
    })

    // Should still show the page with default data
    await waitFor(() => {
      expect(screen.getByText('今日家庭动态')).toBeInTheDocument()
    })
  })

  it('renders BottomChat component', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })

    // Check for the floating chat button
    expect(screen.getByTitle('打开家庭知识助手')).toBeInTheDocument()
  })

  it('displays "more functions" button', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        stats: { total_members: 5, total_stories: 10, total_photos: 25 }
      })
    })

    await act(async () => {
      render(<App />)
    })

    await waitFor(() => {
      expect(screen.getByText('更多功能 →')).toBeInTheDocument()
    })
  })

})