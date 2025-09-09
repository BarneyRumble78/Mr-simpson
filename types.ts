import React from 'react';

export type Subject = {
  name: string;
  // fix: Changed type from React.ReactNode to React.ReactElement for better type safety with React.cloneElement.
  // fix: Explicitly set props type to <any> to allow cloning with new props like className.
  icon: React.ReactElement<any>;
  color: string;
};

export type Difficulty = 'Beginner' | 'Intermediate' | 'Advanced';

export interface GeneratedProblem {
  problemStatement: string;
  fullSolution: string;
  codeSnippet?: string;
}

export interface FillInTheGapsProblem {
  partialSolution: string;
  missingStep: string;
}

export interface ProblemState {
    problemStatement: string;
    partialSolution: string;
    fullSolution: string;
    missingStep: string;
    codeSnippet?: string;
}

export interface UserPerformance {
    [key: string]: { // Difficulty
        correct: number;
        total: number;
    }
}

export interface UserState {
    subject: Subject | null;
    difficulty: Difficulty;
    streak: number;
    performance: UserPerformance;
}
