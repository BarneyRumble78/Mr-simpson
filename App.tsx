import React from 'react';
import SubjectSelector from './components/SubjectSelector';
import LearningCanvas from './components/LearningCanvas';
import Header from './components/Header';
import { useUserState } from './hooks/useUserState';

const App: React.FC = () => {
  const { 
    subject, 
    difficulty, 
    streak,
    startLearning, 
    goBack,
    changeDifficulty,
    recordSuccess,
    resetStreak,
  } = useUserState();

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans flex flex-col">
      <Header streak={streak} />
      <main className="flex-grow container mx-auto p-4 md:p-8 flex flex-col items-center justify-center">
        {!subject ? (
          <SubjectSelector onStart={startLearning} initialDifficulty={difficulty} />
        ) : (
          <LearningCanvas 
            subject={subject} 
            difficulty={difficulty} 
            streak={streak}
            onBack={goBack} 
            onCorrect={recordSuccess}
            onStuck={resetStreak}
            onChangeDifficulty={changeDifficulty}
          />
        )}
      </main>
      <footer className="text-center p-4 text-xs text-gray-500">
        <p>Synapse: An AI-Powered Blueprint for Next-Generation Problem-Based Learning</p>
      </footer>
    </div>
  );
};

export default App;
