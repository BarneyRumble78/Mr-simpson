import React, { useState, useEffect, useCallback } from 'react';
import { generateProblemAndSolution, createFillInTheGaps, evaluateAnswer } from '../services/geminiService';
import type { Subject, Difficulty, ProblemState } from '../types';
import LoadingSpinner from './LoadingSpinner';
import Button from './Button';

interface LearningCanvasProps {
  subject: Subject;
  difficulty: Difficulty;
  streak: number;
  onBack: () => void;
  onCorrect: (difficulty: Difficulty) => void;
  onStuck: () => void;
  onChangeDifficulty: (newDifficulty: Difficulty) => void;
}

const difficulties: Difficulty[] = ['Beginner', 'Intermediate', 'Advanced'];
const CORRECT_STREAK_TO_LEVEL_UP = 3;

const LearningCanvas: React.FC<LearningCanvasProps> = ({ subject, difficulty, streak, onBack, onCorrect, onStuck, onChangeDifficulty }) => {
  const [problem, setProblem] = useState<ProblemState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [showFullSolution, setShowFullSolution] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [showLevelUp, setShowLevelUp] = useState(false);

  const fetchNewProblem = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setProblem(null);
    setFeedback(null);
    setUserAnswer('');
    setShowFullSolution(false);
    setIsCorrect(false);
    setShowLevelUp(false);

    try {
      const generated = await generateProblemAndSolution(subject.name, difficulty);
      const gaps = await createFillInTheGaps(generated.fullSolution);
      setProblem({
        problemStatement: generated.problemStatement,
        fullSolution: generated.fullSolution,
        partialSolution: gaps.partialSolution,
        missingStep: gaps.missingStep,
        codeSnippet: generated.codeSnippet,
      });
    } catch (e: any) {
      setError(e.message || 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [subject.name, difficulty]);

  useEffect(() => {
    fetchNewProblem();
  }, [fetchNewProblem]);

  const handleSubmit = async () => {
    if (!userAnswer.trim() || !problem) return;
    setIsEvaluating(true);
    setFeedback(null);
    try {
      const result = await evaluateAnswer(problem.problemStatement, problem.partialSolution, problem.missingStep, userAnswer);
      setFeedback(result);
      if (result.toLowerCase().startsWith('correct')) {
        setIsCorrect(true);
        onCorrect(difficulty);

        // Adaptive learning logic
        const currentDifficultyIndex = difficulties.indexOf(difficulty);
        if (streak + 1 >= CORRECT_STREAK_TO_LEVEL_UP && currentDifficultyIndex < difficulties.length - 1) {
            setShowLevelUp(true);
        }
      }
    } catch (e: any) {
      setFeedback(e.message || 'Error evaluating your answer.');
    } finally {
      setIsEvaluating(false);
    }
  };
  
  const handleShowSolution = () => {
      setShowFullSolution(true);
      onStuck(); // Reset streak
  }
  
  const handleLevelUp = () => {
      const currentDifficultyIndex = difficulties.indexOf(difficulty);
      const nextDifficulty = difficulties[currentDifficultyIndex + 1];
      if (nextDifficulty) {
          onChangeDifficulty(nextDifficulty);
      }
      setShowLevelUp(false);
  }

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center"><LoadingSpinner /> <p className="mt-4 text-gray-400">Generating your next challenge...</p></div>;
    }
    if (error) {
      return <div aria-live="assertive" className="text-center text-red-400 bg-red-900/50 p-6 rounded-lg">
        <h3 className="font-bold text-lg mb-2">An Error Occurred</h3>
        <p>{error}</p>
        <Button onClick={fetchNewProblem} className="mt-4">Try Again</Button>
      </div>;
    }
    if (problem) {
      return (
        <div className="space-y-6 w-full">
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-400 mb-2">Problem</h3>
                <p className="text-gray-200 whitespace-pre-wrap">{problem.problemStatement}</p>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-400 mb-2">Partial Solution</h3>
                <p className="text-gray-300 whitespace-pre-wrap">{problem.partialSolution}</p>
            </div>
          
            {!isCorrect && !showFullSolution && (
              <div className="space-y-4">
                <textarea
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Enter the missing step here..."
                  className="w-full p-4 bg-gray-900 border-2 border-gray-600 rounded-lg focus:outline-none focus:border-cyan-500 transition text-gray-200"
                  rows={4}
                  aria-label="Your answer for the missing step"
                />
                <Button onClick={handleSubmit} disabled={isEvaluating} className="w-full sm:w-auto">
                  {isEvaluating ? <><LoadingSpinner small={true}/> Evaluating...</> : 'Submit Answer'}
                </Button>
              </div>
            )}

            {feedback && (
                <div aria-live="polite" className={`p-4 rounded-lg border ${isCorrect ? 'bg-green-900/50 border-green-700 text-green-300' : 'bg-yellow-900/50 border-yellow-700 text-yellow-300'}`}>
                    <p className="font-semibold">{isCorrect ? 'Feedback' : 'Hint'}</p>
                    <p className="whitespace-pre-wrap">{feedback}</p>
                </div>
            )}
            
            {showLevelUp && (
                <div className="p-4 rounded-lg bg-cyan-900/50 border border-cyan-700 text-center">
                    <p className="font-semibold text-cyan-300 mb-2">Great job! You've answered {CORRECT_STREAK_TO_LEVEL_UP} in a row correctly.</p>
                    <p className="text-gray-300 mb-4">Ready to try a more challenging problem?</p>
                    <Button onClick={handleLevelUp}>Go to {difficulties[difficulties.indexOf(difficulty) + 1]}</Button>
                </div>
            )}

            {showFullSolution && (
                 <div className="bg-gray-800 p-6 rounded-lg border border-cyan-700 space-y-4">
                    <div>
                        <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-400 mb-2">Complete Solution</h3>
                        <p className="text-gray-200 whitespace-pre-wrap">{problem.fullSolution}</p>
                    </div>
                    {problem.codeSnippet && (
                        <div>
                            <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-400 mb-2">Code Example</h3>
                            <pre className="bg-gray-900 p-4 rounded-md text-sm text-gray-300 overflow-x-auto">
                                <code>{problem.codeSnippet}</code>
                            </pre>
                        </div>
                    )}
                </div>
            )}
          
            <div className="flex flex-wrap gap-4 pt-4">
                {isCorrect && !showLevelUp && <Button onClick={fetchNewProblem}>Next Problem</Button>}
                {!showFullSolution && !isCorrect && <Button onClick={handleShowSolution} variant="secondary">I'm Stuck, Show Solution</Button>}
            </div>
        </div>
      );
    }
    return null;
  };


  return (
    <div className="w-full max-w-4xl p-4 md:p-8 bg-gray-800/50 rounded-xl border border-gray-700 shadow-2xl flex flex-col">
       <div className="flex justify-between items-center mb-6">
            <div>
                <h2 className="text-2xl font-bold text-white">{subject.name}</h2>
                <p className="text-gray-400">{difficulty} Level</p>
            </div>
            <Button onClick={onBack} variant="secondary">Change Subject</Button>
       </div>
       <div className="flex-grow flex items-center justify-center">
        {renderContent()}
       </div>
    </div>
  );
};

export default LearningCanvas;
