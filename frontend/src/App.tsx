import { useState, useEffect } from 'react'
import { BottomChat } from './components/chat'
import './App.css'

interface ActivityItem {
  id: number
  type: 'birthday' | 'photo' | 'story' | 'health' | 'event'
  content: string
  detail: string
  icon: string
}

function App() {
  const [recentActivities, setRecentActivities] = useState<ActivityItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 获取今日家庭动态
    fetch('/api/family/overview/')
      .then(res => res.json())
      .then(() => {
        // 模拟今日动态数据
        setRecentActivities([
          { id: 1, type: 'birthday', content: '妈妈生日提醒', detail: '3天后', icon: '🎂' },
          { id: 2, type: 'photo', content: '新照片: 家庭聚餐', detail: '今天上传', icon: '📸' },
          { id: 3, type: 'story', content: '爷爷分享了新故事', detail: '2小时前', icon: '📝' }
        ])
        setIsLoading(false)
      })
      .catch(err => {
        console.error('获取数据失败:', err)
        setIsLoading(false)
      })
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏠 家庭知识库</h1>
          <div className="header-actions">
            <button className="ai-toggle desktop-only">🤖 AI助手</button>
            <button className="user-menu">👤</button>
          </div>
        </div>
      </header>

      <main className="app-main">
        {/* 今日家庭动态 - Hero Section */}
        <section className="hero-section">
          <h2>今日家庭动态</h2>
          <div className="activities-grid">
            {isLoading ? (
              <div className="loading">加载中...</div>
            ) : (
              recentActivities.map(activity => (
                <div key={activity.id} className="activity-card">
                  <div className="activity-icon">{activity.icon}</div>
                  <div className="activity-content">
                    <h3>{activity.content}</h3>
                    <p>{activity.detail}</p>
                  </div>
                  <button className="activity-action">查看详情</button>
                </div>
              ))
            )}
          </div>
        </section>

        {/* 快速操作和主要功能 */}
        <div className="content-grid">
          <section className="quick-actions">
            <h2>快速操作</h2>
            <div className="actions-grid">
              <button className="action-button primary">
                <span className="icon">➕</span>
                <span className="text">添加内容</span>
              </button>
              <button className="action-button">
                <span className="icon">🔍</span>
                <span className="text">智能搜索</span>
              </button>
              <button className="action-button">
                <span className="icon">📋</span>
                <span className="text">待办事项</span>
              </button>
              <button className="action-button">
                <span className="icon">📊</span>
                <span className="text">家庭报告</span>
              </button>
            </div>
          </section>

          <section className="main-functions">
            <h2>主要功能</h2>
            <div className="functions-grid">
              <button className="function-button">
                <span className="icon">👥</span>
                <span className="text">家庭成员</span>
              </button>
              <button className="function-button">
                <span className="icon">📖</span>
                <span className="text">家庭故事</span>
              </button>
              <button className="function-button">
                <span className="icon">🎉</span>
                <span className="text">重要事件</span>
              </button>
              <button className="function-button">
                <span className="icon">📸</span>
                <span className="text">照片回忆</span>
              </button>
            </div>
            <button className="more-functions">更多功能 →</button>
          </section>
        </div>
      </main>

      {/* AI Chat Component - Self-positioned */}
      <BottomChat />
    </div>
  )
}

export default App
