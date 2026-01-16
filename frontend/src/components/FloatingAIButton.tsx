import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { todoAPI } from '@/lib/todoAPI';
import { Todo } from '@/types/todo';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const TodoChatbot = ({
  isOpen,
  onClose,
  onCreateTask,
  onDeleteTask,
  onTaskUpdated
}: {
  isOpen: boolean;
  onClose: () => void;
  onCreateTask: (taskData: { title: string; description?: string; due_date?: string; priority?: 'low' | 'medium' | 'high' }) => void;
  onDeleteTask?: () => void;
  onTaskUpdated?: () => void;
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: `I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!`,
      sender: 'bot',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to check if the message is a request to view tasks
  const isViewTaskRequest = (message: string): boolean => {
    const lowerMessage = message.toLowerCase().trim();
    const viewRequests = [
      "show me my tasks", "view task list", "show all tasks", "what tasks do i have?",
      "list my tasks", "display my todo list", "see my tasks", "check my tasks",
      "get my tasks", "show my to-do list", "view my tasks", "show task list",
      "view all tasks", "what do i have to do?", "show me tasks", "list tasks"
    ];
    return viewRequests.includes(lowerMessage);
  };

  // Function to extract task information from user message for creation
  const extractTaskInfo = (message: string): { title: string; description?: string; due_date?: string; priority?: 'low' | 'medium' | 'high' } | null => {
    // First check if this is a view request - if so, don't extract task info
    if (isViewTaskRequest(message)) {
      return null; // This is a view request, not a create request
    }

    // Look for common patterns in task requests
    const titleMatch = message.match(/(?:title:|task:|to do:|to-do:)\s*(.*?)(?:,|$)/i);
    const descriptionMatch = message.match(/(?:description:|desc:)\s*(.*?)(?:,|$)/i);
    const dueDateMatch = message.match(/(?:due date:|by:|until:)\s*(\d{4}-\d{2}-\d{2}|today|tomorrow|\d+\s*(?:day|week|month))/i);
    const priorityMatch = message.match(/(?:priority:|urgency:)\s*(low|medium|high)/i);

    // If no structured format found, try to extract from free text
    if (!titleMatch) {
      // Simple extraction: take the first sentence or up to 50 characters as title
      const text = message.replace(/(hi|hello|hey|please|can you|could you|create|make|add)\s*/gi, '');
      const title = text.substring(0, 50).trim();
      // Don't create tasks for view-related phrases
      if (title && !title.toLowerCase().includes('show') && !title.toLowerCase().includes('view') &&
          !title.toLowerCase().includes('list') && !title.toLowerCase().includes('task') &&
          !title.toLowerCase().includes('what') && !title.toLowerCase().includes('do')) {
        return {
          title: title.charAt(0).toUpperCase() + title.slice(1),
          description: message.length > 50 ? message.substring(50) : undefined,
          priority: priorityMatch ? priorityMatch[1] as 'low' | 'medium' | 'high' : 'medium'
        };
      }
      return null;
    }

    return {
      title: titleMatch[1].trim() || 'Untitled Task',
      description: descriptionMatch ? descriptionMatch[1].trim() : undefined,
      due_date: dueDateMatch ? dueDateMatch[1].toLowerCase() : undefined,
      priority: priorityMatch ? priorityMatch[1] as 'low' | 'medium' | 'high' : 'medium'
    };
  };

  // Function to extract task identification for deletion
  const extractTaskForDeletion = (message: string): { title?: string; taskId?: string } | null => {
    // Look for deletion keywords and task identifiers
    const deleteKeywords = ['delete', 'remove', 'cancel', 'complete', 'done'];
    const hasDeleteKeyword = deleteKeywords.some(keyword =>
      message.toLowerCase().includes(keyword)
    );

    if (!hasDeleteKeyword) {
      return null;
    }

    // Look for the most likely task title patterns
    // Try to extract the full task title after "delete" or "remove"
    const fullTitleMatch = message.match(/(?:delete|remove|cancel)\s+(?:the\s+)?(.+?)(?:\.|$|,|and|please|now|from|my)/i);
    if (fullTitleMatch) {
      return { title: fullTitleMatch[1].trim() };
    }

    // Extract task by title with more variations
    const titleMatch = message.match(/(?:task|called|named|titled|the)\s+(.*?)(?:\.|$|,|and|from|my)/i);
    if (titleMatch) {
      return { title: titleMatch[1].trim() };
    }

    // Extract any sequence after delete/remove that looks like a task title
    const simpleMatch = message.match(/(?:delete|remove|cancel)\s+(.+)$/i);
    if (simpleMatch) {
      return { title: simpleMatch[1].trim() };
    }

    // Extract task by ID if mentioned
    const idMatch = message.match(/(?:id|number)\s*(\w+)/i);
    if (idMatch) {
      return { taskId: idMatch[1].trim() };
    }

    // For simple deletion requests like "delete the first task" or "remove my shopping task"
    const text = message.replace(/(please|can you|could you|now|just)\s*/gi, '');
    const words = text.split(/\s+/);
    // Look for task-like phrases (skip common words)
    const taskIndicators = words.filter(word =>
      word.length > 2 &&
      !['the', 'my', 'a', 'an', 'and', 'or', 'but', 'for', 'to', 'of', 'in', 'on', 'is', 'are', 'was', 'were'].includes(word.toLowerCase())
    );

    if (taskIndicators.length > 0) {
      // Join multiple words to form a more complete title
      return { title: taskIndicators.join(' ') }; // Take all potential task indicators
    }

    return null;
  };

  // Function to extract task information for updates
  const extractTaskForUpdate = (message: string): { title?: string; updates: { title?: string; description?: string; priority?: 'low' | 'medium' | 'high'; status?: 'pending' | 'completed' } } | null => {
    // Look for update keywords
    const updateKeywords = ['update', 'change', 'modify', 'edit', 'adjust', 'set', 'make'];
    const hasUpdateKeyword = updateKeywords.some(keyword =>
      message.toLowerCase().includes(keyword)
    );

    if (!hasUpdateKeyword) {
      return null;
    }

    // Extract what needs to be updated
    const updates: { title?: string; description?: string; priority?: 'low' | 'medium' | 'high'; status?: 'pending' | 'completed' } = {};

    // Extract title using multiple patterns to handle different formats
    let taskTitle: string | undefined = undefined;

    // Pattern 1: "Update [task title] to [value]" or "Change [task title] to [value]"
    const updatePatternMatch = message.match(/(?:update|change|modify|edit|adjust|set|make)\s+(.+?)\s+(?:to|as|into|is)\s+/i);
    if (updatePatternMatch) {
      taskTitle = updatePatternMatch[1].trim();
      // Remove "task" if it's part of the title (e.g., "Buy milk task")
      taskTitle = taskTitle.replace(/\s+task$/i, '').trim();
    }

    // Pattern 2: "[task title] called/named/titled [value]"
    if (!taskTitle) {
      const titleMatch = message.match(/(?:task|called|named|titled)\s+(.*?)(?:\.|$|,|and|to|so)/i);
      taskTitle = titleMatch ? titleMatch[1].trim() : undefined;
    }

    // Extract new title
    const newTitleMatch = message.match(/(?:title|name)\s+(.*?)(?:\.|$|,|and)/i);
    if (newTitleMatch) {
      updates.title = newTitleMatch[1].trim();
    }

    // Extract priority - look for priority values in the message
    // Handles "to high priority", "to high", "high priority", etc.
    const priorityPatterns = [
      /(?:to|as|into|is)\s+(low|medium|high)\s+priority/i,
      /(?:to|as|into|is)\s+(low|medium|high)(?:\s|$|\.|,)/i,
      /(low|medium|high)\s+priority/i,
    ];

    for (const pattern of priorityPatterns) {
      const priorityMatch = message.match(pattern);
      if (priorityMatch) {
        updates.priority = priorityMatch[1] as 'low' | 'medium' | 'high';
        break;
      }
    }

    // Extract description
    const descMatch = message.match(/(?:description|desc|details?)\s+(.*?)(?:\.|$|,|and)/i);
    if (descMatch) {
      updates.description = descMatch[1].trim();
    }

    // Extract status
    const statusMatch = message.match(/(?:status|to|as)\s+(completed|done|finished|pending|active)/i);
    if (statusMatch) {
      const statusText = statusMatch[1].toLowerCase();
      updates.status = statusText === 'completed' || statusText === 'done' || statusText === 'finished' ? 'completed' : 'pending';
    }

    // If we have updates, return them
    if (Object.keys(updates).length > 0 || taskTitle) {
      return { title: taskTitle, updates };
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Check for gratitude expressions first (exact phrase matching to avoid conflicts with other commands)
    const inputLower = inputValue.toLowerCase().trim();

    // More specific gratitude phrases to avoid conflicts with task commands
    const gratitudeIndicators = [
      "thank you", "thanks", "thank you so much", "thanks for your help",
      "thank you for helping", "appreciate it", "you're awesome", "grateful",
      "many thanks", "much appreciated", "cheers", "ta", "thnx", "thanx"
    ];

    // Check for abusive language/profanity
    const abusiveLanguageIndicators = [
      "fuck", "shit", "damn", "hell", "bitch", "asshole", "stupid", "dumb",
      "idiot", "crap", "bullshit", "nonsense", "garbage", "meaningless",
      "waste of time", "pointless", "useless", "rubbish", "nonsensical",
      "fool", "idiotic", "stupidity", "dumbass", "retard", "moronic", "dumbfuck",
      "jackass", "ass", "suck", "sucks", "sucker", "losers", "loser", "hate",
      "hates", "hated", "stupidly", "dumbly", "idiotically", "worthless",
      "pathetic", "ridiculous", "ridicule", "mock", "mocking", "laughable",
      "mental", "psycho", "crazy", "insane", "nuts", "bonkers", "loony", "lunatic",
      "shutup", "shut up", "f*ck", "f--k", "screw you", "go away", "stop"
    ];

    const hasAbusiveLanguage = abusiveLanguageIndicators.some(abusive =>
      inputLower.includes(abusive)
    );

    if (hasAbusiveLanguage) {
      // Respond to abusive language without creating a task
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        sender: 'user',
        timestamp: new Date(),
      };

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!",
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage, botMessage]);
      setInputValue('');
      setIsLoading(false);
      return;
    }

    // Check if the message is a gratitude expression (exact match or starts/ends with gratitude)
    const isGratitude = gratitudeIndicators.some(gratitude =>
      inputLower === gratitude ||
      inputLower.startsWith(gratitude + " ") ||
      inputLower.endsWith(" " + gratitude) ||
      inputLower.includes(" " + gratitude + " ")
    );

    if (isGratitude) {
      // Respond to gratitude without creating a task
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        sender: 'user',
        timestamp: new Date(),
      };

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "You're welcome! I'm glad I was able to help you.",
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage, botMessage]);
      setInputValue('');
      setIsLoading(false);
      return;
    }

    // Check for emotional expressions like "I like you", "I love you", etc.
    const emotionalExpressions = [
      "i like you",
      "i love you",
      "i adore you",
      "i appreciate you",
      "you are nice",
      "you're nice",
      "you are great",
      "you're great",
      "you are awesome",
      "you're awesome",
      "you are cool",
      "you're cool",
      "you are amazing",
      "you're amazing",
      "you are wonderful",
      "you're wonderful",
      "i enjoy talking to you",
      "i like talking to you"
    ];

    const isEmotionalExpression = emotionalExpressions.some(emotion =>
      inputLower === emotion ||
      inputLower.startsWith(emotion + " ") ||
      inputLower.endsWith(" " + emotion) ||
      inputLower.includes(" " + emotion + " ")
    );

    if (isEmotionalExpression) {
      // Respond to emotional expressions without creating a task
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputValue,
        sender: 'user',
        timestamp: new Date(),
      };

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!",
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage, botMessage]);
      setInputValue('');
      setIsLoading(false);
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Check if this is a task update request
      const updateInfo = extractTaskForUpdate(inputValue);

      if (updateInfo) {
        try {
          // Get all tasks to find the one to update
          const allTasks = await todoAPI.getAll();

          // Find the task to update by title or other criteria
          let taskToUpdate = null;

          if (updateInfo.title) {
            // Use fuzzy matching to find the best match
            const searchTerm = updateInfo.title.toLowerCase().trim();

            // First try exact match
            taskToUpdate = allTasks.find((task: any) =>
              task.title.toLowerCase().trim() === searchTerm
            );

            // If no exact match, try partial match
            if (!taskToUpdate) {
              taskToUpdate = allTasks.find((task: any) =>
                task.title.toLowerCase().includes(searchTerm)
              );
            }

            // If still no match, try matching individual words with a more sophisticated approach
            if (!taskToUpdate) {
              const searchWords = searchTerm.split(/\s+/);

              // Find the task with the highest word match ratio
              let bestMatch = null;
              let bestScore = 0;

              for (const task of allTasks) {
                const taskTitle = task.title.toLowerCase();

                // Count exact word matches
                const matches = searchWords.filter(word => taskTitle.includes(word));
                const exactMatches = matches.length;

                // Calculate score based on percentage of matched words
                const score = exactMatches > 0 ? exactMatches / searchWords.length : 0;

                // Also consider if the search term is contained in the task title
                const containsSearch = taskTitle.includes(searchTerm) ? 0.5 : 0;
                const combinedScore = score + containsSearch;

                if (combinedScore > bestScore && combinedScore > 0.3) { // Require at least 30% match
                  bestScore = combinedScore;
                  bestMatch = task;
                }
              }

              taskToUpdate = bestMatch;
            }
          }

          if (taskToUpdate) {
            // Update the task
            const updatedTask = await todoAPI.updateTask(taskToUpdate.id, updateInfo.updates);

            // Notify parent component
            if (typeof onTaskUpdated === 'function') {
              onTaskUpdated();
            }

            // Bot confirms task update
            const botMessage: Message = {
              id: (Date.now() + 1).toString(),
              content: `✏️ Successfully updated task: "${taskToUpdate.title}". Changes have been applied to your task.`,
              sender: 'bot',
              timestamp: new Date(),
            };

            setMessages(prev => [...prev, botMessage]);
          } else {
            // Task not found
            const botMessage: Message = {
              id: (Date.now() + 1).toString(),
              content: `I couldn't find a task matching your description. Could you be more specific?`,
              sender: 'bot',
              timestamp: new Date(),
            };

            setMessages(prev => [...prev, botMessage]);
          }
        } catch (updateError) {
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            content: 'Sorry, I encountered an error updating your task. Please try again.',
            sender: 'bot',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      } else {
        // Check if this is a task deletion request
        const deletionInfo = extractTaskForDeletion(inputValue);

        if (deletionInfo) {
          try {
            // Get all tasks to find the one to delete
            const allTasks = await todoAPI.getAll();

            // Find the task to delete by title or other criteria
            let taskToDelete = null;

            if (deletionInfo.title) {
              // Use fuzzy matching to find the best match
              const searchTerm = deletionInfo.title.toLowerCase().trim();

              // First try exact match
              taskToDelete = allTasks.find((task: any) =>
                task.title.toLowerCase().trim() === searchTerm
              );

              // If no exact match, try partial match
              if (!taskToDelete) {
                taskToDelete = allTasks.find((task: any) =>
                  task.title.toLowerCase().includes(searchTerm)
                );
              }

              // If still no match, try matching individual words with a more sophisticated approach
              if (!taskToDelete) {
                const searchWords = searchTerm.split(/\s+/);

                // Find the task with the highest word match ratio
                let bestMatch = null;
                let bestScore = 0;

                for (const task of allTasks) {
                  const taskTitle = task.title.toLowerCase();

                  // Count exact word matches
                  const matches = searchWords.filter(word => taskTitle.includes(word));
                  const exactMatches = matches.length;

                  // Calculate score based on percentage of matched words
                  const score = exactMatches > 0 ? exactMatches / searchWords.length : 0;

                  // Also consider if the search term is contained in the task title
                  const containsSearch = taskTitle.includes(searchTerm) ? 0.5 : 0;
                  const combinedScore = score + containsSearch;

                  if (combinedScore > bestScore && combinedScore > 0.3) { // Require at least 30% match
                    bestScore = combinedScore;
                    bestMatch = task;
                  }
                }

                taskToDelete = bestMatch;
              }
            } else if (deletionInfo.taskId) {
              // Find task by ID
              taskToDelete = allTasks.find((task: any) => task.id === deletionInfo.taskId);
            }

            if (taskToDelete) {
              try {
                // Delete the task
                await todoAPI.deleteTask(taskToDelete.id);

                // Notify parent component
                if (typeof onDeleteTask === 'function') {
                  // Call the refresh function to update the task list
                  onDeleteTask();

                  // Small delay to ensure UI updates
                  setTimeout(() => {
                    console.log('Task deletion refresh triggered');
                  }, 100);
                } else {
                  console.warn('onDeleteTask callback is not a function');
                }

                // Bot confirms task deletion
                const botMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: `🗑️ Successfully deleted task: "${taskToDelete.title}". Refreshing your task list now...`,
                  sender: 'bot',
                  timestamp: new Date(),
                };

                setMessages(prev => [...prev, botMessage]);
              } catch (specificDeleteError: any) {
                console.error('Error deleting specific task:', specificDeleteError);

                let errorMessageContent = 'Sorry, I encountered an error deleting your task. Please try again.';

                // Check if it's a 404 (task not found) or 403 (permission denied)
                if (specificDeleteError.response?.status === 404) {
                  errorMessageContent = `The task "${taskToDelete.title}" could not be found. It may have been deleted already.`;
                } else if (specificDeleteError.response?.status === 403) {
                  errorMessageContent = `You don't have permission to delete the task "${taskToDelete.title}".`;
                }

                const errorMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: errorMessageContent,
                  sender: 'bot',
                  timestamp: new Date(),
                };
                setMessages(prev => [...prev, errorMessage]);
              }
            } else {
              // Task not found - provide a list of available tasks to help user
              const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                content: `I couldn't find a task matching your description. Available tasks: ${allTasks.slice(0, 5).map((t: any) => `"${t.title}"`).join(', ')}. Could you be more specific?`,
                sender: 'bot',
                timestamp: new Date(),
              };

              setMessages(prev => [...prev, botMessage]);
            }
          } catch (deleteError) {
            console.error('General error in deletion process:', deleteError);

            const errorMessage: Message = {
              id: (Date.now() + 1).toString(),
              content: 'Sorry, I encountered an error processing your deletion request. Please try again.',
              sender: 'bot',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
          }
        } else {
          // Check if this is a view task request
          if (isViewTaskRequest(inputValue)) {
            // Fetch and display all tasks
            try {
              const allTasks = await todoAPI.getAll();

              if (allTasks && allTasks.length > 0) {
                // Create a table-like format with emojis
                let taskListResponse = `📋 *Here are your tasks:*\n\n`;
                taskListResponse += "```\n";
                taskListResponse += `#${' '.repeat(3)}Task${' '.repeat(24)}Status${' '.repeat(10)}Priority${' '.repeat(8)}Due Date${' '.repeat(10)}\n`;
                taskListResponse += "-".repeat(70) + "\n";

                allTasks.forEach((task: any, index: number) => {
                  const status = task.status || 'pending';
                  const priority = task.priority || 'medium';
                  const dueDate = task.due_date ? task.due_date : 'None';

                  // Add status emoji
                  const statusEmoji = status.toLowerCase() === 'completed' ? '✅' : '⏳';

                  // Add priority emoji
                  let priorityEmoji = '';
                  if (priority.toLowerCase() === 'high') {
                    priorityEmoji = '🔴';
                  } else if (priority.toLowerCase() === 'medium') {
                    priorityEmoji = '🟡';
                  } else if (priority.toLowerCase() === 'low') {
                    priorityEmoji = '🟢';
                  }

                  const taskTitle = task.title.substring(0, 23); // Limit title length
                  const paddedIndex = (index + 1).toString().padEnd(3);
                  const paddedTitle = taskTitle.padEnd(25);
                  const capitalizedStatus = status.charAt(0).toUpperCase() + status.slice(1);
                  const paddedStatusText = capitalizedStatus.padEnd(12);
                  const paddedPriority = priority.padEnd(8);
                  const paddedDueDate = dueDate.padEnd(12);

                  taskListResponse += `${paddedIndex}${paddedTitle}${statusEmoji} ${paddedStatusText}${priorityEmoji} ${paddedPriority}${paddedDueDate}\n`;
                });

                taskListResponse += "```\n\n";
                taskListResponse += "💡 *Tip: You can add, update, or delete tasks by telling me what you'd like to do!*";

                const botMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: taskListResponse,
                  sender: 'bot',
                  timestamp: new Date(),
                };

                setMessages(prev => [...prev, botMessage]);
              } else {
                const botMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: "You don't have any tasks yet. You can add a new task by telling me what you'd like to do!",
                  sender: 'bot',
                  timestamp: new Date(),
                };

                setMessages(prev => [...prev, botMessage]);
              }
            } catch (viewError) {
              const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                content: 'Sorry, I encountered an error retrieving your tasks. Please try again.',
                sender: 'bot',
                timestamp: new Date(),
              };
              setMessages(prev => [...prev, errorMessage]);
            }
          } else {
            // Check if this is a task creation request
            const taskInfo = extractTaskInfo(inputValue);

            if (taskInfo) {
              // Create the task
              try {
                const newTask = await todoAPI.createTask({
                  title: taskInfo.title,
                  description: taskInfo.description,
                  due_date: taskInfo.due_date,
                  priority: taskInfo.priority
                });

                // Notify parent component
                if (typeof onCreateTask === 'function') {
                  onCreateTask(taskInfo);
                }

                // Bot confirms task creation
                const botMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: `✅ Successfully created task: "${taskInfo.title}". You can view it in your task list.`,
                  sender: 'bot',
                  timestamp: new Date(),
                };

                setMessages(prev => [...prev, botMessage]);
              } catch (taskError) {
                const errorMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: 'Sorry, I encountered an error creating your task. Please try again.',
                  sender: 'bot',
                  timestamp: new Date(),
                };
                setMessages(prev => [...prev, errorMessage]);
              }
            } else {
              // Check for inappropriate terms before processing
              const userInputLower = inputValue.toLowerCase().trim();
              const inappropriateTerms = ['duffer', 'idiot', 'stupid', 'dummy', 'fool', 'moron', 'jerk', 'asshole', 'dumb'];

              if (inappropriateTerms.some(term => userInputLower.includes(term))) {
                // Don't create a task with inappropriate content, respond with standard message
                const botMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!",
                  sender: 'bot',
                  timestamp: new Date(),
                };

                setMessages(prev => [...prev, botMessage]);
              } else {
                // For any other messages that are not task-related, respond with the standard message
                const botMessage: Message = {
                  id: (Date.now() + 1).toString(),
                  content: "I am AI Todo Assistant, you can add, update, or delete tasks by telling me what you'd like to do!",
                  sender: 'bot',
                  timestamp: new Date(),
                };

                setMessages(prev => [...prev, botMessage]);
              }
            }
          }
        }
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request.',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setInputValue('');
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md z-50 bg-white dark:bg-gray-900 shadow-2xl rounded-l-lg overflow-hidden transform transition-transform duration-300 ease-in-out">
      <div className="flex flex-col h-full">
        <div className="p-4 bg-gradient-to-r from-green-500 to-teal-600 text-white flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold">AI Todo Assistant</h2>
            <p className="text-sm opacity-90">Ask me to manage your tasks</p>
          </div>
          <Button
            onClick={onClose}
            variant="ghost"
            size="sm"
            className="text-white hover:bg-white/20"
          >
            ✕
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[calc(100vh-180px)]">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs sm:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                }`}
              >
                <p>{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'
                }`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 max-w-xs px-4 py-2 rounded-lg">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              disabled={isLoading || !inputValue.trim()}
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// This component will be used in the dashboard page with the refresh function passed as a prop
interface FloatingAIButtonProps {
  onTaskCreated?: () => void;
  onDeleteTask?: () => void;
  onTaskUpdated?: () => void;
}

const FloatingAIButton: React.FC<FloatingAIButtonProps> = ({ onTaskCreated, onDeleteTask, onTaskUpdated }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleCreateTask = (taskData: { title: string; description?: string; due_date?: string; priority?: 'low' | 'medium' | 'high' }) => {
    console.log('Task created via AI Assistant:', taskData);
    // Call the parent callback to refresh the task list if provided
    if (onTaskCreated) {
      onTaskCreated();
    }
  };

  return (
    <>
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg bg-[#4F6F52] hover:bg-[#4F6F52]/90 text-white dark:bg-[#4F6F52] dark:hover:bg-[#4F6F52]/90 flex items-center justify-center"
        aria-label="Open AI Todo Assistant"
      >
        <span className="text-lg font-bold">AI</span>
      </Button>

      <TodoChatbot
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onCreateTask={handleCreateTask}
        onDeleteTask={onDeleteTask}
        onTaskUpdated={onTaskUpdated}
      />
    </>
  );
};

export default FloatingAIButton;