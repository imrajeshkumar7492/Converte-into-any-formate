import React, { useState, useRef } from 'react';
import { Upload, ChevronDown, FileText, Image, Video, Music, Archive, Clock, Settings, Download, X, Check } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from '../hooks/use-toast';

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

  const handleFiles = async (files) => {
    if (files.length > 0) {
      setSelectedFiles(files);
      setIsProcessing(true);
      
      try {
        // Upload files to get supported formats
        const formData = new FormData();
        Array.from(files).forEach(file => {
          formData.append('files', file);
        });

        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const uploadResult = await response.json();
        
        // Create conversion items with real supported formats
        const newConversions = uploadResult.files.map((uploadedFile, index) => ({
          id: uploadedFile.id,
          file: files[index],
          originalFormat: uploadedFile.source_format,
          targetFormat: '',
          status: 'ready',
          progress: 0,
          supportedFormats: uploadedFile.supported_formats,
          fileInfo: uploadedFile.file_info
        }));
        
        setConversions(newConversions);
        setShowConversionInterface(true);
        
        toast({
          title: "Files uploaded successfully!",
          description: `${files.length} file(s) ready for conversion.`,
        });
      } catch (error) {
        console.error('Upload error:', error);
        toast({
          title: "Upload failed",
          description: "Please try again.",
          variant: "destructive"
        });
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('image/')) return <Image className="w-5 h-5 text-green-500" />;
    if (type.startsWith('video/')) return <Video className="w-5 h-5 text-blue-500" />;
    if (type.startsWith('audio/')) return <Music className="w-5 h-5 text-purple-500" />;
    return <FileText className="w-5 h-5 text-gray-500" />;
  };

  const getFormatOptions = (conversion) => {
    // Use the supported formats from the backend response
    return conversion.supportedFormats || ['PDF', 'JPG', 'PNG', 'MP4', 'MP3', 'DOC', 'TXT'];
  };

  const handleFormatChange = (conversionId, format) => {
    setConversions(prev => 
      prev.map(conv => 
        conv.id === conversionId 
          ? { ...conv, targetFormat: format }
          : conv
      )
    );
  };

  const handleConvertAll = async () => {
    const readyConversions = conversions.filter(conv => conv.targetFormat);
    
    if (readyConversions.length === 0) {
      toast({
        title: "Please select output formats",
        description: "Choose a target format for each file to start conversion.",
        variant: "destructive"
      });
      return;
    }

    setIsConverting(true);
    
    // Mock conversion process for each file
    for (let conversion of readyConversions) {
      // Update status to converting
      setConversions(prev => 
        prev.map(conv => 
          conv.id === conversion.id 
            ? { ...conv, status: 'converting', progress: 0 }
            : conv
        )
      );

      // Simulate conversion progress
      for (let progress = 0; progress <= 100; progress += 20) {
        await new Promise(resolve => setTimeout(resolve, 300));
        setConversions(prev => 
          prev.map(conv => 
            conv.id === conversion.id 
              ? { ...conv, progress }
              : conv
          )
        );
      }

      // Mark as completed
      setConversions(prev => 
        prev.map(conv => 
          conv.id === conversion.id 
            ? { ...conv, status: 'completed', progress: 100 }
            : conv
        )
      );
      
      setCompletedConversions(prev => [...prev, conversion.id]);
    }
    
    setIsConverting(false);
    toast({
      title: "Conversion Complete!",
      description: `${readyConversions.length} file(s) converted successfully.`,
    });
  };

  const handleDownload = (conversionId) => {
    const conversion = conversions.find(c => c.id === conversionId);
    if (conversion && conversion.status === 'completed') {
      // Create a mock download file
      const blob = new Blob(['Mock converted file content'], { type: 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${conversion.file.name.split('.')[0]}.${conversion.targetFormat.toLowerCase()}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Download Started!",
        description: `${conversion.file.name} downloaded successfully.`,
      });
    }
  };

  const handleDownloadAll = () => {
    const completedConversions = conversions.filter(c => c.status === 'completed');
    
    if (completedConversions.length === 0) {
      toast({
        title: "No files to download",
        description: "Please convert files first before downloading.",
        variant: "destructive"
      });
      return;
    }

    // Download each completed file
    completedConversions.forEach((conversion, index) => {
      setTimeout(() => {
        handleDownload(conversion.id);
      }, index * 500); // Stagger downloads
    });

    toast({
      title: "Downloads Started!",
      description: `${completedConversions.length} file(s) downloading...`,
    });
  };

  const removeFile = (conversionId) => {
    setConversions(prev => prev.filter(conv => conv.id !== conversionId));
    if (conversions.length === 1) {
      setShowConversionInterface(false);
      setSelectedFiles([]);
    }
  };

  const addMoreFiles = () => {
    fileInputRef.current?.click();
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

        {!showConversionInterface ? (
          /* Upload Area */
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
            </div>
          </div>
        ) : (
          /* Conversion Interface */
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Convert Files</h3>
              <Button 
                variant="outline" 
                onClick={addMoreFiles}
                className="text-purple-600 border-purple-200 hover:bg-purple-50"
              >
                <Upload className="w-4 h-4 mr-2" />
                Add More Files
              </Button>
            </div>

            {/* File Conversion List */}
            <div className="space-y-4 mb-6">
              {conversions.map((conversion) => (
                <div key={conversion.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(conversion.file)}
                      <div className="text-left">
                        <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                          {conversion.file.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {(conversion.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(conversion.id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                    {/* Original Format */}
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600 whitespace-nowrap">From:</span>
                      <span className="bg-gray-100 px-3 py-1 rounded-md text-sm font-medium">
                        {conversion.originalFormat}
                      </span>
                    </div>

                    {/* Arrow - hidden on mobile */}
                    <div className="hidden md:flex justify-center">
                      <span className="text-gray-400 text-lg">→</span>
                    </div>

                    {/* Target Format Selection */}
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600 whitespace-nowrap">To:</span>
                      <Select 
                        value={conversion.targetFormat} 
                        onValueChange={(value) => handleFormatChange(conversion.id, value)}
                      >
                        <SelectTrigger className="w-full md:w-32">
                          <SelectValue placeholder="Choose format" />
                        </SelectTrigger>
                        <SelectContent>
                          {getFormatOptions(conversion.originalFormat).map((format) => (
                            <SelectItem key={format} value={format}>
                              {format}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Status/Progress and Download */}
                    <div className="flex items-center justify-between md:justify-end space-x-2">
                      <div className="flex-1 md:flex-none">
                        {conversion.status === 'ready' && (
                          <span className="text-sm text-gray-500">Ready</span>
                        )}
                        {conversion.status === 'converting' && (
                          <div className="space-y-1">
                            <div className="text-sm text-blue-600">Converting...</div>
                            <div className="w-20 bg-blue-200 rounded-full h-2">
                              <div 
                                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${conversion.progress}%` }}
                              ></div>
                            </div>
                          </div>
                        )}
                        {conversion.status === 'completed' && (
                          <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1 text-green-600">
                              <Check className="w-4 h-4" />
                              <span className="text-sm">Complete</span>
                            </div>
                            <Button
                              size="sm"
                              onClick={() => handleDownload(conversion.id)}
                              className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 text-xs"
                            >
                              <Download className="w-3 h-3 mr-1" />
                              Download
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Convert Button */}
            <div className="flex justify-center space-x-4">
              <Button
                onClick={handleConvertAll}
                disabled={isConverting || conversions.every(c => !c.targetFormat)}
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-medium px-8 py-3 text-lg disabled:opacity-50"
              >
                {isConverting ? 'Converting...' : 'Convert All'}
              </Button>
              
              {completedConversions.length > 0 && (
                <Button
                  onClick={handleDownloadAll}
                  variant="outline"
                  className="border-green-200 text-green-600 hover:bg-green-50 font-medium px-8 py-3"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download All ({completedConversions.length})
                </Button>
              )}
            </div>
          </div>
        )}

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