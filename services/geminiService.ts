import { GoogleGenAI, Type } from "@google/genai";
import type { Difficulty, GeneratedProblem } from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

export const generateProblemAndSolution = async (subject: string, difficulty: Difficulty): Promise<GeneratedProblem> => {
  const prompt = `You are an expert tutor in ${subject}. Your task is to generate a challenging, multi-step problem for a student at an ${difficulty} level.

Think step-by-step to construct the problem:
1.  First, devise a core concept to test within ${subject}.
2.  Second, frame it in a real-world or interesting scenario that requires critical thinking.
3.  Third, write a clear, unambiguous problem statement.
4.  Fourth, provide a detailed, step-by-step solution that explains the reasoning behind each step.
5.  Finally, if applicable for ${subject} (especially for Physics, Computer Science, or advanced Math), provide a small, relevant code snippet in Python that either solves the problem or visualizes a key part of it. If a code snippet isn't relevant, this can be omitted.`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            problemStatement: {
              type: Type.STRING,
              description: "The full text of the problem or question."
            },
            fullSolution: {
              type: Type.STRING,
              description: "A detailed, step-by-step solution to the problem."
            },
            codeSnippet: {
                type: Type.STRING,
                description: "An optional, relevant Python code snippet to solve or visualize the problem.",
            }
          },
          required: ["problemStatement", "fullSolution"],
        },
      },
    });

    const jsonText = response.text.trim();
    return JSON.parse(jsonText);
  } catch (error) {
    console.error("Error generating problem:", error);
    throw new Error("Failed to generate a new problem from the AI. Please check your API key and try again.");
  }
};

export const createFillInTheGaps = async (fullSolution: string) => {
  const prompt = `You are a teaching assistant creating a 'fill-in-the-gap' exercise. Here is a step-by-step solution to a problem:

--- SOLUTION START ---
${fullSolution}
--- SOLUTION END ---

Your task is to rewrite the solution, but strategically remove one single, critical step that tests a key concept. Replace the removed step with a clear placeholder like '>>> [YOUR STEP HERE] <<<'. Also, provide the exact text of the step you removed.`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            partialSolution: {
              type: Type.STRING,
              description: "The solution with one critical step removed and replaced by a placeholder."
            },
            missingStep: {
              type: Type.STRING,
              description: "The exact text of the step that was removed."
            }
          },
          required: ["partialSolution", "missingStep"],
        },
      },
    });
    
    const jsonText = response.text.trim();
    return JSON.parse(jsonText);
  } catch (error) {
    console.error("Error creating fill-in-the-gaps problem:", error);
    throw new Error("Failed to process the problem into a fill-in-the-gaps exercise.");
  }
};

export const evaluateAnswer = async (problemStatement: string, partialSolution: string, missingStep: string, userAnswer: string) => {
  const prompt = `You are a supportive and pedagogical AI tutor. A student is working on the following problem:
--- PROBLEM ---
${problemStatement}

They were given this partial solution, and were asked to fill in the blank '>>> [YOUR STEP HERE] <<<':
--- PARTIAL SOLUTION ---
${partialSolution}

The correct missing step is:
--- CORRECT STEP ---
${missingStep}

The student submitted this answer:
--- STUDENT's ANSWER ---
${userAnswer}

Please evaluate the student's answer.
- If it is correct or conceptually identical, start with "Correct!". Congratulate them and briefly explain why it's the right step.
- If it is incorrect, do NOT give them the direct answer. Instead, start with "Not quite, but you're on the right track." Provide a gentle, encouraging hint to guide them toward the correct logic or identify their misconception. Point them in the right direction without revealing the solution.
- Keep your feedback concise (2-3 sentences) and helpful.
`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
    });
    return response.text;
  } catch (error) {
    console.error("Error evaluating answer:", error);
    throw new Error("Failed to get feedback from the AI.");
  }
};
