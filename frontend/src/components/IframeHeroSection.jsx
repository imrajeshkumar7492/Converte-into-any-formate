import React, { useState, useRef } from 'react';
import { Upload, ChevronDown, FileText, Image, Video, Music, Download, X, Check, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useToast } from '../hooks/use-toast';

const IframeHeroSection = () => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showConversionInterface, setShowConversionInterface] = useState(false);
  const [conversions, setConversions] = useState([]);
  const [isConverting, setIsConverting] = useState(false);
  const [completedConversions, setCompletedConversions] = useState([]);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  // Mock supported formats for static deployment
  const getSupportedFormats = (originalFormat) => {
    const formatMap = {
      'JPG': ['PNG', 'WEBP', 'BMP', 'TIFF', 'GIF', 'PDF', 'ICO', 'SVG'],
      'PNG': ['JPG', 'WEBP', 'BMP', 'TIFF', 'GIF', 'PDF', 'ICO', 'SVG'],
      'PDF': ['DOC', 'DOCX', 'TXT', 'RTF', 'ODT', 'JPG', 'PNG'],
      'MP4': ['AVI', 'MOV', 'WMV', 'FLV', 'MKV', 'WEBM', 'MP3', 'WAV'],
      'MP3': ['WAV', 'FLAC', 'AAC', 'OGG', 'M4A', 'WMA', 'AIFF'],
      'DOCX': ['DOC', 'PDF', 'TXT', 'RTF', 'ODT']
    };
    return formatMap[originalFormat] || ['PDF', 'JPG', 'PNG', 'TXT'];
  };

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
        // Mock file processing for static deployment
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const newConversions = files.map((file, index) => {
          const originalFormat = file.name.split('.').pop().toUpperCase();
          return {
            id: `file-${index}-${Date.now()}`,
            file: file,
            originalFormat: originalFormat,
            targetFormat: '',
            status: 'ready',
            progress: 0,
            supportedFormats: getSupportedFormats(originalFormat)
          };
        });
        
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
          description: error.message,
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
    
    // Mock conversion process for static deployment
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

        // Simulate progress
        for (let progress = 10; progress <= 100; progress += 20) {
          await new Promise(resolve => setTimeout(resolve, 300));
          setConversions(prev => 
            prev.map(conv => 
              conv.id === conversion.id 
                ? { ...conv, progress }
                : conv
            )
          );
        }

        // Create mock converted file
        const mockContent = `Mock converted file: ${conversion.file.name} -> ${conversion.targetFormat}`;
        const blob = new Blob([mockContent], { type: 'text/plain' });
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
      }
    }
    
    setIsConverting(false);
    
    if (completedCount > 0) {
      toast({
        title: "Conversion completed!",
        description: `${completedCount} file(s) converted successfully!`,
      });
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
      
      toast({
        title: "Download started",
        description: `${conversion.file.name} downloaded successfully!`,
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

    completedConversions.forEach((conversion, index) => {
      setTimeout(() => {
        handleDownload(conversion.id);
      }, index * 500);
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

  const resetInterface = () => {
    setConversions([]);
    setCompletedConversions([]);
    setShowConversionInterface(false);
    setSelectedFiles([]);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      {!showConversionInterface ? (
        /* Upload Area */
        <div className="bg-white rounded-lg shadow-lg border p-8">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
              isDragOver 
                ? 'border-blue-400 bg-blue-50' 
                : 'border-gray-300 hover:border-blue-300'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {isProcessing && (
              <div className="absolute inset-0 bg-white/90 flex items-center justify-center z-10 rounded-lg">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-200 border-t-blue-600 mx-auto mb-2"></div>
                  <p className="text-sm font-medium text-gray-700">Processing files...</p>
                </div>
              </div>
            )}
            
            <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              File Converter
            </h3>
            
            <p className="text-gray-600 mb-6">
              Drop files here or click to browse
            </p>
            
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
            >
              <Upload className="w-4 h-4 mr-2" />
              Choose Files
            </Button>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              accept="*/*"
            />
            
            <div className="flex flex-wrap justify-center gap-4 mt-4 text-xs text-gray-500">
              <span className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>40+ formats</span>
              </span>
              <span className="flex items-center space-x-1">
                <CheckCircle className="w-3 h-3 text-green-500" />
                <span>Secure</span>
              </span>
            </div>
          </div>
        </div>
      ) : (
        /* Conversion Interface */
        <div className="bg-white rounded-lg shadow-lg border p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">Convert Files</h3>
              <p className="text-gray-600 text-sm">Select output formats for your files</p>
            </div>
            <div className="flex space-x-2">
              <Button 
                variant="outline" 
                onClick={addMoreFiles}
                className="text-sm px-3 py-1"
              >
                <Upload className="w-4 h-4 mr-1" />
                Add More
              </Button>
              <Button 
                variant="outline" 
                onClick={resetInterface}
                className="text-sm px-3 py-1"
              >
                Reset
              </Button>
            </div>
          </div>

          {/* File List */}
          <div className="space-y-4 mb-6">
            {conversions.map((conversion) => (
              <div key={conversion.id} className="bg-gray-50 rounded-lg p-4 border">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-white rounded-lg">
                      {getFileIcon(conversion.file)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm truncate">
                        {conversion.file.name}
                      </p>
                      <p className="text-xs text-gray-600">
                        {(conversion.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(conversion.id)}
                    className="text-gray-400 hover:text-red-500 p-1"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
                  {/* Source Format */}
                  <div>
                    <span className="text-xs font-medium text-gray-700 block mb-1">From</span>
                    <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded text-sm font-medium text-center">
                      {conversion.originalFormat}
                    </div>
                  </div>

                  {/* Arrow */}
                  <div className="hidden md:flex justify-center">
                    <span className="text-gray-400">→</span>
                  </div>

                  {/* Target Format */}
                  <div>
                    <span className="text-xs font-medium text-gray-700 block mb-1">To</span>
                    <Select 
                      value={conversion.targetFormat} 
                      onValueChange={(value) => handleFormatChange(conversion.id, value)}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Choose format" />
                      </SelectTrigger>
                      <SelectContent>
                        {conversion.supportedFormats.map((format) => (
                          <SelectItem key={format} value={format}>
                            {format}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Status */}
                  <div>
                    {conversion.status === 'ready' && (
                      <div className="text-xs text-gray-600">Ready</div>
                    )}
                    {conversion.status === 'converting' && (
                      <div className="space-y-1">
                        <div className="text-xs text-blue-600">Converting...</div>
                        <div className="w-full bg-gray-200 rounded-full h-1">
                          <div 
                            className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                            style={{ width: `${conversion.progress}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-500">{conversion.progress}%</div>
                      </div>
                    )}
                    {conversion.status === 'completed' && (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-1 text-green-600 text-xs">
                          <Check className="w-3 h-3" />
                          <span>Complete</span>
                        </div>
                        <Button
                          onClick={() => handleDownload(conversion.id)}
                          className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 text-xs"
                        >
                          <Download className="w-3 h-3 mr-1" />
                          Download
                        </Button>
                      </div>
                    )}
                    {conversion.status === 'failed' && (
                      <div className="text-xs text-red-600">Failed</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4">
            <Button
              onClick={handleConvertAll}
              disabled={isConverting || conversions.every(c => !c.targetFormat)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 disabled:opacity-50"
            >
              {isConverting ? 'Converting...' : 'Convert All'}
            </Button>
            
            {completedConversions.length > 0 && (
              <Button
                onClick={handleDownloadAll}
                variant="outline"
                className="px-6 py-2"
              >
                <Download className="w-4 h-4 mr-2" />
                Download All ({completedConversions.length})
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default IframeHeroSection;