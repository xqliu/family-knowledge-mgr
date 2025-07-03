import { useState, useEffect } from 'react'
import { ChatInterface } from './components/chat'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('检测中...')
  const [familyData, setFamilyData] = useState<{
    stats?: {
      total_members?: number
      total_stories?: number
      total_photos?: number
    }
  } | null>(null)

  useEffect(() => {
    // 测试API连接
    fetch('/api/health/')
      .then(res => res.json())
      .then(data => {
        setApiStatus(data.message)
        // 获取家庭数据
        return fetch('/api/family/overview/')
      })
      .then(res => res.json())
      .then(data => {
        setFamilyData(data)
      })
      .catch(err => {
        console.error('API连接失败:', err)
        setApiStatus('API连接失败')
      })
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏠 家庭知识库</h1>
          <p className="subtitle">Family Knowledge Hub</p>
        </div>
      </header>

      <main className="app-main">
        <div className="status-card">
          <h2>系统状态</h2>
          <p><span className="status-text">API状态:</span> <span className="status">{apiStatus} ✅</span></p>
          <p><span className="status-text">前端:</span> <span className="status-success">React + TypeScript + Vite ✅</span></p>
          <p><span className="status-text">后端:</span> <span className="status-success">Django + API ✅</span></p>
        </div>

        {familyData && (
          <div className="data-card">
            <h2>家庭概览</h2>
            <div className="stats">
              <div className="stat">
                <span className="number">{familyData.stats?.total_members || 0}</span>
                <span className="label">家庭成员</span>
              </div>
              <div className="stat">
                <span className="number">{familyData.stats?.total_stories || 0}</span>
                <span className="label">家庭故事</span>
              </div>
              <div className="stat">
                <span className="number">{familyData.stats?.total_photos || 0}</span>
                <span className="label">家庭照片</span>
              </div>
            </div>
          </div>
        )}

        <div className="chat-card">
          <h2>🤖 AI智慧助手</h2>
          <p className="chat-description">
            询问关于家庭记忆、传统、健康、事件等问题，获得智能回答和相关资料。
          </p>
          <ChatInterface className="app-chat" />
        </div>

        <div className="links-card">
          <h2>快速访问</h2>
          <div className="links">
            <a href="/admin/" className="link-button" target="_blank">
              📊 Django Admin
            </a>
            <a href="/api/health/" className="link-button" target="_blank">
              🔍 API健康检查
            </a>
            <a href="/api/family/overview/" className="link-button" target="_blank">
              👨‍👩‍👧‍👦 家庭数据API
            </a>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <p>✨ 单体部署架构演示 - React前端 + Django后端</p>
        </div>
      </footer>
    </div>
  )
}

export default App
