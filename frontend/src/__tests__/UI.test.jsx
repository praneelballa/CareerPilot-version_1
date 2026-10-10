import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Layout } from '../components/Layout';
import { DashboardView } from '../components/DashboardView';
import { JobCard } from '../components/JobCard';

describe('UI Redesign Components', () => {
  it('renders Layout sidebar navigation', () => {
    const setActiveView = vi.fn();
    render(<Layout activeView="dashboard" setActiveView={setActiveView} candidateName="Jane Doe" />);
    
    expect(screen.getByText('CareerPilot')).toBeDefined();
    expect(screen.getByText('Jane Doe')).toBeDefined();
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThan(0);
  });

  it('renders Dashboard empty state if no profile', () => {
    render(<DashboardView profile={null} />);
    expect(screen.getByText('Welcome to CareerPilotAI')).toBeDefined();
  });

  it('renders JobCard properly', () => {
    const mockJob = {
      job_id: '123', company: 'Google', title: 'SWE', 
      description: 'Test desc', required_skills: ['React'], composite_score: 95
    };
    render(<JobCard job={mockJob} onAnalyze={vi.fn()} onTailor={vi.fn()} />);
    
    expect(screen.getByText('Google')).toBeDefined();
    expect(screen.getByText('SWE')).toBeDefined();
    expect(screen.getByText('95%')).toBeDefined();
  });
});