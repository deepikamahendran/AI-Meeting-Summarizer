import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Brain } from 'lucide-react';
import { Header } from '../components/Layout/Header';
import { InputSection } from '../components/Dashboard/InputSection';
import { ResultsSection } from '../components/Dashboard/ResultsSection';
import { Meeting, MeetingAnalysis } from '../types';
import { AIProcessor } from '../utils/aiProcessor';

export const DashboardPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [currentMeeting, setCurrentMeeting] = useState<Meeting | null>(null);
  const [analysis, setAnalysis] = useState<MeetingAnalysis | null>(null);

  const handleTranscriptSubmit = async (transcript: string, participants: string[]) => {
    setLoading(true);
    
    try {
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const meeting: Meeting = {
        id: uuidv4(),
        title: `Meeting Analysis - ${new Date().toLocaleDateString()}`,
        date: new Date().toLocaleDateString(),
        duration: '45 mins',
        participants: participants.length > 0 ? participants : ['Sarah Johnson', 'Mike Chen', 'Lisa Rodriguez'],
        transcript,
        createdAt: new Date().toISOString()
      };

      const meetingAnalysis = AIProcessor.analyzeMeeting(transcript, meeting.participants);
      
      setCurrentMeeting(meeting);
      setAnalysis(meetingAnalysis);
    } catch (error) {
      console.error('Error processing meeting:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Meeting Analysis Dashboard</h1>
          <p className="text-gray-600">Transform your meeting transcripts into actionable insights and task assignments</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-1">
            <InputSection onTranscriptSubmit={handleTranscriptSubmit} loading={loading} />
          </div>
          
          <div className="xl:col-span-2">
            {loading && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-12 text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Processing Your Meeting</h3>
                <p className="text-gray-600">Our AI is analyzing the transcript and extracting key insights...</p>
                <div className="mt-6 space-y-2">
                  <div className="h-2 bg-blue-100 rounded-full">
                    <div className="h-2 bg-blue-600 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                  </div>
                  <p className="text-sm text-gray-500">Analyzing meeting content and identifying action items</p>
                </div>
              </div>
            )}
            
            {!loading && currentMeeting && analysis && (
              <ResultsSection meeting={currentMeeting} analysis={analysis} />
            )}
            
            {!loading && !currentMeeting && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-12 text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Analyze</h3>
                <p className="text-gray-600">Upload your meeting transcript to get started with AI-powered analysis</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};