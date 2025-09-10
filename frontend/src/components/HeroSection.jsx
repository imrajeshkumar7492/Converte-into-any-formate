import React, { useState, useRef } from 'react';
import { Upload, ChevronDown, FileText, Image, Video, Music, Archive, Clock, Settings, Download, X, Check } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from '../hooks/use-toast';
import { mockConversionProcess } from '../data/mockData';

const HeroSection = () => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [showConversionInterface, setShowConversionInterface] = useState(false);
  const [conversions, setConversions] = useState([]);
  const [isConverting, setIsConverting] = useState(false);
  const [completedConversions, setCompletedConversions] = useState([]);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    if (files.length > 0) {
      setSelectedFiles(files);
      
      // Create conversion items for each file
      const newConversions = Array.from(files).map((file, index) => ({
        id: Date.now() + index,
        file: file,
        originalFormat: file.name.split('.').pop().toUpperCase(),
        targetFormat: '',
        status: 'ready', // ready, converting, completed
        progress: 0
      }));
      
      setConversions(newConversions);
      setShowConversionInterface(true);
      
      toast({
        title: "Files uploaded successfully!",
        description: `${files.length} file(s) ready for conversion.`,
      });
    }
  };

  const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('image/')) return <Image className="w-5 h-5 text-green-500" />;
    if (type.startsWith('video/')) return <Video className="w-5 h-5 text-blue-500" />;
    if (type.startsWith('audio/')) return <Music className="w-5 h-5 text-purple-500" />;
    return <FileText className="w-5 h-5 text-gray-500" />;
  };

  return (
    <section className="bg-gray-50 py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        {/* Title */}
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
          File Converter
        </h1>
        
        <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
          Easily convert files from one format to another, online.
        </p>

        {/* Upload Area */}
        <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-200 p-8 mb-8 transition-all duration-300 hover:border-purple-300">
          <div
            className={`relative ${isDragOver ? 'border-purple-400 bg-purple-50' : ''} transition-all duration-300`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {/* Choose Files Button */}
            <div className="mb-6">
              <Button
                onClick={() => fileInputRef.current?.click()}
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-medium px-8 py-3 text-lg rounded-lg transition-all duration-300 transform hover:scale-105"
              >
                <Upload className="w-5 h-5 mr-2" />
                Choose Files
                <ChevronDown className="w-4 h-4 ml-2" />
              </Button>
            </div>

            {/* File Input */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              accept="*/*"
            />

            {/* Drop Zone */}
            <div className="text-center">
              <Upload className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg mb-2">Drop any files here!</p>
              <p className="text-sm text-gray-400">
                Max file size 1GB. 
                <a href="#" className="text-purple-500 hover:text-purple-600 ml-1 font-medium">
                  Sign Up
                </a> for more
              </p>
            </div>

            {/* Processing Indicator */}
            {isProcessing && (
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <div className="text-blue-600 font-medium mb-2">
                  {mockConversionProcess.steps[processingStep]}
                </div>
                <div className="w-full bg-blue-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((processingStep + 1) / mockConversionProcess.steps.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Selected Files */}
            {selectedFiles.length > 0 && !isProcessing && (
              <div className="mt-6 space-y-2">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h3>
                {selectedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      {getFileIcon(file)}
                      <span className="text-sm text-gray-700 truncate max-w-xs">{file.name}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Terms */}
        <p className="text-sm text-gray-500">
          By proceeding, you agree to our{' '}
          <a href="#" className="text-purple-500 hover:text-purple-600 font-medium">
            Terms of Use
          </a>
          .
        </p>

        {/* Advanced Settings Toggle */}
        <div className="mt-8">
          <button className="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors duration-200">
            Advanced settings (optional)
          </button>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;