import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Slider } from './ui/slider';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Separator } from './ui/separator';
import { Badge } from './ui/badge';
import { 
  Settings, Image, FileText, Video, File, Palette, 
  Maximize, Minimize, RotateCw, Lock, Unlock, Eye,
  Crop, Sparkles, Shield, Archive, Zap
} from 'lucide-react';

const UnifiedSettingsPanel = ({ 
  conversionType, 
  options, 
  setOptions, 
  isOpen, 
  onClose 
}) => {
  const [activeTab, setActiveTab] = useState('general');

  // Reset options when conversion type changes
  useEffect(() => {
    if (conversionType) {
      setOptions(getDefaultOptions(conversionType));
    }
  }, [conversionType]);

  const getDefaultOptions = (type) => {
    const defaults = {
      // Image options
      quality: 85,
      width: null,
      height: null,
      maintain_aspect: true,
      dpi: 300,
      rotation: 0,
      sharpness: 1.2,
      contrast: 1.1,
      brightness: 1.0,
      denoise: false,
      
      // PDF options
      password: '',
      watermark_text: 'CONFIDENTIAL',
      watermark_opacity: 0.5,
      watermark_position: 'center',
      rotation: 90,
      language: 'eng',
      page_range: '',
      compression_level: 'medium',
      
      // Video options
      target_format: 'mp4',
      resolution: '1080p',
      fps: 30,
      bitrate: '2000k',
      audio_codec: 'aac',
      audio_bitrate: '128k',
      
      // Audio options
      audio_format: 'mp3',
      audio_quality: 'high',
      sample_rate: 44100,
      
      // Batch options
      batch_name: '',
      target_format: 'png',
      preserve_structure: true,
      
      // AI options
      ai_language: 'en',
      ai_model: 'gpt-3.5-turbo',
      extract_tables: true,
      extract_images: true,
    };
    
    return { ...defaults, ...options };
  };

  const getConversionCategory = (type) => {
    if (type.includes('image') || type.includes('jpg') || type.includes('png') || type.includes('webp')) {
      return 'image';
    } else if (type.includes('pdf')) {
      return 'pdf';
    } else if (type.includes('video') || type.includes('gif')) {
      return 'video';
    } else if (type.includes('audio')) {
      return 'audio';
    } else if (type.includes('batch')) {
      return 'batch';
    } else if (type.includes('doc') || type.includes('xls') || type.includes('ppt')) {
      return 'document';
    }
    return 'general';
  };

  const renderImageSettings = () => (
    <div className="space-y-6">
      {/* Quality Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Quality & Compression</Label>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Quality: {options.quality}%</span>
            <Badge variant="outline">{options.quality >= 90 ? 'High' : options.quality >= 70 ? 'Medium' : 'Low'}</Badge>
          </div>
          <Slider
            value={[options.quality]}
            onValueChange={(value) => setOptions(prev => ({ ...prev, quality: value[0] }))}
            max={100}
            min={10}
            step={5}
            className="w-full"
          />
        </div>
      </div>

      <Separator />

      {/* Resize Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Resize & Dimensions</Label>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="width">Width (px)</Label>
            <Input
              id="width"
              type="number"
              value={options.width || ''}
              onChange={(e) => setOptions(prev => ({ ...prev, width: parseInt(e.target.value) || null }))}
              placeholder="Auto"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="height">Height (px)</Label>
            <Input
              id="height"
              type="number"
              value={options.height || ''}
              onChange={(e) => setOptions(prev => ({ ...prev, height: parseInt(e.target.value) || null }))}
              placeholder="Auto"
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Switch
            checked={options.maintain_aspect}
            onCheckedChange={(checked) => setOptions(prev => ({ ...prev, maintain_aspect: checked }))}
          />
          <Label className="text-sm">Maintain aspect ratio</Label>
        </div>
      </div>

      <Separator />

      {/* DPI Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Resolution & DPI</Label>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>DPI: {options.dpi}</span>
            <Badge variant="outline">{options.dpi >= 300 ? 'Print Quality' : options.dpi >= 150 ? 'High Quality' : 'Web Quality'}</Badge>
          </div>
          <Slider
            value={[options.dpi]}
            onValueChange={(value) => setOptions(prev => ({ ...prev, dpi: value[0] }))}
            max={600}
            min={72}
            step={1}
            className="w-full"
          />
        </div>
      </div>

      <Separator />

      {/* Rotation Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Rotation</Label>
        <Select value={options.rotation?.toString() || '0'} onValueChange={(value) => setOptions(prev => ({ ...prev, rotation: parseInt(value) }))}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="0">No rotation</SelectItem>
            <SelectItem value="90">90° Clockwise</SelectItem>
            <SelectItem value="180">180°</SelectItem>
            <SelectItem value="270">270° (90° Counter-clockwise)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Enhancement Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Image Enhancement</Label>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Sharpness: {options.sharpness?.toFixed(1) || '1.2'}</Label>
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
            <Label>Contrast: {options.contrast?.toFixed(1) || '1.1'}</Label>
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
            <Label className="text-sm">Reduce noise</Label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPdfSettings = () => (
    <div className="space-y-6">
      {/* Security Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Security & Protection</Label>
        <div className="space-y-2">
          <Label htmlFor="password">Password Protection</Label>
          <Input
            id="password"
            type="password"
            value={options.password || ''}
            onChange={(e) => setOptions(prev => ({ ...prev, password: e.target.value }))}
            placeholder="Enter password (optional)"
          />
        </div>
      </div>

      <Separator />

      {/* Watermark Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Watermark</Label>
        <div className="space-y-2">
          <Label htmlFor="watermark_text">Watermark Text</Label>
          <Input
            id="watermark_text"
            value={options.watermark_text || ''}
            onChange={(e) => setOptions(prev => ({ ...prev, watermark_text: e.target.value }))}
            placeholder="CONFIDENTIAL"
          />
        </div>
        <div className="space-y-2">
          <Label>Opacity: {Math.round((options.watermark_opacity || 0.5) * 100)}%</Label>
          <Slider
            value={[options.watermark_opacity || 0.5]}
            onValueChange={(value) => setOptions(prev => ({ ...prev, watermark_opacity: value[0] }))}
            max={1}
            min={0.1}
            step={0.1}
            className="w-full"
          />
        </div>
        <div className="space-y-2">
          <Label>Position</Label>
          <Select value={options.watermark_position || 'center'} onValueChange={(value) => setOptions(prev => ({ ...prev, watermark_position: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="top-left">Top Left</SelectItem>
              <SelectItem value="top-right">Top Right</SelectItem>
              <SelectItem value="center">Center</SelectItem>
              <SelectItem value="bottom-left">Bottom Left</SelectItem>
              <SelectItem value="bottom-right">Bottom Right</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Separator />

      {/* OCR Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">OCR & Text Recognition</Label>
        <div className="space-y-2">
          <Label>Language</Label>
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
              <SelectItem value="por">Portuguese</SelectItem>
              <SelectItem value="rus">Russian</SelectItem>
              <SelectItem value="chi_sim">Chinese (Simplified)</SelectItem>
              <SelectItem value="jpn">Japanese</SelectItem>
              <SelectItem value="kor">Korean</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Separator />

      {/* Page Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Page Processing</Label>
        <div className="space-y-2">
          <Label htmlFor="page_range">Page Range (optional)</Label>
          <Input
            id="page_range"
            value={options.page_range || ''}
            onChange={(e) => setOptions(prev => ({ ...prev, page_range: e.target.value }))}
            placeholder="e.g., 1-5, 10, 15-20"
          />
        </div>
        <div className="space-y-2">
          <Label>Compression Level</Label>
          <Select value={options.compression_level || 'medium'} onValueChange={(value) => setOptions(prev => ({ ...prev, compression_level: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low (Best Quality)</SelectItem>
              <SelectItem value="medium">Medium (Balanced)</SelectItem>
              <SelectItem value="high">High (Smaller Size)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  const renderVideoSettings = () => (
    <div className="space-y-6">
      {/* Format Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Output Format</Label>
        <Select value={options.target_format || 'mp4'} onValueChange={(value) => setOptions(prev => ({ ...prev, target_format: value }))}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="mp4">MP4</SelectItem>
            <SelectItem value="avi">AVI</SelectItem>
            <SelectItem value="mov">MOV</SelectItem>
            <SelectItem value="mkv">MKV</SelectItem>
            <SelectItem value="webm">WebM</SelectItem>
            <SelectItem value="gif">GIF</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Resolution Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Resolution & Quality</Label>
        <div className="space-y-2">
          <Label>Resolution</Label>
          <Select value={options.resolution || '1080p'} onValueChange={(value) => setOptions(prev => ({ ...prev, resolution: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="480p">480p (SD)</SelectItem>
              <SelectItem value="720p">720p (HD)</SelectItem>
              <SelectItem value="1080p">1080p (Full HD)</SelectItem>
              <SelectItem value="1440p">1440p (2K)</SelectItem>
              <SelectItem value="2160p">2160p (4K)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Frame Rate: {options.fps} FPS</Label>
          <Slider
            value={[options.fps || 30]}
            onValueChange={(value) => setOptions(prev => ({ ...prev, fps: value[0] }))}
            max={60}
            min={15}
            step={5}
            className="w-full"
          />
        </div>
      </div>

      <Separator />

      {/* Audio Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Audio Settings</Label>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Audio Codec</Label>
            <Select value={options.audio_codec || 'aac'} onValueChange={(value) => setOptions(prev => ({ ...prev, audio_codec: value }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="aac">AAC</SelectItem>
                <SelectItem value="mp3">MP3</SelectItem>
                <SelectItem value="ac3">AC3</SelectItem>
                <SelectItem value="flac">FLAC</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Audio Bitrate</Label>
            <Select value={options.audio_bitrate || '128k'} onValueChange={(value) => setOptions(prev => ({ ...prev, audio_bitrate: value }))}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="64k">64 kbps</SelectItem>
                <SelectItem value="128k">128 kbps</SelectItem>
                <SelectItem value="192k">192 kbps</SelectItem>
                <SelectItem value="256k">256 kbps</SelectItem>
                <SelectItem value="320k">320 kbps</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAudioSettings = () => (
    <div className="space-y-6">
      {/* Format Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Output Format</Label>
        <Select value={options.audio_format || 'mp3'} onValueChange={(value) => setOptions(prev => ({ ...prev, audio_format: value }))}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="mp3">MP3</SelectItem>
            <SelectItem value="wav">WAV</SelectItem>
            <SelectItem value="aac">AAC</SelectItem>
            <SelectItem value="flac">FLAC</SelectItem>
            <SelectItem value="ogg">OGG</SelectItem>
            <SelectItem value="m4a">M4A</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Quality Settings */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Quality Settings</Label>
        <div className="space-y-2">
          <Label>Quality Level</Label>
          <Select value={options.audio_quality || 'high'} onValueChange={(value) => setOptions(prev => ({ ...prev, audio_quality: value }))}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low (64 kbps)</SelectItem>
              <SelectItem value="medium">Medium (128 kbps)</SelectItem>
              <SelectItem value="high">High (192 kbps)</SelectItem>
              <SelectItem value="lossless">Lossless</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label>Sample Rate: {options.sample_rate} Hz</Label>
          <Slider
            value={[options.sample_rate || 44100]}
            onValueChange={(value) => setOptions(prev => ({ ...prev, sample_rate: value[0] }))}
            max={96000}
            min={8000}
            step={1000}
            className="w-full"
          />
        </div>
      </div>
    </div>
  );

  const renderBatchSettings = () => (
    <div className="space-y-6">
      {/* Batch Info */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Batch Information</Label>
        <div className="space-y-2">
          <Label htmlFor="batch_name">Batch Name (optional)</Label>
          <Input
            id="batch_name"
            value={options.batch_name || ''}
            onChange={(e) => setOptions(prev => ({ ...prev, batch_name: e.target.value }))}
            placeholder="My batch conversion"
          />
        </div>
      </div>

      <Separator />

      {/* Target Format */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Target Format</Label>
        <Select value={options.target_format || 'png'} onValueChange={(value) => setOptions(prev => ({ ...prev, target_format: value }))}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="png">PNG</SelectItem>
            <SelectItem value="jpg">JPG</SelectItem>
            <SelectItem value="webp">WEBP</SelectItem>
            <SelectItem value="pdf">PDF</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Processing Options */}
      <div className="space-y-3">
        <Label className="text-sm font-medium">Processing Options</Label>
        <div className="flex items-center space-x-2">
          <Switch
            checked={options.preserve_structure}
            onCheckedChange={(checked) => setOptions(prev => ({ ...prev, preserve_structure: checked }))}
          />
          <Label className="text-sm">Preserve folder structure</Label>
        </div>
      </div>
    </div>
  );

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div className="text-center py-8">
        <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-700 mb-2">General Settings</h3>
        <p className="text-gray-500 text-sm">
          Select a conversion tool to see specific settings and options.
        </p>
      </div>
    </div>
  );

  const getTabContent = () => {
    const category = getConversionCategory(conversionType);
    
    switch (category) {
      case 'image':
        return renderImageSettings();
      case 'pdf':
        return renderPdfSettings();
      case 'video':
        return renderVideoSettings();
      case 'audio':
        return renderAudioSettings();
      case 'batch':
        return renderBatchSettings();
      default:
        return renderGeneralSettings();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Conversion Settings
            </CardTitle>
            <CardDescription>
              Configure all options for your {conversionType || 'conversion'} in one place
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ×
          </Button>
        </CardHeader>
        <CardContent className="overflow-y-auto max-h-[calc(90vh-120px)]">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="general" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                General
              </TabsTrigger>
              <TabsTrigger value="image" className="flex items-center gap-2">
                <Image className="w-4 h-4" />
                Image
              </TabsTrigger>
              <TabsTrigger value="pdf" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                PDF
              </TabsTrigger>
              <TabsTrigger value="video" className="flex items-center gap-2">
                <Video className="w-4 h-4" />
                Video
              </TabsTrigger>
              <TabsTrigger value="audio" className="flex items-center gap-2">
                <File className="w-4 h-4" />
                Audio
              </TabsTrigger>
              <TabsTrigger value="batch" className="flex items-center gap-2">
                <Archive className="w-4 h-4" />
                Batch
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="general" className="mt-6">
              {renderGeneralSettings()}
            </TabsContent>
            
            <TabsContent value="image" className="mt-6">
              {renderImageSettings()}
            </TabsContent>
            
            <TabsContent value="pdf" className="mt-6">
              {renderPdfSettings()}
            </TabsContent>
            
            <TabsContent value="video" className="mt-6">
              {renderVideoSettings()}
            </TabsContent>
            
            <TabsContent value="audio" className="mt-6">
              {renderAudioSettings()}
            </TabsContent>
            
            <TabsContent value="batch" className="mt-6">
              {renderBatchSettings()}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default UnifiedSettingsPanel;