import React, { useState, useRef } from 'react';
import { Upload, ChevronDown, FileText, Image, Video, Music, Archive, Clock, Settings, Download, X, Check } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from '../hooks/use-toast';
import AdvancedSettings from './AdvancedSettings';
import FilePreview from './FilePreview';
import { ErrorHandler, showErrorToast, showSuccessToast } from '../utils/errorHandler';

const HeroSection = () => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);
  const [showConversionInterface, setShowConversionInterface] = useState(false);
  const [conversions, setConversions] = useState([]);
  const [isConverting, setIsConverting] = useState(false);
  const [completedConversions, setCompletedConversions] = useState([]);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [advancedSettings, setAdvancedSettings] = useState({
    imageQuality: 95,
    maxWidth: null,
    maxHeight: null,
    compressionLevel: 'high',
    preserveMetadata: true,
    batchProcessing: true,
    autoDownload: false,
    outputFormat: 'original'
  });
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
      // Validate files first
      const validationErrors = [];
      Array.from(files).forEach((file, index) => {
        const errors = ErrorHandler.validateFile(file);
        if (errors.length > 0) {
          validationErrors.push({ file: file.name, errors });
        }
      });

      if (validationErrors.length > 0) {
        validationErrors.forEach(({ file, errors }) => {
          errors.forEach(error => {
            showErrorToast(error, toast);
          });
        });
        return;
      }

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
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
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
        
        showSuccessToast(`${files.length} file(s) uploaded successfully and ready for conversion!`, toast);
      } catch (error) {
        console.error('Upload error:', error);
        showErrorToast(error, toast);
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
    let completedCount = 0;
    
    // Convert each file
    for (let conversion of readyConversions) {
      try {
        // Update status to converting
        setConversions(prev => 
          prev.map(conv => 
            conv.id === conversion.id 
              ? { ...conv, status: 'converting', progress: 0 }
              : conv
          )
        );

        // Simulate progress while conversion happens
        const progressInterval = setInterval(() => {
          setConversions(prev => 
            prev.map(conv => {
              if (conv.id === conversion.id && conv.progress < 90) {
                return { ...conv, progress: conv.progress + 10 };
              }
              return conv;
            })
          );
        }, 500);

        // Perform actual conversion
        const formData = new FormData();
        formData.append('file', conversion.file);
        formData.append('target_format', conversion.targetFormat.toLowerCase());
        
        // Add advanced settings
        formData.append('image_quality', advancedSettings.imageQuality);
        if (advancedSettings.maxWidth) formData.append('max_width', advancedSettings.maxWidth);
        if (advancedSettings.maxHeight) formData.append('max_height', advancedSettings.maxHeight);
        formData.append('compression_level', advancedSettings.compressionLevel);
        formData.append('preserve_metadata', advancedSettings.preserveMetadata);

        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/convert`, {
          method: 'POST',
          body: formData,
        });

        clearInterval(progressInterval);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Conversion failed with status ${response.status}`);
        }

        // Get the converted file as blob
        const blob = await response.blob();
        
        // Validate converted file
        if (blob.size === 0) {
          throw new Error('Converted file is empty');
        }
        
        // Create download URL and store it
        const downloadUrl = URL.createObjectURL(blob);
        
        // Mark as completed
        setConversions(prev => 
          prev.map(conv => 
            conv.id === conversion.id 
              ? { 
                  ...conv, 
                  status: 'completed', 
                  progress: 100,
                  downloadUrl: downloadUrl,
                  convertedBlob: blob
                }
              : conv
          )
        );
        
        completedCount++;
        setCompletedConversions(prev => [...prev, conversion.id]);

      } catch (error) {
        console.error('Conversion error:', error);
        
        // Mark as failed
        setConversions(prev => 
          prev.map(conv => 
            conv.id === conversion.id 
              ? { 
                  ...conv, 
                  status: 'failed', 
                  progress: 0,
                  error: error.message
                }
              : conv
          )
        );

        showErrorToast(error, toast);
      }
    }
    
    setIsConverting(false);
    
    if (completedCount > 0) {
      showSuccessToast(`${completedCount} file(s) converted successfully!`, toast);
    }
  };

  const handleDownload = (conversionId) => {
    const conversion = conversions.find(c => c.id === conversionId);
    if (conversion && conversion.status === 'completed' && conversion.downloadUrl) {
      const link = document.createElement('a');
      link.href = conversion.downloadUrl;
      link.download = `${conversion.file.name.split('.')[0]}.${conversion.targetFormat.toLowerCase()}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      showSuccessToast(`Download started: ${conversion.file.name}`, toast);
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

    showSuccessToast(`${completedConversions.length} file(s) downloading...`, toast);
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
    <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"></div>
      <div className="absolute top-0 left-1/4 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
      <div className="absolute top-0 right-1/4 w-72 h-72 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-1/3 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse animation-delay-4000"></div>
      
      <div className="relative max-w-6xl mx-auto text-center">
        {/* Title */}
        <div className="mb-8">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Professional File Converter
          </h1>
          
          <p className="text-xl sm:text-2xl text-gray-700 mb-8 max-w-4xl mx-auto leading-relaxed">
            Convert files between 40+ formats with enterprise-grade quality, 
            lightning-fast processing, and perfect format preservation.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-700">100% Secure</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-700">No Registration</span>
            </div>
            <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-full px-4 py-2 shadow-sm">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-700">Unlimited Conversions</span>
            </div>
          </div>
        </div>

        {!showConversionInterface ? (
          /* Upload Area */
          <div className="relative">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-12 mb-8 transition-all duration-500 hover:shadow-3xl hover:scale-[1.02]">
              <div
                className={`relative ${isDragOver ? 'border-blue-400 bg-blue-50/50' : ''} transition-all duration-300`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {isProcessing && (
                  <div className="absolute inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center z-10 rounded-3xl">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
                      <p className="text-lg font-medium text-gray-700">Processing files...</p>
                      <p className="text-sm text-gray-500 mt-2">Please wait while we analyze your files</p>
                    </div>
                  </div>
                )}
                
                {/* Choose Files Button */}
                <div className="mb-8">
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white font-semibold px-12 py-4 text-xl rounded-2xl transition-all duration-300 transform hover:scale-105 hover:shadow-xl shadow-lg"
                  >
                    <Upload className="w-6 h-6 mr-3" />
                    Choose Files to Convert
                    <ChevronDown className="w-5 h-5 ml-3" />
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
                  <div className="relative mb-6">
                    <Upload className="w-24 h-24 text-gray-300 mx-auto mb-4 animate-bounce" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-full animate-pulse"></div>
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-800 mb-3">Drop files here or click to browse</h3>
                  <p className="text-gray-600 text-lg mb-6">
                    Support for images, documents, videos, audio, and archives
                  </p>
                  
                  <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center space-x-1">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>Max 1GB per file</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>40+ formats supported</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span>100% secure</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Conversion Interface */
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8 mb-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 space-y-4 sm:space-y-0">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Convert Your Files</h3>
                <p className="text-gray-600">Select output formats and convert your files with professional quality</p>
              </div>
              <Button 
                variant="outline" 
                onClick={addMoreFiles}
                className="bg-white/80 hover:bg-white text-blue-600 border-blue-200 hover:border-blue-300 px-6 py-3 rounded-xl font-medium transition-all duration-300 hover:shadow-lg"
              >
                <Upload className="w-5 h-5 mr-2" />
                Add More Files
              </Button>
            </div>

            {/* File Conversion List */}
            <div className="space-y-6 mb-8">
              {conversions.map((conversion) => (
                <div key={conversion.id} className="bg-gradient-to-r from-gray-50 to-blue-50/30 rounded-2xl p-6 border border-gray-200/50 hover:border-blue-200 transition-all duration-300 hover:shadow-lg">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                      <div className="p-3 bg-white rounded-xl shadow-sm">
                        {getFileIcon(conversion.file)}
                      </div>
                      <div className="text-left flex-1">
                        <p className="text-lg font-semibold text-gray-900 truncate max-w-xs">
                          {conversion.file.name}
                        </p>
                        <p className="text-sm text-gray-600">
                          {(conversion.file.size / 1024 / 1024).toFixed(2)} MB • {conversion.originalFormat}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setPreviewFile(conversion.file);
                          setShowPreview(true);
                        }}
                        className="text-gray-400 hover:text-blue-500 hover:bg-blue-50 p-2 rounded-lg transition-all duration-200"
                        title="Preview file"
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(conversion.id)}
                        className="text-gray-400 hover:text-red-500 hover:bg-red-50 p-2 rounded-lg transition-all duration-200"
                        title="Remove file"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
                    {/* Original Format */}
                    <div className="flex flex-col space-y-2">
                      <span className="text-sm font-medium text-gray-700">Source Format</span>
                      <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-xl text-sm font-semibold text-center">
                        {conversion.originalFormat}
                      </div>
                    </div>

                    {/* Arrow - hidden on mobile */}
                    <div className="hidden md:flex justify-center">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xl font-bold">→</span>
                      </div>
                    </div>

                    {/* Target Format Selection */}
                    <div className="flex flex-col space-y-2">
                      <span className="text-sm font-medium text-gray-700">Target Format</span>
                      <Select 
                        value={conversion.targetFormat} 
                        onValueChange={(value) => handleFormatChange(conversion.id, value)}
                      >
                        <SelectTrigger className="w-full bg-white border-2 border-gray-200 hover:border-blue-300 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200">
                          <SelectValue placeholder="Choose format" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl border-2 border-gray-200 shadow-xl">
                          {getFormatOptions(conversion).map((format) => (
                            <SelectItem key={format} value={format} className="hover:bg-blue-50 rounded-lg">
                              {format}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Status/Progress and Download */}
                    <div className="flex flex-col space-y-3">
                      {conversion.status === 'ready' && (
                        <div className="flex items-center space-x-2 text-gray-600">
                          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                          <span className="text-sm font-medium">Ready to convert</span>
                        </div>
                      )}
                      {conversion.status === 'converting' && (
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2 text-blue-600">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                            <span className="text-sm font-medium">Converting...</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                              style={{ width: `${conversion.progress}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">{conversion.progress}% complete</span>
                        </div>
                      )}
                      {conversion.status === 'completed' && (
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2 text-green-600">
                            <Check className="w-4 h-4" />
                            <span className="text-sm font-medium">Conversion complete!</span>
                          </div>
                          <Button
                            onClick={() => handleDownload(conversion.id)}
                            className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white px-4 py-2 text-sm font-medium rounded-xl transition-all duration-300 hover:shadow-lg"
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                        </div>
                      )}
                      {conversion.status === 'failed' && (
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2 text-red-600">
                            <X className="w-4 h-4" />
                            <span className="text-sm font-medium">Conversion failed</span>
                          </div>
                          {conversion.error && (
                            <p className="text-xs text-red-500 bg-red-50 px-2 py-1 rounded" title={conversion.error}>
                              {conversion.error.substring(0, 30)}...
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Convert Button */}
            <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Button
                onClick={handleConvertAll}
                disabled={isConverting || conversions.every(c => !c.targetFormat)}
                className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 text-white font-semibold px-12 py-4 text-lg rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-xl shadow-lg"
              >
                {isConverting ? (
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    <span>Converting...</span>
                  </div>
                ) : (
                  'Convert All Files'
                )}
              </Button>
              
              {completedConversions.length > 0 && (
                <Button
                  onClick={handleDownloadAll}
                  variant="outline"
                  className="border-2 border-green-200 text-green-600 hover:bg-green-50 hover:border-green-300 font-semibold px-8 py-4 text-lg rounded-2xl transition-all duration-300 hover:shadow-lg"
                >
                  <Download className="w-5 h-5 mr-3" />
                  Download All ({completedConversions.length})
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Terms */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            By using our service, you agree to our{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700 font-medium underline">
              Terms of Use
            </a>
            {' '}and{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700 font-medium underline">
              Privacy Policy
            </a>
            .
          </p>
        </div>

        {/* Advanced Settings Toggle */}
        <div className="mt-8 text-center">
          <button 
            onClick={() => setShowAdvancedSettings(true)}
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-blue-600 text-sm font-medium transition-colors duration-200 hover:underline"
          >
            <Settings className="w-4 h-4" />
            <span>Advanced settings (optional)</span>
          </button>
        </div>

        {/* Advanced Settings Modal */}
        <AdvancedSettings
          isOpen={showAdvancedSettings}
          onClose={() => setShowAdvancedSettings(false)}
          settings={advancedSettings}
          onSettingsChange={setAdvancedSettings}
        />

        {/* File Preview Modal */}
        <FilePreview
          file={previewFile}
          isOpen={showPreview}
          onClose={() => {
            setShowPreview(false);
            setPreviewFile(null);
          }}
          onDownload={previewFile ? () => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(previewFile);
            link.download = previewFile.name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            setShowPreview(false);
            setPreviewFile(null);
          } : null}
        />
      </div>
    </section>
  );
};

export default HeroSection;