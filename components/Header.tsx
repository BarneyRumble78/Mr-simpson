import React from 'react';

const BrainIcon = () => (
    <svg xmlns="http://www.w.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-8 w-8 text-cyan-400">
        <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v1.2a1 1 0 0 0 .94.99c.67.06 1.25.43 1.63.95 .38.52.53 1.2.37 1.87a2.5 2.5 0 0 1-4.06.91 1 1 0 0 0-1.28.3c-.18.23-.38.48-.58.74a2.5 2.5 0 0 1-4.3 0" /><path d="M14.5 2a2.5 2.5 0 0 0-2.5 2.5v1.2a1 1 0 0 1-.94.99c-.67.06-1.25.43-1.63.95-.38.52-.53 1.2-.37 1.87a2.5 2.5 0 0 0 4.06.91 1 1 0 0 1 1.28.3c.18.23.38.48.58.74a2.5 2.5 0 0 0 4.3 0" /><path d="M12 10.5v1.2a1 1 0 0 0 .94.99c.67.06 1.25.43 1.63.95 .38.52.53 1.2.37 1.87a2.5 2.5 0 0 1-4.06.91 1 1 0 0 0-1.28.3c-.18.23-.38.48-.58.74a2.5 2.5 0 0 1-4.3 0" /><path d="M12 22a2.5 2.5 0 0 1-2.5-2.5v-1.2a1 1 0 0 0-.94-.99c-.67-.06-1.25-.43-1.63-.95-.38-.52-.53-1.2-.37-1.87a2.5 2.5 0 0 1 4.06-.91 1 1 0 0 0 1.28-.3c.18-.23.38-.48.58-.74a2.5 2.5 0 0 1 4.3 0" /><path d="M17 21.5a2.5 2.5 0 0 0-2.5-2.5v-1.2a1 1 0 0 1 .94-.99c.67-.06 1.25-.43 1.63-.95 .38-.52.53-1.2.37-1.87a2.5 2.5 0 0 0-4.06-.91 1 1 0 0 1-1.28-.3c-.18-.23-.38-.48-.58-.74a2.5 2.5 0 0 0-4.3 0" /><path d="M7 21.5a2.5 2.5 0 0 1 2.5-2.5v-1.2a1 1 0 0 0-.94-.99c-.67-.06-1.25-.43-1.63-.95-.38-.52-.53-1.2-.37-1.87a2.5 2.5 0 0 1 4.06-.91 1 1 0 0 0 1.28-.3c.18-.23.38-.48.58-.74a2.5 2.5 0 0 1 4.3 0" />
    </svg>
);

const FireIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6 text-orange-400">
        <path d="M14.5 9.5a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z" /><path d="M12 18c4 0 6-2 6-4 0-2-2-4-4-4-2 0-4 2-6 4-2 2-2 4 0 4Z" /><path d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2Z" /><path d="M18.5 12.5a1.5 1.5 0 0 0 0-3" /><path d="M5.5 12.5a1.5 1.5 0 0 1 0-3" />
    </svg>
);


interface HeaderProps {
    streak: number;
}

const Header: React.FC<HeaderProps> = ({ streak }) => {
  return (
    <header className="w-full bg-gray-900/80 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-10">
      <div className="container mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <BrainIcon />
            <h1 className="ml-3 text-2xl font-bold tracking-tight text-white">Synapse</h1>
          </div>
          {streak > 0 && (
            <div className="flex items-center gap-2" title={`${streak} problem streak!`}>
              <FireIcon />
              <span className="text-xl font-bold text-orange-400">{streak}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
