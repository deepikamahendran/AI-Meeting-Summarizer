import { v4 as uuidv4 } from 'uuid';
import { MeetingAnalysis, ActionItem, Task } from '../types';

export class AIProcessor {
  static analyzeMeeting(transcript: string, participants: string[] = []): MeetingAnalysis {
    // Simulate AI processing with intelligent text analysis
    const words = transcript.toLowerCase().split(/\s+/);
    const sentences = transcript.split(/[.!?]+/).filter(s => s.trim().length > 0);
    
    // Extract key topics using keyword analysis
    const topicKeywords = {
      'project management': ['project', 'timeline', 'milestone', 'deliverable', 'deadline'],
      'budget & finance': ['budget', 'cost', 'expense', 'revenue', 'financial', 'funding'],
      'team coordination': ['team', 'assign', 'responsible', 'collaborate', 'coordinate'],
      'client relations': ['client', 'customer', 'stakeholder', 'presentation', 'meeting'],
      'technical discussion': ['technical', 'development', 'implementation', 'architecture', 'solution']
    };

    const keyTopics = Object.entries(topicKeywords)
      .filter(([_, keywords]) => 
        keywords.some(keyword => words.includes(keyword))
      )
      .map(([topic, _]) => topic);

    // Generate intelligent summary
    const summary = this.generateSummary(transcript, sentences);

    // Extract action items
    const actionItems = this.extractActionItems(transcript);

    // Extract and assign tasks
    const tasks = this.extractTasks(transcript, participants);

    // Generate next steps
    const nextSteps = this.generateNextSteps(actionItems, tasks);

    return {
      summary,
      actionItems,
      tasks,
      keyTopics,
      nextSteps
    };
  }

  private static generateSummary(transcript: string, sentences: string[]): string {
    // Simulate intelligent summarization
    const keyPhrases = [
      'discussed', 'agreed', 'decided', 'concluded', 'reviewed', 
      'presented', 'analyzed', 'proposed', 'suggested', 'recommended'
    ];

    const importantSentences = sentences
      .filter(sentence => 
        keyPhrases.some(phrase => sentence.toLowerCase().includes(phrase))
      )
      .slice(0, 4)
      .map(sentence => sentence.trim());

    if (importantSentences.length === 0) {
      return `Meeting focused on key business discussions and strategic planning. Participants reviewed current progress, discussed upcoming milestones, and aligned on next steps for continued success.`;
    }

    return importantSentences.join('. ') + '.';
  }

  private static extractActionItems(transcript: string): ActionItem[] {
    const actionKeywords = [
      'action', 'todo', 'follow up', 'next step', 'need to', 'should', 
      'must', 'required', 'implement', 'review', 'analyze', 'prepare', 'contact'
    ];

    const sentences = transcript.split(/[.!?]+/);
    const actionItems: ActionItem[] = [];

    sentences.forEach(sentence => {
      const lowerSentence = sentence.toLowerCase();
      if (actionKeywords.some(keyword => lowerSentence.includes(keyword))) {
        const priority = lowerSentence.includes('urgent') || lowerSentence.includes('asap') ? 'High' :
                        lowerSentence.includes('important') ? 'Medium' : 'Low';
        
        const category = lowerSentence.includes('client') ? 'Client Relations' :
                        lowerSentence.includes('budget') ? 'Budget & Finance' :
                        lowerSentence.includes('technical') ? 'Technical' :
                        'General';

        actionItems.push({
          id: uuidv4(),
          description: sentence.trim(),
          priority,
          category
        });
      }
    });

    // Add some intelligent defaults if no action items found
    if (actionItems.length === 0) {
      actionItems.push(
        {
          id: uuidv4(),
          description: 'Schedule follow-up meeting to review progress',
          priority: 'Medium',
          category: 'General'
        },
        {
          id: uuidv4(),
          description: 'Share meeting summary with all stakeholders',
          priority: 'Low',
          category: 'Communication'
        }
      );
    }

    return actionItems.slice(0, 6); // Limit to 6 items
  }

  private static extractTasks(transcript: string, participants: string[]): Task[] {
    const taskKeywords = [
      'assign', 'responsible', 'owner', 'lead', 'manage', 'handle', 
      'complete', 'deliver', 'finish', 'due', 'deadline'
    ];

    const sentences = transcript.split(/[.!?]+/);
    const tasks: Task[] = [];
    const assignees = participants.length > 0 ? participants : ['Team Lead', 'Project Manager', 'Developer', 'Analyst'];

    sentences.forEach((sentence, index) => {
      const lowerSentence = sentence.toLowerCase();
      if (taskKeywords.some(keyword => lowerSentence.includes(keyword))) {
        const priority = lowerSentence.includes('urgent') || lowerSentence.includes('critical') ? 'High' :
                        lowerSentence.includes('important') ? 'Medium' : 'Low';
        
        const assignee = assignees[index % assignees.length];
        const dueDate = new Date(Date.now() + (Math.floor(Math.random() * 14) + 1) * 24 * 60 * 60 * 1000)
          .toISOString().split('T')[0];

        tasks.push({
          id: uuidv4(),
          description: sentence.trim(),
          assignee,
          dueDate,
          priority,
          status: 'Pending'
        });
      }
    });

    // Add default tasks if none found
    if (tasks.length === 0) {
      const defaultTasks = [
        'Review and finalize project requirements',
        'Prepare client presentation materials',
        'Update project timeline and milestones',
        'Conduct stakeholder feedback session'
      ];

      defaultTasks.forEach((taskDesc, index) => {
        tasks.push({
          id: uuidv4(),
          description: taskDesc,
          assignee: assignees[index % assignees.length],
          dueDate: new Date(Date.now() + (index + 3) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          priority: index === 0 ? 'High' : 'Medium',
          status: 'Pending'
        });
      });
    }

    return tasks.slice(0, 5); // Limit to 5 tasks
  }

  private static generateNextSteps(actionItems: ActionItem[], tasks: Task[]): string[] {
    const steps = [
      'Distribute meeting summary to all participants',
      'Set up follow-up meetings for high-priority items',
      'Monitor task completion and provide updates'
    ];

    if (actionItems.some(item => item.priority === 'High')) {
      steps.unshift('Address high-priority action items immediately');
    }

    if (tasks.some(task => task.priority === 'High')) {
      steps.push('Ensure high-priority tasks have adequate resources');
    }

    return steps;
  }
}