import React from 'react';
import { render, screen } from '../../../utils/test-utils';
import LoadingSpinner, { Skeleton, ProgressBar, LoadingStates } from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders with custom text', () => {
    render(<LoadingSpinner text="Custom loading text" />);
    expect(screen.getByText('Custom loading text')).toBeInTheDocument();
  });

  it('hides text when showText is false', () => {
    render(<LoadingSpinner showText={false} />);
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-4', 'h-4');

    rerender(<LoadingSpinner size="lg" />);
    expect(spinner).toHaveClass('w-8', 'h-8');
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<LoadingSpinner variant="success" />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('text-green-600');

    rerender(<LoadingSpinner variant="error" />);
    expect(spinner).toHaveClass('text-red-600');
  });

  it('renders fullscreen when specified', () => {
    render(<LoadingSpinner fullScreen />);
    const container = screen.getByRole('status').closest('div');
    expect(container).toHaveClass('fixed', 'inset-0', 'z-50');
  });

  it('has proper accessibility attributes', () => {
    render(<LoadingSpinner text="Loading data" />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-label', 'Loading');
    expect(screen.getByText('Loading data')).toHaveClass('sr-only');
  });
});

describe('Skeleton', () => {
  it('renders single line skeleton', () => {
    render(<Skeleton />);
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('animate-pulse', 'bg-gray-200');
  });

  it('renders multiple line skeleton', () => {
    render(<Skeleton lines={3} />);
    const skeletons = screen.getAllByRole('generic');
    expect(skeletons).toHaveLength(3);
  });

  it('applies custom height class', () => {
    render(<Skeleton height="h-8" />);
    const skeleton = screen.getByRole('generic');
    expect(skeleton).toHaveClass('h-8');
  });
});

describe('ProgressBar', () => {
  it('renders with progress value', () => {
    render(<ProgressBar progress={75} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '75');
  });

  it('clamps progress values', () => {
    const { rerender } = render(<ProgressBar progress={150} />);
    expect(screen.getByText('100%')).toBeInTheDocument();

    rerender(<ProgressBar progress={-25} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const { rerender } = render(<ProgressBar progress={50} size="sm" />);
    const bar = screen.getByRole('progressbar').closest('div');
    expect(bar).toHaveClass('h-1');

    rerender(<ProgressBar progress={50} size="lg" />);
    expect(bar).toHaveClass('h-3');
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<ProgressBar progress={50} variant="success" />);
    const bar = screen.getByRole('progressbar');
    expect(bar).toHaveClass('bg-green-600');

    rerender(<ProgressBar progress={50} variant="error" />);
    expect(bar).toHaveClass('bg-red-600');
  });

  it('hides percentage when showPercentage is false', () => {
    render(<ProgressBar progress={50} showPercentage={false} />);
    expect(screen.queryByText('50%')).not.toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(<ProgressBar progress={60} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    expect(progressBar).toHaveAttribute('aria-valuemax', '100');
    expect(progressBar).toHaveAttribute('aria-label', 'Progress: 60%');
  });
});

describe('LoadingStates', () => {
  it('renders loading state', () => {
    render(
      <LoadingStates loading={true} error={null}>
        <div>Content</div>
      </LoadingStates>
    );
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
    expect(screen.queryByText('Content')).not.toBeInTheDocument();
  });

  it('renders error state', () => {
    render(
      <LoadingStates loading={false} error="Something went wrong">
        <div>Content</div>
      </LoadingStates>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.queryByText('Content')).not.toBeInTheDocument();
  });

  it('renders children when no loading or error', () => {
    render(
      <LoadingStates loading={false} error={null}>
        <div>Content</div>
      </LoadingStates>
    );
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.queryByText('Loading data...')).not.toBeInTheDocument();
    expect(screen.queryByText('Try Again')).not.toBeInTheDocument();
  });

  it('renders custom loading component', () => {
    const customLoader = <div>Custom loader</div>;
    render(
      <LoadingStates loading={true} error={null} loadingComponent={customLoader}>
        <div>Content</div>
      </LoadingStates>
    );
    expect(screen.getByText('Custom loader')).toBeInTheDocument();
  });

  it('renders custom error component', () => {
    const customError = <div>Custom error</div>;
    render(
      <LoadingStates loading={false} error="Error" errorComponent={customError}>
        <div>Content</div>
      </LoadingStates>
    );
    expect(screen.getByText('Custom error')).toBeInTheDocument();
  });
});
