import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { Upload, FileText, Image, File, Download, Check, X, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Conversion type options
const CONVERSION_OPTIONS = {
  'Image Conversions': {
    'jpg_to_png': 'JPG to PNG',
    'png_to_jpg': 'PNG to JPG',
    'webp_to_png': 'WEBP to PNG', 
    'png_to_webp': 'PNG to WEBP',
    'heic_to_jpg': 'HEIC to JPG'
  },
  'PDF Operations': {
    'merge_pdf': 'Merge PDFs',
    'split_pdf': 'Split PDF',
    'compress_pdf': 'Compress PDF'
  },
  'Document to PDF': {
    'docx_to_pdf': 'Word to PDF',
    'xlsx_to_pdf': 'Excel to PDF', 
    'pptx_to_pdf': 'PowerPoint to PDF',
    'jpg_to_pdf': 'Image to PDF'
  },
  'PDF to Other': {
    'pdf_to_jpg': 'PDF to Images'
  }
};

const FileIcon = ({ file }) => {
  const ext = file.name?.split('.').pop()?.toLowerCase();
  
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'].includes(ext)) {
    return <Image className="w-5 h-5 text-blue-500" />;
  } else if (['pdf'].includes(ext)) {
    return <FileText className="w-5 h-5 text-red-500" />;
  } else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)) {
    return <File className="w-5 h-5 text-green-500" />;
  }
  return <File className="w-5 h-5 text-gray-500" />;
};

const JobCard = ({ job, onDownload }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <Check className="w-4 h-4" />;
      case 'processing': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'failed': return <X className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <Card className="mb-4 transition-all duration-200 hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            {CONVERSION_OPTIONS['Image Conversions'][job.conversion_type] || 
             CONVERSION_OPTIONS['PDF Operations'][job.conversion_type] ||
             CONVERSION_OPTIONS['Document to PDF'][job.conversion_type] ||
             CONVERSION_OPTIONS['PDF to Other'][job.conversion_type] ||
             job.conversion_type}
          </CardTitle>
          <Badge className={`${getStatusColor(job.status)} flex items-center gap-1 px-3 py-1`}>
            {getStatusIcon(job.status)}
            {job.status}
          </Badge>
        </div>
        <CardDescription className="text-sm text-gray-600">
          Job ID: {job.id}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {job.status === 'processing' && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{job.progress}%</span>
            </div>
            <Progress value={job.progress} className="w-full" />
          </div>
        )}
        
        {job.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-800 text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              {job.error_message}
            </p>
          </div>
        )}
        
        {job.status === 'completed' && job.download_urls?.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Download Results:</p>
            <div className="flex flex-wrap gap-2">
              {job.download_urls.map((url, index) => (
                <Button
                  key={index}
                  onClick={() => onDownload(url)}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download {index + 1}
                </Button>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [conversionType, setConversionType] = useState('');
  const [jobs, setJobs] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [processing, setProcessing] = useState(false);

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback((jobId) => {
    const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/api/ws/${jobId}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, ...data }
            : job
        )
      );
      
      if (data.completed) {
        toast.success('Conversion completed!');
      } else if (data.error) {
        toast.error(`Conversion failed: ${data.error}`);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return ws;
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const startConversion = async () => {
    if (!conversionType || selectedFiles.length === 0) {
      toast.error('Please select files and conversion type');
      return;
    }

    setProcessing(true);
    
    try {
      // Create job
      const jobResponse = await axios.post(`${API}/jobs`, {
        conversion_type: conversionType,
        options: {}
      });
      
      const job = jobResponse.data;
      setJobs(prev => [job, ...prev]);
      
      // Upload files
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      await axios.post(`${API}/jobs/${job.id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Connect WebSocket for updates
      connectWebSocket(job.id);
      
      // Start job
      await axios.post(`${API}/jobs/${job.id}/start`);
      
      // Clear form
      setSelectedFiles([]);
      setConversionType('');
      
      toast.success('Conversion started!');
      
    } catch (error) {
      console.error('Error starting conversion:', error);
      toast.error('Failed to start conversion');
    } finally {
      setProcessing(false);
    }
  };

  const downloadFile = async (url) => {
    try {
      const response = await axios.get(`${BACKEND_URL}${url}`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data]);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = url.split('/').pop();
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download file');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            Converte
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Convert your files effortlessly. Images, PDFs, Documents - all in one place.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Upload className="w-6 h-6 text-blue-600" />
                  Upload & Convert
                </CardTitle>
                <CardDescription>
                  Drag and drop your files or click to browse
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* File Drop Zone */}
                <div
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
                    dragActive
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Drop your files here
                  </p>
                  <p className="text-gray-500 mb-4">
                    or click to browse your computer
                  </p>
                  <input
                    type="file"
                    multiple
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button 
                    onClick={() => document.getElementById('file-upload').click()}
                    variant="outline"
                    className="border-blue-200 text-blue-600 hover:bg-blue-50"
                  >
                    Choose Files
                  </Button>
                </div>

                {/* Selected Files */}
                {selectedFiles.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-medium text-gray-700">Selected Files:</h3>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                          <div className="flex items-center gap-3">
                            <FileIcon file={file} />
                            <div>
                              <p className="font-medium text-sm">{file.name}</p>
                              <p className="text-xs text-gray-500">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            </div>
                          </div>
                          <Button
                            onClick={() => removeFile(index)}
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700 hover:bg-red-50"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Conversion Type Selection */}
                <div className="space-y-3">
                  <label className="font-medium text-gray-700">Conversion Type:</label>
                  <Select value={conversionType} onValueChange={setConversionType}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select conversion type" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(CONVERSION_OPTIONS).map(([category, options]) => (
                        <div key={category}>
                          <div className="px-2 py-1 text-sm font-semibold text-gray-700 bg-gray-100">
                            {category}
                          </div>
                          {Object.entries(options).map(([value, label]) => (
                            <SelectItem key={value} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </div>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Convert Button */}
                <Button
                  onClick={startConversion}
                  disabled={!conversionType || selectedFiles.length === 0 || processing}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-3 text-lg"
                >
                  {processing ? (
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  ) : (
                    <Upload className="w-5 h-5 mr-2" />
                  )}
                  {processing ? 'Converting...' : 'Start Conversion'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Jobs Section */}
          <div className="space-y-6">
            <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <FileText className="w-6 h-6 text-green-600" />
                  Conversion Jobs
                </CardTitle>
                <CardDescription>
                  Track your conversion progress and download results
                </CardDescription>
              </CardHeader>
              <CardContent>
                {jobs.length === 0 ? (
                  <div className="text-center py-12">
                    <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No conversion jobs yet</p>
                    <p className="text-sm text-gray-400 mt-2">
                      Upload files and start converting to see jobs here
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {jobs.map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        onDownload={downloadFile}
                      />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-16 grid md:grid-cols-3 gap-6">
          <Card className="text-center shadow-lg border-0 bg-white/60 backdrop-blur-sm">
            <CardContent className="pt-6">
              <Image className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Image Conversion</h3>
              <p className="text-gray-600 text-sm">
                Convert between JPG, PNG, WEBP, and HEIC formats
              </p>
            </CardContent>
          </Card>
          
          <Card className="text-center shadow-lg border-0 bg-white/60 backdrop-blur-sm">
            <CardContent className="pt-6">
              <FileText className="w-12 h-12 text-red-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">PDF Tools</h3>
              <p className="text-gray-600 text-sm">
                Merge, split, and compress PDF files easily
              </p>
            </CardContent>
          </Card>
          
          <Card className="text-center shadow-lg border-0 bg-white/60 backdrop-blur-sm">
            <CardContent className="pt-6">
              <File className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Document Conversion</h3>
              <p className="text-gray-600 text-sm">
                Convert Word, Excel, PowerPoint to PDF format
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default App;