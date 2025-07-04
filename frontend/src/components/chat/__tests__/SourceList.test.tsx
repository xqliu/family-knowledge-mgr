import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test-utils';
import { SourceList } from '../SourceList';
import type { ChatSource } from '../types';

describe('SourceList', () => {
  const mockSources: ChatSource[] = [
    {
      type: 'story',
      id: 1,
      title: '家庭传统故事',
      relevance: 0.9,
      story_type: '传统',
      people: ['张三', '李四'],
      date: '2023-01-01'
    },
    {
      type: 'event',
      id: 2,
      title: '重要庆祝活动',
      relevance: 0.7,
      event_type: '庆祝',
      importance: '高'
    },
    {
      type: 'heritage',
      id: 3,
      title: '家族智慧',
      relevance: 0.5,
      heritage_type: '智慧',
      person: '爷爷'
    },
    {
      type: 'health',
      id: 4,
      title: '家族健康记录',
      relevance: 0.8,
      is_hereditary: true
    },
    {
      type: 'person',
      id: 5,
      title: '家庭成员信息',
      relevance: 0.6
    },
    {
      type: 'multimedia',
      id: 6,
      title: '家庭照片',
      relevance: 0.4
    },
    {
      type: 'unknown',
      id: 7,
      title: '其他内容',
      relevance: 0.3
    }
  ];

  it('renders empty list when no sources provided', () => {
    render(<SourceList sources={[]} />);
    
    const sourceList = document.querySelector('.source-list');
    expect(sourceList).toBeInTheDocument();
    expect(sourceList?.children).toHaveLength(0);
  });

  it('renders all sources with correct structure', () => {
    render(<SourceList sources={mockSources} />);
    
    const sourceItems = document.querySelectorAll('.source-item');
    expect(sourceItems).toHaveLength(mockSources.length);
  });

  it('displays correct icons for each source type', () => {
    render(<SourceList sources={mockSources} />);
    
    // Check that icons are rendered (they are in spans with class 'source-icon')
    const iconElements = document.querySelectorAll('.source-icon');
    expect(iconElements).toHaveLength(mockSources.length);
    
    expect(iconElements[0]).toHaveTextContent('📖'); // story
    expect(iconElements[1]).toHaveTextContent('🎉'); // event
    expect(iconElements[2]).toHaveTextContent('🏛️'); // heritage
    expect(iconElements[3]).toHaveTextContent('🏥'); // health
    expect(iconElements[4]).toHaveTextContent('👤'); // person
    expect(iconElements[5]).toHaveTextContent('🎬'); // multimedia
    expect(iconElements[6]).toHaveTextContent('📄'); // unknown/default
  });

  it('displays correct Chinese labels for source types', () => {
    render(<SourceList sources={mockSources} />);
    
    expect(screen.getByText('家庭故事')).toBeInTheDocument();
    expect(screen.getByText('重要事件')).toBeInTheDocument();
    expect(screen.getByText('文化传承')).toBeInTheDocument();
    expect(screen.getByText('健康记录')).toBeInTheDocument();
    expect(screen.getByText('家庭成员')).toBeInTheDocument();
    expect(screen.getByText('多媒体')).toBeInTheDocument();
    expect(screen.getByText('其他')).toBeInTheDocument();
  });

  it('displays relevance percentages with correct colors', () => {
    render(<SourceList sources={mockSources} />);
    
    const relevanceElements = document.querySelectorAll('.source-relevance');
    expect(relevanceElements).toHaveLength(mockSources.length);
    
    // Check percentages
    expect(relevanceElements[0]).toHaveTextContent('90%');
    expect(relevanceElements[1]).toHaveTextContent('70%');
    expect(relevanceElements[2]).toHaveTextContent('50%');
    expect(relevanceElements[3]).toHaveTextContent('80%');
    expect(relevanceElements[4]).toHaveTextContent('60%');
    expect(relevanceElements[5]).toHaveTextContent('40%');
    expect(relevanceElements[6]).toHaveTextContent('30%');
    
    // Check colors
    expect(relevanceElements[0]).toHaveStyle('color: #10b981'); // >= 0.8 (green)
    expect(relevanceElements[1]).toHaveStyle('color: #f59e0b'); // >= 0.6 (yellow)
    expect(relevanceElements[2]).toHaveStyle('color: #ef4444'); // < 0.6 (red)
    expect(relevanceElements[3]).toHaveStyle('color: #10b981'); // >= 0.8 (green)
    expect(relevanceElements[4]).toHaveStyle('color: #f59e0b'); // >= 0.6 (yellow)
    expect(relevanceElements[5]).toHaveStyle('color: #ef4444'); // < 0.6 (red)
    expect(relevanceElements[6]).toHaveStyle('color: #ef4444'); // < 0.6 (red)
  });

  it('displays source titles', () => {
    render(<SourceList sources={mockSources} />);
    
    mockSources.forEach(source => {
      expect(screen.getByText(source.title)).toBeInTheDocument();
    });
  });

  it('displays story-specific details when available', () => {
    const storySource: ChatSource = {
      type: 'story',
      id: 1,
      title: '测试故事',
      relevance: 0.8,
      story_type: '传统故事'
    };
    
    render(<SourceList sources={[storySource]} />);
    
    expect(screen.getByText('故事类型:')).toBeInTheDocument();
    expect(screen.getByText('传统故事')).toBeInTheDocument();
  });

  it('displays event-specific details when available', () => {
    const eventSource: ChatSource = {
      type: 'event',
      id: 1,
      title: '测试事件',
      relevance: 0.8,
      event_type: '庆祝活动'
    };
    
    render(<SourceList sources={[eventSource]} />);
    
    expect(screen.getByText('事件类型:')).toBeInTheDocument();
    expect(screen.getByText('庆祝活动')).toBeInTheDocument();
  });

  it('displays heritage-specific details when available', () => {
    const heritageSource: ChatSource = {
      type: 'heritage',
      id: 1,
      title: '测试传承',
      relevance: 0.8,
      heritage_type: '家族智慧'
    };
    
    render(<SourceList sources={[heritageSource]} />);
    
    expect(screen.getByText('传承类型:')).toBeInTheDocument();
    expect(screen.getByText('家族智慧')).toBeInTheDocument();
  });

  it('displays person details when available', () => {
    const personSource: ChatSource = {
      type: 'story',
      id: 1,
      title: '测试',
      relevance: 0.8,
      person: '张三'
    };
    
    render(<SourceList sources={[personSource]} />);
    
    expect(screen.getByText('相关人员:')).toBeInTheDocument();
    expect(screen.getByText('张三')).toBeInTheDocument();
  });

  it('displays people array when available', () => {
    const peopleSource: ChatSource = {
      type: 'story',
      id: 1,
      title: '测试',
      relevance: 0.8,
      people: ['张三', '李四', '王五']
    };
    
    render(<SourceList sources={[peopleSource]} />);
    
    expect(screen.getByText('涉及人员:')).toBeInTheDocument();
    expect(screen.getByText('张三, 李四, 王五')).toBeInTheDocument();
  });

  it('displays date when available', () => {
    const dateSource: ChatSource = {
      type: 'event',
      id: 1,
      title: '测试事件',
      relevance: 0.8,
      date: '2023-12-25'
    };
    
    render(<SourceList sources={[dateSource]} />);
    
    expect(screen.getByText('日期:')).toBeInTheDocument();
    expect(screen.getByText('2023-12-25')).toBeInTheDocument();
  });

  it('displays importance when available', () => {
    const importanceSource: ChatSource = {
      type: 'event',
      id: 1,
      title: '测试事件',
      relevance: 0.8,
      importance: '非常重要'
    };
    
    render(<SourceList sources={[importanceSource]} />);
    
    expect(screen.getByText('重要程度:')).toBeInTheDocument();
    expect(screen.getByText('非常重要')).toBeInTheDocument();
  });

  it('displays hereditary information when true', () => {
    const hereditarySource: ChatSource = {
      type: 'health',
      id: 1,
      title: '遗传病史',
      relevance: 0.8,
      is_hereditary: true
    };
    
    render(<SourceList sources={[hereditarySource]} />);
    
    expect(screen.getByText('遗传性:')).toBeInTheDocument();
    expect(screen.getByText('是')).toBeInTheDocument();
  });

  it('does not display hereditary information when false', () => {
    const nonHereditarySource: ChatSource = {
      type: 'health',
      id: 1,
      title: '普通病史',
      relevance: 0.8,
      is_hereditary: false
    };
    
    render(<SourceList sources={[nonHereditarySource]} />);
    
    expect(screen.queryByText('遗传性:')).not.toBeInTheDocument();
  });

  it('does not display optional fields when not provided', () => {
    const minimalSource: ChatSource = {
      type: 'story',
      id: 1,
      title: '最小化源',
      relevance: 0.8
    };
    
    render(<SourceList sources={[minimalSource]} />);
    
    expect(screen.queryByText('故事类型:')).not.toBeInTheDocument();
    expect(screen.queryByText('相关人员:')).not.toBeInTheDocument();
    expect(screen.queryByText('涉及人员:')).not.toBeInTheDocument();
    expect(screen.queryByText('日期:')).not.toBeInTheDocument();
    expect(screen.queryByText('重要程度:')).not.toBeInTheDocument();
    expect(screen.queryByText('遗传性:')).not.toBeInTheDocument();
  });

  it('generates unique keys for sources', () => {
    const duplicateTypeSources: ChatSource[] = [
      { type: 'story', id: 1, title: '故事1', relevance: 0.8 },
      { type: 'story', id: 2, title: '故事2', relevance: 0.7 },
      { type: 'story', id: 1, title: '故事3', relevance: 0.6 } // Same type and id
    ];
    
    render(<SourceList sources={duplicateTypeSources} />);
    
    const sourceItems = document.querySelectorAll('.source-item');
    expect(sourceItems).toHaveLength(3);
    
    // Should render all three items even with duplicate type/id combinations
    expect(screen.getByText('故事1')).toBeInTheDocument();
    expect(screen.getByText('故事2')).toBeInTheDocument();
    expect(screen.getByText('故事3')).toBeInTheDocument();
  });

  it('handles empty people array', () => {
    const emptyPeopleSource: ChatSource = {
      type: 'story',
      id: 1,
      title: '测试',
      relevance: 0.8,
      people: []
    };
    
    render(<SourceList sources={[emptyPeopleSource]} />);
    
    expect(screen.queryByText('涉及人员:')).not.toBeInTheDocument();
  });

  describe('helper functions', () => {
    it('getSourceIcon returns correct icons for story type', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('📖');
    });

    it('getSourceIcon returns correct icons for event type', () => {
      const { container } = render(<SourceList sources={[{ type: 'event', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('🎉');
    });

    it('getSourceIcon returns correct icons for heritage type', () => {
      const { container } = render(<SourceList sources={[{ type: 'heritage', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('🏛️');
    });

    it('getSourceIcon returns correct icons for health type', () => {
      const { container } = render(<SourceList sources={[{ type: 'health', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('🏥');
    });

    it('getSourceIcon returns correct icons for person type', () => {
      const { container } = render(<SourceList sources={[{ type: 'person', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('👤');
    });

    it('getSourceIcon returns correct icons for multimedia type', () => {
      const { container } = render(<SourceList sources={[{ type: 'multimedia', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('🎬');
    });

    it('getSourceIcon returns default icon for unknown type', () => {
      const { container } = render(<SourceList sources={[{ type: 'unknown', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const iconElement = container.querySelector('.source-icon');
      expect(iconElement).toHaveTextContent('📄');
    });

    it('getSourceTypeLabel returns correct label for story type', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('家庭故事');
    });

    it('getSourceTypeLabel returns correct label for event type', () => {
      const { container } = render(<SourceList sources={[{ type: 'event', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('重要事件');
    });

    it('getSourceTypeLabel returns correct label for heritage type', () => {
      const { container } = render(<SourceList sources={[{ type: 'heritage', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('文化传承');
    });

    it('getSourceTypeLabel returns correct label for health type', () => {
      const { container } = render(<SourceList sources={[{ type: 'health', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('健康记录');
    });

    it('getSourceTypeLabel returns correct label for person type', () => {
      const { container } = render(<SourceList sources={[{ type: 'person', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('家庭成员');
    });

    it('getSourceTypeLabel returns correct label for multimedia type', () => {
      const { container } = render(<SourceList sources={[{ type: 'multimedia', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('多媒体');
    });

    it('getSourceTypeLabel returns default label for unknown type', () => {
      const { container } = render(<SourceList sources={[{ type: 'unknown', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const typeElement = container.querySelector('.source-type');
      expect(typeElement).toHaveTextContent('其他');
    });

    it('getRelevanceColor returns green for high relevance (>= 0.8)', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.9 }]} />);
      const relevanceElement = container.querySelector('.source-relevance');
      expect(relevanceElement).toHaveStyle('color: #10b981');
    });

    it('getRelevanceColor returns green for relevance equal to 0.8', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.8 }]} />);
      const relevanceElement = container.querySelector('.source-relevance');
      expect(relevanceElement).toHaveStyle('color: #10b981');
    });

    it('getRelevanceColor returns yellow for medium relevance (>= 0.6)', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.7 }]} />);
      const relevanceElement = container.querySelector('.source-relevance');
      expect(relevanceElement).toHaveStyle('color: #f59e0b');
    });

    it('getRelevanceColor returns yellow for relevance equal to 0.6', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.6 }]} />);
      const relevanceElement = container.querySelector('.source-relevance');
      expect(relevanceElement).toHaveStyle('color: #f59e0b');
    });

    it('getRelevanceColor returns red for low relevance (< 0.6)', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.5 }]} />);
      const relevanceElement = container.querySelector('.source-relevance');
      expect(relevanceElement).toHaveStyle('color: #ef4444');
    });

    it('getRelevanceColor returns red for very low relevance', () => {
      const { container } = render(<SourceList sources={[{ type: 'story', id: 1, title: 'Test', relevance: 0.1 }]} />);
      const relevanceElement = container.querySelector('.source-relevance');
      expect(relevanceElement).toHaveStyle('color: #ef4444');
    });
  });
});