import { useState, useEffect, useCallback } from 'react';
import type { Subject, Difficulty, UserState, UserPerformance } from '../types';

const APP_STATE_KEY = 'synapse-user-state';

const initialPerformance: UserPerformance = {
    Beginner: { correct: 0, total: 0 },
    Intermediate: { correct: 0, total: 0 },
    Advanced: { correct: 0, total: 0 },
};

const getInitialState = (): UserState => {
    try {
        const item = window.localStorage.getItem(APP_STATE_KEY);
        if (item) {
            const parsed = JSON.parse(item);
            // Ensure performance object has all keys, in case format changes
            return {
                ...parsed,
                subject: null, // Always start at subject selection screen
                performance: { ...initialPerformance, ...parsed.performance },
            };
        }
    } catch (error) {
        console.warn("Error reading localStorage key “" + APP_STATE_KEY + "”:", error);
    }

    return {
        subject: null,
        difficulty: 'Intermediate',
        streak: 0,
        performance: initialPerformance,
    };
};


export const useUserState = () => {
    const [userState, setUserState] = useState<UserState>(getInitialState);
    
    useEffect(() => {
        try {
            // Create a version to save, excluding non-serializable parts of subject
            const stateToSave = {
                ...userState,
                subject: userState.subject ? { name: userState.subject.name, color: userState.subject.color } : null
            };
            window.localStorage.setItem(APP_STATE_KEY, JSON.stringify(stateToSave));
        } catch (error) {
            console.warn("Error setting localStorage key “" + APP_STATE_KEY + "”:", error);
        }
    }, [userState]);

    const startLearning = useCallback((subject: Subject, difficulty: Difficulty) => {
        setUserState(prev => ({ ...prev, subject, difficulty }));
    }, []);

    const goBack = useCallback(() => {
        setUserState(prev => ({ ...prev, subject: null }));
    }, []);
    
    const changeDifficulty = useCallback((difficulty: Difficulty) => {
        setUserState(prev => ({...prev, difficulty}));
    }, []);

    const recordSuccess = useCallback((difficulty: Difficulty) => {
        setUserState(prev => {
            const newPerformance = { ...prev.performance };
            newPerformance[difficulty].correct += 1;
            newPerformance[difficulty].total += 1;
            
            return {
                ...prev,
                streak: prev.streak + 1,
                performance: newPerformance,
            };
        });
    }, []);

    const resetStreak = useCallback(() => {
        setUserState(prev => ({ ...prev, streak: 0 }));
    }, []);

    return {
        ...userState,
        startLearning,
        goBack,
        changeDifficulty,
        recordSuccess,
        resetStreak,
    };
};
