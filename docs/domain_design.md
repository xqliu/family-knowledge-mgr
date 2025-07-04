# 家族知识管理系统 - 领域设计文档

## 项目概述

家族知识管理系统是一个基于Django的Web应用，旨在帮助家庭保存、组织和传承家族记忆、关系和重要信息。系统采用RAG（检索增强生成）技术，提供智能查询和自然语言交互能力。

## 系统定位

- **目标用户**: 5-10个家庭成员
- **使用场景**: 家族记忆保存、健康档案管理、传承文化记录
- **技术特点**: Django Admin作为主界面，集成AI对话和智能查询
- **部署平台**: Heroku (512MB内存限制)

## 核心领域模型

### 1. 人物 (People)

**目的**: 管理家庭成员和重要人物信息

**核心属性**:

- 姓名、生日、性别
- 个人简介、照片
- 联系方式

**关系**:

- 与其他人物的关系 (多对多)
- 参与的事件 (多对多)
- 健康档案 (一对多)
- 职业履历 (一对多)

### 2. 故事 (Story)

**目的**: 记录家族记忆、轶事和重要经历

**核心属性**:

- 标题、内容
- 创建时间、发生时间
- 故事类型（回忆、传说、经历等）

**关系**:

- 相关人物 (多对多)
- 相关事件 (多对多)
- 相关地点 (多对一)
- 多媒体附件 (多对多)

### 3. 事件 (Event)

**目的**: 记录重要时间节点和活动

**核心属性**:

- 事件名称、描述
- 开始/结束时间
- 事件类型（聚会、纪念日、里程碑等）

**关系**:

- 参与人员 (多对多)
- 事件地点 (多对一)
- 相关机构 (多对一)
- 多媒体记录 (多对多)

### 4. 关系 (Relationship)

**目的**: 定义人物之间的关系网络

**核心属性**:

- 关系类型（父子、夫妻、朋友、同事等）
- 关系开始时间
- 关系描述

**关系**:

- 连接两个人物实体
- 关系变化历史

### 5. 多媒体 (Multimedia)

**目的**: 管理各种文件资料

**核心属性**:

- 文件类型（照片、视频、文档、音频）
- 文件路径、大小
- 拍摄/创建时间
- 标题、描述

**关系**:

- 相关人物 (多对多)
- 相关事件 (多对多)
- 拍摄地点 (多对一)

### 6. 健康医疗 (Health)

**目的**: 管理个人和家族健康档案

**核心属性**:

- 记录类型（体检、疾病、用药、手术等）
- 记录时间、描述
- 医生/医院信息
- 是否为遗传性

**关系**:

- 所属人物 (多对一)
- 相关机构 (多对一)
- 相关文档 (多对多)

### 7. 传承 (Heritage)

**目的**: 记录家族价值观、传统和智慧

**核心属性**:

- 传承类型（家训、传统、智慧、技能等）
- 内容描述
- 传承人、传承对象
- 重要程度

**关系**:

- 传承者 (多对一)
- 相关故事 (多对多)
- 相关事件 (多对多)

### 8. 未来规划 (Planning)

**目的**: 记录家庭目标和愿景

**核心属性**:

- 规划名称、描述
- 时间范围（短期、中期、长期）
- 优先级、状态
- 预期结果

**关系**:

- 相关人物 (多对多)
- 相关资产 (多对多)

## 支撑领域模型

### 9. 地点 (Location)

**目的**: 统一管理地理位置信息

**核心属性**:

- 地点名称、地址
- 经纬度坐标
- 地点类型（家、办公、旅游等）
- 地点意义/故事

**关系**:

- 发生的事件 (一对多)
- 相关照片 (一对多)
- 相关人物居住史 (多对多)

### 10. 机构 (Institution)

**目的**: 统一管理外部机构信息

**核心属性**:

- 机构名称、类型
- 官网链接、联系方式
- 地址、成立时间
- 与家族关系描述

**机构类型**:

- 医院、学校、公司
- 政府机构、宗教场所
- 餐厅、娱乐场所

**关系**:

- 职业履历 (一对多)
- 健康记录 (一对多)
- 相关事件 (一对多)

### 11. 职业履历 (Career)

**目的**: 记录工作和教育经历

**核心属性**:

- 职位名称、级别
- 开始/结束时间
- 工作内容、成就
- 薪资范围（可选）

**关系**:

- 所属人物 (多对一)
- 所属机构 (多对一)
- 相关事件 (多对多)

### 12. 资产文档 (Assets)

**目的**: 管理重要财产和文件

**核心属性**:

- 资产名称、类型
- 估值、获得时间
- 存放位置、重要程度
- 法律状态

**资产类型**:

- 房产、车辆、珠宝
- 保险、股票、存款
- 重要证件、法律文件

**关系**:

- 所有者 (多对多)
- 相关文档 (多对多)
- 传承规划 (多对多)

### 13. 时间线 (Timeline)

**目的**: 提供时间维度的信息组织

**核心属性**:

- 时间点、时间段
- 事件重要程度
- 时代背景描述

**关系**:

- 关联各种时间相关的实体
- 支持时间序列查询

## 数据关系设计原则

### 1. 主体明确原则

- 每个信息有明确的主要归属领域
- 通过外键关系连接相关实体

### 2. 多对多关系处理

- 使用中间表存储关系的额外属性
- 支持关系的时间范围和状态变化

### 3. 标签和分类

- 使用标签字段标记特殊属性
- 支持自定义分类和标记

### 4. 版本控制

- 重要信息支持历史版本记录
- 追踪数据变更历史

## AI集成设计

### Text2SQL功能

- Django模型自动转换为SQL schema
- 自然语言查询转换为安全的只读SQL
- 支持复杂的跨表关联查询

### RAG对话系统

- 文本内容向量化存储在pgvector
- 结构化查询 + 语义搜索的混合检索
- 上下文感知的智能对话生成

### 智能功能

- 自动从文本中提取人物、时间、地点
- 照片中的人脸识别和关联
- 智能推荐相关内容和关系

## 技术架构

### 后端技术栈

- **Web框架**: Django 4.x
- **数据库**: PostgreSQL + pgvector扩展
- **AI集成**: LangChain + Anthropic Claude
- **缓存**: Redis (25MB)

### 前端界面

- **主界面**: Django Admin (自定义扩展)
- **响应式设计**: 支持移动设备访问
- **自定义页面**: 时间线视图、关系图谱等

### 部署环境

- **平台**: Heroku
- **资源限制**: 512MB内存，10GB PostgreSQL
- **文件存储**: Heroku文件系统 + 外部存储

## 安全和隐私

### 数据安全

- 用户认证和权限控制
- 敏感信息加密存储
- 数据备份和恢复机制

### 隐私保护

- 分级权限控制（个人、家庭、公开）
- 敏感健康信息特殊保护
- 数据导出和删除功能

## 扩展性考虑

### 功能扩展

- 插件化的AI功能模块
- 自定义字段和实体类型
- 第三方服务集成接口

### 性能扩展

- 数据库查询优化
- 缓存策略优化
- 大文件存储策略

这个设计文档为整个系统的开发提供了清晰的指导，确保各个组件之间的一致性和完整性。
