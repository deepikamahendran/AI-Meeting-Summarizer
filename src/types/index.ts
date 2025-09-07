export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  company: string;
}

export interface Meeting {
  id: string;
  title: string;
  date: string;
  duration: string;
  participants: string[];
  transcript: string;
  summary?: string;
  actionItems?: ActionItem[];
  tasks?: Task[];
  createdAt: string;
}

export interface ActionItem {
  id: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  category: string;
}

export interface Task {
  id: string;
  description: string;
  assignee: string;
  dueDate: string;
  priority: 'High' | 'Medium' | 'Low';
  status: 'Pending' | 'In Progress' | 'Completed';
}

export interface MeetingAnalysis {
  summary: string;
  actionItems: ActionItem[];
  tasks: Task[];
  keyTopics: string[];
  nextSteps: string[];
}