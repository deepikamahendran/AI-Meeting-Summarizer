import React, { useState } from 'react';
import { FileText, Upload, Clipboard, Mic, Play, Brain } from 'lucide-react';

interface InputSectionProps {
  onTranscriptSubmit: (transcript: string, participants: string[]) => void;
  loading: boolean;
}

export const InputSection: React.FC<InputSectionProps> = ({ onTranscriptSubmit, loading }) => {
  const [activeTab, setActiveTab] = useState<'text' | 'audio' | 'paste'>('text');
  const [transcript, setTranscript] = useState('');
  const [participants, setParticipants] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'audio' && audioFile) {
      // Simulate audio processing - in real implementation, you'd send to speech-to-text service
      const simulatedTranscript = `Audio meeting transcript from ${audioFile.name}. Discussion covered project milestones, budget allocation, and team assignments. Action items include reviewing client requirements, preparing presentation materials, and scheduling follow-up meetings. Team leads will coordinate with respective departments to ensure timely completion of deliverables.`;
      onTranscriptSubmit(simulatedTranscript, participants.split(',').map(p => p.trim()).filter(p => p));
    } else if (transcript.trim()) {
      onTranscriptSubmit(transcript, participants.split(',').map(p => p.trim()).filter(p => p));
    }
  };

  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAudioFile(file);
    }
  };

  const sampleTranscript = `Good morning everyone, thanks for joining today's project review meeting. Let's start with the current status update.

Sarah: Our Q1 milestones are on track. We've completed 85% of the client requirements analysis and the technical architecture review is scheduled for next week.

Mike: From the development side, we need to address the API integration challenges. I suggest we allocate additional resources to the backend team to meet our deadline.

Lisa: Budget-wise, we're within the allocated range. However, if we add more developers as Mike suggested, we'll need approval for the additional 15% increase.

Sarah: I'll handle getting budget approval from stakeholders. Mike, can you prepare a detailed resource requirement document by Friday?

Mike: Absolutely. I'll also coordinate with the QA team to ensure testing timelines align with development.

Lisa: Great. For next steps, I'll schedule a client presentation for next Tuesday. We should prepare demo materials and progress reports.

Sarah: Perfect. Let's reconvene next Monday to review everything before the client meeting. Any other concerns?

Mike: Just want to confirm - the production deployment is still planned for month-end, correct?

Sarah: Yes, that's the target. Thanks everyone, meeting adjourned.`;

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100">
      <div className="p-6 border-b border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Meeting Input</h2>
        
        <div className="flex space-x-1 mb-6">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              activeTab === 'text' 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'text-gray-600 hover:bg-gray-50 border border-transparent'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Text Input</span>
          </button>
          <button
            onClick={() => setActiveTab('audio')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              activeTab === 'audio' 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'text-gray-600 hover:bg-gray-50 border border-transparent'
            }`}
          >
            <Mic className="w-4 h-4" />
            <span>Audio Upload</span>
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
              activeTab === 'paste' 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'text-gray-600 hover:bg-gray-50 border border-transparent'
            }`}
          >
            <Clipboard className="w-4 h-4" />
            <span>Paste Text</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {activeTab === 'text' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Meeting Transcript
              </label>
              <div className="relative">
                <textarea
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Enter or paste your meeting transcript here..."
                  required
                />
                <button
                  type="button"
                  onClick={() => setTranscript(sampleTranscript)}
                  className="absolute top-2 right-2 text-xs text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded transition-colors duration-200"
                >
                  <Play className="w-3 h-3 inline mr-1" />
                  Try Sample
                </button>
              </div>
            </div>
          )}

          {activeTab === 'audio' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Audio File
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors duration-200">
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">Upload your meeting audio file</p>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleAudioUpload}
                  className="hidden"
                  id="audio-upload"
                />
                <label
                  htmlFor="audio-upload"
                  className="bg-blue-50 text-blue-600 px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors duration-200 inline-block"
                >
                  Choose File
                </label>
                {audioFile && (
                  <p className="text-sm text-green-600 mt-2">Selected: {audioFile.name}</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'paste' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paste Meeting Transcript
              </label>
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Ctrl+V to paste your meeting transcript..."
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Meeting Participants (Optional)
            </label>
            <input
              type="text"
              value={participants}
              onChange={(e) => setParticipants(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter participant names separated by commas (e.g., Sarah, Mike, Lisa)"
            />
          </div>

          <button
            type="submit"
            disabled={loading || (!transcript.trim() && !audioFile)}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing Meeting...</span>
              </>
            ) : (
              <>
                <Brain className="w-5 h-5" />
                <span>Analyze Meeting</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};