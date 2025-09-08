import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import { 
  Upload, FileText, Image, File, Download, Check, X, AlertCircle, Loader2, 
  Settings, Zap, Star, Monitor, Smartphone, Tablet, Camera, Video, 
  FileImage, FilePlus, FileX, Lock, Unlock, Crop, RotateCw, Eye,
  Palette, Maximize, Minimize, Archive, BookOpen, Clock, TrendingUp,
  Shield, Award, Sparkles, Play, Pause, Square, Moon, Sun
} from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Progress } from './components/ui/progress';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Separator } from './components/ui/separator';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Slider } from './components/ui/slider';
import { Switch } from './components/ui/switch';
import { toast } from 'sonner';
import axios from 'axios';
import UnifiedSettingsPanel from './components/UnifiedSettingsPanel';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Enhanced conversion categories and options
const CONVERSION_TOOLS = {
  'Image Processing': {
    icon: <Image className="w-5 h-5" />,
    color: 'bg-blue-500',
    tools: {
      'jpg_to_png': { name: 'JPG to PNG', icon: <FileImage className="w-4 h-4" /> },
      'png_to_jpg': { name: 'PNG to JPG', icon: <FileImage className="w-4 h-4" /> },
      'webp_to_png': { name: 'WEBP to PNG', icon: <FileImage className="w-4 h-4" /> },
      'png_to_webp': { name: 'PNG to WEBP', icon: <FileImage className="w-4 h-4" /> },
      'heic_to_jpg': { name: 'HEIC to JPG', icon: <FileImage className="w-4 h-4" /> },
      'image_enhance': { name: 'Enhance Quality', icon: <Sparkles className="w-4 h-4" /> },
      'image_resize': { name: 'Resize Image', icon: <Maximize className="w-4 h-4" /> },
      'image_compress': { name: 'Compress Image', icon: <Minimize className="w-4 h-4" /> }
    }
  },
  'PDF Tools': {
    icon: <FileText className="w-5 h-5" />,
    color: 'bg-red-500',
    tools: {
      'merge_pdf': { name: 'Merge PDFs', icon: <FilePlus className="w-4 h-4" /> },
      'split_pdf': { name: 'Split PDF', icon: <FileX className="w-4 h-4" /> },
      'compress_pdf': { name: 'Compress PDF', icon: <Minimize className="w-4 h-4" /> },
      'rotate_pdf': { name: 'Rotate PDF', icon: <RotateCw className="w-4 h-4" /> },
      'pdf_ocr': { name: 'PDF OCR', icon: <Eye className="w-4 h-4" /> },
      'pdf_watermark': { name: 'Add Watermark', icon: <Shield className="w-4 h-4" /> },
      'pdf_protect': { name: 'Password Protect', icon: <Lock className="w-4 h-4" /> },
      'pdf_unlock': { name: 'Remove Password', icon: <Unlock className="w-4 h-4" /> }
    }
  },
  'Document Conversion': {
    icon: <File className="w-5 h-5" />,
    color: 'bg-green-500',
    tools: {
      'docx_to_pdf': { name: 'Word to PDF', icon: <FileText className="w-4 h-4" /> },
      'xlsx_to_pdf': { name: 'Excel to PDF', icon: <FileText className="w-4 h-4" /> },
      'pptx_to_pdf': { name: 'PowerPoint to PDF', icon: <FileText className="w-4 h-4" /> },
      'jpg_to_pdf': { name: 'Image to PDF', icon: <FileText className="w-4 h-4" /> },
      'pdf_to_jpg': { name: 'PDF to Images', icon: <FileImage className="w-4 h-4" /> },
      'pdf_to_docx': { name: 'PDF to Word', icon: <File className="w-4 h-4" /> }
    }
  },
  'Video & Audio': {
    icon: <Video className="w-5 h-5" />,
    color: 'bg-purple-500',
    tools: {
      'video_to_gif': { name: 'Video to GIF', icon: <Video className="w-4 h-4" /> },
      'webm_to_gif': { name: 'WEBM to GIF', icon: <Video className="w-4 h-4" /> },
      'video_compress': { name: 'Compress Video', icon: <Minimize className="w-4 h-4" /> },
      'audio_convert': { name: 'Convert Audio', icon: <Play className="w-4 h-4" /> }
    }
  },
  'Batch Operations': {
    icon: <Archive className="w-5 h-5" />,
    color: 'bg-orange-500',
    tools: {
      'batch_image_convert': { name: 'Batch Images', icon: <Archive className="w-4 h-4" /> },
      'batch_pdf_merge': { name: 'Batch PDF Merge', icon: <Archive className="w-4 h-4" /> },
      'batch_compress': { name: 'Batch Compress', icon: <Archive className="w-4 h-4" /> }
    }
  }
};

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low Priority', color: 'bg-gray-500' },
  { value: 'normal', label: 'Normal', color: 'bg-blue-500' },
  { value: 'high', label: 'High Priority', color: 'bg-orange-500' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-500' }
];

// Professional hero images
const HERO_IMAGES = [
  'https://images.unsplash.com/photo-1573164713988-8665fc963095',
  'https://images.unsplash.com/photo-1573164713712-03790a178651',
  'https://images.unsplash.com/photo-1754548930574-6a995e5eb5a7',
  'https://images.unsplash.com/photo-1754039985001-ccafee437736'
];

const FileIcon = ({ file }) => {
  const ext = file.name?.split('.').pop()?.toLowerCase();
  
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'].includes(ext)) {
    return <Image className="w-5 h-5 text-blue-500" />;
  } else if (['pdf'].includes(ext)) {
    return <FileText className="w-5 h-5 text-red-500" />;
  } else if (['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)) {
    return <File className="w-5 h-5 text-green-500" />;
  } else if (['mp4', 'avi', 'mov', 'webm'].includes(ext)) {
    return <Video className="w-5 h-5 text-purple-500" />;
  }
  return <File className="w-5 h-5 text-gray-500" />;
};

const JobCard = ({ job, onDownload, onCancel }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'processing': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      case 'cancelled': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-amber-100 text-amber-800 border-amber-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <Check className="w-4 h-4" />;
      case 'processing': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'failed': return <X className="w-4 h-4" />;
      case 'cancelled': return <Square className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getPriorityBadge = (priority) => {
    const priorityConfig = PRIORITY_OPTIONS.find(p => p.value === priority) || PRIORITY_OPTIONS[1];
    return (
      <Badge className={`${priorityConfig.color} text-white text-xs px-2 py-1`}>
        {priorityConfig.label}
      </Badge>
    );
  };

  // Find tool info
  let toolInfo = null;
  for (const category of Object.values(CONVERSION_TOOLS)) {
    if (category.tools[job.conversion_type]) {
      toolInfo = category.tools[job.conversion_type];
      break;
    }
  }

  return (
    <Card className="mb-4 transition-all duration-300 hover:shadow-lg border-0 bg-white/90 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {toolInfo?.icon}
            <CardTitle className="text-lg font-semibold">
              {toolInfo?.name || job.conversion_type}
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {job.priority && getPriorityBadge(job.priority)}
            <Badge className={`${getStatusColor(job.status)} flex items-center gap-1 px-3 py-1`}>
              {getStatusIcon(job.status)}
              {job.status}
            </Badge>
          </div>
        </div>
        <CardDescription className="text-sm text-gray-600 flex items-center gap-2">
          <span>Job ID: {job.id}</span>
          {job.metadata?.batch_name && (
            <>
              <Separator orientation="vertical" className="h-4" />
              <span>Batch: {job.metadata.batch_name}</span>
            </>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {job.status === 'processing' && (
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Progress: {job.current_stage || 'Processing'}</span>
              <span>{job.progress}%</span>
            </div>
            <Progress value={job.progress} className="w-full h-2" />
            {job.estimated_completion && (
              <p className="text-xs text-gray-500">
                ETA: {new Date(job.estimated_completion).toLocaleTimeString()}
              </p>
            )}
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
        
        {job.metadata && Object.keys(job.metadata).length > 0 && (
          <div className="bg-slate-50 rounded-lg p-3">
            <p className="text-sm font-medium text-gray-700 mb-2">Process Details:</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
              {job.metadata.file_count && (
                <span>Files: {job.metadata.file_count}</span>
              )}
              {job.metadata.total_input_size && (
                <span>Size: {(job.metadata.total_input_size / 1024 / 1024).toFixed(1)}MB</span>
              )}
              {job.metadata.compression_ratio && (
                <span>Saved: {job.metadata.compression_ratio}</span>
              )}
              {job.metadata.pages_processed && (
                <span>Pages: {job.metadata.pages_processed}</span>
              )}
            </div>
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
                  className="flex items-center gap-2 bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100"
                >
                  <Download className="w-4 h-4" />
                  Download {job.download_urls.length > 1 ? `${index + 1}` : ''}
                </Button>
              ))}
            </div>
          </div>
        )}
        
        {job.status === 'processing' && onCancel && (
          <Button
            onClick={() => onCancel(job.id)}
            variant="outline"
            size="sm"
            className="text-red-600 border-red-200 hover:bg-red-50"
          >
            <X className="w-4 h-4 mr-1" />
            Cancel
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

const AdvancedOptions = ({ conversionType, options, setOptions }) => {
  if (!conversionType) return null;

  const renderImageOptions = () => (
    <div className="space-y-4">
      {conversionType.includes('compress') && (
        <div className="space-y-2">
          <Label>Quality: {options.quality || 85}%</Label>
          <Slider
            value={[options.quality || 85]}
            onValueChange={(value) => setOptions(prev => ({ ...prev, quality: value[0] }))}
            max={100}
            min={10}
            step={5}
            className="w-full"
          />
        </div>
      )}
      
      {conversionType.includes('resize') && (
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="width">Width (px)</Label>
            <Input
              id="width"
              type="number"
              value={options.width || ''}
              onChange={(e) => setOptions(prev => ({ ...prev, width: parseInt(e.target.value) || undefined }))}
              placeholder="Auto"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="height">Height (px)</Label>
            <Input
              id="height"
              type="number"
              value={options.height || ''}
              onChange={(e) => setOptions(prev => ({ ...prev, height: parseInt(e.target.value) || undefined }))}
              placeholder="Auto"
            />
          </div>
        </div>
      )}
      
      {conversionType.includes('enhance') && (
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Sharpness: {(options.sharpness || 1.2).toFixed(1)}</Label>
            <Slider
              value={[options.sharpness || 1.2]}
              onValueChange={(value) => setOptions(prev => ({ ...prev, sharpness: value[0] }))}
              max={3}
              min={0.5}
              step={0.1}
              className="w-full"
            />
          </div>
          <div className="space-y-2">
            <Label>Contrast: {(options.contrast || 1.1).toFixed(1)}</Label>
            <Slider
              value={[options.contrast || 1.1]}
              onValueChange={(value) => setOptions(prev => ({ ...prev, contrast: value[0] }))}
              max={2}
              min={0.5}
              step={0.1}
              className="w-full"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              checked={options.denoise || false}
              onCheckedChange={(checked) => setOptions(prev => ({ ...prev, denoise: checked }))}
            />
            <Label>Reduce Noise</Label>
          </div>
        </div>
      )}
    </div>
  );

  const renderPdfOptions = () => (
    <div className="space-y-4">
      {conversionType.includes('protect') && (
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={options.password || ''}
            onChange={(e) => setOptions(prev => ({ ...prev, password: e.target.value }))}
            placeholder="Enter password"
          />
        </div>
      )}
      
      {conversionType.includes('watermark') && (
        <div className="space-y-2">
          <Label htmlFor="watermark_text">Watermark Text</Label>
          <Input
            id="watermark_text"
            value={options.watermark_text || ''}
            onChange={(e) => setOptions(prev => ({ ...prev, watermark_text: e.target.value }))}
            placeholder="CONFIDENTIAL"
          />
        </div>
      )}
      
      {conversionType.includes('rotate') && (
        <div className="space-y-2">
          <Label>Rotation</Label>
          <Select value={options.rotation?.toString() || '90'} onValueChange={(value) => setOptions(prev => ({ ...prev, rotation: parseInt(value) }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="90">90° Clockwise</SelectItem>
              <SelectItem value="180">180°</SelectItem>
              <SelectItem value="270">270° (90° Counter-clockwise)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}
      
      {conversionType.includes('ocr') && (
        <div className="space-y-2">
          <Label>OCR Language</Label>
          <Select value={options.language || 'eng'} onValueChange={(value) => setOptions(prev => ({ ...prev, language: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="eng">English</SelectItem>
              <SelectItem value="spa">Spanish</SelectItem>
              <SelectItem value="fra">French</SelectItem>
              <SelectItem value="deu">German</SelectItem>
              <SelectItem value="ita">Italian</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}
    </div>
  );

  const renderBatchOptions = () => (
    <div className="space-y-4">
      {conversionType.includes('image') && (
        <div className="space-y-2">
          <Label>Target Format</Label>
          <Select value={options.target_format || 'png'} onValueChange={(value) => setOptions(prev => ({ ...prev, target_format: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="png">PNG</SelectItem>
              <SelectItem value="jpg">JPG</SelectItem>
              <SelectItem value="webp">WEBP</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}
      
      <div className="space-y-2">
        <Label>Quality: {options.quality || 90}%</Label>
        <Slider
          value={[options.quality || 90]}
          onValueChange={(value) => setOptions(prev => ({ ...prev, quality: value[0] }))}
          max={100}
          min={50}
          step={5}
          className="w-full"
        />
      </div>
    </div>
  );

  // Determine which options to show based on conversion type
  if (conversionType.includes('image') || conversionType.includes('enhance') || conversionType.includes('resize') || conversionType.includes('compress')) {
    return renderImageOptions();
  } else if (conversionType.includes('pdf')) {
    return renderPdfOptions();
  } else if (conversionType.includes('batch')) {
    return renderBatchOptions();
  }
  
  return null;
};

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [conversionType, setConversionType] = useState('');
  const [priority, setPriority] = useState('normal');
  const [options, setOptions] = useState({});
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState({});
  const [dragActive, setDragActive] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [activeCategory, setActiveCategory] = useState('Image Processing');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showUnifiedSettings, setShowUnifiedSettings] = useState(false);

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
        toast.success('Conversion completed!', {
          description: 'Your files are ready for download'
        });
      } else if (data.error) {
        toast.error(`Conversion failed: ${data.error}`);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return ws;
  }, []);

  // Load stats on component mount
  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await axios.get(`${API}/stats`);
        setStats(response.data);
      } catch (error) {
        console.error('Error loading stats:', error);
      }
    };
    
    loadStats();
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
        priority: priority,
        options: options
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
      setOptions({});
      
      toast.success('Conversion started!', {
        description: `Job ${job.id} is now processing`
      });
      
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
      
      toast.success('File downloaded successfully!');
      
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download file');
    }
  };

  const cancelJob = async (jobId) => {
    try {
      await axios.delete(`${API}/jobs/${jobId}`);
      setJobs(prev => prev.map(job => 
        job.id === jobId 
          ? { ...job, status: 'cancelled' }
          : job
      ));
      toast.success('Job cancelled successfully');
    } catch (error) {
      console.error('Cancel error:', error);
      toast.error('Failed to cancel job');
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      darkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100'
    }`}>
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900">
        <div className="absolute inset-0 bg-black/20"></div>
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `url(${HERO_IMAGES[0]})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'blur(1px)'
          }}
        ></div>
        <div className="relative container mx-auto px-4 py-16">
          {/* Header Controls */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setDarkMode(!darkMode)}
              className="text-white hover:bg-white/20"
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowUnifiedSettings(true)}
              className="text-white hover:bg-white/20"
            >
              <Settings className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="text-center text-white">
            <div className="flex items-center justify-center mb-6">
              <div className="bg-white/10 backdrop-blur-sm rounded-full p-4 border border-white/20">
                <Zap className="w-12 h-12 text-blue-400" />
              </div>
            </div>
            <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
              Converte Pro
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto mb-8">
              The most powerful file conversion platform on the internet. Transform any file format with 
              professional-grade tools, advanced processing, and lightning-fast results.
            </p>
            <div className="flex items-center justify-center gap-8 text-sm text-blue-200">
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                <span>Enterprise Grade</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                <span>Secure Processing</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                <span>Lightning Fast</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className={`${darkMode ? 'bg-slate-800/80 border-slate-700' : 'bg-white/80 border-gray-200'} backdrop-blur-sm border-b`}>
        <div className="container mx-auto px-4 py-4">
          <div className={`flex items-center justify-center gap-8 text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-500" />
              <span>{stats.success_rate || '0%'} Success Rate</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-500" />
              <span>{stats.total_jobs || 0} Files Converted</span>
            </div>
            <div className="flex items-center gap-2">
              <Archive className="w-4 h-4 text-green-500" />
              <span>{stats.total_data_processed || '0MB'} Data Processed</span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Tool Selection Panel */}
          <div className="lg:col-span-1">
            <Card className={`sticky top-8 shadow-xl border-0 backdrop-blur-sm ${darkMode ? 'bg-slate-800/90' : 'bg-white/90'}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Settings className="w-6 h-6 text-blue-600" />
                  Conversion Tools
                </CardTitle>
                <CardDescription>
                  Choose from professional-grade conversion tools
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={activeCategory} onValueChange={setActiveCategory} className="w-full">
                  <TabsList className="grid w-full grid-cols-1 h-auto gap-2 bg-transparent p-0">
                    {Object.entries(CONVERSION_TOOLS).map(([category, info]) => (
                      <TabsTrigger
                        key={category}
                        value={category}
                        className="flex items-center gap-2 w-full justify-start data-[state=active]:bg-blue-100 data-[state=active]:text-blue-700 p-3 rounded-lg"
                      >
                        <div className={`${info.color} p-1 rounded text-white`}>
                          {info.icon}
                        </div>
                        <span className="font-medium">{category}</span>
                      </TabsTrigger>
                    ))}
                  </TabsList>
                  
                  {Object.entries(CONVERSION_TOOLS).map(([category, info]) => (
                    <TabsContent key={category} value={category} className="mt-6">
                      <div className="grid gap-2">
                        {Object.entries(info.tools).map(([key, tool]) => (
                          <Button
                            key={key}
                            variant={conversionType === key ? "default" : "outline"}
                            onClick={() => setConversionType(key)}
                            className="flex items-center gap-2 justify-start h-auto p-3"
                          >
                            {tool.icon}
                            <span>{tool.name}</span>
                          </Button>
                        ))}
                      </div>
                    </TabsContent>
                  ))}
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Upload Section */}
            <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2 text-2xl">
                      <Upload className="w-6 h-6 text-blue-600" />
                      File Processing Center
                    </CardTitle>
                    <CardDescription>
                      Upload your files and configure processing options
                    </CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center gap-2"
                  >
                    <Settings className="w-4 h-4" />
                    {showAdvanced ? 'Hide' : 'Show'} Advanced
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Priority Selection */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Processing Priority</Label>
                    <Select value={priority} onValueChange={setPriority}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {PRIORITY_OPTIONS.map(option => (
                          <SelectItem key={option.value} value={option.value}>
                            <div className="flex items-center gap-2">
                              <div className={`w-2 h-2 rounded-full ${option.color}`}></div>
                              {option.label}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Selected Tool</Label>
                    <div className="p-2 bg-gray-50 rounded border text-sm">
                      {conversionType ? (
                        Object.values(CONVERSION_TOOLS).flatMap(category => 
                          Object.entries(category.tools)
                        ).find(([key]) => key === conversionType)?.[1]?.name || conversionType
                      ) : (
                        'No tool selected'
                      )}
                    </div>
                  </div>
                </div>

                {/* Advanced Options */}
                {showAdvanced && conversionType && (
                  <div className="bg-slate-50 rounded-lg p-4 space-y-4">
                    <h3 className="font-medium text-gray-700 flex items-center gap-2">
                      <Settings className="w-4 h-4" />
                      Advanced Options
                    </h3>
                    <AdvancedOptions 
                      conversionType={conversionType}
                      options={options}
                      setOptions={setOptions}
                    />
                  </div>
                )}

                {/* File Drop Zone */}
                <div
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                    dragActive
                      ? 'border-blue-500 bg-blue-50 scale-105'
                      : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="flex flex-col items-center gap-4">
                    <div className="bg-blue-100 rounded-full p-4">
                      <Upload className="w-8 h-8 text-blue-600" />
                    </div>
                    <div>
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
                        <Upload className="w-4 h-4 mr-2" />
                        Choose Files
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Selected Files */}
                {selectedFiles.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-medium text-gray-700 flex items-center gap-2">
                      <File className="w-4 h-4" />
                      Selected Files ({selectedFiles.length})
                    </h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 transition-all hover:bg-gray-100">
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

                {/* Start Conversion Button */}
                <Button
                  onClick={startConversion}
                  disabled={!conversionType || selectedFiles.length === 0 || processing}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-4 text-lg shadow-lg"
                >
                  {processing ? (
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  ) : (
                    <Zap className="w-5 h-5 mr-2" />
                  )}
                  {processing ? 'Processing...' : 'Start Conversion'}
                </Button>
              </CardContent>
            </Card>

            {/* Jobs Section */}
            <Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Monitor className="w-6 h-6 text-green-600" />
                  Processing Queue
                </CardTitle>
                <CardDescription>
                  Monitor your conversion jobs and download results
                </CardDescription>
              </CardHeader>
              <CardContent>
                {jobs.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="bg-gray-100 rounded-full p-6 w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                      <FileText className="w-8 h-8 text-gray-400" />
                    </div>
                    <p className="text-gray-500 text-lg">No conversion jobs yet</p>
                    <p className="text-sm text-gray-400 mt-2">
                      Select a tool and upload files to get started
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {jobs.map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        onDownload={downloadFile}
                        onCancel={cancelJob}
                      />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Feature Showcase */}
        <div className="mt-16 grid md:grid-cols-4 gap-6">
          <Card className="text-center shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300">
            <CardContent className="pt-6">
              <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Image className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Advanced Image Processing</h3>
              <p className="text-gray-600 text-sm">
                Professional image enhancement, resizing, and format conversion with quality controls
              </p>
            </CardContent>
          </Card>
          
          <Card className="text-center shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300">
            <CardContent className="pt-6">
              <div className="bg-red-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <FileText className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Professional PDF Suite</h3>
              <p className="text-gray-600 text-sm">
                OCR, watermarking, password protection, and advanced PDF manipulation tools
              </p>
            </CardContent>
          </Card>
          
          <Card className="text-center shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300">
            <CardContent className="pt-6">
              <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Video className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Media Conversion</h3>
              <p className="text-gray-600 text-sm">
                Video to GIF, audio format conversion, and media compression tools
              </p>
            </CardContent>
          </Card>

          <Card className="text-center shadow-lg border-0 bg-white/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300">
            <CardContent className="pt-6">
              <div className="bg-orange-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Archive className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Batch Processing</h3>
              <p className="text-gray-600 text-sm">
                Process hundreds of files simultaneously with intelligent queue management
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Unified Settings Panel */}
      <UnifiedSettingsPanel
        conversionType={conversionType}
        options={options}
        setOptions={setOptions}
        isOpen={showUnifiedSettings}
        onClose={() => setShowUnifiedSettings(false)}
      />
    </div>
  );
}

export default App;