import React from 'react';
import { Download, Clock, Users, Target, CheckCircle, AlertCircle, Calendar, User } from 'lucide-react';
import { Meeting, MeetingAnalysis } from '../../types';
import { PDFGenerator } from '../../utils/pdfGenerator';

interface ResultsSectionProps {
  meeting: Meeting;
  analysis: MeetingAnalysis;
}

export const ResultsSection: React.FC<ResultsSectionProps> = ({ meeting, analysis }) => {
  const handleDownloadPDF = async () => {
    try {
      await PDFGenerator.generateMeetingReport(meeting, analysis);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High':
        return 'text-red-700 bg-red-100 border-red-200';
      case 'Medium':
        return 'text-yellow-700 bg-yellow-100 border-yellow-200';
      case 'Low':
        return 'text-green-700 bg-green-100 border-green-200';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Meeting Analysis Results</h2>
            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span>{meeting.date}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>{meeting.duration}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4" />
                <span>{meeting.participants.length} participants</span>
              </div>
            </div>
          </div>
          
          <button
            onClick={handleDownloadPDF}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      {/* Summary Section */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Target className="w-5 h-5 text-blue-600" />
          <span>Meeting Summary</span>
        </h3>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
        </div>
        
        {analysis.keyTopics.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Key Topics Discussed:</h4>
            <div className="flex flex-wrap gap-2">
              {analysis.keyTopics.map((topic, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action Items */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span>Action Items</span>
        </h3>
        <div className="space-y-3">
          {analysis.actionItems.map((item) => (
            <div key={item.id} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0">
                <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5" />
              </div>
              <div className="flex-1">
                <p className="text-gray-800 font-medium">{item.description}</p>
                <div className="flex items-center space-x-3 mt-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(item.priority)}`}>
                    {item.priority} Priority
                  </span>
                  <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded-full border">
                    {item.category}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Task Assignments */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <User className="w-5 h-5 text-purple-600" />
          <span>Task Assignments</span>
        </h3>
        <div className="space-y-4">
          {analysis.tasks.map((task) => (
            <div key={task.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-gray-800 font-medium flex-1 mr-4">{task.description}</h4>
                <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Assigned to:</span>
                  <p className="font-medium text-gray-800">{task.assignee}</p>
                </div>
                <div>
                  <span className="text-gray-500">Due Date:</span>
                  <p className="font-medium text-gray-800">{task.dueDate}</p>
                </div>
                <div>
                  <span className="text-gray-500">Status:</span>
                  <p className="font-medium text-orange-600">{task.status}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Next Steps */}
      {analysis.nextSteps.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Target className="w-5 h-5 text-indigo-600" />
            <span>Recommended Next Steps</span>
          </h3>
          <div className="space-y-2">
            {analysis.nextSteps.map((step, index) => (
              <div key={index} className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </span>
                <p className="text-gray-700">{step}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};