import React, { useState } from 'react';
import type { Subject, Difficulty } from '../types';
import Button from './Button';

const subjects: Subject[] = [
  { 
    name: 'Mathematics', 
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path><path d="m7 13 2.5 2.5 5-5"></path></svg>
    ), 
    color: 'text-emerald-400' 
  },
  { 
    name: 'Physics', 
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2.5c2.4 0 4.7.9 6.5 2.5S21 8.6 21 11c0 2.4-.9 4.7-2.5 6.5S15.4 20 13 20c-2.4 0-4.7-.9-6.5-2.5S4 13.4 4 11c0-2.4.9-4.7 2.5-6.5S8.6 2 11 2m0-1.5c-4.8 0-8.8 3.6-9.5 8.2-1 5.4 2.8 10.3 8 10.3 4.4 0 8-3.6 8-8s-3.6-8-8-8z"/><path d="M12 4.4c1.2 1.2 1.2 3.1 0 4.2-1.2 1.2-3.1 1.2-4.2 0-1.2-1.2-1.2-3.1 0-4.2 1.1-1.1 3-1.1 4.2 0z"/></svg>
    ), 
    color: 'text-sky-400' 
  },
  { 
    name: 'Computer Science', 
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
    ),
    color: 'text-violet-400' 
  },
];

const difficulties: Difficulty[] = ['Beginner', 'Intermediate', 'Advanced'];

interface SubjectSelectorProps {
  onStart: (subject: Subject, difficulty: Difficulty) => void;
  initialDifficulty: Difficulty;
}

const SubjectSelector: React.FC<SubjectSelectorProps> = ({ onStart, initialDifficulty }) => {
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>(initialDifficulty);

  const handleStart = () => {
    if (selectedSubject) {
      onStart(selectedSubject, selectedDifficulty);
    }
  };

  return (
    <div className="w-full max-w-4xl text-center flex flex-col items-center">
      <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">Welcome to Synapse</h2>
      <p className="text-lg text-gray-400 mb-8">Choose a subject to begin your personalized learning journey.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-8">
        {subjects.map((subject) => (
          <button
            key={subject.name}
            onClick={() => setSelectedSubject(subject)}
            className={`relative p-8 rounded-lg border-2 transition-all duration-300 transform hover:-translate-y-1 ${
              selectedSubject?.name === subject.name ? 'border-cyan-400 bg-gray-800 scale-105' : 'border-gray-700 bg-gray-800/50 hover:border-gray-500'
            }`}
          >
            {/* fix: Removed type assertion as `subject.icon` is now correctly typed as React.ReactElement. */}
            <div className={`mx-auto mb-4 h-12 w-12 ${subject.color}`}>{React.cloneElement(subject.icon, { className: "h-full w-full"})}</div>
            <h3 className="text-xl font-semibold text-white">{subject.name}</h3>
             {selectedSubject?.name === subject.name && (
                <div className="absolute -top-3 -right-3 h-7 w-7 bg-cyan-400 rounded-full flex items-center justify-center">
                   <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-900" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                </div>
            )}
          </button>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 mb-8">
        <label htmlFor="difficulty" className="text-gray-300 font-medium">Select Difficulty:</label>
        <div className="relative">
          <select
            id="difficulty"
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value as Difficulty)}
            className="appearance-none bg-gray-800 border-2 border-gray-700 rounded-md py-2 pl-3 pr-10 text-white focus:outline-none focus:border-cyan-500 transition"
          >
            {difficulties.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
             <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
          </div>
        </div>
      </div>

      <Button onClick={handleStart} disabled={!selectedSubject}>
        Start Learning
      </Button>
    </div>
  );
};

export default SubjectSelector;
