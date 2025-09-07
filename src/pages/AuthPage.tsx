import React, { useState } from 'react';
import { Brain, Users, Target, Zap } from 'lucide-react';
import { LoginForm } from '../components/Auth/LoginForm';
import { SignupForm } from '../components/Auth/SignupForm';

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 flex-col justify-center p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/90 to-indigo-800/90"></div>
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-8">
            <div className="bg-white/10 backdrop-blur-sm p-3 rounded-xl">
              <Brain className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">AI Meeting Summarizer</h1>
              <p className="text-blue-100">Enterprise Solution</p>
            </div>
          </div>

          <h2 className="text-4xl font-bold mb-6 leading-tight">
            Transform Your Meetings Into 
            <span className="text-yellow-300"> Actionable Insights</span>
          </h2>

          <p className="text-xl text-blue-100 mb-12">
            Streamline your enterprise meetings with AI-powered analysis, 
            automatic task assignment, and comprehensive reporting.
          </p>

          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg">
                <Target className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Smart Summarization</h3>
                <p className="text-blue-100">AI extracts key points and decisions from your meetings</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Automatic Task Assignment</h3>
                <p className="text-blue-100">Assign action items to team members instantly</p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="bg-white/10 backdrop-blur-sm p-2 rounded-lg">
                <Zap className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Enterprise Ready</h3>
                <p className="text-blue-100">Professional reports and seamless team collaboration</p>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-20 right-20 w-32 h-32 bg-white/5 rounded-full"></div>
        <div className="absolute bottom-20 left-20 w-24 h-24 bg-yellow-300/10 rounded-full"></div>
        <div className="absolute top-1/2 right-10 w-16 h-16 bg-indigo-300/10 rounded-full"></div>
      </div>

      {/* Right Side - Auth Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Header */}
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">AI Meeting Summarizer</h1>
            </div>
          </div>

          {isLogin ? (
            <LoginForm onSwitchToSignup={() => setIsLogin(false)} />
          ) : (
            <SignupForm onSwitchToLogin={() => setIsLogin(true)} />
          )}
        </div>
      </div>
    </div>
  );
};