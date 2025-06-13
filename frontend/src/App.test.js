import { render, screen } from '@testing-library/react';
import App from './App';

test('renders microphone button', () => {
  render(<App />);
  const micButton = screen.getByAltText(/Mic Button/i);
  expect(micButton).toBeInTheDocument();
});